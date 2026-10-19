SELECT
    DATE_TRUNC(
        'month',
        CAST(order_purchase_timestamp AS TIMESTAMP)
    )::DATE AS order_month,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'canceled'
    ) AS canceled_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE order_status = 'canceled'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate_pct
FROM raw_orders
GROUP BY 1
ORDER BY 1;
