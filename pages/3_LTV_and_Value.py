from __future__ import annotations

import streamlit as st

from src.utils import (
    apply_theme,
    bar_chart,
    build_bundle,
    ensure_data_loaded,
    format_currency,
    page_header,
    render_data_source_banner,
    render_insight_panel,
    relabel_home_navigation,
    scatter_chart,
    show_empty_filtered_state,
    sidebar_filters,
)


st.set_page_config(page_title="LTV and Value", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("LTV and Customer Value", "Understand where future revenue sits, who your highest-value customers are, and which accounts deserve proactive retention.")
render_data_source_banner()

if ensure_data_loaded():
    base_df = st.session_state["base_transactions"]
    filters = sidebar_filters(base_df)
    churn_window = st.sidebar.selectbox("Churn definition", [30, 60, 90], index=1)
    bundle = build_bundle(base_df, filters, churn_window=churn_window)

    if bundle["empty"]:
        show_empty_filtered_state()
    else:
        customers = bundle["customers"]
        segment_df = bundle["segment_summary"]
        cohort_df = bundle["cohorts"]
        concentration = bundle["concentration"]

        a, b, c, d = st.columns(4, gap="medium")
        with a:
            st.metric("Historical Revenue", format_currency(float(customers["historical_ltv"].sum())))
        with b:
            st.metric("Projected 90D LTV", format_currency(float(customers["estimated_90d_ltv"].sum())))
        with c:
            st.metric("Top 10% Revenue Share", f"{concentration['top_10_pct']:.0%}")
        with d:
            st.metric("High-Value At-Risk", f"{int(customers['high_value_at_risk'].sum()):,}")

        left, right = st.columns([1.2, 1], gap="large")
        with left:
            st.plotly_chart(
                scatter_chart(
                    customers,
                    "total_orders",
                    "historical_ltv",
                    "value_band",
                    "estimated_90d_ltv",
                    "Customer Value Distribution",
                ),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(bar_chart(segment_df, "customer_segment_label", "revenue", "Value by Segment", horizontal=True), use_container_width=True)

        if not cohort_df.empty:
            st.plotly_chart(bar_chart(cohort_df, "cohort_month", "avg_ltv", "Average Value by Cohort"), use_container_width=True)

        hv_low_frequency = customers.loc[customers["high_value_low_frequency"]].copy()
        hv_risk = customers.loc[customers["high_value_at_risk"]].copy()

        render_insight_panel("Business Summary", bundle["ltv_insights"])

        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("### Top Customers")
            st.dataframe(
                customers[
                    ["customer_id", "historical_ltv", "estimated_90d_ltv", "customer_segment_label", "recency_days", "total_orders"]
                ].sort_values("historical_ltv", ascending=False).head(25),
                use_container_width=True,
                hide_index=True,
            )
        with right:
            st.markdown("### High-Value Low-Frequency Users")
            st.dataframe(
                hv_low_frequency[
                    ["customer_id", "historical_ltv", "total_orders", "avg_order_value", "recency_days", "customer_segment_label"]
                ].sort_values("historical_ltv", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### High-Value At-Risk Customers")
        st.dataframe(
            hv_risk[
                ["customer_id", "historical_ltv", "estimated_90d_ltv", "recency_days", "risk_level", "customer_segment_label"]
            ].sort_values("historical_ltv", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
