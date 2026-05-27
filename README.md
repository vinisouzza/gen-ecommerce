# GEN-ECOMMERCE

Projeto de pipeline analítico com Dagster, DuckDB, dbt e Gemini/AI para geração de SQL.

## Visão geral

Este projeto demonstra um fluxo de dados simples:

1. `raw_vendas` — ingere `data/vendas.csv` e salva em DuckDB.
2. `vendas_agregadas_sql` — chama o agente Gemini para gerar uma query SQL de agregação e escreve o arquivo `dbt_project/models/vendas_agregadas.sql`.
3. `dbt_run` — executa o dbt para materializar a transformação e criar o modelo analítico.

O resultado esperado é visualizar no Dagster a sequência:
`raw_vendas -> vendas_agregadas -> dbt_run`.

## Estrutura do projeto

- `pipeline.py` — definição dos assets Dagster.
- `ai_agent.py` — camada de API Gemini/OpenAI que gera o SQL e a documentação.
- `dbt_project/` — projeto dbt com `profiles.yml`, `dbt_project.yml` e modelo/metadata.
- `data/vendas.csv` — dados de vendas de exemplo.
- `db/gen_ecommerce_lab.duckdb` — banco DuckDB local gerado pelo pipeline.
- `view_results.py` — script auxiliar para inspecionar tabelas no DuckDB.
- `requirements.txt` — dependências Python do ambiente.

## Preparação (passo a passo)

1. Clone o repositório:

```bash
git clone https://github.com/vinisouzza/gen-ecommerce.git
cd gen-ecommerce
```

2. Crie e ative o ambiente virtual Python:

```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Configure a chave de API Gemini/OpenAI:

```bash
copy .env.example .env
```

Edite o arquivo `.env` e defina:

```ini
GEMINI_API_KEY=seu_token_aqui
```


5. Execute o Dagster:

```bash
dagster dev -f pipeline.py
```

6. Abra o navegador em `http://localhost:3000`.

7. Na interface Dagster, acesse a aba **Lineage**.

8. Clique em **Materialize all** para executar o fluxo.

## Como funciona

- `raw_vendas` carrega o CSV para DuckDB.
- `vendas_agregadas_sql` chama `ai_agent.gerar_sql_e_doc_gemini()` para obter JSON com `sql` e `explanation`.
- O SQL gerado é salvo em `dbt_project/models/vendas_agregadas.sql`.
- `dbt_run` roda `dbt run --profiles-dir .` dentro de `dbt_project`.

## Verificação pós-execução

Após o materialize, você pode visualizar o banco e tabelas com:

```bash
python view_results.py
```

