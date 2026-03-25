from __future__ import annotations

from io import StringIO
from typing import Dict, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.churn import apply_churn_logic, churn_summary
from src.feature_engineering import build_customer_features, build_monthly_trends, cohort_summary, enrich_transactions, revenue_concentration
from src.insights import churn_insights, executive_insights, ltv_insights, segment_insights
from src.ltv import estimate_ltv, ltv_summary
from src.recommendations import build_experiment_cards, segment_actions_table
from src.segmentation import assign_segments, segment_summary


PALETTE = {
    "bg": "#f4f1eb",
    "surface": "#fbfaf7",
    "surface_alt": "#f0ece4",
    "ink": "#18212b",
    "muted": "#627081",
    "border": "#ddd6ca",
    "accent": "#2f6f6d",
    "accent_soft": "#dbeceb",
    "warm": "#b08d57",
    "danger": "#a44d4d",
}


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

            :root {{
                --bg: {PALETTE["bg"]};
                --surface: {PALETTE["surface"]};
                --surface-alt: {PALETTE["surface_alt"]};
                --ink: {PALETTE["ink"]};
                --muted: {PALETTE["muted"]};
                --border: {PALETTE["border"]};
                --accent: {PALETTE["accent"]};
                --accent-soft: {PALETTE["accent_soft"]};
                --warm: {PALETTE["warm"]};
                --danger: {PALETTE["danger"]};
            }}

            html, body, [class*="css"]  {{
                font-family: 'IBM Plex Sans', sans-serif;
                color: var(--ink);
            }}

            .stApp {{
                background:
                    radial-gradient(circle at top right, rgba(176, 141, 87, 0.12), transparent 20%),
                    linear-gradient(180deg, #f7f4ef 0%, var(--bg) 100%);
            }}

            h1, h2, h3, h4 {{
                font-family: 'Manrope', sans-serif;
                color: var(--ink);
                letter-spacing: -0.02em;
            }}

            section[data-testid="stSidebar"] {{
                background: rgba(251, 250, 247, 0.92);
                border-right: 1px solid rgba(24, 33, 43, 0.08);
            }}

            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] label {{
                color: var(--ink);
            }}

            div[data-testid="stMetric"] {{
                background: rgba(251, 250, 247, 0.96);
                border: 1px solid rgba(24, 33, 43, 0.08);
                border-radius: 22px;
                padding: 18px 18px 14px 18px;
                box-shadow: 0 12px 30px rgba(28, 35, 41, 0.06);
            }}

            div[data-testid="stMetric"] label {{
                font-family: 'Manrope', sans-serif;
                font-size: 0.88rem;
                font-weight: 700;
                color: var(--muted);
            }}

            div[data-testid="stMetricValue"] {{
                font-family: 'Manrope', sans-serif;
                font-size: 1.9rem;
                font-weight: 800;
            }}

            .panel {{
                background: rgba(251, 250, 247, 0.92);
                border: 1px solid rgba(24, 33, 43, 0.08);
                border-radius: 26px;
                padding: 22px 24px;
                box-shadow: 0 16px 38px rgba(28, 35, 41, 0.06);
            }}

            .hero {{
                background:
                    linear-gradient(135deg, rgba(47, 111, 109, 0.14), rgba(176, 141, 87, 0.12)),
                    rgba(251, 250, 247, 0.96);
                border: 1px solid rgba(24, 33, 43, 0.08);
                border-radius: 30px;
                padding: 28px 30px;
                box-shadow: 0 18px 45px rgba(28, 35, 41, 0.07);
                margin-bottom: 1rem;
            }}

            .eyebrow {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                background: rgba(47, 111, 109, 0.10);
                color: var(--accent);
                font-size: 0.8rem;
                font-weight: 700;
                margin-bottom: 0.8rem;
                letter-spacing: 0.02em;
                text-transform: uppercase;
            }}

            .panel h3 {{
                margin-top: 0;
                margin-bottom: 0.6rem;
            }}

            .small-muted {{
                color: var(--muted);
                font-size: 0.95rem;
            }}

            .insight-list {{
                margin: 0;
                padding-left: 1.1rem;
            }}

            .insight-list li {{
                margin-bottom: 0.55rem;
                color: var(--ink);
            }}

            .card-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 14px;
            }}

            .mini-card {{
                background: rgba(240, 236, 228, 0.65);
                border: 1px solid rgba(24, 33, 43, 0.06);
                border-radius: 20px;
                padding: 16px 18px;
                min-height: 122px;
            }}

            .mini-card h4 {{
                margin: 0 0 0.4rem 0;
                font-size: 1rem;
            }}

            .mini-card p {{
                margin: 0;
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.45;
            }}

            .stDataFrame, .stTable {{
                background: rgba(251, 250, 247, 0.92);
                border-radius: 18px;
            }}

            [data-testid="stExpander"] {{
                border: 1px solid rgba(24, 33, 43, 0.08);
                border-radius: 18px;
                overflow: hidden;
            }}

            .stButton button, .stDownloadButton button {{
                border-radius: 999px;
                border: none;
                background: linear-gradient(135deg, var(--accent), #214d4c);
                color: white;
                font-weight: 700;
                padding: 0.65rem 1rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def relabel_home_navigation() -> None:
    components.html(
        """
        <script>
        const renameHome = () => {
          const root = window.parent.document;
          const navLinks = root.querySelectorAll('a[data-testid="stSidebarNavLink"]');
          navLinks.forEach((link) => {
            const span = link.querySelector('span');
            if (span && span.textContent && span.textContent.trim().toLowerCase() === 'app') {
              span.textContent = 'Home';
            }
          });
        };
        renameHome();
        const observer = new MutationObserver(renameHome);
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
        </script>
        """,
        height=0,
        width=0,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Customer Intelligence Copilot</div>
            <h1>{title}</h1>
            <p class="small-muted">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title: str, body: str) -> None:
    st.markdown(f'<div class="panel"><h3>{title}</h3><p class="small-muted">{body}</p></div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label, value, delta=delta)


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_pct(value: float) -> str:
    return f"{value:.1%}"


def _format_chart_value(value: float) -> str:
    if pd.isna(value):
        return ""
    numeric_value = float(value)
    abs_value = abs(numeric_value)
    if abs_value >= 1_000_000:
        return f"{numeric_value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{numeric_value / 1_000:.1f}K"
    if numeric_value.is_integer():
        return str(int(numeric_value))
    return f"{numeric_value:.1f}"


def build_plotly_template() -> go.layout.Template:
    return go.layout.Template(
        layout={
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "IBM Plex Sans, sans-serif", "color": PALETTE["ink"]},
            "xaxis": {"gridcolor": "rgba(98, 112, 129, 0.12)", "zeroline": False},
            "yaxis": {"gridcolor": "rgba(98, 112, 129, 0.12)", "zeroline": False},
            "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
            "margin": {"l": 10, "r": 10, "t": 40, "b": 10},
        }
    )


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title, template=build_plotly_template())
    fig.update_traces(line={"width": 3})
    fig.update_layout(title={"x": 0, "xanchor": "left"}, height=360)
    fig.update_xaxes(automargin=True, tickangle=-25)
    fig.update_yaxes(automargin=True)
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, horizontal: bool = False) -> go.Figure:
    chart_df = df.copy()
    chart_df["_chart_value_label"] = chart_df[y].apply(_format_chart_value)
    fig = px.bar(
        chart_df,
        x=y if horizontal else x,
        y=x if horizontal else y,
        color=color or x,
        title=title,
        template=build_plotly_template(),
        orientation="h" if horizontal else "v",
        color_discrete_sequence=["#2f6f6d", "#b08d57", "#65758b", "#9aa5b1", "#d4c8b3", "#7a5c45"],
        text="_chart_value_label",
    )
    fig.update_layout(showlegend=False, title={"x": 0, "xanchor": "left"}, height=360)
    fig.update_xaxes(automargin=True, tickangle=-20 if not horizontal else 0)
    fig.update_yaxes(automargin=True)
    fig.update_traces(
        textposition="outside" if not horizontal else "inside",
        insidetextanchor="middle",
        textfont={"size": 11, "color": PALETTE["ink"]},
        cliponaxis=False,
    )
    return fig


def pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.55,
        template=build_plotly_template(),
        color_discrete_sequence=["#2f6f6d", "#b08d57", "#7a8aa0", "#94a3b8", "#d5cab6", "#5d6b77"],
    )
    fig.update_traces(
        textinfo="none",
        hovertemplate="%{label}<br>%{percent}<br>Value: %{value}<extra></extra>",
    )
    fig.update_layout(
        title={"x": 0, "xanchor": "left"},
        height=380,
        margin={"l": 10, "r": 10, "t": 56, "b": 10},
        legend={"font": {"size": 11}, "orientation": "v", "x": 1.02, "y": 0.98, "xanchor": "left", "yanchor": "top"},
    )
    return fig


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str, size: str, title: str) -> go.Figure:
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        template=build_plotly_template(),
        color_discrete_sequence=["#2f6f6d", "#b08d57", "#7a8aa0", "#a44d4d", "#3e4c5c"],
    )
    fig.update_traces(marker={"opacity": 0.85, "line": {"width": 0.6, "color": "#ffffff"}})
    fig.update_layout(
        title={"x": 0, "xanchor": "left"},
        height=420,
        margin={"l": 18, "r": 18, "t": 56, "b": 18},
        legend={"orientation": "v", "x": 1.02, "y": 0.98, "xanchor": "left", "yanchor": "top", "font": {"size": 11}},
    )
    fig.update_xaxes(automargin=True, tickangle=0, title_standoff=12)
    fig.update_yaxes(automargin=True, title_standoff=12)
    return fig


def get_base_dataset() -> pd.DataFrame:
    return st.session_state.get("base_transactions", pd.DataFrame())


def ensure_data_loaded() -> bool:
    if get_base_dataset().empty:
        st.info("Load demo data or upload a CSV on the Home page to unlock the analytics workspace.")
        return False
    return True


def render_data_source_banner() -> None:
    source_type = st.session_state.get("data_source_type", "demo")
    source_label = "Using Demo Data" if source_type == "demo" else "Using Uploaded Data"
    source_detail = st.session_state.get("data_source_name", "online_retail_II.csv" if source_type == "demo" else "Custom file")
    st.markdown(
        f"""
        <div class="panel" style="padding:16px 20px; margin-bottom: 1rem;">
            <strong>{source_label}</strong>
            <span class="small-muted" style="margin-left: 0.45rem;">{source_detail}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_filters(base_df: pd.DataFrame) -> Dict[str, object]:
    st.sidebar.markdown("### Analysis Filters")
    min_date = base_df["order_date"].min().date()
    max_date = base_df["order_date"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range[0], date_range[1]
    else:
        start_date, end_date = min_date, max_date

    filters: Dict[str, object] = {"date_range": (pd.Timestamp(start_date), pd.Timestamp(end_date))}
    for column, label in [("country", "Country"), ("category", "Category"), ("segment", "Source Segment")]:
        options = sorted(base_df[column].dropna().astype(str).unique().tolist()) if column in base_df.columns else []
        filters[column] = st.sidebar.multiselect(label, options)

    st.sidebar.markdown("### Context")
    st.sidebar.caption("Pages recalculate metrics from the filtered dataset so every view stays coherent.")
    return filters


def filter_transactions(base_df: pd.DataFrame, filters: Dict[str, object]) -> pd.DataFrame:
    transactions = base_df.copy()
    start_date, end_date = filters["date_range"]
    transactions = transactions.loc[transactions["order_date"].between(start_date, end_date)]
    for column in ["country", "category", "segment"]:
        selected = filters.get(column)
        if selected and column in transactions.columns:
            transactions = transactions.loc[transactions[column].astype(str).isin(selected)]
    return transactions


def build_bundle(base_df: pd.DataFrame, filters: Dict[str, object], churn_window: int) -> Dict[str, object]:
    transactions = filter_transactions(base_df, filters)
    if transactions.empty:
        return {"transactions": pd.DataFrame(), "customers": pd.DataFrame(), "empty": True}

    transactions = enrich_transactions(transactions)
    customers = build_customer_features(transactions)
    customers = apply_churn_logic(customers, churn_window)
    customers = estimate_ltv(customers)
    customers = assign_segments(customers)

    segment_df = segment_summary(customers)
    trends = build_monthly_trends(transactions)
    cohort_df = cohort_summary(customers)
    concentration = revenue_concentration(customers)
    churn_stats = churn_summary(customers)
    ltv_stats = ltv_summary(customers)

    metrics = {
        "total_customers": int(customers["customer_id"].nunique()),
        "total_revenue": float(transactions["revenue"].sum()),
        "average_order_value": float(transactions["revenue"].mean()),
        "repeat_purchase_rate": float(customers["repeat_purchase_flag"].mean()),
        "churn_rate": churn_stats["churn_rate"],
        "at_risk_customers": churn_stats["at_risk_customers"],
        "projected_90d_ltv": ltv_stats["projected_90d_ltv"],
        "high_value_at_risk": int(customers["high_value_at_risk"].sum()),
        "top_10_pct": concentration["top_10_pct"],
        "top_20_pct": concentration["top_20_pct"],
    }

    return {
        "transactions": transactions,
        "customers": customers,
        "segment_summary": segment_df,
        "trends": trends,
        "cohorts": cohort_df,
        "concentration": concentration,
        "metrics": metrics,
        "executive_insights": executive_insights(customers, metrics),
        "churn_insights": churn_insights(customers, churn_window),
        "ltv_insights": ltv_insights(customers, concentration),
        "segment_insights": segment_insights(segment_df),
        "experiment_cards": build_experiment_cards(customers, metrics),
        "segment_actions": segment_actions_table(segment_df),
        "empty": False,
    }


def show_empty_filtered_state() -> None:
    st.warning("No data remains after the current filters. Adjust the sidebar selections to continue.")


def download_customer_csv(customer_df: pd.DataFrame) -> None:
    csv_buffer = StringIO()
    customer_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download processed customer summary",
        data=csv_buffer.getvalue(),
        file_name="customer_summary.csv",
        mime="text/csv",
    )


def render_insight_panel(title: str, insights: list[str]) -> None:
    items = "".join(f"<li>{insight}</li>" for insight in insights)
    st.markdown(
        f'<div class="panel"><h3>{title}</h3><ul class="insight-list">{items}</ul></div>',
        unsafe_allow_html=True,
    )


def render_experiment_cards(cards: list[dict[str, str]]) -> None:
    columns = st.columns(2, gap="large")
    for index, card in enumerate(cards):
        with columns[index % 2]:
            with st.container(border=True):
                st.markdown(f"### {card['title']}")
                st.caption(card["target_segment"])
                st.write(card["business_hypothesis"])
                st.markdown(f"**Primary KPI:** {card['primary_kpi']}")
                st.markdown(f"**Secondary KPI:** {card['secondary_kpi']}")
                st.markdown(f"**Expected Impact:** {card['expected_impact']}")


def quality_assumptions() -> Dict[str, str]:
    return {
        "Churn assumption": "Customers are treated as churned when they have been inactive for the selected 30, 60, or 90 day window.",
        "LTV assumption": "Estimated 90-day LTV projects near-term revenue from recent order value and observed purchase cadence rather than a predictive ML model.",
        "Segmentation assumption": "Segments are assigned with transparent business rules using recency, frequency, and value signals.",
    }
