import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# CONTRATO DE DADOS (Pydantic)
# Garante que a IA responda estritamente neste formato JSON
# =====================================================================
class AIQueryResponse(BaseModel):
    sql: str = Field(description="A query SQL DuckDB limpa para executar a agregação solicitada.")
    explanation: str = Field(description="Uma explicação curta da query gerada em português para documentação.")

def gerar_sql_e_doc_gemini(descricao: str) -> AIQueryResponse:
    """
    Chama a API gratuita do Gemini utilizando o SDK compatível da OpenAI.
    Isso força o modelo a obedecer o JSON Schema do Pydantic.
    """
    # Inicializa o cliente apontando para a URL de compatibilidade do Gemini
    client = OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    prompt = f"""
    Você é um engenheiro de dados especialista em DuckDB SQL.
    Escreva uma query SQL que atenda estritamente a este requisito: "{descricao}"
    
    Temos duas tabelas de origem:
    1. 'raw_vendas' com colunas: id (INT), data (DATE), produto (VARCHAR), quantidade (INT), preco_unitario (DOUBLE).
    2. 'raw_metas' com colunas: produto (VARCHAR), meta_receita (DOUBLE).
    
    Sua resposta DEVE ser estruturada conforme o JSON Schema especificado. 
    Não adicione tags de markdown do tipo ```sql na query. Retorne apenas o código limpo.
    """
    
    response = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format=AIQueryResponse,
        temperature=0.0
    )
    
    # O SDK retorna uma lista de choices; usamos a primeira opção válida.
    if not response.choices:
        raise ValueError("Gemini retornou nenhuma escolha (choices está vazio).")

    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise ValueError(f"Gemini retornou uma escolha sem conteúdo parseado: {response}")

    return parsed