import os
from pathlib import Path
from typing import IO, Union

import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))


def _maybe_cache(file: IO[bytes], name: str) -> None:
    if os.environ.get("NO_CACHE_MODE") not in {"1", "true", "True"}:
        DATA_DIR.mkdir(exist_ok=True)
        dest = DATA_DIR / Path(name).name
        dest.write_bytes(file.read())
        file.seek(0)

def load_any(file: Union[str, Path, IO[bytes]]) -> pd.DataFrame:
    name = getattr(file, "name", str(file))
    if hasattr(file, "read"):
        _maybe_cache(file, name)
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith((".xls", ".xlsx")):
        return pd.read_excel(file)
    raise ValueError(f"Unsupported file type: {name}")

