import pandas as pd
from app.core.llm_driver import _schema_desc, _extract_json


def test_schema_desc():
    df = pd.DataFrame({
        "num": [1, 2, 3],
        "cat": ["a", "b", "a"],
    })
    desc = _schema_desc(df)
    assert "num" in desc
    assert "int" in desc
    assert "cat" in desc


def test_schema_desc_redact():
    df = pd.DataFrame({"name": ["a"], "age": [1]})
    desc = _schema_desc(df, redact_cols=["name"])
    assert "<redacted>" in desc


def test_extract_json():
    intent, code = _extract_json('{"intent": "do", "code": "print(1)"}')
    assert intent == "do"
    assert code == "print(1)"
