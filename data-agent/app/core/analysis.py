import pandas as pd


def basic_summary(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isna().sum().to_dict(),
    }


def coerce_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    try:
        df[col] = pd.to_datetime(df[col], errors="raise")
    except Exception:
        pass
    return df


def coerce_column(df: pd.DataFrame, col: str, kind: str) -> pd.DataFrame:
    """Coerce a column to int, float or datetime."""
    if col not in df.columns:
        return df
    if kind == "int":
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    elif kind == "float":
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
    elif kind in {"date", "datetime"}:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def missing_heatmap(df: pd.DataFrame):
    """Return a matplotlib heatmap of missing values as BytesIO."""
    from io import BytesIO

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.imshow(df.isna(), aspect="auto", cmap="viridis")
    ax.set_title("Missing values")
    ax.set_xlabel("columns")
    ax.set_ylabel("rows")
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf


def detect_outliers(
    series: pd.Series, method: str = "iqr", threshold: float = 3.0
) -> pd.Series:
    """Detect outliers in a numeric series using IQR or z-score."""
    if method == "zscore":
        z = (series - series.mean()) / series.std(ddof=0)
        return z.abs() > threshold
    # default to IQR
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (series < lower) | (series > upper)


def basic_insights(df: pd.DataFrame) -> dict:
    """Return missing value percentage and outlier counts per column."""
    missing_pct = (df.isna().mean() * 100).round(2).to_dict()
    outlier_counts: dict[str, int] = {}
    for col in df.select_dtypes(include=["number"]).columns:
        mask = detect_outliers(df[col].dropna())
        outlier_counts[col] = int(mask.sum())
    return {"missing_pct": missing_pct, "outlier_counts": outlier_counts}
