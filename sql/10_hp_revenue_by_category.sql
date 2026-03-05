WITH hp_customers AS (
    SELECT customer_id
    FROM (
        SELECT 
            o.customer_id,
            SUM(oi.price) AS monetary
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY o.customer_id
    ) t
    WHERE monetary > 500
)
SELECT 
    p.product_category_name,
    COUNT(oi.order_id) AS units_sold,
    SUM(oi.price) AS total_revenue,
    ROUND(SUM(oi.price) * 100.0 / SUM(SUM(oi.price)) OVER (), 2) AS revenue_percentage
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
JOIN hp_customers hp ON o.customer_id = hp.customer_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC;