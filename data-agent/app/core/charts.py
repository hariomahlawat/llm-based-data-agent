import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

def line_plot(df: pd.DataFrame, x: str, y: str) -> BytesIO:
    """Return PNG buffer for a line chart."""
    fig, ax = plt.subplots()
    df.plot(x=x, y=y, ax=ax)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {x}")
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf
