
-- 02 Cohort retention: first-order cohort (CTE) + months-since-first matrix
CREATE OR REPLACE TABLE mart_cohort_retention AS
WITH first_order AS (SELECT customer_id, DATE_TRUNC('month', MIN(order_date))::DATE AS cohort_month FROM fct_orders GROUP BY 1),
cohort_size AS (SELECT cohort_month, COUNT(*) AS cohort_customers FROM first_order GROUP BY 1)
SELECT f.cohort_month, cs.cohort_customers,
 CAST(DATE_DIFF('month', f.cohort_month, DATE_TRUNC('month', o.order_date)) AS INTEGER) AS months_since_first,
 COUNT(DISTINCT o.customer_id) AS active_customers,
 ROUND(COUNT(DISTINCT o.customer_id)*1.0/cs.cohort_customers,4) AS retention_rate
FROM fct_orders o JOIN first_order f USING(customer_id) JOIN cohort_size cs USING(cohort_month)
GROUP BY 1,2,3 ORDER BY 1,3;
