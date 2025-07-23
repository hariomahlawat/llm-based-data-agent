from __future__ import annotations

import base64
import io
from typing import Any, Dict

import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

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
from .core.llm_driver import ask_llm
from .services.postprocess import extract_outputs, figure_to_png
from .services.safe_exec import run as safe_run

app = FastAPI(title="Data Agent API")

DATASETS: Dict[str, pd.DataFrame] = {}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    data = await file.read()
    buf = io.BytesIO(data)
    buf.name = file.filename
    df = load_any(buf)
    ds_id = str(len(DATASETS) + 1)
    DATASETS[ds_id] = df
    return {"dataset_id": ds_id, "rows": len(df)}


@app.get("/summary/{ds_id}")
def summary(ds_id: str):
    df = DATASETS.get(ds_id)
    if df is None:
        return JSONResponse(status_code=404, content={"error": "dataset not found"})
    return basic_summary(df)


@app.post("/chart/{ds_id}")
async def chart(ds_id: str, spec: Dict[str, Any]):
    df = DATASETS.get(ds_id)
    if df is None:
        return JSONResponse(status_code=404, content={"error": "dataset not found"})

    chart_type = spec.get("type")
    params = spec.get("params", {})

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


@app.post("/nl2code/{ds_id}")
async def nl2code(ds_id: str, payload: Dict[str, str]):
    df = DATASETS.get(ds_id)
    if df is None:
        return JSONResponse(status_code=404, content={"error": "dataset not found"})
    question = payload.get("question", "")
    intent, code = ask_llm(question, df)
    return {"intent": intent, "code": code}


@app.post("/run_code/{ds_id}")
async def run_code(ds_id: str, payload: Dict[str, str]):
    df = DATASETS.get(ds_id)
    if df is None:
        return JSONResponse(status_code=404, content={"error": "dataset not found"})
    code = payload.get("code", "")
    locals_out, stdout = safe_run(code, {"df": df, "pd": pd, "plt": plt})
    dfs, pngs, figs, texts = extract_outputs(locals_out)
    for fig in figs:
        pngs.append(figure_to_png(fig))
    tables = [df_out.to_csv(index=False) for df_out in dfs]
    images = [base64.b64encode(p.getvalue()).decode() for p in pngs]
    return {"stdout": stdout, "tables": tables, "images": images, "texts": texts}
