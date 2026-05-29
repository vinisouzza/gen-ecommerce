import duckdb
from tabulate import TableFormat

def visualizar_dados():
    print("\n" + "="*60)
    print("   RESULTADO FINAL NO DUCKDB (TABELA: vendas_agregadas)   ")
    print("="*60)
    
    # Conecta no banco local
    conn = duckdb.connect("db/gen_ecommerce_lab.duckdb")
    
    # Transforma a consulta em um DataFrame do Pandas para exibir bonito
    df = conn.execute("SELECT * FROM vendas_agregadas").df()
    
    # Exibe o resultado formatado no terminal
    print(df.to_markdown(index=False))
    
    conn.close()
    print("="*60 + "\n")

if __name__ == "__main__":
    visualizar_dados()