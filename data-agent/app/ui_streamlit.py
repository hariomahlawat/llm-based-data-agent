import streamlit as st
from core.file_loader import load_any
from core.analysis import basic_summary
from core.charts import line_plot

st.set_page_config(page_title="Data Summarization & Charting Agent",
                   layout="wide")

st.title("📊 Data Summarization & Charting Agent")

uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded:
    df = load_any(uploaded)

    st.subheader("Preview")
    st.dataframe(df.head())

    st.subheader("Basic Summary")
    st.json(basic_summary(df))

    st.divider()

    st.subheader("Quick Line Plot")
    num_cols = df.select_dtypes("number").columns.tolist()
    x_col = st.selectbox("X-axis", options=df.columns, index=0)
    y_col = st.selectbox("Y-axis (numeric)", options=num_cols)

    if st.button("Plot"):
        png = line_plot(df, x_col, y_col)
        st.image(png)
        st.download_button("Download PNG", data=png,
                           file_name="chart.png", mime="image/png")
else:
    st.info("Upload a file to begin.")

