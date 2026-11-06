SELECT customer_id, COUNT(*) AS frequency, SUM(order_total) AS monetary, MAX(order_date) AS last_order FROM {{ ref('stg_orders') }} GROUP BY 1
