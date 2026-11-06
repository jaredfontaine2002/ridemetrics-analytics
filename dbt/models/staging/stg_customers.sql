SELECT customer_id, signup_date::DATE AS signup_date, country, acquisition_channel FROM {{ source('raw','customers') }}
