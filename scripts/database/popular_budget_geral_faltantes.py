#!/usr/bin/env python3
"""
Script para popular budget_geral com grupos faltantes em meses antigos
Adiciona valor 0 para grupos que não existem em determinados meses
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


def popular_grupos_faltantes():
    """
    Para cada mês de 2025, adiciona grupos faltantes com valor 0
    """
    session = Session()
    
    try:
        # 1. Buscar todos os grupos de despesa disponíveis
        result = session.execute(text("""
            SELECT nome_grupo 
            FROM base_grupos_config 
            WHERE categoria_geral = 'Despesa'
            ORDER BY nome_grupo
        """))
        
        todos_grupos = [row[0] for row in result]
        logger.info(f"📚 Total de grupos disponíveis: {len(todos_grupos)}")
        logger.info(f"  Grupos: {', '.join(todos_grupos)}")
        
        # 2. Para cada mês de 2025, verificar quais grupos existem
        meses_2025 = [f"2025-{str(i).zfill(2)}" for i in range(1, 13)]
        total_inseridos = 0
        
        for mes_ref in meses_2025:
            # Buscar grupos já existentes no mês
            result = session.execute(text("""
                SELECT categoria_geral 
                FROM budget_geral 
                WHERE user_id = 1 
                AND mes_referencia = :mes_ref
            """), {"mes_ref": mes_ref})
            
            grupos_existentes = set(row[0] for row in result)
            grupos_faltantes = set(todos_grupos) - grupos_existentes
            
            if grupos_faltantes:
                logger.info(f"\n📅 {mes_ref}: {len(grupos_faltantes)} grupos faltantes")
                
                for grupo in sorted(grupos_faltantes):
                    # Inserir com valor 0
                    session.execute(text("""
                        INSERT INTO budget_geral 
                        (user_id, categoria_geral, mes_referencia, valor_planejado, created_at, updated_at)
                        VALUES (1, :grupo, :mes_ref, 0, datetime('now'), datetime('now'))
                    """), {"grupo": grupo, "mes_ref": mes_ref})
                    
                    total_inseridos += 1
                    logger.info(f"  ➕ {grupo}")
            else:
                logger.info(f"✅ {mes_ref}: Completo ({len(grupos_existentes)} grupos)")
        
        # 3. Commit
        session.commit()
        
        logger.info(f"\n🎉 Total de grupos inseridos: {total_inseridos}")
        
        # 4. Validar
        logger.info(f"\n📊 Validação pós-inserção:")
        for mes_ref in meses_2025:
            result = session.execute(text("""
                SELECT COUNT(*) 
                FROM budget_geral 
                WHERE user_id = 1 
                AND mes_referencia = :mes_ref
            """), {"mes_ref": mes_ref})
            
            count = result.scalar()
            status = "✅" if count == len(todos_grupos) else "⚠️"
            logger.info(f"  {status} {mes_ref}: {count}/{len(todos_grupos)} grupos")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando população de grupos faltantes em budget_geral...\n")
    popular_grupos_faltantes()
    logger.info("\n✅ População concluída!")
