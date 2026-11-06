
"""A/B test: free shipping $75 (treatment) vs $99 (control). Pre-registered style."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep
from statsmodels.stats.power import NormalIndPower
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CH=ROOT/"reports/charts"; CH.mkdir(parents=True,exist_ok=True)
s=pd.read_csv(ROOT/"data/raw/sessions.csv",parse_dates=["session_date"])
per=s.groupby(["session_id","experiment_variant"]).agg(converted=("event_name",lambda x:int((x=="purchase").any())),revenue=("revenue","sum"),is_new=("is_new_customer","first")).reset_index()
g=per.groupby("experiment_variant").agg(n=("converted","size"),conv=("converted","sum"),rate=("converted","mean"),rps=("revenue","mean"))
print(g)
c=g.loc["control"]; t=g.loc["treatment"]
count=np.array([t.conv,c.conv]); nobs=np.array([t.n,c.n])
z,p=proportions_ztest(count,nobs)
table=pd.crosstab(per.experiment_variant,per.converted); chi2,p_chi,_,_=stats.chi2_contingency(table)
lo,hi=confint_proportions_2indep(t.conv,t.n,c.conv,c.n)
lift=(t.rate-c.rate)/c.rate
# AOV guardrail + revenue per session
aov_c=per[(per.experiment_variant=="control")&(per.converted==1)].revenue; aov_t=per[(per.experiment_variant=="treatment")&(per.converted==1)].revenue
tt=stats.ttest_ind(per[per.experiment_variant=="treatment"].revenue,per[per.experiment_variant=="control"].revenue,equal_var=False)
seg=per.groupby(["experiment_variant","is_new"]).converted.mean().unstack()
# power: detectable at current n
power=NormalIndPower().solve_power(effect_size=0.02, nobs1=int(c.n), alpha=0.05, ratio=t.n/c.n)
plt.figure(figsize=(7,4)); plt.bar(["Control $99","Treatment $75"],[c.rate,t.rate]); plt.ylabel("Conversion rate"); plt.title("A/B Conversion Rate"); plt.tight_layout(); plt.savefig(CH/"ab_test_conversion.png",dpi=150); plt.close()
print("=== FINDINGS 02 A/B Test ===")
print(f"Control {c.rate:.3%} (n={int(c.n)}) Treatment {t.rate:.3%} (n={int(t.n)})")
print(f"Relative lift {lift:.1%} | Absolute diff {t.rate-c.rate:.3%} | 95% CI [{lo:.3%}, {hi:.3%}]")
print(f"Two-proportion z={z:.2f} p={p:.4g} | Chi-square p={p_chi:.4g}")
print(f"Revenue/session control ${c.rps:.2f} treatment ${t.rps:.2f} t-test p={tt.pvalue:.4g}")
print(f"AOV guardrail control ${aov_c.mean():.2f} treatment ${aov_t.mean():.2f}")
print("Segment (new vs returning) conversion:"); print(seg.to_string())
rec="SHIP" if (p<0.05 and lo>0 and t.rps>=c.rps) else "DO NOT SHIP / investigate"
print(f"RECOMMENDATION: {rec} — treatment lifts conversion with CI above zero" if rec=="SHIP" else f"RECOMMENDATION: {rec}")
