"""
Migration: Adiciona tabela budget_planning para planejamento orçamentário

Cria tabela para armazenar orçamento planejado por TipoGasto/mês
Permite comparação Realizado vs Planejado no dashboard

Data: 2026-01-10
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco"""
    with engine.connect() as conn:
        result = conn.execute(text(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        ))
        return result.fetchone() is not None


def run_migration():
    """Executa a migração para criar tabela budget_planning"""
    try:
        logger.info("🚀 Iniciando migração: Criar tabela budget_planning")
        
        # Verificar se tabela já existe
        if table_exists("budget_planning"):
            logger.warning("⚠️  Tabela budget_planning já existe. Pulando criação.")
            return
        
        with engine.begin() as conn:
            # Criar tabela budget_planning
            logger.info("📝 Criando tabela budget_planning...")
            conn.execute(text("""
                CREATE TABLE budget_planning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tipo_gasto VARCHAR(50) NOT NULL,
                    mes_referencia VARCHAR(7) NOT NULL,
                    valor_planejado FLOAT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE (user_id, tipo_gasto, mes_referencia)
                )
            """))
            logger.info("✅ Tabela budget_planning criada")
            
            # Criar índices
            logger.info("📝 Criando índices...")
            conn.execute(text(
                "CREATE INDEX idx_budget_user_id ON budget_planning(user_id)"
            ))
            conn.execute(text(
                "CREATE INDEX idx_budget_mes_referencia ON budget_planning(mes_referencia)"
            ))
            logger.info("✅ Índices criados")
            
            logger.info("✅ Migração concluída com sucesso!")
            
            # Exibir schema da tabela criada
            result = conn.execute(text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='budget_planning'"
            ))
            schema = result.fetchone()
            if schema:
                logger.info(f"📋 Schema criado:\n{schema[0]}")
    
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        raise


if __name__ == "__main__":
    run_migration()
