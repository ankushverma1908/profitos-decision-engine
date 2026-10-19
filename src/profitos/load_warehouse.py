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
    missing = [
        filename for filename in TABLES.values()
        if not (RAW / filename).is_file()
    ]
    if missing:
        raise FileNotFoundError(
            f"Missing CSV files in {RAW}: {missing}"
        )
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(WAREHOUSE)) as con:
        for table, filename in TABLES.items():
            csv_path = (RAW / filename).as_posix().replace("'", "''")
            con.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT *
                FROM read_csv_auto('{csv_path}', header = true)
            """)
            count = con.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count:,} rows loaded")
    print(f"\nWarehouse created: {WAREHOUSE}")
if __name__ == "__main__":
    main()
