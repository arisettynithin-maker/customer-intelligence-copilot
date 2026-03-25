from __future__ import annotations

import streamlit as st

from src.utils import (
    apply_theme,
    bar_chart,
    build_bundle,
    ensure_data_loaded,
    format_currency,
    page_header,
    pie_chart,
    render_data_source_banner,
    render_insight_panel,
    relabel_home_navigation,
    show_empty_filtered_state,
    sidebar_filters,
)


st.set_page_config(page_title="Segmentation", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Segmentation", "Break the customer base into practical business segments and connect each cohort to a clear action.")
render_data_source_banner()

if ensure_data_loaded():
    base_df = st.session_state["base_transactions"]
    filters = sidebar_filters(base_df)
    churn_window = st.sidebar.selectbox("Churn definition", [30, 60, 90], index=1)
    bundle = build_bundle(base_df, filters, churn_window=churn_window)

    if bundle["empty"]:
        show_empty_filtered_state()
    else:
        segment_df = bundle["segment_summary"]
        customers = bundle["customers"]

        left, right = st.columns([1, 1.2], gap="large")
        with left:
            st.plotly_chart(pie_chart(segment_df, "customer_segment_label", "customers", "Segment Counts"), use_container_width=True)
        with right:
            st.plotly_chart(bar_chart(segment_df, "customer_segment_label", "revenue", "Revenue Contribution by Segment", horizontal=True), use_container_width=True)

        behavior_profile = customers.groupby("customer_segment_label", as_index=False).agg(
            avg_orders=("total_orders", "mean"),
            avg_revenue=("total_revenue", "mean"),
            avg_recency=("recency_days", "mean"),
            repeat_rate=("repeat_purchase_flag", "mean"),
            churn_rate=("is_churned", "mean"),
        )

        left, right = st.columns(2, gap="large")
        with left:
            st.plotly_chart(bar_chart(behavior_profile, "customer_segment_label", "repeat_rate", "Repeat Purchase Behavior", horizontal=True), use_container_width=True)
        with right:
            st.plotly_chart(bar_chart(behavior_profile, "customer_segment_label", "churn_rate", "Churn Risk by Segment", horizontal=True), use_container_width=True)

        render_insight_panel("Segment Recommendation Panel", bundle["segment_insights"])

        action_table = bundle["segment_actions"].copy()
        action_table["revenue"] = action_table["revenue"].map(format_currency)
        st.dataframe(action_table, use_container_width=True, hide_index=True)
