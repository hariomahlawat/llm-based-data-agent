from __future__ import annotations

from typing import Any, Dict, List
import streamlit as st


def get_history() -> List[Dict[str, Any]]:
    """Return history list stored in session_state."""
    return st.session_state.setdefault("history", [])


def add_record(prompt: str, code: str, dfs: List[str], pngs: List[bytes]) -> None:
    """Append a record to history."""
    record = {
        "prompt": prompt,
        "code": code,
        "dfs": dfs,
        "pngs": pngs,
    }
    get_history().append(record)


def clear_history() -> None:
    """Remove all records."""
    st.session_state["history"] = []
