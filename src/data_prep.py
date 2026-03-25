from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd


COLUMN_ALIASES = {
    "customer_id": [
        "customer_id",
        "customerid",
        "customer",
        "client_id",
        "client",
        "user_id",
    ],
    "order_id": ["order_id", "orderid", "invoice", "invoice_no", "invoiceno", "invoice number", "transaction_id"],
    "order_date": ["order_date", "orderdate", "invoice_date", "invoicedate", "date", "purchase_date"],
    "revenue": ["revenue", "sales", "amount", "order_value", "total", "gmv"],
    "quantity": ["quantity", "qty", "units"],
    "product": ["product", "product_name", "sku_name", "item", "description", "stockcode"],
    "category": ["category", "product_category", "department"],
    "country": ["country", "market", "region_country"],
    "segment": ["segment", "customer_segment", "persona"],
    "unit_price": ["unit_price", "unitprice", "price_per_unit", "price"],
}

REQUIRED_COLUMNS = ["customer_id", "order_id", "order_date", "revenue"]


@dataclass
class ValidationResult:
    is_valid: bool
    message: str
    mapped_columns: Dict[str, str]
    missing_columns: list[str]


def _normalize_name(name: str) -> str:
    return "".join(char.lower() for char in str(name) if char.isalnum())


def map_columns(df: pd.DataFrame) -> Dict[str, str]:
    normalized = {_normalize_name(column): column for column in df.columns}
    mapped: Dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            original = normalized.get(_normalize_name(alias))
            if original:
                mapped[canonical] = original
                break
    return mapped


def validate_columns(df: pd.DataFrame) -> ValidationResult:
    mapped = map_columns(df)
    missing = []
    for column in REQUIRED_COLUMNS:
        if column == "revenue":
            if "revenue" not in mapped and not {"quantity", "unit_price"}.issubset(mapped):
                missing.append(column)
        elif column not in mapped:
            missing.append(column)
    if missing:
        missing_list = ", ".join(missing)
        message = (
            "The uploaded file is missing required fields after automatic mapping. "
            f"Please include columns for: {missing_list}. Revenue can also be derived from quantity and unit price."
        )
        return ValidationResult(False, message, mapped, missing)
    return ValidationResult(True, "Columns validated successfully.", mapped, [])


def standardize_dataframe(df: pd.DataFrame, mapped_columns: Dict[str, str]) -> pd.DataFrame:
    renamed = df.rename(columns={source: target for target, source in mapped_columns.items()}).copy()
    standardized_columns = list(dict.fromkeys(["customer_id", "order_id", "order_date"] + list(mapped_columns.keys())))
    standardized = renamed[standardized_columns].copy()

    standardized["customer_id"] = standardized["customer_id"].astype(str).str.strip()
    standardized["order_id"] = standardized["order_id"].astype(str).str.strip()
    standardized["order_date"] = pd.to_datetime(standardized["order_date"], errors="coerce", utc=False)

    for optional_column in ["quantity", "unit_price"]:
        if optional_column in standardized.columns:
            standardized[optional_column] = pd.to_numeric(standardized[optional_column], errors="coerce")

    if "revenue" in standardized.columns:
        standardized["revenue"] = pd.to_numeric(standardized["revenue"], errors="coerce")
    elif {"quantity", "unit_price"}.issubset(standardized.columns):
        standardized["revenue"] = standardized["quantity"] * standardized["unit_price"]
    else:
        standardized["revenue"] = np.nan

    for text_column in ["product", "category", "country", "segment"]:
        if text_column in standardized.columns:
            standardized[text_column] = standardized[text_column].astype(str).replace("nan", np.nan)

    cancelled_mask = standardized["order_id"].str.lower().str.startswith("c", na=False)
    standardized = standardized.loc[~cancelled_mask].copy()
    standardized = standardized.dropna(subset=["order_date"])
    standardized = standardized.loc[standardized["quantity"].fillna(1) > 0].copy() if "quantity" in standardized.columns else standardized
    standardized = standardized.loc[standardized["unit_price"].fillna(1) > 0].copy() if "unit_price" in standardized.columns else standardized
    standardized = standardized.loc[standardized["revenue"].fillna(-1) >= 0].copy()
    standardized["customer_id"] = standardized["customer_id"].replace({"": np.nan, "nan": np.nan, "None": np.nan})
    standardized = standardized.loc[standardized["customer_id"].notna() & standardized["order_id"].ne("")]
    standardized = standardized.sort_values("order_date").reset_index(drop=True)
    return standardized


def data_quality_report(raw_df: pd.DataFrame, standardized_df: pd.DataFrame, mapped_columns: Dict[str, str]) -> Dict[str, object]:
    duplicate_count = int(raw_df.duplicated().sum())
    missing_values = raw_df.isna().sum().sort_values(ascending=False).to_dict()
    source_order_col = mapped_columns.get("order_id")
    cancelled_rows = int(raw_df[source_order_col].astype(str).str.lower().str.startswith("c").sum()) if source_order_col else 0

    invalid_revenue_rows = 0
    if "revenue" in mapped_columns:
        invalid_revenue_rows = int(pd.to_numeric(raw_df[mapped_columns["revenue"]], errors="coerce").isna().sum())
    elif {"quantity", "unit_price"}.issubset(mapped_columns):
        qty = pd.to_numeric(raw_df[mapped_columns["quantity"]], errors="coerce")
        price = pd.to_numeric(raw_df[mapped_columns["unit_price"]], errors="coerce")
        invalid_revenue_rows = int((qty.isna() | price.isna() | (qty <= 0) | (price <= 0)).sum())

    missing_customer_ids = 0
    if "customer_id" in mapped_columns:
        missing_customer_ids = int(raw_df[mapped_columns["customer_id"]].isna().sum())

    date_min = standardized_df["order_date"].min()
    date_max = standardized_df["order_date"].max()

    return {
        "row_count_raw": int(len(raw_df)),
        "row_count_processed": int(len(standardized_df)),
        "duplicate_count": duplicate_count,
        "cancelled_rows": cancelled_rows,
        "missing_values": missing_values,
        "invalid_revenue_rows": invalid_revenue_rows,
        "missing_customer_ids": missing_customer_ids,
        "date_range": (date_min, date_max),
        "mapped_columns": mapped_columns,
    }


def prepare_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object], ValidationResult]:
    validation = validate_columns(df)
    if not validation.is_valid:
        return pd.DataFrame(), {}, validation
    standardized = standardize_dataframe(df, validation.mapped_columns)
    quality = data_quality_report(df, standardized, validation.mapped_columns)
    return standardized, quality, validation
