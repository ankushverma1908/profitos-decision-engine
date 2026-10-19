
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"

# Primary/business key columns to inspect for duplicates.
KEY_COLUMNS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": [
        "order_id", "payment_sequential"
    ],
    "olist_order_reviews_dataset.csv": ["review_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}


def inspect_file(file_path):
    df = pd.read_csv(file_path, low_memory=False)

    missing_cells = int(df.isna().sum().sum())
    total_cells = int(df.shape[0] * df.shape[1])

    result = {
        "file": file_path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": missing_cells,
        "missing_pct": round(
            missing_cells / total_cells * 100, 2
        ) if total_cells else 0,
        "key_duplicate_rows": None,
        "key_missing_rows": None,
    }

    keys = KEY_COLUMNS.get(file_path.name)

    if keys and all(column in df.columns for column in keys):
        result["key_duplicate_rows"] = int(
            df.duplicated(subset=keys).sum()
        )
        result["key_missing_rows"] = int(
            df[keys].isna().any(axis=1).sum()
        )

    print("\n" + "=" * 65)
    print(f"FILE: {file_path.name}")
    print(f"ROWS: {len(df):,}")
    print(f"COLUMNS: {len(df.columns)}")
    print(f"FULL DUPLICATE ROWS: {result['duplicate_rows']:,}")
    print(f"MISSING CELLS: {missing_cells:,}")
    print(f"MISSING DATA: {result['missing_pct']}%")

    if keys:
        print(f"KEY COLUMNS: {keys}")
        print(f"DUPLICATE KEY ROWS: {result['key_duplicate_rows']:,}")
        print(f"ROWS WITH MISSING KEY: {result['key_missing_rows']:,}")

    print("\nCOLUMN DETAILS:")
    print(
        pd.DataFrame({
            "data_type": df.dtypes.astype(str),
            "missing_values": df.isna().sum(),
            "unique_values": df.nunique(dropna=True),
        }).to_string()
    )

    return result


def main():
    if not RAW_DATA.exists():
        raise FileNotFoundError(f"Data folder not found: {RAW_DATA}")

    files = sorted(RAW_DATA.glob("*.csv"))

    if not files:
        raise FileNotFoundError(f"No CSV files found in: {RAW_DATA}")

    print(f"ProfitOS data-quality inspection")
    print(f"Data directory: {RAW_DATA}")
    print(f"CSV files found: {len(files)}")

    results = []

    for file_path in files:
        results.append(inspect_file(file_path))

    REPORTS.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS / "data_quality_report.csv"

    report = pd.DataFrame(results)
    report.to_csv(report_path, index=False)

    print("\n" + "=" * 65)
    print("INSPECTION COMPLETE")
    print(report.to_string(index=False))
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
