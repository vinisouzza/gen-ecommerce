{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    oi.product_id,
    p.product_category_name,
    oi.price,
    oi.freight_value,
    o.order_status,
    o.order_purchase_date,
    o.order_delivered_date,
    o.dias_para_entrega
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
LEFT JOIN {{ ref('stg_order_items') }} oi ON o.order_id = oi.order_id
LEFT JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id