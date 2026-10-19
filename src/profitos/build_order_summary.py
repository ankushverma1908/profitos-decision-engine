from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "warehouse" / "profitos.duckdb"
SQL_FILE = ROOT / "sql" / "marts" / "order_business_summary.sql"
OUTPUT = ROOT / "data" / "processed" / "order_business_summary.parquet"
def main():
    sql = SQL_FILE.read_text(encoding="utf-8-sig")
    with duckdb.connect(str(DB), read_only=True) as con:
        result = con.execute(sql).df()
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        result.to_parquet(OUTPUT, index=False)
        print("\nORDER-LEVEL BUSINESS SUMMARY\n")
        print(f"Total rows: {len(result):,}")
        print(f"Unique orders: {result['order_id'].nunique():,}")
        print(f"Duplicate order IDs: {result['order_id'].duplicated().sum():,}")
        print(f"Total item sales: R${result['item_sales'].sum():,.2f}")
        print(f"Total freight charged: R${result['freight_charged'].sum():,.2f}")
        print(f"Total recorded payment value: R${result['total_payment_value'].sum():,.2f}")
        print(f"\nSaved to: {OUTPUT}")
if __name__ == "__main__":
    main()
