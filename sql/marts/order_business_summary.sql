WITH item_summary AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS item_sales,
        SUM(freight_value) AS freight_charged
    FROM raw_order_items
    GROUP BY order_id
),
payment_summary AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment_value,
        COUNT(*) AS payment_record_count
    FROM raw_payments
    GROUP BY order_id
)
SELECT
    o.order_id,
    CAST(o.order_purchase_timestamp AS TIMESTAMP) AS purchase_timestamp,
    CAST(
        DATE_TRUNC(
            'month',
            CAST(o.order_purchase_timestamp AS TIMESTAMP)
        ) AS DATE
    ) AS order_month,
    o.order_status,
    COALESCE(i.item_count, 0) AS item_count,
    ROUND(COALESCE(i.item_sales, 0), 2) AS item_sales,
    ROUND(COALESCE(i.freight_charged, 0), 2) AS freight_charged,
    ROUND(COALESCE(p.total_payment_value, 0), 2) AS total_payment_value,
    COALESCE(p.payment_record_count, 0) AS payment_record_count
FROM raw_orders o
LEFT JOIN item_summary i
    ON o.order_id = i.order_id
LEFT JOIN payment_summary p
    ON o.order_id = p.order_id;
