
"""RideMetrics Streamlit dashboard — Summit Cycles."""
import streamlit as st, pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title="RideMetrics — Summit Cycles",layout="wide")
st.title("🚴 RideMetrics — Retention, Churn & Experiment Analytics")
st.caption("Summit Cycles (fictional DTC bike shop) · Synthetic data · Jared Fontaine")
def load(p, fallback=None):
    fp=ROOT/p
    if fp.exists(): return pd.read_csv(fp)
    st.warning(f"Missing {p} — run the pipeline first."); return fallback
orders=load("data/raw/orders.csv"); rfm=load("data/marts/rfm_segments.csv"); churn=load("data/marts/churn_risk.csv"); fc=load("data/marts/forecast.csv")
tab1,tab2,tab3,tab4,tab5=st.tabs(["Executive KPIs","Cohort & RFM","A/B Test","Churn Risk","Forecast"])
with tab1:
    if orders is not None:
        c1,c2,c3,c4=st.columns(4); c1.metric("Revenue",f"${orders.order_total.sum():,.0f}"); c2.metric("Orders",f"{len(orders):,}"); c3.metric("AOV",f"${orders.order_total.mean():.2f}"); c4.metric("Customers",orders.customer_id.nunique())
        st.line_chart(orders.assign(m=pd.to_datetime(orders.order_date).dt.to_period("M").astype(str)).groupby("m").order_total.sum())
with tab2:
    if rfm is not None: st.dataframe(rfm.groupby("segment").agg(customers=("monetary","size"),revenue=("monetary","sum"))); st.bar_chart(rfm.groupby("segment").monetary.sum())
    p=ROOT/"reports/charts/cohort_retention.png"
    if p.exists(): st.image(str(p))
with tab3:
    st.write("Free shipping $75 (treatment) vs $99 (control). See analysis/02_ab_test.py and reports/FINDINGS.md for z-test, CI and ship decision.")
    p=ROOT/"reports/charts/ab_test_conversion.png"
    if p.exists(): st.image(str(p))
with tab4:
    if churn is not None: st.dataframe(churn.sort_values("churn_score",ascending=False).head(50)); st.bar_chart(churn.risk_tier.value_counts())
with tab5:
    if fc is not None: st.dataframe(fc); st.line_chart(fc.set_index("month")[["forecast","lower","upper"]])
