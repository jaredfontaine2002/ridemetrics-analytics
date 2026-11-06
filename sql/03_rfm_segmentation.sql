
-- 03 RFM with NTILE(5) window functions (snapshot = max order date)
CREATE OR REPLACE TABLE mart_rfm AS
WITH snap AS (SELECT MAX(order_date) AS snapshot_date FROM fct_orders),
rfm AS (SELECT customer_id, DATE_DIFF('day', MAX(order_date), (SELECT snapshot_date FROM snap)) AS recency_days, COUNT(*) AS frequency, SUM(order_total) AS monetary FROM fct_orders GROUP BY 1),
scored AS (SELECT *,
 NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
 NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
 NTILE(5) OVER (ORDER BY monetary ASC) AS m_score FROM rfm)
SELECT *, CASE WHEN r_score>=4 AND f_score>=4 THEN 'Champions' WHEN r_score>=3 AND f_score>=3 THEN 'Loyal' WHEN r_score>=4 AND f_score<=2 THEN 'Potential' WHEN r_score<=2 AND f_score>=3 THEN 'At Risk' WHEN r_score<=2 AND f_score<=2 THEN 'Lost' ELSE 'Other' END AS segment FROM scored;
