WITH first_orders AS (
    SELECT customer_id, MIN(order_purchase_timestamp)::date AS first_order_date
    FROM orders
    GROUP BY customer_id
),
cohorts AS (
    SELECT 
        DATE_TRUNC('month', first_order_date) AS cohort_month,
        DATE_TRUNC('month', order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT o.customer_id) AS users
    FROM orders o
    JOIN first_orders f ON o.customer_id = f.customer_id
    GROUP BY 1,2
)
SELECT cohort_month,
       order_month,
       users,
       ROUND(users * 100.0 / SUM(users) OVER (PARTITION BY cohort_month),2) AS retention_rate_pct
FROM cohorts
ORDER BY cohort_month, order_month;