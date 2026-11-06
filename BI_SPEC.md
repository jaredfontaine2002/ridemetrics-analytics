# BI Spec — Rebuild in Tableau / Power BI (1 page)
Data sources: data/marts/*.csv (mart_rfm, cohort_retention_matrix, churn_risk, forecast, mart_ab_test) + fct_orders.
## Power BI DAX
- Total Revenue = SUM(fct_orders[order_total])
- AOV = DIVIDE([Total Revenue], COUNTROWS(fct_orders))
- Retention Rate = DIVIDE(active_customers, cohort_customers) (from cohort mart)
- CLV = [AOV] * AVERAGE(mart_rfm[frequency]) * 0.38
Pages: Executive (KPI cards + revenue trend), Cohort (matrix heatmap), RFM (treemap by segment), A/B (bar + CI), Churn (risk table, slicer by tier).
## Tableau calc fields
- AOV: SUM([Order Total])/COUNTD([Order Id]); Retention: SUM([Active])/SUM([Cohort Size]); CLV: [AOV]*AVG([Frequency])*0.38; Risk Tier: use churn_risk.csv tier directly.
Same marts, same definitions — design is BI-tool portable by construction.
