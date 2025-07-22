import streamlit as st
from core.file_loader import load_any
from core.analysis import basic_summary
from core.charts import (
    line_plot, bar_plot, hist_plot, box_plot, scatter_plot
)

st.set_page_config(page_title="Data Summarization & Charting Agent", layout="wide")
st.title("📊 Data Summarization & Charting Agent")

uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if not uploaded:
    st.info("Upload a file to begin.")
    st.stop()                   # <- prevents executing the rest without df

# ---- once a file is present ----
df = load_any(uploaded)

st.subheader("Preview")
st.dataframe(df.head())

st.subheader("Basic Summary")
st.json(basic_summary(df))

st.divider()
st.subheader("Charts")

chart_type = st.selectbox(
    "Chart type",
    ["line", "bar", "histogram", "box", "scatter"]
)

num_cols = df.select_dtypes("number").columns.tolist()
all_cols = df.columns.tolist()
cat_cols = [c for c in all_cols if c not in num_cols]

png = None

if chart_type == "line":
    x = st.selectbox("X axis", options=all_cols)
    y = st.selectbox("Y axis (numeric)", options=num_cols)
    if st.button("Plot line"):
        png = line_plot(df, x, y)

elif chart_type == "bar":
    x = st.selectbox("Category (x)", options=all_cols)
    y_opt = st.selectbox("Value (y) [optional]", options=["<count>"] + num_cols)
    agg = st.selectbox("Aggregation", options=["sum", "mean", "count", "min", "max"])
    if st.button("Plot bar"):
        y_val = None if y_opt == "<count>" else y_opt
        png = bar_plot(df, x, y_val, agg=agg)

elif chart_type == "histogram":
    cols = st.multiselect("Numeric columns", options=num_cols, default=num_cols[:1])
    bins = st.slider("Bins", 5, 100, 30)
    if st.button("Plot histogram"):
        png = hist_plot(df, cols, bins=bins)

elif chart_type == "box":
    cols = st.multiselect("Numeric columns", options=num_cols, default=num_cols[:1])
    if st.button("Plot box"):
        png = box_plot(df, cols)

elif chart_type == "scatter":
    x = st.selectbox("X axis (numeric)", options=num_cols)
    y = st.selectbox("Y axis (numeric)", options=num_cols, index=min(1, len(num_cols) - 1))
    hue = st.selectbox("Color by (optional category)", options=["<none>"] + cat_cols)
    if st.button("Plot scatter"):
        png = scatter_plot(df, x, y, None if hue == "<none>" else hue)

if png:
    st.image(png)
    st.download_button("Download PNG", data=png, file_name="chart.png", mime="image/png")
