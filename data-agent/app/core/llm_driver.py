"""Lightweight wrapper for calling a local LLM via Ollama.

This module exposes two helper functions used by the Streamlit UI:

``ask_llm``
    Convert a natural language question about ``df`` into executable Python code.

``check_model_ready``
    Verify that the configured model is available from the Ollama server.

The original implementation lived in a file named ``llm_driver`` (without the
``.py`` extension).  When Python imports ``core.llm_driver`` it only considers
``llm_driver.py``, therefore the UI could not find ``ask_llm`` which resulted in
``ImportError``.  The logic from that file is consolidated here so that the
module behaves as expected.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import List

import requests


OLLAMA_URL = "http://localhost:11434/api"
MODEL_NAME = "mistral:7b-instruct"  # change to what you actually pulled

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

FEW_SHOTS: List[tuple[str, str]] = [
    (
        "Show total sales by region",
        "result_df = df.groupby('region')['sales'].sum().reset_index()\nprint(result_df.head())",
    ),
    (
        "Histogram of unit_price",
        "from io import BytesIO\nfig, ax = plt.subplots()\ndf['unit_price'].hist(bins=30, ax=ax)\nax.set_title('unit_price histogram')\npng = BytesIO()\nfig.savefig(png, format='png', bbox_inches='tight')\npng.seek(0)\nplt.close(fig)",
    ),
]


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


def check_model_ready(model: str = MODEL_NAME) -> tuple[bool, str]:
    """Check that ``model`` exists on the local Ollama server."""

    try:
        models = _post_ollama("/tags", {})  # list models
    except Exception as e:  # pragma: no cover - network failure
        return False, f"Ollama unreachable: {e}"

    names = [m.get("name") for m in models.get("models", [])]
    if model not in names:
        return False, f"Model '{model}' not found. Pull with: ollama pull {model}"
    return True, "OK"


@lru_cache(maxsize=128)
def ask_llm(question: str, columns: tuple[str, ...]) -> str:
    """Return Python code answering ``question`` about ``df`` with ``columns``."""

    ok, msg = check_model_ready()
    if not ok:
        # return a trivial fallback (user can still paste code manually)
        return "# LLM unavailable: " + msg

    prompt = _build_prompt(question, list(columns))
    resp = _post_ollama(
        "/generate",
        {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        },
    )
    raw = resp.get("response", "")
    return _extract_code(raw)

