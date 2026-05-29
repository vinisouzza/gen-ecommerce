-- Esta query seleciona as colunas especificadas da tabela raw_products, mantendo os nomes originais em snake_case para limpeza inicial.

SELECT product_id, product_category_name, product_name_length, product_description_lenght FROM raw_products