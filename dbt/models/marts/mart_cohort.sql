WITH f AS (SELECT customer_id, DATE_TRUNC('month',MIN(order_date)) AS cohort_month FROM {{ ref('stg_orders') }} GROUP BY 1) SELECT * FROM f
