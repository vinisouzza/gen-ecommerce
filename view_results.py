import duckdb
import pandas as pd

# 1. Conecta ao banco de dados existente
con = duckdb.connect('db/gen_ecommerce_lab.duckdb')

# 2. Lista todas as tabelas dentro do banco
tabelas = con.execute("SHOW TABLES").fetchall()

if not tabelas:
    print("O banco de dados está vazio! Nenhuma tabela foi encontrada.")
else:
    print(f"Tabelas encontradas: {[t[0] for t in tabelas]}")
    
    # 3. Itera sobre cada tabela e exibe uma amostra
    for tabela in tabelas:
        nome_tabela = tabela[0]
        print(f"\n{'='*20} Conteúdo da tabela: {nome_tabela} {'='*20}")
        
        # Consulta os dados e converte para DataFrame do Pandas para facilitar a leitura
        df = con.execute(f"SELECT * FROM {nome_tabela} LIMIT 5").df()
        print(df)
        
        # Mostra também o esquema da tabela (nomes das colunas)
        print(f"\nColunas de {nome_tabela}:")
        print(con.execute(f"DESCRIBE {nome_tabela}").df()[['column_name', 'column_type']])

con.close()