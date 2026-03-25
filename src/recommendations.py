from __future__ import annotations

import pandas as pd


def build_experiment_cards(customer_df: pd.DataFrame, metrics: dict[str, float]) -> list[dict[str, str]]:
    high_value_at_risk = int(customer_df["high_value_at_risk"].sum())
    one_time_share = float((customer_df["total_orders"] == 1).mean()) if len(customer_df) else 0.0
    repeat_growth_pool = int(customer_df["customer_segment_label"].isin(["Repeat Customers", "Loyal Customers"]).sum())

    cards = [
        {
            "title": "Win-back campaign for inactive high-value customers",
            "target_segment": "High-value at-risk and dormant customers",
            "business_hypothesis": (
                "A personalized retention touchpoint can recover meaningful revenue from customers already proven to spend."
            ),
            "primary_kpi": "Reactivated revenue",
            "secondary_kpi": "30-day repeat purchase rate",
            "expected_impact": f"Priority opportunity with {high_value_at_risk} high-value customers needing intervention.",
        },
        {
            "title": "Second-purchase nudging for first-time buyers",
            "target_segment": "New customers and one-time buyers",
            "business_hypothesis": (
                "Moving customers to a second order quickly will improve retention and long-term value."
            ),
            "primary_kpi": "Second purchase conversion",
            "secondary_kpi": "Time to second order",
            "expected_impact": f"One-time buyers represent {one_time_share:.0%} of the current customer base.",
        },
        {
            "title": "Loyalty campaign for repeat medium-value buyers",
            "target_segment": "Repeat customers with strong frequency but mid-tier spend",
            "business_hypothesis": "Light loyalty mechanics can increase order cadence without deep discounting.",
            "primary_kpi": "Orders per customer",
            "secondary_kpi": "Average order value",
            "expected_impact": f"Applies to a growth pool of roughly {repeat_growth_pool} customers.",
        },
        {
            "title": "Personalized offers for top-value segments",
            "target_segment": "Champions and top-value customers",
            "business_hypothesis": "Relevant offers and premium bundles will expand share of wallet from the best accounts.",
            "primary_kpi": "Incremental revenue per targeted customer",
            "secondary_kpi": "Offer redemption rate",
            "expected_impact": f"Useful when top customers drive {metrics.get('top_20_pct', 0):.0%} of revenue.",
        },
    ]
    return cards


def segment_actions_table(segment_summary_df: pd.DataFrame) -> pd.DataFrame:
    action_map = {
        "New Customers": "Activate",
        "One-Time Buyers": "Activate",
        "Repeat Customers": "Cross-sell",
        "Loyal Customers": "Retain",
        "High-Value Customers": "Retain",
        "At-Risk Customers": "Win back",
        "Dormant Customers": "Win back",
        "Champions": "Upsell",
    }
    table = segment_summary_df[["customer_segment_label", "customers", "revenue", "recommended_action"]].copy()
    table["playbook"] = table["customer_segment_label"].map(action_map)
    return table

