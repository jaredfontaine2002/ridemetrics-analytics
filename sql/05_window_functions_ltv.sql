
-- 05 Window functions: ROW_NUMBER/RANK/LAG, running totals, cumulative LTV
CREATE OR REPLACE TABLE mart_ltv AS
WITH ordered AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_seq,
 RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS order_rank_by_value,
 LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date,
 SUM(order_total) OVER (PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
 FROM fct_orders)
SELECT * FROM ordered;
