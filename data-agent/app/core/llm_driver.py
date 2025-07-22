# app/core/llm_driver.py
from __future__ import annotations

import re
import requests
from functools import lru_cache
from typing import List, Tuple

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
Input: a question about a pandas DataFrame named df (with given columns).
Output: ONLY Python code. No prose, no explanation.
Rules:
- Use pandas as pd and matplotlib.pyplot as plt if plotting.
- Store table outputs in variables like result_df/result_series.
- If you create a plot, save it to a BytesIO variable named png.
- Do not import anything or access disk/network.
- Use only the provided column names.
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

# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------
def _extract_code(text: str) -> str:
    m = re.search(r"```python(.*?)```", text, re.S | re.I)
    if m:
        return m.group(1).strip()
    return text.strip()


def _build_prompt(question: str, columns: list[str]) -> str:
    shots = ""
    for q, code in FEW_SHOTS:
        shots += f"Q: {q}\n```python\n{code}\n```\n\n"
    cols = ", ".join(columns)
    return f"""{SYSTEM_PROMPT}

DataFrame columns: {cols}

{shots}Q: {question}
```python
"""


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
def ask_llm(question: str, columns: tuple[str, ...]) -> str:
    ok, msg, model = check_model_ready()
    if not ok:
        return f"# LLM unavailable: {msg}"

    prompt = _build_prompt(question, list(columns))
    resp = _post_ollama("/generate", {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    })
    raw = resp.get("response", "")
    return _extract_code(raw)
