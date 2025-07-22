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


def line_plot(df: pd.DataFrame, x: str, y: str, log_y: bool = False):
    fig, ax = plt.subplots()
    df.plot(x=x, y=y, ax=ax)
    ax.set_title(f"{y} vs {x}")
    if log_y:
        ax.set_yscale("log")
    return _fig_to_png(fig)


def bar_plot(df: pd.DataFrame, x: str, y: Optional[str], agg: str = "sum",
             stacked: bool = False, hue: Optional[str] = None):
    fig, ax = plt.subplots()

    if hue:
        pivot = df.pivot_table(index=x, columns=hue, values=y or x,
                               aggfunc=("count" if y is None else agg))
        pivot.plot(kind="bar", stacked=stacked, ax=ax)
        ax.set_ylabel(("count" if y is None else f"{agg}({y})"))
    else:
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


def hist_plot(df: pd.DataFrame, cols: Sequence[str], bins: int = 30,
              log_y: bool = False):
    fig, ax = plt.subplots()
    df[list(cols)].plot(kind="hist", bins=bins, alpha=0.6, ax=ax)
    ax.set_title(f"Histogram ({', '.join(cols)})")
    ax.set_xlabel("value")
    ax.set_ylabel("frequency")
    if log_y:
        ax.set_yscale("log")
    return _fig_to_png(fig)


def box_plot(df: pd.DataFrame, cols: Sequence[str], by: Optional[str] = None):
    fig, ax = plt.subplots()
    if by and by in df.columns:
        df.boxplot(column=list(cols), by=by, ax=ax)
        ax.set_title(f"Box plot grouped by {by}")
        plt.suptitle("")
        ax.set_xlabel(by)
    else:
        df[list(cols)].plot(kind="box", ax=ax)
        ax.set_title(f"Box plot ({', '.join(cols)})")
    return _fig_to_png(fig)


def scatter_plot(df: pd.DataFrame, x: str, y: str, hue: Optional[str] = None,
                 log_x: bool = False, log_y: bool = False):
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
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    return _fig_to_png(fig)


def facet_line(df: pd.DataFrame, x: str, y: str, facet_by: str):
    levels = df[facet_by].dropna().unique()[:8]
    n = len(levels)
    cols = 2
    rows = (n + 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(10, 4 * rows), squeeze=False)
    for ax, lvl in zip(axes.ravel(), levels):
        sub = df[df[facet_by] == lvl]
        sub.plot(x=x, y=y, ax=ax, title=str(lvl))
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    fig.suptitle(f"{y} vs {x} faceted by {facet_by}")
    fig.tight_layout()
    return _fig_to_png(fig)

