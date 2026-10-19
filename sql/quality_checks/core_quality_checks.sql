-- 1. Duplicate order IDs in the orders table
SELECT
    'duplicate_order_ids' AS check_name,
    COUNT(*) AS issue_count
FROM (
    SELECT order_id
    FROM raw_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
)
UNION ALL
-- 2. Missing order IDs in payment records
SELECT
    'missing_payment_order_ids',
    COUNT(*)
FROM raw_payments
WHERE order_id IS NULL OR TRIM(order_id) = ''
UNION ALL
-- 3. Negative payment values
SELECT
    'negative_payment_values',
    COUNT(*)
FROM raw_payments
WHERE payment_value < 0
UNION ALL
-- 4. Payments referencing unknown orders
SELECT
    'payments_without_matching_order',
    COUNT(*)
FROM raw_payments p
LEFT JOIN raw_orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL
UNION ALL
-- 5. Order items referencing unknown orders
SELECT
    'items_without_matching_order',
    COUNT(*)
FROM raw_order_items i
LEFT JOIN raw_orders o
    ON i.order_id = o.order_id
WHERE o.order_id IS NULL
UNION ALL
-- 6. Order items with negative price or freight
SELECT
    'items_with_negative_price_or_freight',
    COUNT(*)
FROM raw_order_items
WHERE price < 0 OR freight_value < 0;
