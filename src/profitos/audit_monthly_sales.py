from pathlib import Path
import pandas as pd
root = Path(__file__).resolve().parents[2]
file = root / "data" / "processed" / "order_business_summary.parquet"
df = pd.read_parquet(file)
df["purchase_timestamp"] = pd.to_datetime(
    df["purchase_timestamp"], errors="coerce"
)
df["item_sales"] = pd.to_numeric(df["item_sales"], errors="coerce")
df = df.dropna(subset=["purchase_timestamp", "item_sales"])
df["month"] = df["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
audit = (
    df.groupby("month")
    .agg(
        record_count=("item_sales", "size"),
        item_sales=("item_sales", "sum"),
    )
)
full_months = pd.date_range(
    audit.index.min(), audit.index.max(), freq="MS"
)
audit = audit.reindex(full_months)
audit.index.name = "month"
audit["record_count"] = audit["record_count"].fillna(0).astype(int)
audit["item_sales"] = audit["item_sales"].fillna(0.0)
print("\nMONTHLY DATA AUDIT")
print(audit.tail(18).to_string())
print("\nMONTHS WITH NO RECORDS")
print(audit[audit["record_count"] == 0].to_string())
print("\nMONTHS WITH RECORDS BUT ZERO SALES")
print(
    audit[
        (audit["record_count"] > 0) & (audit["item_sales"] == 0)
    ].to_string()
)
