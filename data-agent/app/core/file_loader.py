import pandas as pd
from pathlib import Path
from typing import Union, IO

def load_any(file: Union[str, Path, IO[bytes]]) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a DataFrame.
    Accepts a path-like string or a BytesIO from Streamlit uploader.
    """
    name = getattr(file, "name", str(file))
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith((".xls", ".xlsx")):
        return pd.read_excel(file)
    raise ValueError(f"Unsupported file type for {name!r}")
