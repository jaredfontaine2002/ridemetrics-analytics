# Build log

Notes I kept while building this, in the order things happened. Leaving them in because the dead ends were the useful part.

## Why this project

My two older projects were descriptive — pull the numbers, chart them, done. Every data analyst job posting I read wants more than that: proper SQL, some statistics, a test, a model. So this one is built around questions a shop owner would actually ask, in the order they'd ask them.

## Data first

Generated the data before writing any analysis. Two things I baked in on purpose: a real effect for the $75 shipping threshold (if the test can't find an effect I put there, the test is broken), and churn that gets more likely after bad support experiences and returns. Seed 42 everywhere so the numbers in FINDINGS.md reproduce.

Basket mix came out bike-heavy, so average order value is $1,643, which is high. Noted in the findings rather than quietly re-tuning it until it looked normal.

## SQL before Python

Wrote the warehouse first (star schema in DuckDB), then mirrored it in dbt. Cohort and RFM are SQL problems, NTILE does the segment work fine. Python only comes in where SQL runs out — the test statistics, the model, the forecast.

## The churn leak

Covered in the README but worth repeating here: version one hit AUC 1.000 because recency and the churn label were measured at the same date. Textbook leakage. Rebuilt it time-based — features to 30 Jun 2024, label is the following 180 days. Logistic regression beat the random forest after the fix (0.773 vs 0.717), which I did not expect.

## Forecast: two models in the bin

Seasonal Holt-Winters wouldn't initialise on the backtest split — 21 months is less than two full seasonal cycles. Then a seasonal SARIMAX blew up completely (MAPE around 390%). Final setup: damped-trend Holt-Winters for the backtest (22.7% MAPE, it missed the December drop), seasonal Holt-Winters on the full 24 months for the actual forecast. Picked by backtest score, not by which model sounded fancier.

## Small stuff

- statsmodels renamed a proportions function between versions (confint_proportions_2indep). Cost me twenty minutes.
- Had to re-weight product sampling by category or the baskets were all bikes.
- Dashboard reads the marts, not the raw files, so if the warehouse hasn't run it warns you instead of crashing.
