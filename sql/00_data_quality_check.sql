-- Duplicates
SELECT customer_id, COUNT(*) AS count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Negative
SELECT *
FROM order_items
WHERE price < 0;

-- Null
SELECT *
FROM orders
WHERE order_purchase_timestamp IS NULL;