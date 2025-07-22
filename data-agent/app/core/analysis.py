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

