{{ config(materialized='table') }}

SELECT
    product_id,
    product_category_name,
    COUNT(DISTINCT order_id) AS total_pedidos,
    SUM(price) AS receita_total,
    AVG(price) AS preco_medio
FROM {{ ref('int_orders_completo') }}
GROUP BY product_id, product_category_name
ORDER BY receita_total DESC