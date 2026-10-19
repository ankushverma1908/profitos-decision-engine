from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "warehouse" / "profitos.duckdb"
SQL_FILE = ROOT / "sql" / "marts" / "category_performance.sql"
def main():
    if not DB.exists():
        raise FileNotFoundError(f"Database not found: {DB}")
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")
    sql = SQL_FILE.read_text(encoding="utf-8-sig")
    with duckdb.connect(str(DB), read_only=True) as con:
        result = con.execute(sql).df()
    print("\nTOP 15 PRODUCT CATEGORIES BY ITEM SALES\n")
    print(result.to_string(index=False))
    output = ROOT / "reports" / "category_performance.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(f"\nReport saved to: {output}")
if __name__ == "__main__":
    main()
