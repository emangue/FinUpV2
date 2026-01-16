"""
Popular Grupos Faltantes no Budget Planning

Este script:
1. Lista todos os grupos com despesas em journal_entries
2. Verifica quais NÃO estão no budget_planning
3. Popula todos os meses com média dos últimos 3 meses

Autor: Sistema de Finanças V5
Data: 2026-01-15
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Configurações
DB_PATH = Path(__file__).parent / "app_dev" / "backend" / "database" / "financas_dev.db"
USER_ID = 1


def conectar_banco():
    """Conecta ao banco de dados"""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def listar_grupos_com_despesas(conn):
    """Lista todos os grupos únicos com despesas em journal_entries"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT GRUPO
        FROM journal_entries
        WHERE user_id = ?
          AND CategoriaGeral = 'Despesa'
          AND GRUPO IS NOT NULL
        ORDER BY GRUPO
    """, (USER_ID,))
    
    return [row['GRUPO'] for row in cursor.fetchall()]


def listar_grupos_planning(conn):
    """Lista todos os grupos únicos em budget_planning"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT grupo
        FROM budget_planning
        WHERE user_id = ?
        ORDER BY grupo
    """, (USER_ID,))
    
    return [row['grupo'] for row in cursor.fetchall()]


def calcular_media_3_meses(conn, grupo, mes_referencia):
    """Calcula média dos últimos 3 meses para um grupo específico"""
    cursor = conn.cursor()
    
    # Converter mes_referencia (YYYY-MM) para objeto datetime
    ano, mes = map(int, mes_referencia.split('-'))
    data_ref = datetime(ano, mes, 1)
    
    # Calcular 3 meses anteriores
    mes_1 = data_ref - relativedelta(months=1)
    mes_2 = data_ref - relativedelta(months=2)
    mes_3 = data_ref - relativedelta(months=3)
    
    # Converter para formato YYYYMM
    meses_filtro = [
        mes_1.strftime('%Y%m'),
        mes_2.strftime('%Y%m'),
        mes_3.strftime('%Y%m')
    ]
    
    cursor.execute("""
        SELECT AVG(total) as media
        FROM (
            SELECT SUM(ABS(Valor)) as total
            FROM journal_entries
            WHERE user_id = ?
              AND GRUPO = ?
              AND CategoriaGeral = 'Despesa'
              AND MesFatura IN (?, ?, ?)
            GROUP BY MesFatura
        )
    """, (USER_ID, grupo, meses_filtro[0], meses_filtro[1], meses_filtro[2]))
    
    resultado = cursor.fetchone()
    media = resultado['media'] if resultado['media'] else 0
    
    return round(media, 2)


def gerar_meses_periodo(ano_inicio=2024, ano_fim=2026):
    """Gera lista de meses no formato YYYY-MM"""
    meses = []
    data_atual = datetime(ano_inicio, 1, 1)
    data_fim = datetime(ano_fim, 12, 31)
    
    while data_atual <= data_fim:
        meses.append(data_atual.strftime('%Y-%m'))
        data_atual += relativedelta(months=1)
    
    return meses


def popular_grupo_planning(conn, grupo, meses):
    """Popula budget_planning para um grupo em todos os meses"""
    cursor = conn.cursor()
    
    print(f"\n📊 Populando grupo: {grupo}")
    print(f"   Período: {meses[0]} a {meses[-1]}")
    
    inseridos = 0
    soma_total = 0
    
    for mes_ref in meses:
        # Verificar se já existe
        cursor.execute("""
            SELECT id FROM budget_planning
            WHERE user_id = ?
              AND grupo = ?
              AND mes_referencia = ?
        """, (USER_ID, grupo, mes_ref))
        
        if cursor.fetchone():
            continue  # Já existe, pular
        
        # Calcular média dos últimos 3 meses
        media = calcular_media_3_meses(conn, grupo, mes_ref)
        
        # Inserir registro
        cursor.execute("""
            INSERT INTO budget_planning 
            (user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (USER_ID, grupo, mes_ref, media, media))
        
        inseridos += 1
        soma_total += media
    
    conn.commit()
    
    print(f"   ✅ {inseridos} registros inseridos")
    print(f"   💰 Soma total planejada: R$ {soma_total:,.2f}")
    
    return inseridos


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("🚀 POPULAR GRUPOS FALTANTES NO BUDGET PLANNING")
    print("=" * 80)
    print(f"📁 Banco de dados: {DB_PATH}")
    print(f"👤 User ID: {USER_ID}")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    conn = conectar_banco()
    
    try:
        # Listar grupos com despesas
        grupos_despesas = listar_grupos_com_despesas(conn)
        print(f"\n📊 Grupos com despesas em journal_entries: {len(grupos_despesas)}")
        for g in grupos_despesas:
            print(f"   - {g}")
        
        # Listar grupos no planning
        grupos_planning = listar_grupos_planning(conn)
        print(f"\n📋 Grupos no budget_planning: {len(grupos_planning)}")
        for g in grupos_planning:
            print(f"   - {g}")
        
        # Identificar grupos faltantes
        grupos_faltantes = [g for g in grupos_despesas if g not in grupos_planning]
        
        print("\n" + "=" * 80)
        print(f"⚠️  GRUPOS FALTANTES NO PLANNING: {len(grupos_faltantes)}")
        print("=" * 80)
        
        if not grupos_faltantes:
            print("✅ Todos os grupos já estão no planning!")
            return
        
        for g in grupos_faltantes:
            print(f"   ❌ {g}")
        
        # Confirmar
        print("\n" + "=" * 80)
        confirmacao = input("❓ Deseja popular esses grupos no planning? (sim/não): ").strip().lower()
        
        if confirmacao != 'sim':
            print("❌ Operação cancelada pelo usuário.")
            return
        
        # Gerar meses
        meses = gerar_meses_periodo(2024, 2026)
        print(f"\n📅 Período: {len(meses)} meses ({meses[0]} a {meses[-1]})")
        
        # Popular cada grupo
        print("\n" + "=" * 80)
        print("📝 POPULANDO GRUPOS...")
        print("=" * 80)
        
        total_inseridos = 0
        for grupo in grupos_faltantes:
            inseridos = popular_grupo_planning(conn, grupo, meses)
            total_inseridos += inseridos
        
        # Resumo final
        print("\n" + "=" * 80)
        print("✅ POPULAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print(f"📊 Grupos populados: {len(grupos_faltantes)}")
        print(f"📝 Registros inseridos: {total_inseridos}")
        
        # Validar resultado
        grupos_planning_final = listar_grupos_planning(conn)
        print(f"📋 Grupos totais no planning: {len(grupos_planning_final)}")
        
        print("\n🎯 Processo finalizado!\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}\n")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
