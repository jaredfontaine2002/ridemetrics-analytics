# RideMetrics

Retention, churn and A/B test analysis for a bike shop that sells online.

I work support for cycling companies, so I see the same pattern over and over: a rider buys a bike, has one bad experience (wrong size shipped, a warranty ticket that sits for a week), and just never orders again. The shop keeps spending on ads to replace them. I built this to put numbers on that — who actually comes back, who is about to leave, and whether the free-shipping argument every shop has is worth settling with a test instead of opinions.

The shop in here (Summit Cycles) is made up and so is the data. I generated it myself, seed 42, so anyone can rebuild the exact same dataset. No client data anywhere in this repo. The code doesn't care though — point it at a real Shopify, GA4 and Gorgias export with the same columns and it runs the same way.

## The four questions

1. Who comes back? Cohort retention, RFM segments, customer lifetime value.
2. Does lowering the free-shipping threshold to $75 actually sell more, or just cost money? A/B test, control is $99.
3. Who is about to churn? A model that scores every customer, built so it can't cheat (more on that below, it did cheat the first time).
4. What does next season look like? Revenue forecast with a backtest, not just a line going up.

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
