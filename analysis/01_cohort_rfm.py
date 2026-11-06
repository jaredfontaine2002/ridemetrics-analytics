
"""Cohort retention + RFM + CLV."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CH=ROOT/"reports/charts"; CH.mkdir(parents=True,exist_ok=True); (ROOT/"data/marts").mkdir(parents=True,exist_ok=True)
orders=pd.read_csv(ROOT/"data/raw/orders.csv",parse_dates=["order_date"])
orders["month"]=orders.order_date.dt.to_period("M").dt.to_timestamp()
first=orders.groupby("customer_id").order_date.min().dt.to_period("M").dt.to_timestamp().rename("cohort")
o=orders.join(first,on="customer_id"); o["idx"]=((o.month.dt.year-o.cohort.dt.year)*12+(o.month.dt.month-o.cohort.dt.month))
cohort=o.groupby(["cohort","idx"]).customer_id.nunique().unstack(fill_value=0)
sizes=o.groupby("cohort").customer_id.nunique(); retention=cohort.div(sizes,axis=0)
retention.to_csv(ROOT/"data/marts/cohort_retention_matrix.csv")
plt.figure(figsize=(12,7)); sns.heatmap(retention.iloc[:,:13],annot=True,fmt=".0%",cmap="Blues",vmin=0,vmax=0.6); plt.title("Cohort Retention — Summit Cycles"); plt.tight_layout(); plt.savefig(CH/"cohort_retention.png",dpi=150); plt.close()
# RFM
snap=orders.order_date.max()+pd.Timedelta(days=1)
rfm=orders.groupby("customer_id").agg(recency=("order_date",lambda x:(snap-x.max()).days),frequency=("order_id","count"),monetary=("order_total","sum"))
rfm["r"]=pd.qcut(rfm.recency,5,labels=[5,4,3,2,1]).astype(int); rfm["f"]=pd.qcut(rfm.frequency.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int); rfm["m"]=pd.qcut(rfm.monetary,5,labels=[1,2,3,4,5],duplicates="drop").astype(int)
def seg(r):
    if r.r>=4 and r.f>=4: return "Champions"
    if r.r>=3 and r.f>=3: return "Loyal"
    if r.r>=4 and r.f<=2: return "Potential"
    if r.r<=2 and r.f>=3: return "At Risk"
    if r.r<=2 and r.f<=2: return "Lost"
    return "Other"
rfm["segment"]=rfm.apply(seg,axis=1); rfm.to_csv(ROOT/"data/marts/rfm_segments.csv")
share=rfm.groupby("segment").monetary.sum(); share_pct=(share/share.sum()*100).round(1)
plt.figure(figsize=(8,5)); share.sort_values().plot(kind="barh"); plt.title("Revenue by RFM Segment"); plt.tight_layout(); plt.savefig(CH/"rfm_revenue_share.png",dpi=150); plt.close()
aov=orders.order_total.mean(); freq=rfm.frequency.mean(); margin=0.38; clv_hist=rfm.monetary.mean(); clv_est=aov*freq*margin
m1=retention[1].mean() if 1 in retention else np.nan; m3=retention[3].mean() if 3 in retention else np.nan
print("=== FINDINGS 01 Cohort/RFM ===")
print(f"Cohorts: {len(retention)} | Month-1 retention {m1:.1%} | Month-3 retention {m3:.1%}")
print("Segment revenue share %:"); print(share_pct.to_string())
print(f"AOV ${aov:.2f} | Avg frequency {freq:.2f} | Historical CLV ${clv_hist:.2f} | Simple CLV estimate (AOV*freq*38% margin) ${clv_est:.2f}")
rfm.groupby("segment").size().to_string()
print(rfm.groupby("segment").size())
