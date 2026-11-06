SELECT order_id, customer_id, order_date::DATE AS order_date, order_total, channel FROM {{ source('raw','orders') }}
