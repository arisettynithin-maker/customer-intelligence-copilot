from __future__ import annotations

import pandas as pd
import streamlit as st

from src.utils import apply_theme, page_header, quality_assumptions, relabel_home_navigation, render_data_source_banner


st.set_page_config(page_title="Data Quality and Assumptions", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Data Quality and Assumptions", "Make the input quality, field mappings, and business logic transparent for stakeholders and recruiters reviewing the work.")
render_data_source_banner()

quality = st.session_state.get("data_quality_report")
if not quality:
    st.info("Upload a dataset on the home page to populate the quality and assumptions report.")
else:
    c1, c2, c3, c4, c5 = st.columns(5, gap="medium")
    with c1:
        st.metric("Raw Rows", f"{quality['row_count_raw']:,}")
    with c2:
        st.metric("Processed Rows", f"{quality['row_count_processed']:,}")
    with c3:
        st.metric("Duplicate Rows", f"{quality['duplicate_count']:,}")
    with c4:
        st.metric("Invalid Revenue Rows", f"{quality['invalid_revenue_rows']:,}")
    with c5:
        st.metric("Cancelled Rows", f"{quality.get('cancelled_rows', 0):,}")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("### Missing Values")
        missing_df = pd.DataFrame(
            [{"column": key, "missing_values": value} for key, value in quality["missing_values"].items()]
        )
        st.dataframe(missing_df, use_container_width=True, hide_index=True)

        st.markdown("### Mapped Column Names")
        mapped_df = pd.DataFrame(
            [{"canonical_name": key, "source_column": value} for key, value in quality["mapped_columns"].items()]
        )
        st.dataframe(mapped_df, use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Assumptions")
        assumptions = quality_assumptions()
        for title, text in assumptions.items():
            st.markdown(
                f"""
                <div class="mini-card">
                    <h4>{title}</h4>
                    <p>{text}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("### Date Range")
        st.write(f"{quality['date_range'][0].date()} to {quality['date_range'][1].date()}")
        st.markdown("### Missing Customer IDs")
        st.write(f"{quality['missing_customer_ids']:,}")
