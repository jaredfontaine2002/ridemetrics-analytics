SELECT session_id, customer_id, session_date, event_name, experiment_variant, revenue FROM {{ source('raw','sessions') }}
