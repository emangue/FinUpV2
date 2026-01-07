"""
Migration: Adicionar campos de classificação à tabela preview_transacoes
Data: 2026-01-07
"""

import sys
from pathlib import Path

# Adicionar app ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Verifica se coluna existe na tabela"""
    result = conn.execute(text(f"PRAGMA table_info({table_name})"))
    columns = [row[1] for row in result]
    return column_name in columns


def migrate():
    """
    Adiciona campos de classificação e marcação à preview_transacoes
    """
    logger.info("🔄 Iniciando migration: adicionar campos de classificação")
    
    with engine.connect() as conn:
        try:
            # Lista de colunas para adicionar
            columns_to_add = [
                ('id_transacao', 'VARCHAR(255)'),
                ('id_parcela', 'VARCHAR(255)'),
                ('estabelecimento_base', 'VARCHAR(500)'),
                ('parcela_atual', 'INTEGER'),
                ('total_parcelas', 'INTEGER'),
                ('valor_positivo', 'REAL'),
                ('grupo', 'VARCHAR(255)'),
                ('subgrupo', 'VARCHAR(255)'),
                ('tipo_gasto', 'VARCHAR(255)'),
                ('categoria_geral', 'VARCHAR(255)'),
                ('origem_classificacao', 'VARCHAR(100)'),
                ('tipo_documento', 'VARCHAR(50)'),
                ('nome_cartao', 'VARCHAR(255)'),
                ('data_criacao', 'TIMESTAMP'),
                ('is_duplicate', 'BOOLEAN DEFAULT 0'),
                ('duplicate_reason', 'TEXT'),
            ]
            
            # Adicionar colunas se não existirem
            for column_name, column_type in columns_to_add:
                try:
                    if not column_exists(conn, 'preview_transacoes', column_name):
                        logger.info(f"Adicionando coluna: {column_name}")
                        conn.execute(text(f"""
                            ALTER TABLE preview_transacoes 
                            ADD COLUMN {column_name} {column_type}
                        """))
                        conn.commit()
                    else:
                        logger.info(f"  Coluna {column_name} já existe, pulando...")
                except Exception as e:
                    logger.warning(f"  Erro ao adicionar {column_name}: {str(e)}")
                    conn.rollback()
            
            # Criar índices para performance
            logger.info("Criando índices...")
            indices = [
                ('idx_preview_session_id', 'session_id'),
                ('idx_preview_id_transacao', 'id_transacao'),
                ('idx_preview_id_parcela', 'id_parcela'),
                ('idx_preview_origem', 'origem_classificacao'),
                ('idx_preview_user_id', 'user_id'),
            ]
            
            for index_name, column_name in indices:
                try:
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name}
                        ON preview_transacoes({column_name})
                    """))
                    conn.commit()
                    logger.info(f"  Índice {index_name} criado")
                except Exception as e:
                    logger.info(f"  Índice {index_name} já existe ou erro: {str(e)}")
            
            logger.info("✅ Migration concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro na migration: {str(e)}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()
