from pathlib import Path
import pandas as pd
root = Path(__file__).resolve().parents[2]
file = root / "data" / "raw" / "olist_orders_dataset.csv"
if not file.exists():
    raise FileNotFoundError(f"Raw orders file not found: {file}")
df = pd.read_csv(file)
df["purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"], errors="coerce"
)
df = df.dropna(subset=["purchase_timestamp"])
df["month"] = df["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
audit = (
    df.groupby("month")
    .agg(
        order_count=("order_id", "nunique"),
        valid_purchase_dates=("purchase_timestamp", "count"),
    )
)
print("\nRAW ORDERS: LAST SIX MONTHS")
print(audit.tail(6).to_string())
print("\nRAW ORDERS: SEPTEMBER AND OCTOBER 2018")
print(
    audit.loc["2018-09-01":"2018-10-01"].to_string()
)
