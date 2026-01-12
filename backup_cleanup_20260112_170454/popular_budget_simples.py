#!/usr/bin/env python3
"""
Script para popular a tabela budget_planning com médias pré-calculadas
Usa SQL direto para evitar problemas com relationships do SQLAlchemy
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Path do banco
DB_PATH = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")

def calcular_media_3_meses(conn, user_id: int, tipo_gasto: str, mes_referencia: str) -> float:
    """
    Calcula média dos últimos 3 meses para um tipo de gasto
    CORRIGIDO: Agrupa por mês, soma cada mês, depois calcula média
    (mesmo comportamento do BudgetService.calcular_media_3_meses)
    """
    # Converter mes_referencia (YYYY-MM) para formato YYYYMM
    ano, mes = mes_referencia.split('-')
    mes_fatura_format = f"{ano}{mes}"
    
    # Calcular últimos 3 meses
    data_ref = datetime.strptime(mes_referencia, '%Y-%m')
    meses_anteriores = []
    for i in range(1, 4):  # 3 meses anteriores
        mes_anterior = data_ref - relativedelta(months=i)
        meses_anteriores.append(mes_anterior.strftime('%Y%m'))
    
    print(f"  → Calculando média para {tipo_gasto} em {mes_referencia} (meses: {meses_anteriores})")
    
    # CORRIGIDO: Agrupar por mês e somar cada mês separadamente
    query = """
        SELECT MesFatura, SUM(ABS(Valor)) as total_mes
        FROM journal_entries
        WHERE user_id = ?
          AND TipoGasto = ?
          AND MesFatura IN (?, ?, ?)
          AND IgnorarDashboard = 0
          AND Valor < 0
          AND CategoriaGeral = 'Despesa'
        GROUP BY MesFatura
    """
    
    cursor = conn.execute(
        query,
        (user_id, tipo_gasto, meses_anteriores[0], meses_anteriores[1], meses_anteriores[2])
    )
    
    results = cursor.fetchall()
    
    # Calcular média: soma total / quantidade de meses com dados
    if results:
        total = sum(row[1] for row in results)
        qtd_meses = len(results)
        media = round(total / qtd_meses, 2)  # Arredondar para 2 casas decimais
        print(f"    Meses com dados: {qtd_meses} | Total: R$ {total:.2f} | Média: R$ {media:.2f}")
        return media
    else:
        print(f"    Sem dados")
        return 0.0

def popular_budget_planning():
    """
    Popular tabela budget_planning com todos os tipos de gasto
    para os próximos 12 meses
    """
    print("=" * 60)
    print("🔧 Popular Budget Planning - Versão Simplificada")
    print("=" * 60)
    print()
    
    if not DB_PATH.exists():
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        # 1. Buscar todos os tipos de gasto com transações
        print("📊 Buscando tipos de gasto...")
        cursor = conn.execute("""
            SELECT DISTINCT TipoGasto
            FROM journal_entries
            WHERE user_id = 1
              AND TipoGasto IS NOT NULL
              AND TipoGasto != ''
            ORDER BY TipoGasto
        """)
        
        tipos_gasto = [row[0] for row in cursor.fetchall()]
        print(f"✅ Encontrados {len(tipos_gasto)} tipos de gasto")
        print(f"   {tipos_gasto[:10]}{'...' if len(tipos_gasto) > 10 else ''}")
        print()
        
        # 2. Gerar lista de meses (12 meses a partir de agora)
        print("📅 Gerando lista de meses...")
        data_inicial = datetime.now()
        meses_referencia = []
        for i in range(12):
            mes = data_inicial + relativedelta(months=i)
            meses_referencia.append(mes.strftime('%Y-%m'))
        
        print(f"✅ Gerando previsões para: {meses_referencia[0]} até {meses_referencia[-1]}")
        print()
        
        # 3. Limpar budget_planning existente para user_id=1
        print("🗑️  Limpando registros antigos...")
        conn.execute("DELETE FROM budget_planning WHERE user_id = 1")
        conn.commit()
        print("✅ Registros antigos removidos")
        print()
        
        # 4. Calcular e inserir médias
        print("💰 Calculando e inserindo médias...")
        total_inseridos = 0
        
        for mes_ref in meses_referencia:
            print(f"\n📅 Processando mês: {mes_ref}")
            
            for tipo_gasto in tipos_gasto:
                # Calcular média
                media = calcular_media_3_meses(conn, 1, tipo_gasto, mes_ref)
                
                # Inserir apenas se média > 0
                if media > 0:
                    conn.execute("""
                        INSERT INTO budget_planning 
                        (user_id, tipo_gasto, mes_referencia, valor_planejado, valor_medio_3_meses, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        1,  # user_id
                        tipo_gasto,
                        mes_ref,
                        media,  # valor_planejado = média
                        media,  # valor_medio_3_meses
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    total_inseridos += 1
        
        # Commit final
        conn.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Processo concluído!")
        print(f"   Total de registros inseridos: {total_inseridos}")
        print("=" * 60)
        
        # Verificar resultado
        print("\n🔍 Verificando resultado...")
        cursor = conn.execute("SELECT COUNT(*) FROM budget_planning WHERE user_id = 1")
        count = cursor.fetchone()[0]
        print(f"   Registros na tabela: {count}")
        
        # Mostrar amostra
        print("\n📋 Amostra dos dados inseridos:")
        cursor = conn.execute("""
            SELECT tipo_gasto, mes_referencia, valor_medio_3_meses
            FROM budget_planning
            WHERE user_id = 1
            ORDER BY mes_referencia, tipo_gasto
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"   {row[0]:<30} | {row[1]} | R$ {row[2]:>10.2f}")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular budget_planning: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    popular_budget_planning()
