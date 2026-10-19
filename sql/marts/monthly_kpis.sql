SELECT
    order_month,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'canceled'
    ) AS canceled_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_status = 'delivered'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS delivered_order_rate_pct,
    ROUND(SUM(item_sales), 2) AS item_sales,
    ROUND(SUM(freight_charged), 2) AS freight_charged,
    ROUND(SUM(total_payment_value), 2) AS recorded_payment_value,
    ROUND(AVG(item_sales), 2) AS average_item_sales_per_order
FROM read_parquet('data/processed/order_business_summary.parquet')
GROUP BY order_month
ORDER BY order_month;
