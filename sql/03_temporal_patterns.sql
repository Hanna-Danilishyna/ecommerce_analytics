SELECT 
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    COUNT(*) AS total_orders,
    SUM(oi.price) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_order_value,
    ROUND(SUM(oi.price) * 100.0 / SUM(SUM(oi.price)) OVER (), 2) AS revenue_percentage,
    COUNT(DISTINCT o.customer_id) AS active_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;