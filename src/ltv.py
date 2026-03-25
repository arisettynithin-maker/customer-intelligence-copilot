from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_ltv(customer_df: pd.DataFrame) -> pd.DataFrame:
    customers = customer_df.copy()
    customers["predicted_orders_next_90d"] = np.maximum(
        customers["purchase_frequency"] * 90 * np.where(customers["recency_days"] > 90, 0.35, 0.8),
        0.2,
    )
    customers["estimated_90d_ltv"] = customers["avg_order_value"] * customers["predicted_orders_next_90d"]
    customers["historical_ltv"] = customers["total_revenue"]

    value_score = (
        customers["historical_ltv"].rank(pct=True) * 0.55
        + customers["purchase_frequency"].rank(pct=True) * 0.25
        + (1 - customers["recency_days"].rank(pct=True)) * 0.20
    )
    customers["value_score"] = value_score.round(4)

    customers["value_band"] = "Core"
    customers.loc[customers["value_score"] >= 0.85, "value_band"] = "Top Value"
    customers.loc[customers["value_score"] < 0.35, "value_band"] = "Low Value"
    customers.loc[customers["value_score"].between(0.35, 0.65, inclusive="left"), "value_band"] = "Growth"

    customers["high_value_flag"] = customers["value_band"].eq("Top Value")
    customers["high_value_at_risk"] = customers["high_value_flag"] & (customers["is_at_risk"] | customers["is_churned"])
    customers["high_value_low_frequency"] = customers["high_value_flag"] & (customers["total_orders"] <= 2)
    return customers


def ltv_summary(customer_df: pd.DataFrame) -> dict[str, float]:
    projected_ltv = float(customer_df["estimated_90d_ltv"].sum())
    avg_historical = float(customer_df["historical_ltv"].mean()) if len(customer_df) else 0.0
    avg_projected = float(customer_df["estimated_90d_ltv"].mean()) if len(customer_df) else 0.0
    return {
        "projected_90d_ltv": projected_ltv,
        "avg_historical_ltv": avg_historical,
        "avg_projected_ltv": avg_projected,
    }

