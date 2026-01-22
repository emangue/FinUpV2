"""
Popular Grupos Faltantes no Budget Planning

Este script:
1. Busca todos os grupos disponíveis em base_grupos_config
2. Verifica quais NÃO estão no budget_planning para cada mês
3. Popula todos os meses de 2025-2026 com valor 0

Autor: Sistema de Finanças V5
Data: 2026-01-18
"""

import sqlite3
from pathlib import Path
import logging

# Configurações
DB_PATH = Path(__file__).parent / "app_dev" / "backend" / "database" / "financas_dev.db"
USER_ID = 1

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def conectar_banco():
    """Conecta ao banco de dados"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {DB_PATH}")
    
    return sqlite3.connect(DB_PATH)


def listar_todos_grupos(conn):
    """Lista todos os grupos disponíveis em base_grupos_config"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT nome_grupo 
        FROM base_grupos_config 
        WHERE categoria_geral = 'Despesa'
        ORDER BY nome_grupo
    """)
    
    return [row[0] for row in cursor.fetchall()]


def listar_grupos_mes_planning(conn, mes_ref):
    """Lista grupos existentes em budget_planning para um mês específico"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT grupo
        FROM budget_planning
        WHERE user_id = ? AND mes_referencia = ?
        ORDER BY grupo
    """, (USER_ID, mes_ref))
    
    return set(row[0] for row in cursor.fetchall())




def main():
    """Função principal"""
    logging.info("🚀 Iniciando população de grupos faltantes em budget_planning...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # 1. Buscar todos os grupos disponíveis
        todos_grupos = listar_todos_grupos(conn)
        logging.info(f"📚 Total de grupos disponíveis: {len(todos_grupos)}")
        logging.info(f"  Grupos: {', '.join(todos_grupos)}")
        
        # 2. Para cada mês de 2025 e 2026
        anos_meses = []
        for ano in [2025, 2026]:
            for mes in range(1, 13):
                anos_meses.append(f"{ano}-{mes:02d}")
        
        total_inseridos = 0
        
        for mes_ref in anos_meses:
            # Buscar grupos já existentes neste mês
            grupos_existentes = listar_grupos_mes_planning(conn, mes_ref)
            
            # Calcular grupos faltantes
            grupos_faltantes = [g for g in todos_grupos if g not in grupos_existentes]
            
            if grupos_faltantes:
                logging.info(f"\n📅 {mes_ref}: {len(grupos_faltantes)} grupos faltantes")
                
                for grupo in grupos_faltantes:
                    logging.info(f"  ➕ {grupo}")
                    cursor.execute("""
                        INSERT INTO budget_planning (
                            user_id, 
                            grupo, 
                            mes_referencia, 
                            valor_planejado, 
                            valor_medio_3_meses,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (USER_ID, grupo, mes_ref, 0.0, 0.0))
                    total_inseridos += 1
        
        conn.commit()
        logging.info(f"\n🎉 Total de grupos inseridos: {total_inseridos}")
        
        # 3. Validação pós-inserção
        logging.info("\n📊 Validação pós-inserção:")
        for mes_ref in anos_meses:
            grupos_existentes = listar_grupos_mes_planning(conn, mes_ref)
            count = len(grupos_existentes)
            status = "✅" if count == len(todos_grupos) else "⚠️"
            logging.info(f"  {status} {mes_ref}: {count}/{len(todos_grupos)} grupos")
        
        logging.info("\n✅ População concluída!")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Erro: {e}")
        raise
    finally:
        conn.close()



if __name__ == "__main__":
    main()
