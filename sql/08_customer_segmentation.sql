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
SELECT *,
       CASE 
           WHEN monetary > 1000 AND frequency > 5 AND last_purchase > CURRENT_DATE - INTERVAL '90 days' THEN 'VIP'
           WHEN monetary BETWEEN 500 AND 1000 THEN 'High Potential'
           WHEN last_purchase < CURRENT_DATE - INTERVAL '180 days' THEN 'At Risk'
           ELSE 'Regular'
       END AS segment
FROM customer_rfm;