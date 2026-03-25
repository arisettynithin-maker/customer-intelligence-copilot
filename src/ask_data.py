from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from src.churn import churn_by_dimension
from src.utils import bar_chart, format_currency, format_pct, line_chart


def parse_question(question: str) -> Dict[str, str]:
    normalized = " ".join(question.lower().strip().split())
    if not normalized:
        return {"intent": "empty", "normalized": normalized}

    if any(term in normalized for term in ["prioritize", "experiment", "reduce churn", "intervention", "what should we do", "what should we prioritize"]):
        return {"intent": "recommendation", "normalized": normalized}
    if any(term in normalized for term in ["churn", "at-risk", "at risk", "dormant"]):
        return {"intent": "churn", "normalized": normalized}
    if any(term in normalized for term in ["ltv", "value", "high-value", "high value", "concentration"]):
        return {"intent": "ltv", "normalized": normalized}
    if any(term in normalized for term in ["segment", "one-time", "one time", "repeat purchase", "repeat customers", "distribution"]):
        return {"intent": "segmentation", "normalized": normalized}
    if any(term in normalized for term in ["revenue", "top customers", "top 10 customers", "average order value", "trend", "country"]):
        return {"intent": "revenue", "normalized": normalized}
    return {"intent": "fallback", "normalized": normalized}


def handle_revenue_question(bundle: Dict[str, Any], normalized: str) -> Dict[str, Any]:
    transactions = bundle["transactions"]
    customers = bundle["customers"]
    segment_df = bundle["segment_summary"]
    revenue_trend = bundle["trends"]["revenue_trend"]

    if "trend" in normalized or "over time" in normalized:
        latest_month = revenue_trend.iloc[-1]
        return {
            "title": "Revenue Trend Over Time",
            "summary": f"Monthly revenue is loaded across {len(revenue_trend)} periods, with the latest month contributing {format_currency(float(latest_month['revenue']))}.",
            "chart": line_chart(revenue_trend, "order_month", "revenue", "Revenue Trend Over Time"),
            "recommendation": "Use the trend alongside churn and cohort views to separate seasonality from underlying retention issues.",
        }

    if "country" in normalized and "country" in transactions.columns:
        country_df = (
            transactions.groupby("country", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False).head(10)
        )
        top_country = country_df.iloc[0]
        return {
            "title": "Revenue by Country",
            "summary": f"{top_country['country']} is the top market at {format_currency(float(top_country['revenue']))} in revenue.",
            "chart": bar_chart(country_df, "country", "revenue", "Revenue by Country", horizontal=True),
            "table": country_df,
            "recommendation": "Concentrate retention and expansion plays first in the countries already producing the strongest commercial density.",
        }

    if "segment" in normalized:
        top_segment = segment_df.iloc[0]
        return {
            "title": "Revenue by Segment",
            "summary": f"{top_segment['customer_segment_label']} contributes the most revenue at {format_currency(float(top_segment['revenue']))}.",
            "chart": bar_chart(segment_df, "customer_segment_label", "revenue", "Revenue by Segment", horizontal=True),
            "table": segment_df[["customer_segment_label", "customers", "revenue"]],
            "recommendation": "Protect the lead segment with retention and upsell motions before spreading resources across smaller cohorts.",
        }

    if "top" in normalized and "customer" in normalized:
        top_customers = customers.sort_values("total_revenue", ascending=False).head(10)[
            ["customer_id", "total_revenue", "total_orders", "customer_segment_label", "recency_days"]
        ]
        return {
            "title": "Top Customers by Revenue",
            "summary": f"The top 10 customers contribute {format_currency(float(top_customers['total_revenue'].sum()))} in historical revenue.",
            "table": top_customers,
            "recommendation": "These accounts should sit inside a named retention or account development playbook, not a generic lifecycle journey.",
        }

    if "average order value" in normalized:
        aov_df = (
            customers.groupby("customer_segment_label", as_index=False)["avg_order_value"].mean().sort_values("avg_order_value", ascending=False)
        )
        return {
            "title": "Average Order Value by Segment",
            "summary": f"The highest average order value currently sits with {aov_df.iloc[0]['customer_segment_label']}.",
            "chart": bar_chart(aov_df, "customer_segment_label", "avg_order_value", "Average Order Value by Segment", horizontal=True),
            "table": aov_df,
            "recommendation": "Pair high basket-size segments with premium bundles and cross-sell rather than blanket discounting.",
        }

    return {
        "title": "Revenue Snapshot",
        "summary": f"Total filtered revenue is {format_currency(bundle['metrics']['total_revenue'])} across {bundle['metrics']['total_customers']:,} customers.",
        "recommendation": "Ask for revenue trend, revenue by segment, revenue by country, or top customers by revenue for a more focused cut.",
    }


def handle_churn_question(bundle: Dict[str, Any], normalized: str) -> Dict[str, Any]:
    customers = bundle["customers"]
    metrics = bundle["metrics"]

    if "segment" in normalized:
        segment_churn = churn_by_dimension(customers, "customer_segment_label")
        return {
            "title": "Churn Rate by Segment",
            "summary": f"Overall churn is {format_pct(metrics['churn_rate'])}, with the highest-risk segment sitting at the top of the chart.",
            "chart": bar_chart(segment_churn, "customer_segment_label", "churn_rate", "Churn by Segment", horizontal=True),
            "table": segment_churn[["customer_segment_label", "customers", "churn_rate", "at_risk_rate", "revenue"]],
            "recommendation": "Prioritize the segment combining high churn with meaningful revenue before expanding into lower-value risk pools.",
        }

    if "high-value" in normalized or "high value" in normalized:
        hv_risk = customers.loc[customers["high_value_at_risk"]].sort_values("historical_ltv", ascending=False)
        return {
            "title": "High-Value Customers at Risk",
            "summary": f"There are {len(hv_risk):,} high-value customers currently flagged as at risk or dormant.",
            "table": hv_risk[["customer_id", "historical_ltv", "estimated_90d_ltv", "recency_days", "customer_segment_label"]],
            "recommendation": "Trigger a direct retention intervention for this list before running broader win-back campaigns.",
        }

    if "dormant" in normalized:
        dormant = customers.loc[customers["is_churned"]]
        return {
            "title": "Dormant Customer Count",
            "summary": f"{len(dormant):,} customers are currently beyond the churn inactivity threshold.",
            "table": dormant[["customer_id", "total_revenue", "recency_days", "customer_segment_label"]].sort_values("total_revenue", ascending=False).head(25),
            "recommendation": "Use dormant customer spend history to split premium win-back from low-cost automated reactivation.",
        }

    if "at-risk" in normalized or "at risk" in normalized:
        at_risk = customers.loc[customers["is_at_risk"] | customers["is_churned"]].sort_values("total_revenue", ascending=False)
        return {
            "title": "At-Risk Customers",
            "summary": f"{metrics['at_risk_customers']:,} customers are approaching churn and {int(customers['is_churned'].sum()):,} are already churned.",
            "table": at_risk[["customer_id", "total_revenue", "recency_days", "risk_level", "customer_segment_label"]].head(30),
            "recommendation": "Sort this list by revenue and recency to create a two-tier retention queue: direct outreach for top accounts and automated journeys for the rest.",
        }

    return {
        "title": "Overall Churn Rate",
        "summary": f"The current churn rate is {format_pct(metrics['churn_rate'])}.",
        "recommendation": "Ask for churn by segment, at-risk customers, high-value at-risk customers, or dormant customer count for a sharper view.",
    }


def handle_ltv_question(bundle: Dict[str, Any], normalized: str) -> Dict[str, Any]:
    customers = bundle["customers"]
    segment_df = bundle["segment_summary"]
    concentration = bundle["concentration"]
    cohorts = bundle["cohorts"]

    if "country" in normalized and "country" in customers.columns:
        value_by_country = (
            customers.groupby("country", as_index=False)["historical_ltv"].mean().sort_values("historical_ltv", ascending=False).head(10)
        )
        return {
            "title": "LTV by Country",
            "summary": f"{value_by_country.iloc[0]['country']} has the highest average historical customer value in the current filtered view.",
            "chart": bar_chart(value_by_country, "country", "historical_ltv", "Average LTV by Country", horizontal=True),
            "table": value_by_country,
            "recommendation": "Markets with high customer value should receive differentiated retention and premiumization treatment.",
        }

    if "segment" in normalized:
        return {
            "title": "Value by Segment",
            "summary": f"{segment_df.iloc[0]['customer_segment_label']} currently contributes the most total customer value.",
            "chart": bar_chart(segment_df, "customer_segment_label", "revenue", "Value by Segment", horizontal=True),
            "table": segment_df[["customer_segment_label", "customers", "revenue"]],
            "recommendation": "Anchor growth planning around the segments that already prove both monetization and repeat behavior.",
        }

    if "low-frequency" in normalized or "low frequency" in normalized:
        low_freq = customers.loc[customers["high_value_low_frequency"]].sort_values("historical_ltv", ascending=False)
        return {
            "title": "High-Value Low-Frequency Customers",
            "summary": f"{len(low_freq):,} customers are valuable but still buy infrequently.",
            "table": low_freq[["customer_id", "historical_ltv", "total_orders", "avg_order_value", "recency_days"]],
            "recommendation": "These customers are strong candidates for replenishment reminders, bundles, or replenishment cadence messaging.",
        }

    if "concentration" in normalized or "top customers" in normalized:
        return {
            "title": "Revenue Concentration",
            "summary": f"The top 10% of customers drive {format_pct(concentration['top_10_pct'])} of revenue and the top 20% drive {format_pct(concentration['top_20_pct'])}.",
            "recommendation": "High concentration means a small customer cohort deserves white-glove retention coverage and regular monitoring.",
        }

    if "cohort" in normalized and not cohorts.empty:
        return {
            "title": "Value by Cohort",
            "summary": "Customer value varies by acquisition month, which helps separate strong customer cohorts from weaker ones.",
            "chart": bar_chart(cohorts, "cohort_month", "avg_ltv", "Average Value by Cohort"),
            "table": cohorts,
            "recommendation": "Use cohort differences to identify which acquisition periods or channels likely produced the strongest customers.",
        }

    top_value = customers.sort_values("historical_ltv", ascending=False).head(10)
    return {
        "title": "Top Value Customers",
        "summary": f"The highest-value customers are already visible in the top-value list, led by customer {top_value.iloc[0]['customer_id']}.",
        "table": top_value[["customer_id", "historical_ltv", "estimated_90d_ltv", "customer_segment_label"]],
        "recommendation": "Treat these customers like strategic accounts, especially when they also show elevated churn risk.",
    }


def handle_segmentation_question(bundle: Dict[str, Any], normalized: str) -> Dict[str, Any]:
    customers = bundle["customers"]
    segment_df = bundle["segment_summary"]

    if "repeat" in normalized or "one-time" in normalized or "one time" in normalized:
        comparison = pd.DataFrame(
            [
                {
                    "buyer_type": "One-Time Buyers",
                    "customers": int((customers["total_orders"] == 1).sum()),
                    "share": float((customers["total_orders"] == 1).mean()),
                },
                {
                    "buyer_type": "Repeat Buyers",
                    "customers": int((customers["total_orders"] > 1).sum()),
                    "share": float((customers["total_orders"] > 1).mean()),
                },
            ]
        )
        return {
            "title": "One-Time Buyers vs Repeat Buyers",
            "summary": f"Repeat purchase rate is {format_pct(bundle['metrics']['repeat_purchase_rate'])}, which highlights how much of the base has moved beyond a first order.",
            "chart": bar_chart(comparison, "buyer_type", "customers", "Buyer Type Comparison"),
            "table": comparison,
            "recommendation": "If one-time buyers dominate, second-purchase activation should outrank broad upsell campaigns.",
        }

    if "distribution" in normalized or "segment" in normalized:
        return {
            "title": "Segment Distribution",
            "summary": f"{segment_df.iloc[0]['customer_segment_label']} is the largest segment in the current filtered view.",
            "chart": bar_chart(segment_df, "customer_segment_label", "customers", "Segment Distribution", horizontal=True),
            "table": segment_df[["customer_segment_label", "customers", "revenue", "repeat_rate", "churn_rate"]],
            "recommendation": "Use segment mix to decide whether the business needs more activation, retention, or expansion investment.",
        }

    return {
        "title": "Segmentation Snapshot",
        "summary": "The customer base is already segmented into new, repeat, loyal, high-value, at-risk, dormant, and champion cohorts.",
        "recommendation": "Ask for segment distribution, repeat vs one-time buyers, dormant customers, or revenue contribution by segment for a deeper answer.",
    }


def handle_recommendation_question(bundle: Dict[str, Any], normalized: str) -> Dict[str, Any]:
    customers = bundle["customers"]
    metrics = bundle["metrics"]
    top_actions = []

    if metrics["high_value_at_risk"] > 0:
        top_actions.append("Retain high-value at-risk customers first with direct outreach and tailored offers.")
    if bundle["metrics"]["repeat_purchase_rate"] < 0.5:
        top_actions.append("Improve second-purchase conversion because too much of the base still behaves like one-time buyers.")
    if bundle["concentration"]["top_20_pct"] > 0.45:
        top_actions.append("Protect revenue concentration by creating a named retention playbook for top customers.")

    if not top_actions:
        top_actions = [
            "Scale loyalty and cross-sell programs for repeat and loyal cohorts.",
            "Test premium offers for top-value customers.",
            "Maintain a lightweight automated win-back program for dormant customers.",
        ]

    if "experiment" in normalized or "at-risk" in normalized or "at risk" in normalized:
        recommended_cards = bundle["experiment_cards"][:3]
        return {
            "title": "Recommended Experiments",
            "summary": "The current data points toward a short list of practical tests tied directly to churn and customer value.",
            "cards": recommended_cards,
            "recommendation": top_actions[0],
        }

    return {
        "title": "What To Prioritize First",
        "summary": "The highest-priority actions are ranked from the current churn, repeat behavior, and revenue concentration profile.",
        "bullets": top_actions[:3],
        "recommendation": "Start with the first action, then expand into acquisition or upsell only after the main retention leak is controlled.",
    }


def answer_question(question: str, bundle: Dict[str, Any]) -> Dict[str, Any]:
    parsed = parse_question(question)
    intent = parsed["intent"]
    normalized = parsed["normalized"]

    if intent == "empty":
        return {
            "title": "Ask a Business Question",
            "summary": "Type a question about churn, revenue, LTV, segmentation, or recommended actions to explore the current dataset.",
        }
    if intent == "revenue":
        return handle_revenue_question(bundle, normalized)
    if intent == "churn":
        return handle_churn_question(bundle, normalized)
    if intent == "ltv":
        return handle_ltv_question(bundle, normalized)
    if intent == "segmentation":
        return handle_segmentation_question(bundle, normalized)
    if intent == "recommendation":
        return handle_recommendation_question(bundle, normalized)

    return {
        "title": "Question Not Yet Supported",
        "summary": "Try a question about revenue, churn, LTV, segmentation, or next-best actions. The Ask the Data page is intentionally guided and deterministic.",
        "recommendation": "Suggested prompts: Show churn rate by segment, Show revenue trend over time, Show top 10 customers by revenue, Which customers are high-value and at risk?",
    }
