# RideMetrics — Findings

**Summit Cycles (fictional DTC bike shop) · All data synthetic, seeded (42) · Pipeline run end-to-end 2026-11-06**
Dataset: 2,500 customers · 60 products · 11,841 orders · 29,835 order items · 2,886 support tickets · 28,000 sessions (58,173 GA4-style events) · Jan 2023–Dec 2024 · Total revenue $19,459,486.

---

## 1. Cohort retention, RFM & CLV (`analysis/01_cohort_rfm.py`, `sql/02–03`)

- 24 monthly first-order cohorts. **Month-1 retention 27.9%, Month-3 retention 23.7%** — retention flattens rather than collapsing, i.e. riders who buy a second time tend to stay in the hobby.
- RFM revenue share: **Champions 40.4%** (622 customers), **Loyal 24.8%** (523), **At Risk 17.3%** (355), **Lost 10.5%** (642), Potential 4.1% (189), Other 2.9% (169).
- AOV **$1,643.40** (bike-heavy baskets — a full bike in ~15% of line items), average frequency **4.74 orders**, historical CLV **$7,783.79**, simple margin-adjusted CLV estimate (AOV × frequency × 38% margin) **$2,957.84**.
- **Recommendation:** Champions + Loyal are 45.8% of customers producing 65.2% of revenue — protect them first (early access, no discounting). The At Risk segment is the best win-back target: 355 customers who historically spent at Loyal-like levels; recovering even 10% of their historical spend pattern is worth roughly $330K in annual revenue at segment-average monetary value.

## 2. A/B test — free-shipping threshold (`analysis/02_ab_test.py`, `sql/06`)

Design: session-level randomisation, ~50/50 (control n=13,981, treatment n=14,019). Control = free shipping over $99; treatment = over $75.

| Metric | Control ($99) | Treatment ($75) |
|---|---|---|
| Conversion rate | 8.48% | **9.99%** |
| Revenue / session | $9.47 | **$10.98** |
| AOV (guardrail) | $111.67 | $109.91 (−1.6%) |

- Relative lift **+17.7%**; absolute difference +1.50pp, **95% CI [+0.83pp, +2.18pp]** (entirely above zero).
- Two-proportion z-test **z = 4.34, p = 1.4e-05**; chi-square agrees (p = 1.5e-05). Revenue-per-session Welch t-test p = 0.0007.
- Segment check: lift holds for new (8.74% → 10.35%) and returning (8.17% → 9.55%) visitors — no Simpson's-paradox reversal.
- **Recommendation: SHIP the $75 threshold.** At treatment revenue/session, the lift is worth about **+$1.51 per session**; on 28,000 sessions per test period that annualises to a material six-figure revenue gain, and the small AOV dip is the expected, acceptable cost of smaller baskets qualifying.

## 3. Churn prediction (`analysis/03_churn_model.py`)

**Design choice that matters:** features are computed only from data up to **2024-06-30**; the label is *no purchase in the following 180 days*. The naive version (label and recency both measured at end-of-data) leaks the answer and returns a fake AUC of 1.00 — that version was built, caught, and replaced. Reported numbers are the honest ones.

- Population: 2,279 customers active before the cutoff. **Future-churn rate 31.2%** (712 customers).
- **Logistic Regression: ROC-AUC 0.773**, precision 0.654, recall 0.382 at 0.50 threshold.
- **Random Forest: ROC-AUC 0.717**, precision 0.616, recall 0.388.
- Top Random-Forest drivers: **recency_days (0.231), AOV (0.156), monetary (0.155), tenure (0.125), avg CSAT (0.106), return rate (0.082)** — support experience (CSAT) and returns carry real signal beyond purchase history alone, which is the Gorgias-side insight: a bad ticket is an early churn warning.
- Risk tiers exported to `data/marts/churn_risk.csv`: **High 559, Medium 176, Low 1,544**.
- **Recommendation:** run win-back on the 559 High-risk customers *before* they lapse (the model scores them at the cutoff, while they are still reachable). At historical CLV, retaining even 5% of the High tier ≈ 28 customers ≈ **$218K in lifetime revenue protected**. Lower the decision threshold if the campaign values recall over precision — at 0.50 the model is conservative.

## 4. Revenue forecast (`analysis/04_forecast.py`)

- Backtest (last 3 months held out, damped-trend Holt-Winters): **MAPE 22.7%** — the model tracked Oct–Nov well ($1.31M / $1.36M predicted vs $1.30M / $1.32M actual) and missed the December drop ($1.40M predicted vs $0.85M actual), which is exactly the seasonal effect the backtest model cannot see.
- Method note: seasonal Holt-Winters needs ≥2 full seasonal cycles to initialise, so the final model is fit on all 24 months; a seasonal SARIMAX was tried and rejected after it exploded on the short training window (MAPE ~390%). Model selection by backtest, not fashion.
- Final forecast (seasonal Holt-Winters, 95% intervals in `data/marts/forecast.csv`): **Jan–Jun 2025 total $8,435,132** — Jan $881K rising to the **Apr–Jun peak (Jun $1,969K)**, matching the seasonal pattern in both training years.
- **Recommendation:** plan inventory and support staffing for a ~2.2× swing between January and June revenue; do not annualise winter months.

## Limitations (stated plainly)

1. Synthetic data: effect sizes (A/B lift, churn signal) were baked into the generator, so the analyses *finding* them validates the pipeline, not a real business claim.
2. AOV is high because the synthetic basket mix is bike-heavy; a real shop should re-weight by its own category mix.
3. Churn model uses a stratified random split within the cutoff population; a stricter design would also validate across a second cutoff date.
4. Forecast MAPE (22.7%) is honest but mediocre — 24 months is the minimum viable history for seasonal models; treat the forecast as a planning range, not a promise.
5. CLV here is a simple AOV × frequency × margin estimate, not a full BG/NBD + Gamma-Gamma model — named as the next upgrade in the README.

## Business recommendations, quantified

| Action | Basis | Size of prize |
|---|---|---|
| Ship $75 free-shipping threshold | A/B test, CI entirely > 0 | +$1.51 revenue/session |
| Win-back the 559 High churn-risk customers now | Churn model @ cutoff | ~$218K lifetime revenue per 5% saved |
| At Risk RFM win-back campaign (355 customers) | RFM segment monetary value | ~$330K/yr per 10% recovered |
| Seasonal staffing/inventory plan for Apr–Jun | Forecast 2.2× Jan→Jun swing | Avoids stockouts at the $1.97M peak month |
