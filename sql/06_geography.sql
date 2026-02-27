-- Выручка по штатам клиентов
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    ROUND(SUM(oi.price) * 100.0 / SUM(SUM(oi.price)) OVER (), 2) AS revenue_percentage
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC;

-- Выручка по городам продавцов
SELECT 
    s.seller_city,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    ROUND(SUM(oi.price) * 100.0 / SUM(SUM(oi.price)) OVER (), 2) AS revenue_percentage
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY s.seller_city
ORDER BY total_revenue DESC
LIMIT 20;