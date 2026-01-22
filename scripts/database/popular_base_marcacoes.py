#!/usr/bin/env python3
"""
Script para popular base_marcacoes com todas as combinações
existentes em journal_entries
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


def popular_base_marcacoes():
    """
    Popula base_marcacoes com todas as combinações GRUPO+SUBGRUPO+TipoGasto
    existentes em journal_entries
    """
    session = Session()
    
    try:
        # 1. Buscar todas as combinações únicas em journal_entries
        result = session.execute(text("""
            SELECT DISTINCT 
                GRUPO, 
                SUBGRUPO, 
                TipoGasto
            FROM journal_entries 
            WHERE GRUPO IS NOT NULL 
            AND SUBGRUPO IS NOT NULL 
            AND TipoGasto IS NOT NULL
            ORDER BY GRUPO, SUBGRUPO
        """))
        
        combinacoes = result.fetchall()
        logger.info(f"📊 Encontradas {len(combinacoes)} combinações únicas em journal_entries")
        
        # 2. Para cada combinação, verificar se existe em base_marcacoes
        novas = 0
        existentes = 0
        
        for grupo, subgrupo, tipo_gasto in combinacoes:
            # Verificar se já existe
            check = session.execute(text("""
                SELECT COUNT(*) 
                FROM base_marcacoes 
                WHERE GRUPO = :grupo 
                AND SUBGRUPO = :subgrupo 
                AND TipoGasto = :tipo_gasto
            """), {
                "grupo": grupo,
                "subgrupo": subgrupo,
                "tipo_gasto": tipo_gasto
            })
            
            if check.scalar() == 0:
                # Inserir nova marcação
                session.execute(text("""
                    INSERT INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
                    VALUES (:grupo, :subgrupo, :tipo_gasto)
                """), {
                    "grupo": grupo,
                    "subgrupo": subgrupo,
                    "tipo_gasto": tipo_gasto
                })
                novas += 1
                logger.info(f"  ➕ {grupo} > {subgrupo} ({tipo_gasto})")
            else:
                existentes += 1
        
        # Commit
        session.commit()
        
        logger.info(f"\n📈 Resumo:")
        logger.info(f"  ✅ Novas marcações inseridas: {novas}")
        logger.info(f"  ✓ Marcações já existentes: {existentes}")
        logger.info(f"  📊 Total na base_marcacoes: {novas + existentes}")
        
        # 3. Validar resultado
        total_marcacoes = session.execute(text("SELECT COUNT(*) FROM base_marcacoes")).scalar()
        logger.info(f"\n🎯 Total de marcações na base: {total_marcacoes}")
        
        # Mostrar algumas amostras
        logger.info(f"\n📋 Amostras (primeiras 10):")
        amostras = session.execute(text("""
            SELECT GRUPO, SUBGRUPO, TipoGasto 
            FROM base_marcacoes 
            ORDER BY GRUPO, SUBGRUPO 
            LIMIT 10
        """))
        
        for grupo, subgrupo, tipo_gasto in amostras:
            logger.info(f"  • {grupo} > {subgrupo} ({tipo_gasto})")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando população da base_marcacoes...\n")
    popular_base_marcacoes()
    logger.info("\n✅ População concluída!")
