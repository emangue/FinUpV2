#!/usr/bin/env python3
"""
Script para corrigir TipoGasto e CategoriaGeral de transações
baseando-se na base_grupos_config
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app_dev'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path do banco
DB_PATH = "/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db"

# Criar engine e session
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


def fix_categoria_geral():
    """
    Atualiza TipoGasto e CategoriaGeral em journal_entries
    baseando-se na base_grupos_config
    """
    session = Session()
    
    try:
        # 1. Buscar todos os grupos da base_grupos_config
        result = session.execute(text("""
            SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
            FROM base_grupos_config
        """))
        
        grupos_config = {row[0]: {"tipo_gasto": row[1], "categoria_geral": row[2]} 
                        for row in result}
        
        logger.info(f"📚 Carregados {len(grupos_config)} grupos da base_grupos_config")
        
        # 2. Para cada grupo, atualizar journal_entries
        total_updated = 0
        
        for nome_grupo, config in grupos_config.items():
            # Verificar quantos registros serão afetados
            count_result = session.execute(text("""
                SELECT COUNT(*) 
                FROM journal_entries 
                WHERE GRUPO = :grupo 
                AND (TipoGasto != :tipo_gasto OR CategoriaGeral != :categoria_geral)
            """), {
                "grupo": nome_grupo,
                "tipo_gasto": config["tipo_gasto"],
                "categoria_geral": config["categoria_geral"]
            })
            
            count = count_result.scalar()
            
            if count > 0:
                # Atualizar registros
                session.execute(text("""
                    UPDATE journal_entries 
                    SET TipoGasto = :tipo_gasto,
                        CategoriaGeral = :categoria_geral
                    WHERE GRUPO = :grupo
                """), {
                    "tipo_gasto": config["tipo_gasto"],
                    "categoria_geral": config["categoria_geral"],
                    "grupo": nome_grupo
                })
                
                logger.info(f"  ✅ {nome_grupo}: {count} registros atualizados (TipoGasto={config['tipo_gasto']}, CategoriaGeral={config['categoria_geral']})")
                total_updated += count
        
        # Commit das mudanças
        session.commit()
        logger.info(f"\n🎉 Total de registros atualizados: {total_updated}")
        
        # 3. Validar resultados
        logger.info("\n📊 Validação pós-correção:")
        for nome_grupo, config in list(grupos_config.items())[:5]:  # Mostrar primeiros 5
            result = session.execute(text("""
                SELECT COUNT(*) 
                FROM journal_entries 
                WHERE GRUPO = :grupo 
                AND TipoGasto = :tipo_gasto 
                AND CategoriaGeral = :categoria_geral
            """), {
                "grupo": nome_grupo,
                "tipo_gasto": config["tipo_gasto"],
                "categoria_geral": config["categoria_geral"]
            })
            
            count = result.scalar()
            logger.info(f"  {nome_grupo}: {count} registros corretos")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando correção de TipoGasto e CategoriaGeral...\n")
    fix_categoria_geral()
    logger.info("\n✅ Correção concluída!")
