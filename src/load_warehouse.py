
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
WAREHOUSE = ROOT / "data" / "warehouse" / "profitos.duckdb"

TABLES = {
    "raw_customers": "olist_customers_dataset.csv",
    "raw_geolocation": "olist_geolocation_dataset.csv",
    "raw_orders": "olist_orders_dataset.csv",
    "raw_order_items": "olist_order_items_dataset.csv",
    "raw_payments": "olist_order_payments_dataset.csv",
    "raw_reviews": "olist_order_reviews_dataset.csv",
    "raw_products": "olist_products_dataset.csv",
    "raw_sellers": "olist_sellers_dataset.csv",
    "raw_category_translation": "product_category_name_translation.csv",
}


def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Raw data folder not found: {RAW}")

    missing_files = [
        filename for filename in TABLES.values()
        if not (RAW / filename).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            f"Missing source files: {missing_files}"
        )

    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(WAREHOUSE)) as con:
        for table_name, filename in TABLES.items():
            csv_path = (RAW / filename).as_posix()
            csv_path = csv_path.replace("'", "''")

            con.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM read_csv_auto('{csv_path}', header = true)
            """)

            count = con.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            print(f"{table_name}: {count:,} rows loaded")

    print(f"\nWarehouse created successfully:\n{WAREHOUSE}")


if __name__ == "__main__":
    main()
