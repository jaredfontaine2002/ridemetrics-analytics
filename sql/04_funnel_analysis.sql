
-- 04 Funnel: distinct sessions per GA4 event, by variant/device
CREATE OR REPLACE TABLE mart_funnel AS
SELECT experiment_variant, device, event_name, COUNT(DISTINCT session_id) AS sessions
FROM read_csv_auto('data/raw/sessions.csv') GROUP BY 1,2,3 ORDER BY 1,2,3;
