from __future__ import annotations

import streamlit as st

from src.churn import churn_by_dimension
from src.utils import (
    apply_theme,
    bar_chart,
    build_bundle,
    ensure_data_loaded,
    format_currency,
    format_pct,
    page_header,
    render_data_source_banner,
    render_insight_panel,
    relabel_home_navigation,
    scatter_chart,
    show_empty_filtered_state,
    sidebar_filters,
)


st.set_page_config(page_title="Churn Risk", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Churn Risk", "Track inactivity-based churn, identify high-value retention priorities, and understand where risk is building.")
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
        metrics = bundle["metrics"]
        segment_churn = churn_by_dimension(customers, "customer_segment_label")
        cohort_df = bundle["cohorts"].copy()
        if not cohort_df.empty:
            cohort_df = cohort_df.merge(
                customers.assign(cohort_month=customers["first_order_date"].dt.to_period("M").dt.to_timestamp())
                .groupby("cohort_month", as_index=False)["is_churned"]
                .mean()
                .rename(columns={"is_churned": "churn_rate"}),
                on="cohort_month",
                how="left",
            )

        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1:
            st.metric("Churn Rate", format_pct(metrics["churn_rate"]))
        with c2:
            st.metric("At-Risk Customers", f"{metrics['at_risk_customers']:,}")
        with c3:
            st.metric("High-Value At-Risk", f"{metrics['high_value_at_risk']:,}")
        with c4:
            at_risk_revenue = customers.loc[customers["is_at_risk"] | customers["is_churned"], "total_revenue"].sum()
            st.metric("Revenue In Risk Pool", format_currency(float(at_risk_revenue)))

        left, right = st.columns([1.2, 1], gap="large")
        with left:
            st.plotly_chart(
                scatter_chart(
                    customers,
                    "recency_days",
                    "total_orders",
                    "customer_segment_label",
                    "total_revenue",
                    "Recency vs Frequency",
                ),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(bar_chart(segment_churn, "customer_segment_label", "churn_rate", "Churn by Segment", horizontal=True), use_container_width=True)

        if not cohort_df.empty:
            st.plotly_chart(bar_chart(cohort_df, "cohort_month", "churn_rate", "Churn by Cohort"), use_container_width=True)

        render_insight_panel("Business Summary", bundle["churn_insights"])

        at_risk_customers = customers.loc[customers["is_at_risk"] | customers["is_churned"]].copy()
        st.dataframe(
            at_risk_customers[
                ["customer_id", "customer_segment_label", "total_revenue", "total_orders", "recency_days", "risk_level", "estimated_90d_ltv"]
            ].sort_values(["total_revenue", "recency_days"], ascending=[False, False]),
            use_container_width=True,
            hide_index=True,
        )
