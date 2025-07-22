# app/core/llm_driver.py
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import List, Tuple

import pandas as pd
import requests  # type: ignore

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
# If your Streamlit app runs inside Docker and Ollama runs on host:
# OLLAMA_URL = "http://host.docker.internal:11434/api"
OLLAMA_URL = "http://localhost:11434/api"

PREFERRED_MODELS: List[str] = [
    "mistral:7b-instruct",
    "llama3:8b-instruct",
    "llama3:8b-instruct-q3_K_L",
    "phi3:3.8b-mini-instruct"
]

SYSTEM_PROMPT = """You are a Python data analyst.
Input: a question about a pandas DataFrame named df (with given schema).
Output: a JSON object with keys 'intent' and 'code'. No extra prose.
Rules:
- Use pandas as pd and matplotlib.pyplot as plt if plotting.
- Store table outputs in variables like result_df/result_series.
- If you create a plot, save it to a BytesIO variable named png.
- Do not import anything or access disk/network.
- Use only the provided column names.
- Return valid JSON only, no code fences.
"""

FEW_SHOTS: List[Tuple[str, str]] = [
    (
        "Show total sales by region",
        "result_df = df.groupby('region')['sales'].sum().reset_index()\nprint(result_df.head())"
    ),
    (
        "Histogram of unit_price",
        "from io import BytesIO\nfig, ax = plt.subplots()\n"
        "df['unit_price'].hist(bins=30, ax=ax)\nax.set_title('unit_price histogram')\n"
        "png = BytesIO()\nfig.savefig(png, format='png', bbox_inches='tight')\n"
        "png.seek(0)\nplt.close(fig)"
    ),
]


def _schema_desc(df: pd.DataFrame, redact_cols: List[str] | None = None) -> str:
    lines: List[str] = []
    redact_set = set(redact_cols or [])
    for col in df.columns:
        dtype = str(df[col].dtype)
        if col in redact_set:
            sample = "<redacted>"
        else:
            series = df[col].dropna()
            if series.empty:
                sample = ""  # no values
            elif pd.api.types.is_numeric_dtype(series):
                sample_vals = series.unique()[:3]
                sample = f"sample values: {', '.join(map(str, sample_vals))}"
            else:
                top = series.value_counts().index[:3].tolist()
                sample = f"top categories: {', '.join(map(str, top))}"
        lines.append(f"- {col} ({dtype}): {sample}")
    return "\n".join(lines)

# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------
def _extract_json(text: str) -> tuple[str, str]:
    try:
        data = json.loads(text)
        return data.get("intent", ""), data.get("code", "")
    except Exception:
        return "", text.strip()


def _build_prompt(question: str, df: pd.DataFrame, redact_cols: List[str] | None = None) -> str:
    shots = ""
    for q, code in FEW_SHOTS:
        shots += f"Q: {q}\n{{\"intent\": \"demo\", \"code\": \"{code}\"}}\n\n"
    schema = _schema_desc(df, redact_cols=redact_cols)
    return (
        f"{SYSTEM_PROMPT}\n\nDataFrame schema:\n{schema}\n\n{shots}Q: {question}\n"
    )


def _post_ollama(path: str, payload: dict, timeout: int = 120) -> dict:
    r = requests.post(f"{OLLAMA_URL}{path}", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def check_model_ready() -> tuple[bool, str, str]:
    """
    Returns (ok, message, chosen_model).
    ok=False if Ollama not reachable or no model fits.
    """
    try:
        models = _post_ollama("/tags", {})
    except Exception as e:
        return False, f"Ollama unreachable: {e}", ""

    names = [m.get("name") for m in models.get("models", [])]

    for pref in PREFERRED_MODELS:
        if pref in names:
            return True, "OK", pref

    if names:
        return True, f"Using first available model: {names[0]}", names[0]

    return False, "No models installed. Try: ollama pull mistral:7b-instruct", ""


@lru_cache(maxsize=128)
def ask_llm(question: str, df: pd.DataFrame, retries: int = 1) -> tuple[str, str]:
    ok, msg, model = check_model_ready()
    if not ok:
        return "", f"# LLM unavailable: {msg}"

    error_msg = ""
    intent = ""
    code = ""
    for _ in range(retries + 1):
        q = question
        if error_msg:
            q += f"\nPrevious attempt failed with: {error_msg}\nReturn fixed JSON only."
        pii_env = os.environ.get("PII_COLUMNS", "")
        redact_cols = [c.strip() for c in pii_env.split(",") if c.strip()]
        prompt = _build_prompt(q, df, redact_cols=redact_cols)
        resp = _post_ollama(
            "/generate",
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
        )
        raw = resp.get("response", "")
        intent, code = _extract_json(raw)
        try:
            from .safe_exec import _analyze  # type: ignore

            _analyze(code)
            break
        except Exception as e:
            error_msg = str(e)
    return intent, code
