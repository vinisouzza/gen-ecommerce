import os
import pandas as pd
import duckdb
from dagster import asset, Definitions, AssetExecutionContext, multiprocess_executor
from ai_agent import gerar_sql_e_doc_gemini

# =====================================================================
# CAMADA RAW (Ingestão)
# =====================================================================

def _load_csv_to_duckdb(csv_file: str, table_name: str, conn):
    """Carrega CSV em DuckDB."""
    df = pd.read_csv(f"data/{csv_file}")
    conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")

@asset(compute_kind="DuckDB")
def raw_orders() -> None:
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    _load_csv_to_duckdb("olist_orders_dataset.csv", "raw_orders", conn)
    conn.close()

@asset(compute_kind="DuckDB")
def raw_customers() -> None:
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    _load_csv_to_duckdb("olist_customers_dataset.csv", "raw_customers", conn)
    conn.close()

@asset(compute_kind="DuckDB")
def raw_order_items() -> None:
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    _load_csv_to_duckdb("olist_order_items_dataset.csv", "raw_order_items", conn)
    conn.close()

@asset(compute_kind="DuckDB")
def raw_products() -> None:
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    _load_csv_to_duckdb("olist_products_dataset.csv", "raw_products", conn)
    conn.close()

@asset(compute_kind="DuckDB")
def raw_reviews() -> None:
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    _load_csv_to_duckdb("olist_order_reviews_dataset.csv", "raw_reviews", conn)
    conn.close()

# =====================================================================
# CAMADA AI - Geração de Transformações via IA
# =====================================================================

@asset(
    deps=[raw_orders, raw_customers, raw_order_items, raw_products, raw_reviews],
    compute_kind="Gemini"
)
def gerar_transformacoes_staging(context: AssetExecutionContext) -> None:
    requisitos = {
        "stg_orders": (
            "Crie uma query SQL que limpe e padronize a tabela raw_orders. "
            "Converta order_purchase_timestamp, order_approved_at, order_delivered_customer_date "
            "e order_estimated_delivery_date para TIMESTAMP ou DATE. "
            "Calcule dias_para_entrega = order_delivered_customer_date - order_purchase_timestamp. "
            "Remova linhas duplicadas por order_id."
        ),
        "stg_customers": (
            "Crie uma query SQL que limpe raw_customers. "
            "Verifique se customer_id é único. "
            "Remova linhas onde customer_city ou customer_state sejam nulos. "
            "Mantenha apenas customer_id, customer_unique_id, customer_city, customer_state."
        ),
        "stg_order_items": (
            "Crie uma query SQL que limpe raw_order_items. "
            "Verifique se order_id e product_id existem. "
            "Converta price e freight_value para numeric."
        ),
        "stg_products": (
            "Crie uma query SQL que limpe raw_products. "
            "Renomeie colunas para snake_case e mantenha product_id, product_category_name, product_name_length, product_description_lenght."
        ),
        "stg_reviews": (
            "Crie uma query SQL que limpe raw_reviews. "
            "Converta review_creation_date e review_answer_timestamp para TIMESTAMP."
        ),
    }

    os.makedirs("dbt_project/models/staging", exist_ok=True)

    for modelo, requisito in requisitos.items():
        try:
            ai_response = gerar_sql_e_doc_gemini(requisito)
            sql_query = ai_response.sql
            explicacao = ai_response.explanation

            caminho = f"dbt_project/models/staging/{modelo}.sql"
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(f"-- {explicacao}\n\n{sql_query}")

            context.log.info(f"✅ Modelo {modelo} gerado pela IA")
        except Exception as e:
            context.log.warning(f"⚠️ Erro ao gerar {modelo}: {e}")

# =====================================================================
# CAMADA DBT - Transformações, Testes e Documentação
# =====================================================================

@asset(
    deps=[gerar_transformacoes_staging],
    compute_kind="dbt"
)
def dbt_run(context: AssetExecutionContext) -> None:
    result = os.system("cd dbt_project && dbt run --profiles-dir . && dbt test --profiles-dir .")
    if result == 0:
        context.log.info("✅ dbt executado com sucesso! Modelos e testes prontos.")
    else:
        context.log.error("❌ Erro na execução do dbt")

# =====================================================================
# Definição do Pipeline
# =====================================================================

defs = Definitions(
    assets=[
        raw_orders,
        raw_customers,
        raw_order_items,
        raw_products,
        raw_reviews,
        gerar_transformacoes_staging,
        dbt_run,
    ],
    executor=multiprocess_executor.configured({
        "max_concurrent": 1
    })
)