from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_prep import prepare_dataset
from src.utils import (
    apply_theme,
    download_customer_csv,
    page_header,
    relabel_home_navigation,
    render_data_source_banner,
)


DEMO_DATA_PATH = Path("data/sample/online_retail_II.csv")


@st.cache_data(show_spinner=False)
def read_demo_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def read_uploaded_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(pd.io.common.BytesIO(file_bytes))


def store_processed_dataset(raw_df: pd.DataFrame, source_type: str, source_name: str) -> tuple[bool, str]:
    standardized_df, quality_report, validation = prepare_dataset(raw_df)
    if not validation.is_valid:
        return False, validation.message
    if standardized_df.empty:
        return False, "The file was readable, but no valid rows remained after cleaning. Check date parsing, customer IDs, quantities, prices, and revenue values."

    st.session_state["base_transactions"] = standardized_df
    st.session_state["data_quality_report"] = quality_report
    st.session_state["data_source_type"] = source_type
    st.session_state["data_source_name"] = source_name
    return True, "Dataset loaded successfully."


def load_demo_dataset() -> tuple[bool, str]:
    raw_df = read_demo_data(str(DEMO_DATA_PATH))
    return store_processed_dataset(raw_df, "demo", DEMO_DATA_PATH.name)


def load_uploaded_dataset(uploaded_file) -> tuple[bool, str]:
    raw_df = read_uploaded_data(uploaded_file.name, uploaded_file.getvalue())
    return store_processed_dataset(raw_df, "upload", uploaded_file.name)


st.set_page_config(
    page_title="Customer Intelligence Copilot",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
relabel_home_navigation()

if "base_transactions" not in st.session_state and DEMO_DATA_PATH.exists():
    ok, message = load_demo_dataset()
    if not ok:
        st.session_state["load_error"] = message

page_header(
    "Customer Intelligence Copilot",
    "Choose demo data or bring your own CSV, then explore the same premium analytics workspace across churn, value, segmentation, recommendations, and guided data questions.",
)

render_data_source_banner()

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown(
        """
        <div class="panel">
            <h3>Overview</h3>
            <p class="small-muted">
                Built for business analysts and stakeholders who need a clear view of customer health without waiting on a custom BI workflow.
                The app standardizes raw transaction data, creates customer-level features, and turns the results into executive-ready dashboards.
            </p>
            <p class="small-muted" style="margin-top:0.75rem;"><strong>Created by Nithin Arisetty</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Data Source")
    action_col, upload_col = st.columns([0.55, 0.45], gap="medium")
    with action_col:
        if st.button("Use Demo Data", use_container_width=True, type="primary"):
            with st.spinner("Loading demo data..."):
                ok, message = load_demo_dataset()
            if ok:
                st.success("Demo dataset loaded. The full analytics workspace is ready to explore.")
            else:
                st.error(message)

    with upload_col:
        uploaded_file = st.file_uploader("Upload Your Own CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        upload_signature = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("uploaded_signature") != upload_signature:
            with st.spinner("Loading uploaded dataset..."):
                ok, message = load_uploaded_dataset(uploaded_file)
            if ok:
                st.session_state["uploaded_signature"] = upload_signature
                st.success("Uploaded dataset loaded successfully.")
            else:
                st.error(message)

    st.markdown(
        """
        <div class="panel">
            <h3>Expected Columns</h3>
            <p class="small-muted">
                Canonical fields: <strong>customer_id</strong>, <strong>order_id</strong>, <strong>order_date</strong>, <strong>revenue</strong><br/>
                Raw retail files are also supported, including fields like <strong>Invoice</strong>, <strong>Customer ID</strong>, <strong>InvoiceDate</strong>, <strong>Quantity</strong>, and <strong>Price / UnitPrice</strong>.<br/>
                If revenue is missing, the app derives it automatically from quantity × unit price.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="panel">
            <h3>What The App Delivers</h3>
            <div class="card-grid">
                <div class="mini-card"><h4>Executive Overview</h4><p>Stakeholder-ready KPIs, trends, segment mix, and plain-English insight generation.</p></div>
                <div class="mini-card"><h4>Churn Risk</h4><p>Adjustable inactivity thresholds, at-risk customer views, and retention prioritization.</p></div>
                <div class="mini-card"><h4>LTV & Value</h4><p>Historical revenue, estimated near-term value, concentration analysis, and top customer views.</p></div>
                <div class="mini-card"><h4>Ask the Data</h4><p>Guided question handling for practical business questions using the active dataset.</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

error_message = st.session_state.get("load_error")
if error_message:
    st.error(error_message)

base_df = st.session_state.get("base_transactions", pd.DataFrame())
quality_report = st.session_state.get("data_quality_report", {})

if base_df.empty:
    st.info("No dataset is active yet. Use demo data or upload a CSV to initialize the analytics workspace.")
else:
    preview_col, summary_col = st.columns([1.3, 0.7], gap="large")

    with preview_col:
        st.markdown("### Processed Transaction Preview")
        st.dataframe(base_df.head(25), use_container_width=True, hide_index=True)

    with summary_col:
        st.markdown("### Dataset Snapshot")
        st.metric("Rows", f"{quality_report.get('row_count_processed', len(base_df)):,}")
        st.metric("Customers", f"{base_df['customer_id'].nunique():,}")
        st.metric("Revenue", f"${base_df['revenue'].sum():,.0f}")
        st.metric("Date Range", f"{base_df['order_date'].min().date()} to {base_df['order_date'].max().date()}")
        download_customer_csv(
            base_df.groupby("customer_id", as_index=False)
            .agg(total_revenue=("revenue", "sum"), total_orders=("order_id", "nunique"))
        )
