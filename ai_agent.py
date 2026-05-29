import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class AIQueryResponse(BaseModel):
    sql: str = Field(description="Query SQL DuckDB limpa para executar a agregação ou transformação solicitada.")
    explanation: str = Field(description="Uma explicação curta da query gerada em português para documentação.")

def gerar_sql_e_doc_gemini(descricao: str) -> AIQueryResponse:
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    prompt = f"""
    Você é um engenheiro de dados especialista em DuckDB SQL.
    Responda estritamente no formato JSON compatível com o schema fornecido.
    Escreva apenas a query SQL limpa e uma explicação curta.

    Requisito: {descricao}

    As tabelas brutas do projeto são:
    - raw_orders
    - raw_customers
    - raw_order_items
    - raw_products
    - raw_reviews

    Não adicione tags markdown, não adicione texto extra.
    """

    response = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format=AIQueryResponse,
        temperature=0.0
    )

    if not response.choices:
        raise ValueError("Gemini retornou nenhuma escolha (choices está vazio).")

    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise ValueError(f"Gemini retornou uma escolha sem conteúdo parseado: {response}")

    return parsed