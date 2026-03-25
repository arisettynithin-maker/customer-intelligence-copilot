from __future__ import annotations

import pandas as pd


def assign_segments(customer_df: pd.DataFrame) -> pd.DataFrame:
    customers = customer_df.copy()
    customers["customer_segment_label"] = "Repeat Customers"

    customers.loc[customers["total_orders"] == 1, "customer_segment_label"] = "One-Time Buyers"
    customers.loc[(customers["total_orders"] == 1) & (customers["recency_days"] <= 30), "customer_segment_label"] = "New Customers"
    customers.loc[(customers["total_orders"] >= 4) & (customers["recency_days"] <= 45), "customer_segment_label"] = "Loyal Customers"
    customers.loc[customers["high_value_flag"], "customer_segment_label"] = "High-Value Customers"
    customers.loc[
        customers["high_value_flag"] & (customers["recency_days"] <= 30) & (customers["total_orders"] >= 4),
        "customer_segment_label",
    ] = "Champions"
    customers.loc[customers["is_at_risk"], "customer_segment_label"] = "At-Risk Customers"
    customers.loc[customers["is_churned"], "customer_segment_label"] = "Dormant Customers"
    return customers


SEGMENT_ACTIONS = {
    "New Customers": "Activate with onboarding and second-purchase offers.",
    "One-Time Buyers": "Drive a fast second purchase with targeted nudges.",
    "Repeat Customers": "Cross-sell adjacent products and reinforce habit loops.",
    "Loyal Customers": "Retain with loyalty rewards and early access perks.",
    "High-Value Customers": "Protect share of wallet with white-glove retention.",
    "At-Risk Customers": "Intervene now with win-back and service outreach.",
    "Dormant Customers": "Test selective win-back offers and suppression rules.",
    "Champions": "Upsell premium products and referral programs.",
}


def segment_summary(customer_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        customer_df.groupby("customer_segment_label")
        .agg(
            customers=("customer_id", "nunique"),
            revenue=("total_revenue", "sum"),
            avg_order_value=("avg_order_value", "mean"),
            repeat_rate=("repeat_purchase_flag", "mean"),
            churn_rate=("is_churned", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    summary["recommended_action"] = summary["customer_segment_label"].map(SEGMENT_ACTIONS)
    return summary

