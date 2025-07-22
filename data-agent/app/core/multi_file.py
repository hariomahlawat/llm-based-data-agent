import pandas as pd


def find_common_keys(df1: pd.DataFrame, df2: pd.DataFrame) -> list[str]:
    """Return list of column names present in both dataframes with at least one overlapping value."""
    common = []
    for col in df1.columns.intersection(df2.columns):
        if df1[col].dtype == df2[col].dtype:
            overlap = set(df1[col].dropna().unique()) & set(df2[col].dropna().unique())
            if overlap:
                common.append(col)
    return common


def join_on_common_keys(
    df1: pd.DataFrame, df2: pd.DataFrame, how: str = "inner"
) -> pd.DataFrame:
    """Join two dataframes using detected common keys.

    Raises:
        ValueError: if no common keys detected.
    """
    keys = find_common_keys(df1, df2)
    if not keys:
        raise ValueError("No common join keys found")
    return pd.merge(df1, df2, on=keys, how=how, suffixes=("_left", "_right"))


def compare_numeric_means(df1: pd.DataFrame, df2: pd.DataFrame) -> dict:
    """Compare mean of numeric columns shared between two dataframes."""
    metrics = {}
    common_cols = df1.select_dtypes("number").columns.intersection(
        df2.select_dtypes("number").columns
    )
    for col in common_cols:
        metrics[col] = {
            "df1": float(df1[col].mean()),
            "df2": float(df2[col].mean()),
        }
    return metrics
