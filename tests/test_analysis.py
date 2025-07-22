import pandas as pd
from app.core.analysis import basic_summary, coerce_column, detect_outliers


def test_basic_summary():
    df = pd.DataFrame({"a": [1, 2], "b": [3, None]})
    result = basic_summary(df)
    assert result["rows"] == 2
    assert result["columns"] == ["a", "b"]
    assert result["null_counts"]["b"] == 1


def test_coerce_column_int():
    df = pd.DataFrame({"a": ["1", "2"]})
    out = coerce_column(df.copy(), "a", "int")
    assert str(out["a"].dtype).startswith("Int")


def test_detect_outliers_iqr():
    s = pd.Series([1, 2, 3, 100])
    mask = detect_outliers(s, method="iqr")
    assert mask.sum() == 1
