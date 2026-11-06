SELECT experiment_variant, COUNT(DISTINCT session_id) AS sessions FROM {{ ref('stg_sessions') }} GROUP BY 1
