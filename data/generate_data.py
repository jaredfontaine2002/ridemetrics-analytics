
"""Synthetic data generator for Summit Cycles (fictional DTC bike shop).
Seeded (42), honestly synthetic. Churn signal is baked in via a hidden
customer type: at-risk customers get more low-CSAT tickets, higher returns,
and stop buying earlier -- so the churn model has real signal to find.
Churn label (defined in analysis): no purchase in final 180 days.
"""
import numpy as np, pandas as pd
from pathlib import Path
rng=np.random.default_rng(42)
OUT=Path(__file__).parent/"raw"; OUT.mkdir(parents=True,exist_ok=True)
START=pd.Timestamp("2023-01-01"); END=pd.Timestamp("2024-12-31")
DAYS=(END-START).days

# customers
n=2500
types=rng.choice(["loyal","casual","at_risk"],size=n,p=[0.40,0.35,0.25])
signup_days=np.sort(rng.integers(0,DAYS-180,size=n))
customers=pd.DataFrame({
 "customer_id":[f"CUST-{i:04d}" for i in range(1,n+1)],
 "signup_date":START+pd.to_timedelta(signup_days,unit="D"),
 "country":rng.choice(["US","CA","GB","AU"],size=n,p=[0.72,0.10,0.10,0.08]),
 "acquisition_channel":rng.choice(["organic","paid_search","social","referral","email"],size=n,p=[0.3,0.25,0.2,0.15,0.1]),
 "customer_type_hidden":types,  # kept in raw for auditability; analysts should NOT use as a feature
})
customers.to_csv(OUT/"customers.csv",index=False)

# products
cats={"Bikes":(799,3499,8),"Components":(25,599,18),"Apparel":(29,199,12),"Accessories":(12,149,14),"Nutrition":(9,59,8)}
rows=[]
pid=1
for cat,(lo,hi,cnt) in cats.items():
    for j in range(cnt):
        rows.append({"product_id":f"PROD-{pid:03d}","product_name":f"{cat[:-1] if cat!='Bikes' else 'Bike'} Model {j+1}","category":cat,"unit_price":round(float(rng.uniform(lo,hi)),2),"cost":round(float(rng.uniform(lo,hi))*0.62,2)})
        pid+=1
products=pd.DataFrame(rows); products.to_csv(OUT/"products.csv",index=False)
price_map=dict(zip(products.product_id,products.unit_price))

# orders + items
orders=[]; items=[]; oid=1
for _,c in customers.iterrows():
    t=c.customer_type_hidden
    lam={"loyal":7,"casual":4,"at_risk":2.5}[t]
    k=max(1,int(rng.poisson(lam)))
    # last possible day
    last_cap=DAYS if t!="at_risk" else int(rng.integers(200,480))
    first=min(DAYS-10, int(c.signup_date_day) if False else 0)
    # signup offset
    sday=(c.signup_date-START).days
    hi_day=min(DAYS, sday+last_cap) if t=="at_risk" else DAYS
    if hi_day<=sday+10: hi_day=sday+30
    # seasonal weights approximated by picking months weighted Apr-Jun
    dates=[]
    for _ in range(k):
        for attempt in range(20):
            d=int(rng.integers(sday,hi_day))
            month=(START+pd.Timedelta(days=d)).month
            w=1.6 if month in (4,5,6) else (0.7 if month in (12,1) else 1.0)
            if rng.random()<w/1.6: break
        dates.append(d)
    dates=sorted(set(dates))
    growth=1.0
    for d in dates:
        odate=START+pd.Timedelta(days=int(d))
        n_items=int(rng.integers(1,5))
        total=0.0
        for _ in range(n_items):
            cat=rng.choice(["Bikes","Components","Apparel","Accessories","Nutrition"],p=[0.15,0.25,0.20,0.25,0.15]); pool=products[products.category==cat]; prod=pool.iloc[int(rng.integers(0,len(pool)))]
            qty=int(rng.integers(1,3)); price=float(prod.unit_price)
            ret=bool(rng.random() < (0.18 if t=="at_risk" else 0.05))
            items.append({"order_id":f"ORD-{oid:05d}","product_id":prod.product_id,"quantity":qty,"unit_price":price,"discount_pct":float(rng.choice([0,0,0,0.1,0.15])),"returned":ret})
            total+=qty*price
        orders.append({"order_id":f"ORD-{oid:05d}","customer_id":c.customer_id,"order_date":odate,"order_total":round(total,2),"channel":rng.choice(["web","mobile"],p=[0.65,0.35])})
        oid+=1
orders_df=pd.DataFrame(orders); items_df=pd.DataFrame(items)
orders_df.to_csv(OUT/"orders.csv",index=False); items_df.to_csv(OUT/"order_items.csv",index=False)

# support tickets
trows=[]; tid=1
for _,c in customers.iterrows():
    t=c.customer_type_hidden
    p_ticket={"loyal":0.45,"casual":0.5,"at_risk":0.85}[t]
    if rng.random()<p_ticket:
        for _ in range(int(rng.integers(1,4))):
            csat=int(np.clip(rng.normal(2.6 if t=="at_risk" else 4.4,0.9),1,5)) if t=="at_risk" else int(np.clip(rng.normal(4.4,0.7),1,5))
            trows.append({"ticket_id":f"TKT-{tid:05d}","customer_id":c.customer_id,"created_date":START+pd.Timedelta(days=int(rng.integers(0,DAYS))),"channel":rng.choice(["email","chat","phone"],p=[0.5,0.35,0.15]),"tag":rng.choice(["shipping","product_quality","sizing","delivery","returns"]),"csat":csat})
            tid+=1
tickets=pd.DataFrame(trows); tickets.to_csv(OUT/"support_tickets.csv",index=False)

# sessions (event level, GA4-style) + A/B test
# treatment: free shipping $75 vs control $99 -> ~18% relative conversion lift
erows=[]; sid=1
n_sessions=28000
cust_ids=customers.customer_id.values
for i in range(n_sessions):
    variant="treatment" if rng.random()<0.5 else "control"
    base=0.085; conv=base*1.18 if variant=="treatment" else base
    is_new=bool(rng.random()<0.55)
    sdate=START+pd.Timedelta(days=int(rng.integers(0,DAYS)))
    cid=rng.choice(cust_ids) if not is_new else rng.choice(cust_ids)
    device=rng.choice(["desktop","mobile","tablet"],p=[0.45,0.45,0.10])
    # funnel progression
    stages=["session_start"]
    if rng.random()<0.62: stages.append("view_item")
    if "view_item" in stages and rng.random()<0.38: stages.append("add_to_cart")
    if "add_to_cart" in stages and rng.random()<0.55: stages.append("begin_checkout")
    purchased=False
    if "begin_checkout" in stages:
        # calibrate so overall conversion ~ conv: P(purchase|checkout) approx
        p_purch= min(0.95, conv/ max(0.01,(0.62*0.38*0.55)) )
        if rng.random()<p_purch: stages.append("purchase"); purchased=True
    revenue=round(float(rng.lognormal(4.6,0.5)),2) if purchased else 0.0
    # AOV guardrail: treatment slightly lower AOV (smaller baskets qualify)
    if purchased and variant=="treatment": revenue=round(revenue*0.96,2)
    for st in stages:
        erows.append({"session_id":f"SES-{sid:06d}","customer_id":cid,"session_date":sdate,"event_name":st,"device":device,"is_new_customer":is_new,"experiment_variant":variant,"revenue":revenue if st=="purchase" else 0.0})
    sid+=1
sessions=pd.DataFrame(erows); sessions.to_csv(OUT/"sessions.csv",index=False)
print(f"customers {len(customers)} products {len(products)} orders {len(orders_df)} order_items {len(items_df)} tickets {len(tickets)} session_events {len(sessions)} sessions {sid-1}")
