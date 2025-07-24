from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_upload_and_summary(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    csv = b"a,b\n1,2\n3,4\n"
    resp = client.post("/upload", files={"file": ("t.csv", csv, "text/csv")})
    assert resp.status_code == 200
    ds_id = resp.json()["dataset_id"]
    resp = client.get(f"/summary/{ds_id}")
    data = resp.json()
    assert data["rows"] == 2
    assert data["columns"] == ["a", "b"]


def test_run_code_route(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    csv = b"a,b\n1,2\n3,4\n"
    resp = client.post("/upload", files={"file": ("u.csv", csv, "text/csv")})
    ds_id = resp.json()["dataset_id"]
    code = "print(df['a'].sum())"
    resp = client.post(f"/run_code/{ds_id}", json={"code": code})
    assert resp.status_code == 200
    out = resp.json()
    assert "4" in out["stdout"]


def test_insights_route(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    csv = b"a,b\n1,2\n3,100\n4,\n"
    resp = client.post("/upload", files={"file": ("i.csv", csv, "text/csv")})
    ds_id = resp.json()["dataset_id"]
    resp = client.get(f"/insights/{ds_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "missing_pct" in data
    assert "outlier_counts" in data


def test_env_config(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from importlib import reload
    import app.core.config as cfg
    reload(cfg)
    assert cfg.settings.log_level == "DEBUG"
