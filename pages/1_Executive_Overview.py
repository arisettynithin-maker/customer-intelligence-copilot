from __future__ import annotations

import streamlit as st

from src.utils import (
    apply_theme,
    bar_chart,
    build_bundle,
    download_customer_csv,
    ensure_data_loaded,
    format_currency,
    format_pct,
    line_chart,
    page_header,
    render_data_source_banner,
    pie_chart,
    render_insight_panel,
    relabel_home_navigation,
    show_empty_filtered_state,
    sidebar_filters,
)


st.set_page_config(page_title="Executive Overview", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Executive Overview", "A premium top-line view of customer health, revenue performance, and segment-level business momentum.")
render_data_source_banner()

if ensure_data_loaded():
    base_df = st.session_state["base_transactions"]
    filters = sidebar_filters(base_df)
    bundle = build_bundle(base_df, filters, churn_window=60)

    if bundle["empty"]:
        show_empty_filtered_state()
    else:
        metrics = bundle["metrics"]
        customers = bundle["customers"]
        segment_df = bundle["segment_summary"]
        revenue_trend = bundle["trends"]["revenue_trend"]
        customer_growth = bundle["trends"]["customer_growth"]

        col1, col2, col3, col4, col5, col6 = st.columns(6, gap="medium")
        with col1:
            st.metric("Total Customers", f"{metrics['total_customers']:,}")
        with col2:
            st.metric("Total Revenue", format_currency(metrics["total_revenue"]))
        with col3:
            st.metric("Avg Order Value", format_currency(metrics["average_order_value"]))
        with col4:
            st.metric("Repeat Purchase Rate", format_pct(metrics["repeat_purchase_rate"]))
        with col5:
            st.metric("Churn Rate", format_pct(metrics["churn_rate"]))
        with col6:
            st.metric("Projected 90D Value", format_currency(metrics["projected_90d_ltv"]))

        left, right = st.columns([1.4, 1], gap="large")
        with left:
            st.plotly_chart(line_chart(revenue_trend, "order_month", "revenue", "Revenue Trend Over Time"), use_container_width=True)
        with right:
            st.plotly_chart(pie_chart(segment_df, "customer_segment_label", "customers", "Segment Distribution"), use_container_width=True)

        left, right = st.columns(2, gap="large")
        with left:
            st.plotly_chart(line_chart(customer_growth, "order_month", "active_customers", "Active Customer Trend"), use_container_width=True)
        with right:
            st.plotly_chart(bar_chart(segment_df, "customer_segment_label", "revenue", "Revenue by Segment", horizontal=True), use_container_width=True)

        if "country" in base_df.columns and not bundle["transactions"]["country"].dropna().empty:
            country_summary = (
                bundle["transactions"].groupby("country", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(10)
            )
            st.plotly_chart(bar_chart(country_summary, "country", "revenue", "Revenue by Country", horizontal=True), use_container_width=True)

        render_insight_panel("Executive Insights", bundle["executive_insights"])
        download_customer_csv(customers)
        st.dataframe(
            customers[["customer_id", "customer_segment_label", "total_revenue", "total_orders", "recency_days", "estimated_90d_ltv"]]
            .sort_values("total_revenue", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
