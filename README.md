# RideMetrics

Retention, churn and A/B test analysis for a bike shop that sells online.

I work support for cycling companies, so I see the same pattern over and over: a rider buys a bike, has one bad experience (wrong size shipped, a warranty ticket that sits for a week), and just never orders again. The shop keeps spending on ads to replace them. I built this to put numbers on that — who actually comes back, who is about to leave, and whether the free-shipping argument every shop has is worth settling with a test instead of opinions.

The shop in here (Summit Cycles) is made up and so is the data. I generated it myself, seed 42, so anyone can rebuild the exact same dataset. No client data anywhere in this repo. The code doesn't care though — point it at a real Shopify, GA4 and Gorgias export with the same columns and it runs the same way.

## The four questions

1. Who comes back? Cohort retention, RFM segments, customer lifetime value.
2. Does lowering the free-shipping threshold to $75 actually sell more, or just cost money? A/B test, control is $99.
3. Who is about to churn? A model that scores every customer, built so it can't cheat (more on that below, it did cheat the first time).
4. What does next season look like? Revenue forecast with a backtest, not just a line going up.

## What came out

- Month 1 retention is 27.9%, month 3 is 23.7%. It flattens out instead of falling off a cliff. My read: once a rider buys a second time they tend to stick around. The fight is getting purchase number two.
- Champions are 622 of the 2,500 customers and 40.4% of the revenue. Champions plus Loyal are 65.2%. The At Risk group (355 people) still accounts for 17.3% — that's the cheapest revenue in the building, they already trust the shop.
- The $75 threshold won. Conversion 9.99% vs 8.48% for $99, so +17.7% relative, 95% CI [+0.83, +2.18] points, p = 0.000014. Revenue per session went up too ($10.98 vs $9.47). Average order value dipped 1.6%, which is what you'd expect when smaller orders qualify. I would ship it.
- Churn model: logistic regression AUC 0.773, random forest 0.717. 559 customers scored high risk. The drivers were recency, average order value, total spend, tenure, average CSAT and return rate. CSAT being up there is the part I care about — a bad support ticket shows up in the churn numbers later. That's not a surprise if you've worked a helpdesk, but it's nice to see it measured.
- Forecast: backtest MAPE 22.7%, which is honest, not great. Next 6 months forecast at $8.44M with the usual April to June peak ($1.97M in June). Plan inventory and staffing for about a 2x swing between January and June, don't average the year.

Full numbers, tables and the limitations are in reports/FINDINGS.md. I left the limitations in on purpose.

## The mistake I left in the build log

First version of the churn model scored AUC 1.000. Perfect. Also fake. I was measuring recency at the same end date as the churn label, so the model was basically reading the answer. Fixed version only uses data up to 30 June 2024 and asks who didn't buy in the 180 days after that. AUC dropped to 0.773 and now I believe it. There's more in docs/build-log.md, including the forecast model I tried and threw out.

## How it's put together

- data/generate_data.py builds the raw CSVs (customers, products, orders, order items, sessions, support tickets)
- warehouse.py loads them into DuckDB and runs the SQL in sql/ in order — star schema first, then the cohort, RFM, funnel, LTV and A/B test models
- dbt/ is the same warehouse written as a dbt project (staging, marts, schema tests). I run the DuckDB version locally because it needs zero accounts. On a real job I'd run the dbt version against BigQuery or Snowflake.
- analysis/ has the four Python pieces, one file per question. Each one prints what it found and saves its charts.
- dashboard/app.py is a Streamlit dashboard with five tabs. BI_SPEC.md has the Power BI DAX and Tableau calcs if you want it in those tools instead, I designed it to port over.

Tools: SQL, DuckDB, dbt, Python, pandas, scikit-learn, scipy, statsmodels, Streamlit, Plotly.

## Run it

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python data/generate_data.py
python warehouse.py
python analysis/01_cohort_rfm.py
python analysis/02_ab_test.py
python analysis/03_churn_model.py
python analysis/04_forecast.py
python tests/test_data_quality.py
streamlit run dashboard/app.py
```

Whole thing takes a couple of minutes. `make run` does everything except the dashboard.

## Using real data instead

- Shopify order and customer exports drop into data/raw/ as orders.csv, order_items.csv and customers.csv
- GA4 session export becomes sessions.csv — keep the experiment variant column from whatever testing tool ran the test
- Gorgias ticket export becomes support_tickets.csv — keep customer_id, tag and csat, the CSAT fields are what make the churn model interesting

## What I'd do next

Run the high-risk list against an actual win-back email and see if the tiers hold up. Put margin into the CLV number instead of just revenue. And if the data got bigger I'd move the warehouse to dbt + BigQuery properly instead of running it locally.

— Jared Fontaine. MBA, Google Data Analytics cert (2021), Gorgias Admin + CX certified. I do customer support and analytics for cycling brands — Curated, Planet Cyclery, Cambria Bike, Tune Cycles.
