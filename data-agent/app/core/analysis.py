import pandas as pd

def basic_summary(df: pd.DataFrame) -> dict:
    """Return simple stats used in the MVP."""
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isna().sum().to_dict(),
    }
