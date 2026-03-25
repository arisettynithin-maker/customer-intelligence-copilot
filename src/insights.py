from __future__ import annotations

from typing import List

import pandas as pd


def executive_insights(customer_df: pd.DataFrame, metrics: dict[str, float]) -> List[str]:
    insights: list[str] = []
    churn_rate = metrics.get("churn_rate", 0.0)
    top_20_pct = metrics.get("top_20_pct", 0.0)
    repeat_rate = metrics.get("repeat_purchase_rate", 0.0)
    high_value_at_risk = int(customer_df["high_value_at_risk"].sum()) if "high_value_at_risk" in customer_df else 0
    one_time_share = float((customer_df["total_orders"] == 1).mean()) if len(customer_df) else 0.0

    if churn_rate >= 0.30:
        insights.append(
            f"Churn risk is elevated at {churn_rate:.0%}, which suggests the business should prioritize retention before scaling acquisition."
        )
    else:
        insights.append(
            f"Churn is currently at {churn_rate:.0%}; retention is manageable, but there is still room to tighten re-engagement timing."
        )

    if top_20_pct >= 0.60:
        insights.append(
            f"Revenue is concentrated, with the top 20% of customers contributing {top_20_pct:.0%} of sales, so account protection is strategically important."
        )
    else:
        insights.append(
            f"Revenue concentration is moderate, with the top 20% contributing {top_20_pct:.0%}, which reduces dependency on a narrow customer base."
        )

    if one_time_share >= 0.45:
        insights.append(
            f"One-time buyers account for {one_time_share:.0%} of customers, making second-purchase conversion the clearest growth lever."
        )

    if repeat_rate >= 0.50:
        insights.append(
            f"Repeat behavior is healthy at {repeat_rate:.0%}, which creates room for loyalty, cross-sell, and premiumization tactics."
        )

    if high_value_at_risk > 0:
        insights.append(
            f"There are {high_value_at_risk} high-value customers already showing risk signals, so targeted win-back outreach should be treated as a near-term priority."
        )

    return insights[:4]


def churn_insights(customer_df: pd.DataFrame, churn_window: int) -> List[str]:
    at_risk = int(customer_df["is_at_risk"].sum())
    churned = int(customer_df["is_churned"].sum())
    high_value_at_risk = int(customer_df["high_value_at_risk"].sum())
    return [
        f"The current churn definition flags customers inactive for {churn_window} days or more.",
        f"{at_risk} customers are approaching churn and {churned} are already beyond the inactivity threshold.",
        (
            f"{high_value_at_risk} high-value customers need first-touch retention outreach before broader lifecycle campaigns."
            if high_value_at_risk
            else "Risk is concentrated in lower-value cohorts, so lower-cost automated win-back can carry more of the workload."
        ),
    ]


def ltv_insights(customer_df: pd.DataFrame, concentration: dict[str, float]) -> List[str]:
    avg_historical = customer_df["historical_ltv"].mean() if len(customer_df) else 0
    hv_low_freq = int(customer_df["high_value_low_frequency"].sum())
    return [
        f"Average historical customer value is {avg_historical:,.0f}, providing a baseline for future revenue planning.",
        f"The top 10% of customers contribute {concentration.get('top_10_pct', 0):.0%} of revenue, highlighting where proactive retention matters most.",
        (
            f"{hv_low_freq} high-value customers still buy infrequently, making them strong candidates for replenishment or bundle campaigns."
            if hv_low_freq
            else "Top-value customers already show healthy frequency, so the next opportunity is likely higher basket size rather than cadence."
        ),
    ]


def segment_insights(segment_summary_df: pd.DataFrame) -> List[str]:
    if segment_summary_df.empty:
        return []
    top_segment = segment_summary_df.iloc[0]
    return [
        f"{top_segment['customer_segment_label']} is the leading revenue segment, contributing the largest share of total customer value.",
        "Segments with high repeat rate but rising churn deserve retention-led investment before broader growth spend.",
        "Low-frequency segments should be managed with a clear activation path to avoid over-investing in low-intent cohorts.",
    ]

