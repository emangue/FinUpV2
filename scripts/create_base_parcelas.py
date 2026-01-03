import sys
import os
from sqlalchemy import create_engine, text

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_schema():
    print("🔄 Atualizando schema do banco de dados...")
    
    engine = create_engine('sqlite:///financas.db')
    
    with engine.connect() as conn:
        # Verifica se tabela base_parcelas existe
        try:
            conn.execute(text("SELECT 1 FROM base_parcelas LIMIT 1"))
            print("✓ Tabela base_parcelas já existe")
        except:
            print("⚠ Tabela base_parcelas não encontrada. Criando...")
            
            # Cria tabela
            sql = """
            CREATE TABLE base_parcelas (
                id INTEGER PRIMARY KEY,
                id_parcela VARCHAR(64) NOT NULL UNIQUE,
                estabelecimento_base TEXT NOT NULL,
                valor_parcela FLOAT NOT NULL,
                qtd_parcelas INTEGER NOT NULL,
                grupo_sugerido VARCHAR(100),
                subgrupo_sugerido VARCHAR(100),
                tipo_gasto_sugerido VARCHAR(100),
                qtd_pagas INTEGER DEFAULT 0,
                valor_total_plano FLOAT,
                data_inicio VARCHAR(10),
                status VARCHAR(20) DEFAULT 'ativo',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
            conn.execute(text(sql))
            
            # Cria índice
            conn.execute(text("CREATE UNIQUE INDEX ix_base_parcelas_id_parcela ON base_parcelas (id_parcela)"))
            print("✅ Tabela base_parcelas criada com sucesso!")

if __name__ == "__main__":
    update_schema()
