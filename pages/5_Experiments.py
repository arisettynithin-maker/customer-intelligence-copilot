from __future__ import annotations

import pandas as pd
import streamlit as st

from src.utils import apply_theme, bar_chart, build_bundle, ensure_data_loaded, page_header, relabel_home_navigation, render_data_source_banner, render_experiment_cards, show_empty_filtered_state, sidebar_filters


st.set_page_config(page_title="Experiments and Recommendations", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Experiments and Recommendations", "Translate the analysis into testable retention, activation, and revenue-growth experiments.")
render_data_source_banner()

if ensure_data_loaded():
    base_df = st.session_state["base_transactions"]
    filters = sidebar_filters(base_df)
    churn_window = st.sidebar.selectbox("Churn definition", [30, 60, 90], index=1)
    bundle = build_bundle(base_df, filters, churn_window=churn_window)

    if bundle["empty"]:
        show_empty_filtered_state()
    else:
        st.markdown("### Recommended Experiment Cards")
        render_experiment_cards(bundle["experiment_cards"])

        experiment_priority = [
            {"experiment": "Win-back High-Value", "priority_score": 95},
            {"experiment": "Second Purchase Nudges", "priority_score": 88},
            {"experiment": "Loyalty for Repeat Buyers", "priority_score": 76},
            {"experiment": "Personalized Premium Offers", "priority_score": 71},
        ]
        kpi_focus = [
            {"kpi": "Retention / Reactivation", "weight": 40},
            {"kpi": "Repeat Purchase Rate", "weight": 28},
            {"kpi": "Average Order Value", "weight": 18},
            {"kpi": "Offer Conversion", "weight": 14},
        ]

        left, right = st.columns(2, gap="large")
        with left:
            st.plotly_chart(
                bar_chart(
                    pd.DataFrame(experiment_priority),
                    "experiment",
                    "priority_score",
                    "Experiment Priority",
                    horizontal=True,
                ),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                bar_chart(
                    pd.DataFrame(kpi_focus),
                    "kpi",
                    "weight",
                    "Recommended KPI Focus",
                    horizontal=True,
                ),
                use_container_width=True,
            )

        st.markdown("### Segment Action Plan")
        st.dataframe(bundle["segment_actions"], use_container_width=True, hide_index=True)
