# RideMetrics — Upwork portfolio entry + LinkedIn copy (paste-ready)

## Upwork portfolio item
**Title:** RideMetrics — Retention, Churn & A/B Test Analytics for a DTC Bike Shop

**Description:**
End-to-end advanced analytics project for a fictional DTC bike shop (Summit Cycles, synthetic data, seeded and reproducible).

Built a DuckDB star-schema warehouse with a dbt project (staging → marts, schema tests), then answered four money questions:
• Cohort retention (Month-1 27.9%) + RFM segmentation — Champions are 40.4% of revenue
• A/B test: free shipping $75 vs $99 — +17.7% conversion lift, 95% CI [+0.83pp, +2.18pp], p=0.000014 → SHIP
• Churn prediction with no label leakage (features to Jun 2024, label = next 180 days): Logistic Regression AUC 0.773; 559 customers flagged High risk
• Revenue forecast (Holt-Winters, backtested MAPE 22.7%): $8.44M forecast for Jan–Jun 2025

Stack: SQL (CTEs, window functions), dbt, DuckDB, Python (pandas, scikit-learn, scipy, statsmodels), Streamlit/Plotly, with a Tableau/Power BI rebuild spec (DAX measures included). Same pipeline runs on real Shopify / GA4 / Gorgias exports.

**Skills:** SQL, Python, dbt, Data Analysis, A/B Testing, Cohort Analysis, RFM Segmentation, Churn Analysis, Forecasting, Streamlit, DuckDB, scikit-learn, Statistical Analysis, Data Modeling, Tableau, Power BI

**GitHub:** https://github.com/jaredfontaine2002/ridemetrics-analytics

## LinkedIn Featured / post line
New portfolio project: RideMetrics — cohort + RFM, a properly-powered A/B test (ship decision with CI, not just a p-value), a leakage-free churn model, and a backtested forecast, all on a dbt + DuckDB warehouse. Built for the DTC cycling world I work in every day.

## Resume bullets
- Built end-to-end analytics pipeline (DuckDB + dbt star schema, SQL window functions/CTEs) over 11,841 synthetic orders / $19.5M revenue to produce cohort, RFM and CLV marts
- Analysed a randomised free-shipping A/B test (n=28,000 sessions): +17.7% conversion lift, 95% CI [+0.83pp, +2.18pp], p<0.001, with AOV guardrail and segment checks — ship recommendation quantified at +$1.51 revenue/session
- Trained leakage-free churn models (logistic regression AUC 0.773) scoring 2,279 customers into risk tiers; identified CSAT and return rate as churn drivers beyond purchase history
- Backtested Holt-Winters revenue forecast (MAPE 22.7%) and delivered a 6-month forecast with confidence intervals in a 5-tab Streamlit dashboard
