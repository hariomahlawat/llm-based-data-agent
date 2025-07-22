import pandas as pd
from app.core.multi_file import (compare_numeric_means, find_common_keys,
                                 join_on_common_keys)


def test_find_common_keys():
    df1 = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df2 = pd.DataFrame({"id": [2, 3], "score": [5, 6]})
    keys = find_common_keys(df1, df2)
    assert keys == ["id"]


def test_join_on_common_keys():
    df1 = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df2 = pd.DataFrame({"id": [2, 1], "score": [5, 6]})
    joined = join_on_common_keys(df1, df2)
    assert "score" in joined.columns
    assert len(joined) == 2


def test_compare_numeric_means():
    df1 = pd.DataFrame({"id": [1, 2], "value": [10.0, 30.0]})
    df2 = pd.DataFrame({"id": [1, 2], "value": [20.0, 40.0]})
    metrics = compare_numeric_means(df1, df2)
    assert metrics["value"]["df1"] == 20.0
    assert metrics["value"]["df2"] == 30.0
