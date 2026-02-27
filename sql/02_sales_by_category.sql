SELECT 
    p.product_category_name,
    COUNT(oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_order_value,
    ROUND(SUM(oi.price) * 100.0 / SUM(SUM(oi.price)) OVER (), 2) AS revenue_percentage
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC;