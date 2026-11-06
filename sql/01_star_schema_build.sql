
-- 01 Star schema: raw CSVs -> dims + facts (DuckDB). Kimball-style modeling.
CREATE OR REPLACE TABLE dim_customers AS SELECT customer_id, signup_date::DATE AS signup_date, country, acquisition_channel, DATE_TRUNC('month', signup_date)::DATE AS signup_month FROM read_csv_auto('data/raw/customers.csv');
CREATE OR REPLACE TABLE dim_products AS SELECT * FROM read_csv_auto('data/raw/products.csv');
CREATE OR REPLACE TABLE fct_orders AS SELECT order_id, customer_id, order_date::DATE AS order_date, order_total, channel FROM read_csv_auto('data/raw/orders.csv');
CREATE OR REPLACE TABLE fct_order_items AS SELECT * FROM read_csv_auto('data/raw/order_items.csv');
CREATE OR REPLACE TABLE dim_date AS SELECT d::DATE AS date, EXTRACT(year FROM d) AS year, EXTRACT(month FROM d) AS month, DATE_TRUNC('month',d)::DATE AS month_start FROM (SELECT UNNEST(generate_series(DATE '2023-01-01', DATE '2024-12-31', INTERVAL 1 DAY)) AS d);
