WITH customer_orders AS (
    SELECT 
        o.customer_id,
        MAX(o.order_purchase_timestamp) AS last_purchase,
        COUNT(o.order_id) AS frequency,
        SUM(oi.price) AS monetary
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT 
    customer_id,
    EXTRACT(DAY FROM (CURRENT_DATE - last_purchase)) AS recency_days,
    frequency,
    monetary
FROM customer_orders
ORDER BY monetary DESC
LIMIT 20;