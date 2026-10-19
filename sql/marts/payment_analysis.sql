SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS unique_orders,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_record,
    ROUND(
        SUM(payment_value) /
        NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS payment_per_order
FROM raw_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;
