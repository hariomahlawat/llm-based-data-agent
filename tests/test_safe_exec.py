import pytest

from app.services.safe_exec import _analyze, run


def test_analyze_disallows_import():
    with pytest.raises(ValueError):
        _analyze("import os")


def test_analyze_disallows_exec_call():
    with pytest.raises(ValueError):
        _analyze("exec('print(1)')")


def test_run_timeout():
    with pytest.raises(TimeoutError):
        run("while True:\n    pass", {}, timeout=1)


def test_run_simple():
    locals_out, stdout = run("x=1\nprint('ok')", {}, timeout=2)
    assert locals_out["x"] == 1
    assert stdout.strip() == "ok"
