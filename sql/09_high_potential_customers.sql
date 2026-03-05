WITH customer_rfm AS (
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
    last_purchase,
    frequency,
    monetary,
    EXTRACT(DAY FROM (CURRENT_DATE - last_purchase)) AS recency_days
FROM customer_rfm
WHERE monetary > 500
ORDER BY monetary DESC;