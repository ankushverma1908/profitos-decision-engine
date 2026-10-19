SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name,
        'unknown'
    ) AS category,
    COUNT(DISTINCT i.order_id) AS order_count,
    COUNT(*) AS order_item_count,
    ROUND(SUM(i.price), 2) AS item_sales,
    ROUND(SUM(i.freight_value), 2) AS freight_charged,
    ROUND(AVG(i.price), 2) AS average_item_price
FROM raw_order_items AS i
LEFT JOIN raw_products AS p
    ON i.product_id = p.product_id
LEFT JOIN raw_category_translation AS t
    ON p.product_category_name = t.product_category_name
GROUP BY 1
ORDER BY item_sales DESC
LIMIT 15;
