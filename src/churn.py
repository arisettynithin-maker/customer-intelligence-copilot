from __future__ import annotations

import pandas as pd


def apply_churn_logic(customer_df: pd.DataFrame, churn_window_days: int) -> pd.DataFrame:
    customers = customer_df.copy()
    customers["churn_window_days"] = churn_window_days
    customers["is_churned"] = customers["recency_days"] >= churn_window_days
    customers["is_at_risk"] = customers["recency_days"].between(max(1, churn_window_days // 2), churn_window_days - 1)
    customers["risk_level"] = "Healthy"
    customers.loc[customers["is_at_risk"], "risk_level"] = "At Risk"
    customers.loc[customers["is_churned"], "risk_level"] = "Dormant"
    return customers


def churn_summary(customer_df: pd.DataFrame) -> dict[str, float]:
    total_customers = max(len(customer_df), 1)
    churned = int(customer_df["is_churned"].sum())
    at_risk = int(customer_df["is_at_risk"].sum())
    return {
        "churn_rate": churned / total_customers,
        "at_risk_rate": at_risk / total_customers,
        "churned_customers": churned,
        "at_risk_customers": at_risk,
    }


def churn_by_dimension(customer_df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    if dimension not in customer_df.columns:
        return pd.DataFrame()
    return (
        customer_df.groupby(dimension)
        .agg(
            customers=("customer_id", "nunique"),
            churn_rate=("is_churned", "mean"),
            at_risk_rate=("is_at_risk", "mean"),
            revenue=("total_revenue", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

