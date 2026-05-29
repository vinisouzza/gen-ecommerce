import os
import pandas as pd
import duckdb
from dagster import asset, Definitions, AssetExecutionContext, multiprocess_executor
from ai_agent import gerar_sql_e_doc_gemini
import subprocess

# ---------------------------------------------------------------------
# Asset 1: Ingestão de Dados (Camada Ingest)
# ---------------------------------------------------------------------
@asset(compute_kind="DuckDB")
def raw_vendas() -> None:
    """Lê o arquivo CSV bruto e carrega como tabela inicial no banco analítico DuckDB."""
    os.makedirs("db", exist_ok=True)
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    df = pd.read_csv("data/vendas.csv")
    
    # Salva os dados brutos no DuckDB
    conn.execute("CREATE OR REPLACE TABLE raw_vendas AS SELECT * FROM df")
    conn.close()

@asset(compute_kind="DuckDB")
def raw_metas() -> None:
    """Novo asset: Carrega as metas de vendas por produto"""
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    df = pd.read_csv("data/metas.csv")
    conn.execute("CREATE OR REPLACE TABLE raw_metas AS SELECT * FROM df")
    conn.close()

# ---------------------------------------------------------------------
# Asset 2: Agente Generativo (Geração de Código e Atualização de Metadados)
# ---------------------------------------------------------------------
@asset(deps=[raw_vendas, raw_metas], compute_kind="Gemini")
def vendas_agregadas_sql(context: AssetExecutionContext) -> str:
    """Chama a IA para obter a query SQL ideal e atualiza a documentação no schema.yml do dbt."""
    requisito = """
    Calcule a receita total por produto (quantidade * preco_unitario) da tabela raw_vendas. 
    Faça um JOIN com a tabela raw_metas pelo 'produto'.
    Traga as colunas: produto, receita_total, meta_receita.
    Crie também uma coluna chamada 'atingiu_meta' com o valor 'SIM' caso a receita seja maior ou igual a meta, e 'NAO' caso contrário.
    """
    
    # Invoca o agente Gemini
    ai_response = gerar_sql_e_doc_gemini(requisito)
    sql_query = ai_response.sql
    explicacao = ai_response.explanation
    
    # 1. Cria/Escreve o modelo SQL gerado na pasta do dbt
    caminho_sql = "dbt_project/models/vendas_agregadas.sql"
    with open(caminho_sql, "w", encoding="utf-8") as f:
        f.write(sql_query)
        
    # 2. Atualiza a documentação estática no schema.yml
    caminho_schema = "dbt_project/models/schema.yml"
    with open(caminho_schema, "r", encoding="utf-8") as f:
        schema_content = f.read()
    
    # Altera o texto estático pela documentação gerada pelo Gemini
    novo_schema = schema_content.replace(
        "Aguardando documentação do agente...",
        explicacao
    )
    with open(caminho_schema, "w", encoding="utf-8") as f:
        f.write(novo_schema)
        
    context.log.info(f"[Gemini] SQL Compilado com Sucesso:\n{sql_query}")
    context.log.info(f"[Gemini] Explicação inserida no schema.yml: {explicacao}")
    
    return sql_query

# ---------------------------------------------------------------------
# Asset 3: Transformação e Materialização (dbt run)
# ---------------------------------------------------------------------
@asset(deps=[vendas_agregadas_sql], compute_kind="dbt")
def dbt_run(context: AssetExecutionContext) -> None:
    """Executa o dbt para transformar os dados no DuckDB utilizando a lógica criada pela IA."""
    # Executa o dbt CLI de forma direta
    os.system("cd dbt_project && dbt run --profiles-dir .")
    context.log.info("dbt executado! A tabela analítica 'vendas_agregadas' está pronta.")

# Central de Definições que o Dagster lê para montar o Grafo
defs = Definitions(
    assets=[raw_vendas, raw_metas, vendas_agregadas_sql, dbt_run],
    executor=multiprocess_executor.configured({"max_concurrent": 1})
)