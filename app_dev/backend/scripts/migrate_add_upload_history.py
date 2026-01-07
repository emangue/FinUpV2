"""
Migration: Criar tabela upload_history e adicionar FK em journal_entries
"""
import sys
from pathlib import Path

# Adicionar backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(engine, table_name, column_name):
    """Verifica se coluna existe"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(engine, table_name):
    """Verifica se tabela existe"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def run_migration():
    logger.info("🔄 Iniciando migration: upload_history")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        try:
            # 1. Criar tabela upload_history
            if not table_exists(engine, 'upload_history'):
                logger.info("📝 Criando tabela upload_history...")
                conn.execute(text("""
                    CREATE TABLE upload_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_id VARCHAR(100) UNIQUE NOT NULL,
                        banco VARCHAR(100) NOT NULL,
                        tipo_documento VARCHAR(50) NOT NULL,
                        nome_arquivo VARCHAR(255) NOT NULL,
                        nome_cartao VARCHAR(100),
                        final_cartao VARCHAR(20),
                        mes_fatura VARCHAR(10),
                        status VARCHAR(20) NOT NULL,
                        total_registros INTEGER DEFAULT 0,
                        transacoes_importadas INTEGER DEFAULT 0,
                        transacoes_duplicadas INTEGER DEFAULT 0,
                        classification_stats TEXT,
                        data_upload DATETIME NOT NULL,
                        data_confirmacao DATETIME,
                        error_message TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                conn.commit()
                logger.info("  ✅ Tabela upload_history criada")
            else:
                logger.info("  ⏭️  Tabela upload_history já existe")
            
            # 2. Criar índices
            logger.info("📝 Criando índices...")
            indices = [
                ("idx_upload_history_user_id", "upload_history", "user_id"),
                ("idx_upload_history_session_id", "upload_history", "session_id"),
                ("idx_upload_history_status", "upload_history", "status"),
            ]
            
            for idx_name, table, column in indices:
                try:
                    conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})"))
                    conn.commit()
                    logger.info(f"  ✅ Índice {idx_name} criado")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"  ⚠️  Erro ao criar índice {idx_name}: {e}")
            
            # 3. Adicionar coluna upload_history_id em journal_entries
            if not column_exists(engine, 'journal_entries', 'upload_history_id'):
                logger.info("📝 Adicionando coluna upload_history_id em journal_entries...")
                conn.execute(text("""
                    ALTER TABLE journal_entries 
                    ADD COLUMN upload_history_id INTEGER
                """))
                conn.commit()
                logger.info("  ✅ Coluna upload_history_id adicionada")
                
                # Criar índice
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_journal_entries_upload_history_id 
                    ON journal_entries(upload_history_id)
                """))
                conn.commit()
                logger.info("  ✅ Índice idx_journal_entries_upload_history_id criado")
            else:
                logger.info("  ⏭️  Coluna upload_history_id já existe")
            
            logger.info("✅ Migration concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro na migration: {str(e)}", exc_info=True)
            conn.rollback()
            raise


if __name__ == "__main__":
    run_migration()
