from pathlib import Path
import pandas as pd
root = Path(__file__).resolve().parents[2]
file = root / "data" / "raw" / "olist_orders_dataset.csv"
df = pd.read_csv(file)
df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"], errors="coerce"
)
print("\nLATEST 15 RAW ORDERS")
print(
    df.sort_values("order_purchase_timestamp", ascending=False)[
        ["order_id", "order_purchase_timestamp", "order_status"]
    ].head(15).to_string(index=False)
)
df["month"] = (
    df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
)
recent_months = [
    pd.Timestamp("2018-09-01"),
    pd.Timestamp("2018-10-01"),
]
recent = df[df["month"].isin(recent_months)]
print("\nORDER STATUS BY MONTH: SEPTEMBER AND OCTOBER 2018")
print(
    recent.groupby(["month", "order_status"])
    .size()
    .unstack(fill_value=0)
    .to_string()
)
print("\nLATEST VALID PURCHASE TIMESTAMP")
print(df["order_purchase_timestamp"].max())
