# GEN-ECOMMERCE

Projeto de pipeline analítico autônomo construído com a *Modern Data Stack* (Dagster, DuckDB, dbt) e potencializado por Inteligência Artificial (Gemini) para geração automatizada de transformações SQL e metadados.

## Visão Geral

Este projeto demonstra um fluxo de dados moderno que utiliza IA para interpretar regras de negócio em linguagem natural, traduzi-las para SQL e orquestrar a execução.

O pipeline realiza as seguintes etapas:

1. **Camada de Ingestão:** Os assets `raw_vendas` e `raw_metas` ingerem arquivos CSV (`data/vendas.csv` e `data/metas.csv`) e os salvam em um banco analítico local (DuckDB).
2. **Camada de Inteligência:** O asset `vendas_agregadas_sql` aciona o agente Gemini (com contrato de dados via Pydantic). A IA analisa as tabelas disponíveis e gera uma query SQL que faz o `JOIN` entre vendas e metas, calculando automaticamente quem atingiu o objetivo. A IA também escreve a documentação do modelo.
3. **Camada de Transformação:** O `dbt_run` executa o dbt para materializar a transformação gerada pela IA e criar a tabela analítica final no DuckDB.

O resultado esperado no Dagster é o seguinte grafo de linhagem (*Lineage*):

`[raw_vendas, raw_metas] -> vendas_agregadas_sql -> dbt_run`

## Estrutura do Projeto

* `pipeline.py` — Definição dos assets e orquestração (Dagster). Possui trava de concorrência para otimização do DuckDB.
* `ai_agent.py` — Camada de integração com a API Gemini/OpenAI que gera o SQL limpo e atualiza a documentação via Pydantic.
* `dbt_project/` — Projeto dbt contendo `profiles.yml`, `dbt_project.yml` e a pasta `models/` (onde a IA injeta o código).
* `data/` — Diretório com os dados de origem.
* `vendas.csv` — Dados transacionais de vendas.
* `metas.csv` — Dados de metas de receita por produto.


* `db/gen_ecommerce_lab.duckdb` — Banco de dados analítico local gerado automaticamente.
* `view_results.py` — Script auxiliar para inspecionar e exibir a tabela final processada no terminal.
* `requirements.txt` — Dependências do ambiente Python.

## Preparação (Passo a Passo)

**1. Clone o repositório:**

```bash
git clone https://github.com/vinisouzza/gen-ecommerce.git
cd gen-ecommerce

```

**2. Crie e ative o ambiente virtual Python:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

**3. Instale as dependências:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

**4. Configure a chave de API Gemini/OpenAI:**

```bash
copy .env.example .env

```

Edite o arquivo `.env` e defina seu token:

```ini
GEMINI_API_KEY=seu_token_aqui

```

**5. Execute o Dagster:**

```bash
dagster dev -f pipeline.py

```

**6.** Abra o navegador em `http://localhost:3000`.

**7.** Na interface Dagster, acesse a aba **Lineage**.

**8.** Clique em **Materialize all** para executar o fluxo de ponta a ponta.

## Como a IA atua neste pipeline

Diferente de pipelines tradicionais com SQL estático, este projeto utiliza o Gemini para atuar como um engenheiro de dados virtual:

* **Compreensão de Esquema:** A IA recebe o contexto das tabelas `raw_vendas` e `raw_metas`.
* **Geração de Regras de Negócio:** A partir de um prompt em linguagem natural, a IA escreve o código SQL (`CASE WHEN`) para validar se a receita total do produto superou a meta estabelecida.
* **Governança:** A IA preenche automaticamente o arquivo `schema.yml` do dbt com as descrições do que a query faz, eliminando documentação defasada.

## Verificação Pós-Execução

Após o *Materialize all* ser concluído com sucesso no Dagster, você pode visualizar a tabela final com o cruzamento das vendas e metas digitando no terminal:

```bash
python view_results.py

```