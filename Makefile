run:
	python data/generate_data.py && python warehouse.py && python analysis/01_cohort_rfm.py && python analysis/02_ab_test.py && python analysis/03_churn_model.py && python analysis/04_forecast.py
