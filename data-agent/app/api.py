from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any, Dict
import uuid

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from .core.analysis import basic_summary
from .core.charts import (
    bar_plot,
    box_plot,
    facet_bar,
    facet_hist,
    facet_line,
    hist_plot,
    line_plot,
    scatter_plot,
)
from .core.file_loader import load_any
from .core.config import settings
from .core.llm_driver import ask_llm
from .services.postprocess import extract_outputs, figure_to_png
from .services.safe_exec import run as safe_run
from .core.storage import add_dataset, get_dataset_path, init_db
from .core.error_utils import logger
import traceback


class UploadResponse(BaseModel):
    dataset_id: str
    rows: int


class SummaryResponse(BaseModel):
    rows: int
    columns: list[str]
    dtypes: dict[str, str]
    null_counts: dict[str, int]


class ChartSpec(BaseModel):
    type: str
    params: dict[str, Any] | None = None


class NL2CodeRequest(BaseModel):
    question: str


class NL2CodeResponse(BaseModel):
    intent: str
    code: str


class RunCodeRequest(BaseModel):
    code: str


class RunCodeResponse(BaseModel):
    stdout: str
    tables: list[str]
    images: list[str]
    texts: list[str]

app = FastAPI(title="Data Agent API")

DATASETS: Dict[str, pd.DataFrame] = {}
init_db()


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error("Unhandled error: %s\n%s", exc, tb)
    return JSONResponse(status_code=500, content={"error": "internal server error"})


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    data = await file.read()
    if len(data) > settings.max_file_size:
        return JSONResponse(status_code=400, content={"error": "file too large"})
    ext = Path(file.filename).suffix.lstrip(".")
    if ext not in settings.allowed_file_types:
        return JSONResponse(status_code=400, content={"error": "file type not allowed"})
    ds_path = Path(settings.data_dir)
    ds_path.mkdir(exist_ok=True)
    ds_id = str(uuid.uuid4())
    path = ds_path / f"{ds_id}_{Path(file.filename).name}"
    add_dataset(str(path), ds_id)
    with open(path, "wb") as f:
        f.write(data)
    buf = io.BytesIO(data)
    buf.name = file.filename
    df = load_any(buf)
    DATASETS[ds_id] = df
    return UploadResponse(dataset_id=ds_id, rows=len(df))


@app.get("/summary/{ds_id}", response_model=SummaryResponse)
def summary(ds_id: str):
    df = DATASETS.get(ds_id)
    if df is None:
        try:
            df = load_any(get_dataset_path(ds_id))
        except Exception:
            return JSONResponse(status_code=404, content={"error": "dataset not found"})
        DATASETS[ds_id] = df
    return SummaryResponse(**basic_summary(df))


@app.post("/chart/{ds_id}")
async def chart(ds_id: str, spec: ChartSpec):
    df = DATASETS.get(ds_id)
    if df is None:
        try:
            df = load_any(get_dataset_path(ds_id))
        except Exception:
            return JSONResponse(status_code=404, content={"error": "dataset not found"})
        DATASETS[ds_id] = df

    chart_type = spec.type
    params = spec.params or {}

    if chart_type == "line":
        png = line_plot(df, **params)
    elif chart_type == "bar":
        png = bar_plot(df, **params)
    elif chart_type == "hist":
        png = hist_plot(df, **params)
    elif chart_type == "box":
        png = box_plot(df, **params)
    elif chart_type == "scatter":
        png = scatter_plot(df, **params)
    elif chart_type == "facet_line":
        png = facet_line(df, **params)
    elif chart_type == "facet_bar":
        png = facet_bar(df, **params)
    elif chart_type == "facet_hist":
        png = facet_hist(df, **params)
    else:
        return JSONResponse(status_code=400, content={"error": "unknown chart type"})

    return StreamingResponse(png, media_type="image/png")


@app.post("/nl2code/{ds_id}", response_model=NL2CodeResponse)
async def nl2code(ds_id: str, payload: NL2CodeRequest):
    df = DATASETS.get(ds_id)
    if df is None:
        try:
            df = load_any(get_dataset_path(ds_id))
        except Exception:
            return JSONResponse(status_code=404, content={"error": "dataset not found"})
        DATASETS[ds_id] = df
    intent, code = ask_llm(payload.question, df)
    return NL2CodeResponse(intent=intent, code=code)


@app.post("/run_code/{ds_id}", response_model=RunCodeResponse)
async def run_code(ds_id: str, payload: RunCodeRequest) -> RunCodeResponse:
    df = DATASETS.get(ds_id)
    if df is None:
        try:
            df = load_any(get_dataset_path(ds_id))
        except Exception:
            return JSONResponse(status_code=404, content={"error": "dataset not found"})
        DATASETS[ds_id] = df
    code = payload.code
    locals_out, stdout = safe_run(code, {"df": df, "pd": pd, "plt": plt})
    dfs, pngs, figs, texts = extract_outputs(locals_out)
    for fig in figs:
        pngs.append(figure_to_png(fig))
    tables = [df_out.to_csv(index=False) for df_out in dfs]
    images = [base64.b64encode(p.getvalue()).decode() for p in pngs]
    return RunCodeResponse(stdout=stdout, tables=tables, images=images, texts=texts)
