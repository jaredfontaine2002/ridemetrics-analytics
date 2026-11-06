
import pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_no_null_pks():
    for f,pk in [("customers.csv","customer_id"),("orders.csv","order_id"),("products.csv","product_id")]:
        df=pd.read_csv(ROOT/f"data/raw/{f}"); assert df[pk].notna().all() and df[pk].is_unique
def test_dates_in_range():
    o=pd.read_csv(ROOT/"data/raw/orders.csv",parse_dates=["order_date"]); assert o.order_date.between("2023-01-01","2024-12-31").all()
def test_experiment_split():
    s=pd.read_csv(ROOT/"data/raw/sessions.csv"); per=s.drop_duplicates("session_id"); share=per.experiment_variant.value_counts(normalize=True); assert share.between(0.45,0.55).all(), share
def test_revenue_positive():
    o=pd.read_csv(ROOT/"data/raw/orders.csv"); assert (o.order_total>0).all()
if __name__=="__main__":
    test_no_null_pks(); test_dates_in_range(); test_experiment_split(); test_revenue_positive(); print("All data quality checks passed")
