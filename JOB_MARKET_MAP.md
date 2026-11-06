# Job Market Map — Skill → Where It Is Demonstrated
Demand % from 2025-26 job-posting research summary supplied for this project (SQL 85-94%, Excel 78-82%*, Python 48-71%, Tableau/Power BI 54-65%, Statistics 42-48%, A/B testing ~37%, ETL/ELT ~41%, data modeling ~31-35%, dbt premium 30-50%).
*Excel: this repo uses CSV marts that open directly in Excel; pivot-ready flat files are the Excel deliverable.

| Skill / Technique | % Postings | Demonstrated In |
|---|---|---|
| SQL — CTEs, window functions, joins | 85-94% | sql/02,03,05 (NTILE, ROW_NUMBER, RANK, LAG, running totals) |
| Python / pandas | 48-71% | analysis/*.py, data/generate_data.py |
| Tableau / Power BI | 54-65% | BI_SPEC.md, dashboard/app.py (Streamlit equivalent) |
| Statistics / scipy, statsmodels | 42-48% | analysis/02_ab_test.py, 04_forecast.py |
| A/B testing | ~37% | analysis/02_ab_test.py, sql/06_ab_test_aggregates.sql |
| Data modeling (star schema) | ~31-35% | sql/01_star_schema_build.sql, dbt/ |
| ETL/ELT + dbt | ~41% / dbt mainstream | warehouse.py, dbt/models/, dbt/models/schema.yml tests |
| Cohort / RFM / CLV | core analyst technique | analysis/01_cohort_rfm.py, sql/02,03 |
| Churn / scikit-learn ML | growth area | analysis/03_churn_model.py |
| Forecasting | growth area | analysis/04_forecast.py |
| Cloud warehouse concepts (DuckDB as local BigQuery/Snowflake analogue) | warehouse demand | warehouse.py, README swap-in guide |
