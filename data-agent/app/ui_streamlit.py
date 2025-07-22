import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from core.file_loader import load_any
from core.analysis import basic_summary, coerce_datetime
from core.charts import (
    line_plot, bar_plot, hist_plot, box_plot, scatter_plot, facet_line
)
from core.safe_exec import run as safe_run

st.set_page_config(page_title="Data Summarization & Charting Agent", layout="wide")
st.title("📊 Data Summarization & Charting Agent")

uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if not uploaded:
    st.info("Upload a file to begin.")
    st.stop()

# ---- DataFrame ----
df = load_any(uploaded)

# ---- Optional: date parsing ----
with st.expander("🗓️ Date parsing"):
    date_col = st.selectbox(
        "Column to parse as datetime (optional)",
        ["<none>"] + list(df.columns)
    )
    if date_col != "<none>":
        df = coerce_datetime(df, date_col)

st.subheader("Preview")
st.dataframe(df.head())

st.subheader("Basic Summary")
st.json(basic_summary(df))

st.divider()
st.subheader("Charts")

chart_type = st.selectbox(
    "Chart type",
    ["line", "bar", "histogram", "box", "scatter", "facet line"]
)

num_cols = df.select_dtypes("number").columns.tolist()
all_cols = df.columns.tolist()
cat_cols = [c for c in all_cols if c not in num_cols]

png = None

if chart_type == "line":
    x = st.selectbox("X axis", all_cols)
    y = st.selectbox("Y axis (numeric)", num_cols)
    log_y = st.checkbox("Log scale Y")
    if st.button("Plot line"):
        png = line_plot(df, x, y, log_y=log_y)

elif chart_type == "bar":
    x = st.selectbox("Category (x)", all_cols)
    y_opt = st.selectbox("Value (y) [optional]", ["<count>"] + num_cols)
    agg = st.selectbox("Aggregation", ["sum", "mean", "count", "min", "max"])
    hue = st.selectbox("Hue / color by (optional)", ["<none>"] + cat_cols)
    stacked = st.checkbox("Stacked", value=True)
    if st.button("Plot bar"):
        y_val = None if y_opt == "<count>" else y_opt
        png = bar_plot(df, x, y_val, agg=agg, stacked=stacked,
                       hue=None if hue == "<none>" else hue)

elif chart_type == "histogram":
    cols = st.multiselect("Numeric columns", num_cols, default=num_cols[:1])
    bins = st.slider("Bins", 5, 100, 30)
    log_y = st.checkbox("Log scale Y")
    if st.button("Plot histogram"):
        png = hist_plot(df, cols, bins=bins, log_y=log_y)

elif chart_type == "box":
    cols = st.multiselect("Numeric columns", num_cols, default=num_cols[:1])
    by = st.selectbox("Group by (optional category)", ["<none>"] + cat_cols)
    if st.button("Plot box"):
        png = box_plot(df, cols, by=None if by == "<none>" else by)

elif chart_type == "scatter":
    x = st.selectbox("X axis (numeric)", num_cols)
    y = st.selectbox("Y axis (numeric)", num_cols, index=min(1, len(num_cols) - 1))
    hue = st.selectbox("Color by (optional category)", ["<none>"] + cat_cols)
    log_x = st.checkbox("Log X")
    log_y = st.checkbox("Log Y")
    if st.button("Plot scatter"):
        png = scatter_plot(df, x, y,
                           hue=None if hue == "<none>" else hue,
                           log_x=log_x, log_y=log_y)

elif chart_type == "facet line":
    x = st.selectbox("X axis", all_cols)
    y = st.selectbox("Y axis (numeric)", num_cols)
    facet_by = st.selectbox("Facet by (category)", cat_cols)
    if st.button("Plot facets"):
        png = facet_line(df, x, y, facet_by)

if png:
    st.image(png)
    st.download_button("Download PNG", data=png,
                       file_name="chart.png", mime="image/png")

# ---------------- Safe Exec Panel ----------------
st.divider()
st.subheader("🔒 Run custom code (safe sandbox)")

with st.expander("Paste Python code that uses df / pandas / matplotlib"):
    code = st.text_area(
        "Code",
        height=200,
        placeholder="e.g.\nresult = df.groupby('region')['sales'].sum().reset_index()\nprint(result.head())"
    )
    if st.button("Run code safely"):
        if code.strip():
            try:
                locals_out, stdout_txt = safe_run(
                    code,
                    {"df": df, "pd": pd, "plt": plt}
                )

                if stdout_txt.strip():
                    st.code(stdout_txt, language="text")

                for key, val in locals_out.items():
                    if isinstance(val, pd.DataFrame):
                        st.write(f"**DataFrame: `{key}`**")
                        st.dataframe(val)
            except Exception as e:
                st.error(f"Execution blocked or failed: {e}")

