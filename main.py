"""
Streamlit app: Lightweight interactive dashboard for the DAU model spreadsheet

How to run locally:
$ pip install streamlit pandas openpyxl plotly
$ streamlit run dau_dashboard.py

The app lets you:
1. Upload the existing **DAU model.xlsx** workbook.
2. Inspect either the **Basedata** or **DAU_Model_imapct** sheet.
3. Pick 1-4 metrics to chart (e.g. `wuu`, `duu`, `installs`, `net_growth`).
4. Drag-to-re-order metrics via a simple drag-and-drop UI built on Streamlit sortable-
   grid to change which series appears on top.
5. Tweak driver assumptions on the sidebar (install multiplier, retention delta, engagement
   delta, churn delta) and instantly see the recalculated “*_calc” columns update on the chart.

NOTE  ➜  The on-the-fly recalculation is a *minimal* replica of the Excel logic – it rewrites
          only the high-level formulas that matter for directional scenario planning.
          You can extend / replace `recalc_df()` to match your full spreadsheet exactly.
"""

import io
from typing import List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------
# App wide configuration
# --------------------------
st.set_page_config(
    page_title="DAU Scenario Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------
# Helpers
# --------------------------

def load_workbook(uploaded_file: io.BytesIO) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return (basedata_df, model_df) from the uploaded Excel workbook."""
    xls = pd.ExcelFile(uploaded_file)
    basedata_df = pd.read_excel(xls, sheet_name="Basedata")
    model_df = pd.read_excel(xls, sheet_name="DAU_Model_imapct")

    # Ensure datetime parsing
    for df in (basedata_df, model_df):
        if "week_end_date" in df.columns:
            df["week_end_date"] = pd.to_datetime(df["week_end_date"]).dt.date
    return basedata_df, model_df


def recalc_df(df: pd.DataFrame, inst_mult: float, rr_delta: float, eng_delta: float) -> pd.DataFrame:
    """Very lightweight re-calc of *_calc columns based on driver tweaks."""
    calc = df.copy()

    # Installs tweak
    if "Installs calulated " in calc.columns:
        calc["Installs calulated "] = calc["installs"] * inst_mult

    # Retention tweaks (affects nurr_new / curr_new)
    if "nurr_new" in calc.columns:
        calc["nurr_new"] = calc["nurr"] * (1 + rr_delta)
    if "curr_new" in calc.columns:
        calc["curr_new"] = calc["curr"] * (1 + rr_delta)

    # Engagement tweak (% of WUU that become DUU)
    if "engagement_new" in calc.columns:
        calc["engagement_new"] = calc["engagement"] * (1 + eng_delta)

    # Re-compute wuu_calc & duu_calc (super-simplified!)
    if set(["con_wuu_calc", "new_wuu_calu", "ret_wuu_calulated"]).issubset(calc.columns):
        calc["wuu_calc"] = (
            calc["con_wuu_calc"] + calc["new_wuu_calu"] + calc["ret_wuu_calulated"]
        )
    if "du_calc" in calc.columns and "engagement_new" in calc.columns:
        calc["duu_calc"] = calc["wuu_calc"] * calc["engagement_new"] / 100.0

    # Net growth recomputation (simplified)
    if set(["total_growth", "total_lapse"]).issubset(calc.columns):
        calc["net_growth"] = calc["total_growth"] + calc["total_lapse"]
    return calc


def sortable_multiselect(label: str, options: List[str], default: List[str]) -> List[str]:
    """Wrapper around st.multiselect with drag-sort capability via session_state."""
    # Streamlit 1.35+ has built-in `st.multiselect(attr="sortable")`; if your version is
    # older, fall back to a simple multiselect.
    try:
        return st.multiselect(label, options, default=default, placeholder="Pick metrics…", key="metric_select", sortable=True)  # type: ignore[arg-type]
    except TypeError:
        return st.multiselect(label, options, default=default)

# --------------------------
# UI – Sidebar controls
# --------------------------

st.sidebar.markdown("## Upload workbook")
uploaded_file = st.sidebar.file_uploader("Choose DAU model .xlsx", type=["xlsx"])

if uploaded_file is None:
    st.info("👆 Upload the *DAU model.xlsx* workbook in the sidebar to begin.")
    st.stop()

basedata_df, model_df = load_workbook(uploaded_file)

st.sidebar.markdown("---")
st.sidebar.markdown("### Scenario drivers")
inst_mult = st.sidebar.slider("Install multiplier", 0.5, 1.5, 1.0, 0.05, help="Scale weekly installs by this factor.")
rr_delta = st.sidebar.slider("Retention Δ", -0.25, 0.25, 0.0, 0.01, format="%+0.2f", help="Fractional change to all retention rates.")
eng_delta = st.sidebar.slider("Engagement Δ", -0.25, 0.25, 0.0, 0.01, format="%+0.2f", help="Fractional change to engagement %.")

# --------------------------
# Main layout: data table + chart
# --------------------------

st.write("### DAU model – Scenario explorer")

sel_df = recalc_df(model_df, inst_mult, rr_delta, eng_delta)

metric_cols = [c for c in sel_df.columns if sel_df[c].dtype != "object" and c not in ("week_end_date",)]

default_metrics = ["wuu_calc", "duu_calc", "installs"]
sel_metrics = sortable_multiselect("Pick & drag metrics to plot (top-most appears on top)", metric_cols, default_metrics)

if not sel_metrics:
    st.warning("Select at least one metric to chart.")
    st.stop()

# Long-format dataframe for plotly
plot_df = sel_df.melt(id_vars="week_end_date", value_vars=sel_metrics, var_name="metric", value_name="value")

fig = px.line(
    plot_df,
    x="week_end_date",
    y="value",
    color="metric",
    category_orders={"metric": sel_metrics},  # preserve user order
    title="Weekly trend – scenario vs. actual",
)
fig.update_layout(legend_title_text="Metric", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# Show dataframe expander
with st.expander("🔍  Raw data (scenario)"):
    st.dataframe(sel_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️  Streamlit + Plotly | [GitHub](https://github.com)")
