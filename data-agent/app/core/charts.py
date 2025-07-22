import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from typing import Optional, Sequence


def _fig_to_png(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def line_plot(df: pd.DataFrame, x: str, y: str):
    fig, ax = plt.subplots()
    df.plot(x=x, y=y, ax=ax)
    ax.set_title(f"{y} vs {x}")
    return _fig_to_png(fig)


def bar_plot(df: pd.DataFrame, x: str, y: Optional[str], agg: str = "sum"):
    """
    If y provided, aggregates y by x using agg (sum, mean, count etc).
    If y is None, counts x categories.
    """
    fig, ax = plt.subplots()
    if y:
        grouped = getattr(df.groupby(x)[y], agg)()
        grouped.plot(kind="bar", ax=ax)
        ax.set_ylabel(f"{agg}({y})")
    else:
        df[x].value_counts().plot(kind="bar", ax=ax)
        ax.set_ylabel("count")
    ax.set_xlabel(x)
    ax.set_title("Bar chart")
    return _fig_to_png(fig)


def hist_plot(df: pd.DataFrame, cols: Sequence[str], bins: int = 30):
    """
    Multiple numeric columns allowed, each will be overlaid.
    """
    fig, ax = plt.subplots()
    df[list(cols)].plot(kind="hist", bins=bins, alpha=0.6, ax=ax)
    ax.set_title(f"Histogram ({', '.join(cols)})")
    ax.set_xlabel("value")
    ax.set_ylabel("frequency")
    return _fig_to_png(fig)


def box_plot(df: pd.DataFrame, cols: Sequence[str]):
    fig, ax = plt.subplots()
    df[list(cols)].plot(kind="box", ax=ax)
    ax.set_title(f"Box plot ({', '.join(cols)})")
    return _fig_to_png(fig)


def scatter_plot(df: pd.DataFrame, x: str, y: str, hue: Optional[str] = None):
    """
    Matplotlib scatter with optional color grouping (hue).
    """
    fig, ax = plt.subplots()
    if hue and hue in df.columns:
        for val, chunk in df.groupby(hue):
            ax.scatter(chunk[x], chunk[y], label=str(val), alpha=0.7)
        ax.legend(title=hue)
    else:
        ax.scatter(df[x], df[y], alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"Scatter: {y} vs {x}")
    return _fig_to_png(fig)

