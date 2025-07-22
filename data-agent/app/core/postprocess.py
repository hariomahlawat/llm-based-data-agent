# app/core/postprocess.py
from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def figure_to_png(fig: Figure) -> BytesIO:
    """
    Convert a matplotlib Figure to a PNG buffer, close the figure to free memory.
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def extract_outputs(locals_out: Dict[str, Any]) -> Tuple[
    List[pd.DataFrame],  # dataframes (Series converted to DF)
    List[BytesIO],       # png buffers
    List[Figure],        # raw matplotlib figures (rarely used after conversion)
    List[str]            # plain text blocks (keys starting with 'text')
]:
    """
    Inspect the locals() dict produced by the safe executor and collect
    renderable artifacts.

    - DataFrames: pd.DataFrame objects, or pd.Series promoted to 1-col DFs.
    - PNGs: any BytesIO buffers (model is asked to name plot buffer 'png').
    - Figures: matplotlib Figure objects (converted later to PNG in UI).
    - Text: variables whose key starts with 'text' and value is str.
    """
    dfs: List[pd.DataFrame] = []
    pngs: List[BytesIO] = []
    figs: List[Figure] = []
    texts: List[str] = []

    for key, val in locals_out.items():
        if isinstance(val, pd.DataFrame):
            dfs.append(val)
        elif isinstance(val, pd.Series):
            dfs.append(val.to_frame(name=key))
        elif isinstance(val, BytesIO):
            pngs.append(val)
        elif isinstance(val, Figure):
            figs.append(val)
        elif isinstance(val, str) and key.lower().startswith("text"):
            texts.append(val)

    return dfs, pngs, figs, texts
