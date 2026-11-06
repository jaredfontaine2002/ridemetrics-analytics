
"""Load raw CSVs into DuckDB and run sql/ in order, exporting marts."""
import duckdb, pathlib
ROOT=pathlib.Path(__file__).parent
con=duckdb.connect(str(ROOT/"ridemetrics.duckdb"))
for f in sorted((ROOT/"sql").glob("*.sql")):
    print("Running",f.name); con.execute(f.read_text())
import os
(ROOT/"data/marts").mkdir(parents=True,exist_ok=True)
for tbl in ["dim_customers","dim_products","dim_date","fct_orders","fct_order_items","mart_cohort_retention","mart_rfm","mart_funnel","mart_ltv","mart_ab_test"]:
    try:
        con.execute(f"COPY (SELECT * FROM {tbl}) TO '{ROOT}/data/marts/{tbl}.csv' (HEADER, DELIMITER ',')"); print("exported",tbl)
    except Exception as e: print("skip",tbl,e)
con.close(); print("Done -> ridemetrics.duckdb")
