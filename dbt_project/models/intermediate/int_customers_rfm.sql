{{ config(materialized='table') }}

WITH customer_orders AS (
    SELECT
        customer_id,
        order_id,
        order_purchase_date,
        price
    FROM {{ ref('int_orders_completo') }}
),

rfm AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS frequency,
        DATEDIFF('day', MAX(order_purchase_date), CURRENT_DATE) AS recency_days,
        SUM(price) AS monetary_value
    FROM customer_orders
    GROUP BY customer_id
)

SELECT
    customer_id,
    frequency,
    recency_days,
    monetary_value,
    CASE
        WHEN frequency >= 10 AND monetary_value >= 1000 THEN 'Champions'
        WHEN frequency >= 5 THEN 'Loyal'
        WHEN recency_days <= 30 THEN 'Recent'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM rfm