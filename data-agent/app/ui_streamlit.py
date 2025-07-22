# app/ui_streamlit.py
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from core.analysis import (basic_summary, coerce_column, coerce_datetime,
                           detect_outliers, missing_heatmap)
from core.charts import (bar_plot, box_plot, facet_bar, facet_hist, facet_line,
                         hist_plot, line_plot, scatter_plot)
from core.error_utils import safe_ui
from core.file_loader import load_any
from core.history import add_record, get_history
from core.llm_driver import ask_llm, check_model_ready
from core.logger import get_logger
from core.multi_file import (compare_numeric_means, find_common_keys,
                             join_on_common_keys)
from core.postprocess import extract_outputs, figure_to_png
from core.reporting import history_to_pdf, history_to_pptx, zip_outputs
from core.safe_exec import run as safe_run

# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
# Hide Streamlit cloud links and deploy button
st.set_page_config(
    page_title="Data Summarization & Charting Agent",
    layout="wide",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)
# Remove toolbar items like "Deploy" and external help links
st.set_option("client.toolbarMode", "viewer")
st.set_option("client.showErrorDetails", False)

# Extra CSS to hide any remaining cloud or help links
st.markdown(
    """
    <style>
    [data-testid="stDeployButton"] {display: none !important;}
    .stException a {display: none !important;}
    .stError a {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("📊 Data Summarization & Charting Agent")

# Debug toggle
debug = st.sidebar.checkbox("Show debug tracebacks", value=False)
theme = st.sidebar.selectbox("Theme", ["light", "dark"], index=0)
plt.style.use("dark_background" if theme == "dark" else "default")
logger = get_logger()

# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# File upload (supports one or two files)
# ---------------------------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload CSV or Excel", type=["csv", "xlsx"], accept_multiple_files=True
)
if not uploaded_files:
    st.info("Upload a file to begin.")
    st.stop()

df = load_any(uploaded_files[0])
df2 = load_any(uploaded_files[1]) if len(uploaded_files) > 1 else None

# ---------------------------------------------------------------------
# History side panel and exports
# ---------------------------------------------------------------------
history = get_history()
with st.sidebar.expander("History", expanded=False):
    for idx, item in enumerate(reversed(history)):
        st.markdown(f"**{len(history) - idx}. {item.get('prompt', 'manual')}**")
        st.code(item.get("code", ""), language="python")
        col1, col2 = st.columns(2)
        if col1.button("Re-run", key=f"rerun_{idx}"):
            ok, result, tb = safe_ui(safe_run)(
                item.get("code", ""), {"df": df, "pd": pd, "plt": plt}
            )
            if ok:
                locals_out, stdout_txt = result
                if stdout_txt.strip():
                    st.code(stdout_txt, language="text")
                dfs, pngs, figs, texts = extract_outputs(locals_out)
                for fig in figs:
                    try:
                        pngs.append(figure_to_png(fig))
                    except Exception:
                        pass
                for t in texts:
                    st.write(t)
                for df_out in dfs:
                    st.dataframe(df_out)
                for img in pngs:
                    st.image(img)
                add_record(
                    item.get("prompt", "manual"),
                    item.get("code", ""),
                    [df_out.to_csv(index=False) for df_out in dfs],
                    [img.getvalue() for img in pngs],
                )
            else:
                st.error("Code execution failed.")
                if debug:
                    st.exception(tb)
        if col2.button("Edit", key=f"edit_{idx}"):
            st.session_state["code_edit"] = item.get("code", "")
            st.experimental_rerun()

with st.sidebar.expander("Export", expanded=False):
    if history:
        st.download_button(
            "Download PDF",
            data=history_to_pdf(history).getvalue(),
            file_name="report.pdf",
            mime="application/pdf",
        )
        st.download_button(
            "Download PPTX",
            data=history_to_pptx(history).getvalue(),
            file_name="report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        st.download_button(
            "Download ZIP",
            data=zip_outputs(history).getvalue(),
            file_name="artifacts.zip",
            mime="application/zip",
        )

# ---------------------------------------------------------------------
# Optional: date parsing
# ---------------------------------------------------------------------
with st.expander("🗓️ Date parsing"):
    date_col = st.selectbox(
        "Column to parse as datetime (optional)", ["<none>"] + list(df.columns)
    )
    if date_col != "<none>":
        df = coerce_datetime(df, date_col)

with st.expander("🧹 Data prep wizards"):
    col = st.selectbox("Column", ["<none>"] + list(df.columns))
    dtype = st.selectbox("Convert to", ["int", "float", "datetime"])
    if st.button("Fix column type") and col != "<none>":
        df = coerce_column(df, col, dtype)
        st.experimental_rerun()

    miss_btn = st.button("Show missing value heatmap")
    if miss_btn:
        png = missing_heatmap(df)
        st.image(png)

    out_col = st.selectbox(
        "Outlier column", ["<none>"] + df.select_dtypes("number").columns.tolist()
    )
    method = st.selectbox("Method", ["iqr", "zscore"])
    if st.button("Detect outliers") and out_col != "<none>":
        mask = detect_outliers(df[out_col], method=method)
        st.write(mask.value_counts().to_dict())

# ---------------------------------------------------------------------
# Preview & Summary
# ---------------------------------------------------------------------
st.subheader("Preview")
st.dataframe(df.head())

st.subheader("Basic Summary")
st.json(basic_summary(df))

if df2 is not None:
    st.divider()
    st.subheader("Multi-file Workflows")
    if st.button("Show common keys"):
        st.write(find_common_keys(df, df2))

    with st.expander("Join datasets"):
        join_type = st.selectbox(
            "Join type",
            ["inner", "left", "right", "outer"],
            key="join_type",
        )
        if st.button("Join", key="join_btn"):
            try:
                joined = join_on_common_keys(df, df2, how=join_type)
            except ValueError:
                st.error("No common keys found")
            else:
                st.dataframe(joined.head())

    with st.expander("Compare numeric means"):
        if st.button("Compare", key="compare_btn"):
            metrics = compare_numeric_means(df, df2)
            st.json(metrics)


# ---------------------------------------------------------------------
# Helper for rendering charts with error handling
# ---------------------------------------------------------------------
def render_chart(fn, params: dict):
    ok, png, tb = safe_ui(fn)(df, **params)
    if ok:
        st.image(png)
        st.download_button(
            "Download PNG", data=png, file_name="chart.png", mime="image/png"
        )
        st.toast("Chart created!", icon="✅")
        st.session_state["last_chart"] = {"type": fn.__name__, "params": params}
    else:
        st.error("Chart failed. Please adjust inputs.")
        if debug:
            st.exception(tb)


# ---------------------------------------------------------------------
# Charts UI
# ---------------------------------------------------------------------
st.divider()
st.subheader("Charts")

st.session_state.setdefault("chart_presets", [])
with st.sidebar.expander("Chart presets", expanded=False):
    if st.session_state["chart_presets"]:
        for item in st.session_state["chart_presets"]:
            st.markdown(f"**{item['name']}** - {item['type']}")
            st.json(item["params"])
    if "last_chart" in st.session_state:
        name = st.text_input("Preset name", key="preset_name")
        if st.button("Save preset"):
            st.session_state["chart_presets"].append(
                {
                    "name": name
                    or f"Preset {len(st.session_state['chart_presets']) + 1}",
                    **st.session_state.pop("last_chart"),
                }
            )
            st.success("Preset saved")

chart_type = st.selectbox(
    "Chart type",
    [
        "line",
        "bar",
        "histogram",
        "box",
        "scatter",
        "facet line",
        "facet bar",
        "facet hist",
    ],
)

num_cols = df.select_dtypes("number").columns.tolist()
all_cols = df.columns.tolist()
cat_cols = [c for c in all_cols if c not in num_cols]

if chart_type == "line":
    x = st.selectbox("X axis", all_cols)
    y = st.selectbox("Y axis (numeric)", num_cols)
    log_y = st.checkbox("Log scale Y")
    if st.button("Plot line"):
        params = {"x": x, "y": y, "log_y": log_y}
        render_chart(line_plot, params)

elif chart_type == "bar":
    x = st.selectbox("Category (x)", all_cols)
    y_opt = st.selectbox("Value (y) [optional]", ["<count>"] + num_cols)
    agg = st.selectbox("Aggregation", ["sum", "mean", "count", "min", "max"])
    hue = st.selectbox("Hue / color by (optional)", ["<none>"] + cat_cols)
    stacked = st.checkbox("Stacked", value=True)
    if st.button("Plot bar"):
        y_val = None if y_opt == "<count>" else y_opt
        params = {
            "x": x,
            "y": y_val,
            "agg": agg,
            "stacked": stacked,
            "hue": None if hue == "<none>" else hue,
        }
        render_chart(bar_plot, params)

elif chart_type == "histogram":
    cols = st.multiselect("Numeric columns", num_cols, default=num_cols[:1])
    bins = st.slider("Bins", 5, 100, 30)
    log_y = st.checkbox("Log scale Y")
    if st.button("Plot histogram"):
        params = {"cols": cols, "bins": bins, "log_y": log_y}
        render_chart(hist_plot, params)

elif chart_type == "box":
    cols = st.multiselect("Numeric columns", num_cols, default=num_cols[:1])
    by = st.selectbox("Group by (optional category)", ["<none>"] + cat_cols)
    if st.button("Plot box"):
        params = {"cols": cols, "by": None if by == "<none>" else by}
        render_chart(box_plot, params)

elif chart_type == "scatter":
    x = st.selectbox("X axis (numeric)", num_cols)
    y = st.selectbox("Y axis (numeric)", num_cols, index=min(1, len(num_cols) - 1))
    hue = st.selectbox("Color by (optional category)", ["<none>"] + cat_cols)
    log_x = st.checkbox("Log X")
    log_y = st.checkbox("Log Y")
    if st.button("Plot scatter"):
        params = {
            "x": x,
            "y": y,
            "hue": None if hue == "<none>" else hue,
            "log_x": log_x,
            "log_y": log_y,
        }
        render_chart(scatter_plot, params)

elif chart_type == "facet line":
    x = st.selectbox("X axis", all_cols)
    y = st.selectbox("Y axis (numeric)", num_cols)
    facet_by = st.selectbox("Facet by (category)", cat_cols)
    if st.button("Plot facets"):
        params = {"x": x, "y": y, "facet_by": facet_by}
        render_chart(facet_line, params)

elif chart_type == "facet bar":
    x = st.selectbox("Category (x)", all_cols)
    y_opt = st.selectbox("Value (y) [optional]", ["<count>"] + num_cols)
    facet_by = st.selectbox("Facet by (category)", cat_cols)
    agg = st.selectbox("Aggregation", ["sum", "mean", "count", "min", "max"])
    stacked = st.checkbox("Stacked", value=True)
    if st.button("Plot facets"):
        y_val = None if y_opt == "<count>" else y_opt
        params = {
            "x": x,
            "y": y_val,
            "facet_by": facet_by,
            "agg": agg,
            "stacked": stacked,
        }
        render_chart(facet_bar, params)

elif chart_type == "facet hist":
    col = st.selectbox("Numeric column", num_cols)
    facet_by = st.selectbox("Facet by (category)", cat_cols)
    bins = st.slider("Bins", 5, 100, 30)
    if st.button("Plot facets"):
        params = {"col": col, "facet_by": facet_by, "bins": bins}
        render_chart(facet_hist, params)

# ---------------------------------------------------------------------
# Natural language panel
# ---------------------------------------------------------------------
st.divider()
st.subheader("🤖 Ask in natural language")

with st.expander("LLM → code → safe_exec"):
    nl_q = st.text_input("Question", placeholder="Show sales trend for last 3 months")

    ok_model, msg, chosen_model = check_model_ready()
    if not ok_model:
        st.warning(f"LLM not available: {msg}")
        st.caption("You can still use the sandbox below or manual charts.")
    else:
        st.success(f"LLM ready ({chosen_model})", icon="🟢")

    if st.button("Generate & run", disabled=not ok_model):
        if nl_q.strip():
            with st.spinner("Thinking..."):
                try:
                    intent, code = ask_llm(nl_q, df)
                except Exception as e:
                    st.error("LLM call failed.")
                    if debug:
                        st.exception(e)
                else:
                    if intent:
                        st.caption(intent)
                    st.code(code, language="python")
                    ok, result, tb = safe_ui(safe_run)(
                        code, {"df": df, "pd": pd, "plt": plt}
                    )
                    if ok:
                        locals_out, stdout_txt = result
                        if stdout_txt.strip():
                            st.code(stdout_txt, language="text")

                        # Extract & render
                        dfs, pngs, figs, texts = extract_outputs(locals_out)
                        for fig in figs:
                            try:
                                pngs.append(figure_to_png(fig))
                            except Exception:
                                pass

                        for t in texts:
                            st.write(t)
                        for df_out in dfs:
                            st.dataframe(df_out)
                        for img in pngs:
                            st.image(img)

                        add_record(
                            nl_q,
                            code,
                            [df_out.to_csv(index=False) for df_out in dfs],
                            [img.getvalue() for img in pngs],
                        )

                        st.toast("NL query executed!", icon="✅")
                    else:
                        st.error("Generated code failed or was blocked.")
                        if debug:
                            st.exception(tb)

# ---------------------------------------------------------------------
# Safe code sandbox
# ---------------------------------------------------------------------
st.divider()
st.subheader("🔒 Run custom code (safe sandbox)")

with st.expander("Paste Python code that uses df / pandas / matplotlib"):
    code = st.text_area(
        "Code",
        height=200,
        value=st.session_state.pop("code_edit", ""),
        placeholder="e.g.\nresult = df.groupby('region')['sales'].sum().reset_index()\nprint(result.head())",
    )
    if st.button("Run code safely"):
        if code.strip():
            ok, result, tb = safe_ui(safe_run)(code, {"df": df, "pd": pd, "plt": plt})
            if ok:
                locals_out, stdout_txt = result
                if stdout_txt.strip():
                    st.code(stdout_txt, language="text")

                dfs, pngs, figs, texts = extract_outputs(locals_out)
                for fig in figs:
                    try:
                        pngs.append(figure_to_png(fig))
                    except Exception:
                        pass

                for t in texts:
                    st.write(t)
                for df_out in dfs:
                    st.dataframe(df_out)
                for img in pngs:
                    st.image(img)

                add_record(
                    "manual",
                    code,
                    [df_out.to_csv(index=False) for df_out in dfs],
                    [img.getvalue() for img in pngs],
                )
            else:
                st.error("Code execution failed or was blocked.")
                if debug:
                    st.exception(tb)
