
-- 06 A/B aggregates: one row per session, conversion + revenue per variant
CREATE OR REPLACE TABLE mart_ab_test AS
WITH per_session AS (SELECT session_id, experiment_variant, MAX(is_new_customer::INT) AS is_new, MAX(CASE WHEN event_name='purchase' THEN 1 ELSE 0 END) AS converted, SUM(revenue) AS revenue FROM read_csv_auto('data/raw/sessions.csv') GROUP BY 1,2)
SELECT experiment_variant, COUNT(*) AS sessions, SUM(converted) AS conversions, ROUND(AVG(converted),4) AS conversion_rate, ROUND(AVG(revenue),2) AS revenue_per_session, ROUND(AVG(CASE WHEN converted=1 THEN revenue END),2) AS aov FROM per_session GROUP BY 1;
