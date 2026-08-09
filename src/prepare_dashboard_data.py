"""Build reproducible Tableau-ready tables from the public Olist dataset.

Example
-------
python src/prepare_dashboard_data.py --data-dir data/raw --output-dir outputs/tableau
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_FILES = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "translation": "product_category_name_translation.csv",
}

REQUIRED_COLUMNS = {
    "orders": {
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
    },
    "items": {
        "order_id",
        "order_item_id",
        "product_id",
        "price",
        "freight_value",
    },
    "customers": {
        "customer_id",
        "customer_unique_id",
        "customer_state",
    },
    "products": {"product_id", "product_category_name"},
    "translation": {"product_category_name", "product_category_name_english"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare delivered-order Olist tables for Tableau."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing the five required Olist CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where the four Tableau-ready CSV files will be written.",
    )
    return parser.parse_args()


def _read_required_csvs(data_dir: Path) -> dict[str, pd.DataFrame]:
    missing_files = [
        filename
        for filename in REQUIRED_FILES.values()
        if not (data_dir / filename).is_file()
    ]
    if missing_files:
        missing = ", ".join(sorted(missing_files))
        raise FileNotFoundError(f"Missing required files in {data_dir}: {missing}")

    frames = {
        name: pd.read_csv(data_dir / filename, low_memory=False)
        for name, filename in REQUIRED_FILES.items()
    }

    for name, required in REQUIRED_COLUMNS.items():
        missing_columns = required.difference(frames[name].columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{REQUIRED_FILES[name]} is missing columns: {missing}")

    return frames


def _validate_keys(frames: dict[str, pd.DataFrame]) -> None:
    unique_keys = {
        "orders": ["order_id"],
        "customers": ["customer_id"],
        "products": ["product_id"],
        "translation": ["product_category_name"],
        "items": ["order_id", "order_item_id"],
    }
    for name, keys in unique_keys.items():
        duplicate_count = int(frames[name].duplicated(keys).sum())
        if duplicate_count:
            joined_keys = ", ".join(keys)
            raise ValueError(
                f"{REQUIRED_FILES[name]} has {duplicate_count} duplicate rows "
                f"for expected key(s): {joined_keys}"
            )


def build_order_item_fact(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return one row per delivered order item with documented value fields."""
    _validate_keys(frames)

    orders = frames["orders"].copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    orders = orders.loc[orders["order_status"].eq("delivered")].copy()
    if orders.empty:
        raise ValueError("No delivered orders were found in the supplied orders file.")
    if orders["order_purchase_timestamp"].isna().any():
        invalid_count = int(orders["order_purchase_timestamp"].isna().sum())
        raise ValueError(
            f"Delivered orders contain {invalid_count} invalid purchase timestamp(s)."
        )

    items = frames["items"].copy()
    for column in ("price", "freight_value"):
        items[column] = pd.to_numeric(items[column], errors="coerce")
        if items[column].isna().any():
            invalid_count = int(items[column].isna().sum())
            raise ValueError(f"order_items.{column} has {invalid_count} invalid value(s).")
        if items[column].lt(0).any():
            negative_count = int(items[column].lt(0).sum())
            raise ValueError(
                f"order_items.{column} has {negative_count} negative value(s)."
            )

    fact = items.merge(
        orders[
            ["order_id", "customer_id", "order_purchase_timestamp"]
        ],
        on="order_id",
        how="inner",
        validate="many_to_one",
    )
    fact = fact.merge(
        frames["customers"][
            ["customer_id", "customer_unique_id", "customer_state"]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    fact = fact.merge(
        frames["products"][["product_id", "product_category_name"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    )
    fact = fact.merge(
        frames["translation"][
            ["product_category_name", "product_category_name_english"]
        ],
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )

    if fact[["customer_unique_id", "customer_state"]].isna().any().any():
        raise ValueError(
            "Some delivered order items could not be mapped to a unique customer and state."
        )

    fact["category_name"] = (
        fact["product_category_name_english"]
        .fillna(fact["product_category_name"])
        .fillna("unknown")
    )
    fact["order_month"] = (
        fact["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    )
    fact["merchandise_value"] = fact["price"]
    fact["gross_order_value"] = fact["price"] + fact["freight_value"]
    return fact


def _sales_summary(fact: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    summary = (
        fact.groupby(dimensions, as_index=False, dropna=False)
        .agg(
            orders=("order_id", "nunique"),
            customers=("customer_unique_id", "nunique"),
            items=("order_item_id", "size"),
            merchandise_value=("merchandise_value", "sum"),
            freight_value=("freight_value", "sum"),
            gross_order_value=("gross_order_value", "sum"),
        )
        .sort_values(dimensions)
        .reset_index(drop=True)
    )
    summary["avg_gross_order_value_per_order"] = (
        summary["gross_order_value"] / summary["orders"]
    )
    return summary


def build_output_tables(fact: pd.DataFrame) -> dict[str, pd.DataFrame]:
    monthly = _sales_summary(fact, ["order_month"])
    state = _sales_summary(fact, ["customer_state"])
    category = _sales_summary(fact, ["category_name"])

    ordered_fact = fact.sort_values(
        ["customer_unique_id", "order_purchase_timestamp", "order_id"]
    )
    customers = (
        ordered_fact.groupby("customer_unique_id", as_index=False)
        .agg(
            latest_customer_state=("customer_state", "last"),
            first_purchase_at=("order_purchase_timestamp", "min"),
            last_purchase_at=("order_purchase_timestamp", "max"),
            orders=("order_id", "nunique"),
            items=("order_item_id", "size"),
            merchandise_value=("merchandise_value", "sum"),
            freight_value=("freight_value", "sum"),
            gross_order_value=("gross_order_value", "sum"),
        )
        .sort_values("customer_unique_id")
        .reset_index(drop=True)
    )
    customers["avg_gross_order_value_per_order"] = (
        customers["gross_order_value"] / customers["orders"]
    )

    return {
        "monthly_sales.csv": monthly,
        "state_sales.csv": state,
        "category_sales.csv": category,
        "customer_summary.csv": customers,
    }


def main() -> None:
    args = parse_args()
    data_dir = args.data_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    frames = _read_required_csvs(data_dir)
    fact = build_order_item_fact(frames)
    tables = build_output_tables(fact)

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, table in tables.items():
        table.to_csv(output_dir / filename, index=False, encoding="utf-8-sig")
        print(f"Wrote {len(table):,} rows: {output_dir / filename}")


if __name__ == "__main__":
    main()
