"""
Migration: Adiciona campo balance_validation à tabela upload_history
Para armazenar validação de saldo de extratos bancários

Comando:
    python scripts/migrate_add_balance_validation.py
"""
import sys
from pathlib import Path

# Adicionar path do backend ao sys.path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.core.config import settings

def migrate():
    """Adiciona coluna balance_validation na tabela upload_history"""
    
    print("🔧 Iniciando migração: adicionar balance_validation")
    
    db = SessionLocal()
    
    try:
        # Verificar se coluna já existe
        result = db.execute(text("PRAGMA table_info(upload_history)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'balance_validation' in columns:
            print("✅ Coluna balance_validation já existe")
            return
        
        # Adicionar coluna
        print("📝 Adicionando coluna balance_validation...")
        db.execute(text("""
            ALTER TABLE upload_history 
            ADD COLUMN balance_validation TEXT
        """))
        db.commit()
        
        print("✅ Coluna balance_validation adicionada com sucesso!")
        print("📊 Estrutura atualizada:")
        print("   - balance_validation: TEXT (JSON)")
        print("   - Exemplo: {\"saldo_inicial\": 459.73, \"saldo_final\": 0.0, \"soma_transacoes\": -485.87, \"is_valid\": false, \"diferenca\": 26.14}")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
