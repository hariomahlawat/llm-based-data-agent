import io
import importlib
import pandas as pd


def test_no_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("NO_CACHE_MODE", "1")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    fl = importlib.import_module("app.core.file_loader")
    buf = io.BytesIO(b"a,b\n1,2\n")
    buf.name = "t.csv"
    df = fl.load_any(buf)
    assert isinstance(df, pd.DataFrame)
    assert not any(tmp_path.iterdir())
