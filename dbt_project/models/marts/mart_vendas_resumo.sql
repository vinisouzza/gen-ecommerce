{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('month', order_purchase_date)::DATE AS mes_venda,
    COUNT(DISTINCT order_id) AS total_pedidos,
    SUM(price) AS receita_total,
    AVG(price) AS ticket_medio,
    SUM(freight_value) AS custo_frete_total
FROM {{ ref('int_orders_completo') }}
WHERE order_status = 'delivered'
GROUP BY 1
ORDER BY 1 DESC