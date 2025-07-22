import pandas as pd
from app.core.analysis import basic_summary


def test_basic_summary():
    df = pd.DataFrame({"a": [1, 2], "b": [3, None]})
    result = basic_summary(df)
    assert result["rows"] == 2
    assert result["columns"] == ["a", "b"]
    assert result["null_counts"]["b"] == 1
