from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def enrich_transactions(df: pd.DataFrame) -> pd.DataFrame:
    transactions = df.copy()
    transactions["order_month"] = transactions["order_date"].dt.to_period("M").dt.to_timestamp()
    transactions["order_week"] = transactions["order_date"].dt.to_period("W").dt.start_time
    transactions["order_quarter"] = transactions["order_date"].dt.to_period("Q").dt.to_timestamp()
    transactions["cohort_month"] = transactions.groupby("customer_id")["order_date"].transform("min").dt.to_period("M").dt.to_timestamp()
    return transactions


def build_customer_features(transactions: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    if reference_date is None:
        reference_date = transactions["order_date"].max()

    grouped = transactions.groupby("customer_id")
    customer = grouped.agg(
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
        total_orders=("order_id", "nunique"),
        total_revenue=("revenue", "sum"),
        avg_order_value=("revenue", "mean"),
    )
    customer["tenure_days"] = (reference_date - customer["first_order_date"]).dt.days.clip(lower=1)
    customer["customer_lifespan_days"] = (customer["last_order_date"] - customer["first_order_date"]).dt.days.clip(lower=0)
    customer["recency_days"] = (reference_date - customer["last_order_date"]).dt.days.clip(lower=0)
    customer["purchase_frequency"] = customer["total_orders"] / customer["tenure_days"].replace(0, 1)
    customer["repeat_purchase_flag"] = customer["total_orders"] > 1

    transactions_sorted = transactions.sort_values(["customer_id", "order_date"]).copy()
    transactions_sorted["previous_order_date"] = transactions_sorted.groupby("customer_id")["order_date"].shift(1)
    transactions_sorted["days_since_prior_order"] = (
        transactions_sorted["order_date"] - transactions_sorted["previous_order_date"]
    ).dt.days
    avg_gap = transactions_sorted.groupby("customer_id")["days_since_prior_order"].mean().fillna(0)
    customer["days_between_orders"] = avg_gap

    optional_dimensions = ["country", "category", "segment"]
    for column in optional_dimensions:
        if column in transactions.columns:
            dominant = (
                transactions.groupby(["customer_id", column]).size().reset_index(name="count")
                .sort_values(["customer_id", "count"], ascending=[True, False])
                .drop_duplicates("customer_id")
                .set_index("customer_id")[column]
            )
            customer[column] = dominant

    return customer.reset_index()


def build_monthly_trends(transactions: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    revenue_trend = (
        transactions.groupby("order_month")
        .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"))
        .reset_index()
    )
    customer_growth = (
        transactions.groupby("order_month")["customer_id"].nunique().reset_index(name="active_customers")
    )
    new_customers = (
        transactions.drop_duplicates("customer_id")
        .groupby("cohort_month")["customer_id"]
        .nunique()
        .reset_index(name="new_customers")
        .rename(columns={"cohort_month": "order_month"})
    )
    customer_growth = customer_growth.merge(new_customers, on="order_month", how="left").fillna(0)
    return {"revenue_trend": revenue_trend, "customer_growth": customer_growth}


def cohort_summary(customer_df: pd.DataFrame) -> pd.DataFrame:
    cohort_df = customer_df.copy()
    cohort_df["cohort_month"] = cohort_df["first_order_date"].dt.to_period("M").dt.to_timestamp()
    summary = (
        cohort_df.groupby("cohort_month")
        .agg(customers=("customer_id", "nunique"), revenue=("total_revenue", "sum"), avg_ltv=("total_revenue", "mean"))
        .reset_index()
    )
    return summary


def revenue_concentration(customer_df: pd.DataFrame) -> Dict[str, float]:
    ordered = customer_df.sort_values("total_revenue", ascending=False).copy()
    total_revenue = ordered["total_revenue"].sum()
    if total_revenue <= 0:
        return {"top_10_pct": 0.0, "top_20_pct": 0.0}

    top_10_count = max(1, int(np.ceil(len(ordered) * 0.10)))
    top_20_count = max(1, int(np.ceil(len(ordered) * 0.20)))
    return {
        "top_10_pct": float(ordered.head(top_10_count)["total_revenue"].sum() / total_revenue),
        "top_20_pct": float(ordered.head(top_20_count)["total_revenue"].sum() / total_revenue),
    }

