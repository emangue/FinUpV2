"""
Script para criar as novas tabelas no banco de dados
"""
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import Cartao, TransacaoExclusao

def create_tables():
    """Cria as tabelas no banco de dados"""
    print("Criando tabelas...")
    
    try:
        # Criar todas as tabelas definidas nos models
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        
        # Listar tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tabelas no banco: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_tables()
