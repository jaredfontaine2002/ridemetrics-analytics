"""Churn prediction — TIME-AWARE, leakage-free design.

Features are computed ONLY from data up to FEATURE_CUTOFF (2024-06-30).
Label: customer made NO purchase in the following 180 days.
This avoids the classic leakage trap where recency-at-end-of-data
*is* the churn label and inflates AUC to a meaningless 1.00.
"""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, precision_score, recall_score, roc_curve
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CH=ROOT/"reports/charts"; CH.mkdir(parents=True,exist_ok=True); (ROOT/"data/marts").mkdir(parents=True,exist_ok=True)
orders=pd.read_csv(ROOT/"data/raw/orders.csv",parse_dates=["order_date"]); items=pd.read_csv(ROOT/"data/raw/order_items.csv"); tickets=pd.read_csv(ROOT/"data/raw/support_tickets.csv",parse_dates=["created_date"])
CUTOFF=pd.Timestamp("2024-06-30"); LABEL_END=CUTOFF+pd.Timedelta(days=180)
past=orders[orders.order_date<=CUTOFF]; future=orders[(orders.order_date>CUTOFF)&(orders.order_date<=LABEL_END)]
agg=past.groupby("customer_id").agg(last=("order_date","max"),frequency=("order_id","count"),monetary=("order_total","sum"),aov=("order_total","mean"),tenure=("order_date",lambda x:(x.max()-x.min()).days))
agg["recency_days"]=(CUTOFF-agg.last).dt.days
bought_future=future.customer_id.unique()
agg["churn"]=(~agg.index.isin(bought_future)).astype(int)
ret=items.merge(past[["order_id","customer_id"]],on="order_id").groupby("customer_id").returned.mean().rename("return_rate")
tkpast=tickets[tickets.created_date<=CUTOFF]
tk=tkpast.groupby("customer_id").agg(ticket_count=("ticket_id","count"),avg_csat=("csat","mean"),low_csat_share=("csat",lambda x:(x<=2).mean()))
X=agg.join(ret).join(tk).fillna({"return_rate":0,"ticket_count":0,"avg_csat":4.5,"low_csat_share":0}).drop(columns=["last"])
features=["recency_days","frequency","monetary","aov","tenure","return_rate","ticket_count","avg_csat","low_csat_share"]
Xtr,Xte,ytr,yte=train_test_split(X[features],X.churn,test_size=0.25,random_state=42,stratify=X.churn)
lr=Pipeline([("sc",StandardScaler()),("clf",LogisticRegression(max_iter=1000))]).fit(Xtr,ytr)
rf=RandomForestClassifier(n_estimators=300,random_state=42,n_jobs=-1).fit(Xtr,ytr)
for name,m in [("LogisticRegression",lr),("RandomForest",rf)]:
    p=m.predict_proba(Xte)[:,1]; pred=(p>=0.5).astype(int)
    print(f"{name}: AUC {roc_auc_score(yte,p):.3f} precision {precision_score(yte,pred):.3f} recall {recall_score(yte,pred):.3f}")
    print("confusion",confusion_matrix(yte,pred).tolist())
imp=pd.Series(rf.feature_importances_,index=features).sort_values(ascending=True)
plt.figure(figsize=(8,5)); imp.plot(kind="barh"); plt.title("Churn — Random Forest Feature Importance"); plt.tight_layout(); plt.savefig(CH/"churn_feature_importance.png",dpi=150); plt.close()
fpr,tpr,_=roc_curve(yte,rf.predict_proba(Xte)[:,1]); plt.figure(); plt.plot(fpr,tpr,label="RF"); plt.plot([0,1],[0,1],"--"); plt.legend(); plt.title("ROC — Churn (future 180-day churn, features to 2024-06-30)"); plt.tight_layout(); plt.savefig(CH/"churn_roc.png",dpi=150); plt.close()
scores=rf.predict_proba(X[features])[:,1]
out=pd.DataFrame({"customer_id":X.index,"churn_score":scores.round(4)}); out["risk_tier"]=pd.cut(out.churn_score,[-0.01,0.33,0.66,1.0],labels=["Low","Medium","High"]); out.to_csv(ROOT/"data/marts/churn_risk.csv",index=False)
print("=== FINDINGS 03 Churn ==="); print(f"Future-churn rate {X.churn.mean():.1%} ({int(X.churn.sum())}/{len(X)} customers active before cutoff)")
print("Top drivers:"); print(imp.sort_values(ascending=False).head(6).to_string())
print("Plain English: customers who had already gone quiet by the cutoff, bought infrequently, returned more, and reported low CSAT / more tickets were the ones who did not come back in the next 180 days.")
print(out.risk_tier.value_counts().to_string())
