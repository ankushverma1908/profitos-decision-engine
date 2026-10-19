from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "warehouse" / "profitos.duckdb"
SQL_FILE = ROOT / "sql" / "marts" / "monthly_trends.sql"
OUTPUT = ROOT / "reports" / "monthly_trends.csv"
def main():
    sql = SQL_FILE.read_text(encoding="utf-8-sig")
    with duckdb.connect(str(DB), read_only=True) as con:
        result = con.execute(sql).df()
    print("\nMONTHLY ORDER TRENDS\n")
    print(result.to_string(index=False))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    print(f"\nReport saved to: {OUTPUT}")
if __name__ == "__main__":
    main()
