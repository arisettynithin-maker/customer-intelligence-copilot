from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ask_data import answer_question
from src.utils import (
    apply_theme,
    build_bundle,
    ensure_data_loaded,
    page_header,
    relabel_home_navigation,
    render_data_source_banner,
    render_experiment_cards,
    show_empty_filtered_state,
    sidebar_filters,
)


SUGGESTED_QUESTIONS = [
    "Show churn rate by segment",
    "Show revenue trend over time",
    "Show LTV by country",
    "Show top 10 customers by revenue",
    "Which customers are high-value and at risk?",
    "What should we prioritize first?",
]


st.set_page_config(page_title="Ask the Data", layout="wide")
apply_theme()
relabel_home_navigation()
page_header("Ask the Data", "Ask practical business questions in plain English and get deterministic answers powered by the active customer analytics dataset.")
render_data_source_banner()

if ensure_data_loaded():
    base_df = st.session_state["base_transactions"]
    filters = sidebar_filters(base_df)
    churn_window = st.sidebar.selectbox("Churn definition", [30, 60, 90], index=1)
    bundle = build_bundle(base_df, filters, churn_window=churn_window)

    if bundle["empty"]:
        show_empty_filtered_state()
    else:
        st.markdown("### Guided Questions")
        chip_cols = st.columns(3, gap="small")
        for index, suggestion in enumerate(SUGGESTED_QUESTIONS):
            with chip_cols[index % 3]:
                if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                    st.session_state["ask_data_question"] = suggestion

        default_question = st.session_state.get("ask_data_question", "")
        question = st.text_input(
            "Ask a business question",
            value=default_question,
            placeholder="Example: Which segment contributes the most revenue?",
        )

        if question != default_question:
            st.session_state["ask_data_question"] = question

        if st.button("Run Question", type="primary"):
            st.session_state["ask_data_active_question"] = question

        active_question = st.session_state.get("ask_data_active_question", question)
        response = answer_question(active_question, bundle)

        st.markdown("### Response")
        with st.container(border=True):
            st.markdown(f"## {response['title']}")
            st.write(response["summary"])

            if response.get("chart") is not None:
                st.plotly_chart(response["chart"], use_container_width=True)

            if response.get("table") is not None:
                table = response["table"]
                if isinstance(table, pd.DataFrame):
                    st.dataframe(table, use_container_width=True, hide_index=True)

            if response.get("cards") is not None:
                render_experiment_cards(response["cards"])

            if response.get("bullets") is not None:
                for item in response["bullets"]:
                    st.markdown(f"- {item}")

            if response.get("recommendation"):
                st.markdown("### Recommendation")
                st.write(response["recommendation"])
