"""
Script para popular budget_planning com médias históricas
Cria registros com valor_planejado=0 e valor_medio_3_meses calculado
"""
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

DB_PATH = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db'

def calcular_media_3_meses(conn, user_id: int, tipo_gasto: str, mes_referencia: str) -> float:
    """
    Calcula média dos últimos 3 meses anteriores ao mes_referencia
    """
    ano, mes = map(int, mes_referencia.split('-'))
    
    # Calcular os 3 meses anteriores
    meses_anteriores = []
    for i in range(1, 4):  # 3 meses atrás
        m = mes - i
        a = ano
        if m < 1:
            m += 12
            a -= 1
        mes_fatura = f"{a:04d}{m:02d}"
        meses_anteriores.append(mes_fatura)
    
    # Buscar transações dos 3 meses anteriores
    cursor = conn.cursor()
    placeholders = ','.join(['?' for _ in meses_anteriores])
    query = f"""
        SELECT MesFatura, SUM(ABS(Valor)) as total
        FROM journal_entries
        WHERE user_id = ?
          AND TipoGasto = ?
          AND CategoriaGeral = 'Despesa'
          AND Valor < 0
          AND IgnorarDashboard = 0
          AND MesFatura IN ({placeholders})
        GROUP BY MesFatura
    """
    
    params = [user_id, tipo_gasto] + meses_anteriores
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    if not resultados:
        return 0.0
    
    # Calcular média
    total = sum(r[1] for r in resultados)
    qtd_meses = len(resultados)
    return round(total / qtd_meses, 2)

def popular_medias_historico(user_id: int = 1, ano_inicio: int = 2024, ano_fim: int = 2026):
    """
    Popula budget_planning com médias históricas para todos os meses
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        # Buscar todos os tipos de gasto únicos
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT TipoGasto
            FROM journal_entries
            WHERE user_id = ?
              AND CategoriaGeral = 'Despesa'
              AND TipoGasto IS NOT NULL
            ORDER BY TipoGasto
        """, (user_id,))
        
        tipos_gasto_list = [row[0] for row in cursor.fetchall()]
        print(f"📊 Encontrados {len(tipos_gasto_list)} tipos de gasto únicos")
        
        # Gerar todos os meses do período
        data_inicio = datetime(ano_inicio, 1, 1)
        data_fim = datetime(ano_fim, 12, 31)
        
        registros_criados = 0
        registros_atualizados = 0
        
        # Iterar por cada mês
        mes_atual = data_inicio
        while mes_atual <= data_fim:
            mes_referencia = mes_atual.strftime('%Y-%m')
            print(f"\n📅 Processando {mes_referencia}...")
            
            # Para cada tipo de gasto
            for tipo_gasto in tipos_gasto_list:
                # Verificar se já existe registro
                cursor.execute("""
                    SELECT id, valor_medio_3_meses
                    FROM budget_planning
                    WHERE user_id = ?
                      AND tipo_gasto = ?
                      AND mes_referencia = ?
                """, (user_id, tipo_gasto, mes_referencia))
                
                existing = cursor.fetchone()
                
                # Calcular média
                media = calcular_media_3_meses(conn, user_id, tipo_gasto, mes_referencia)
                
                if existing:
                    # Atualizar apenas se média mudou
                    if existing[1] != media:
                        cursor.execute("""
                            UPDATE budget_planning
                            SET valor_medio_3_meses = ?
                            WHERE id = ?
                        """, (media, existing[0]))
                        registros_atualizados += 1
                else:
                    # Criar novo registro com planejado = 0
                    cursor.execute("""
                        INSERT INTO budget_planning (user_id, tipo_gasto, mes_referencia, valor_planejado, valor_medio_3_meses)
                        VALUES (?, ?, ?, 0.0, ?)
                    """, (user_id, tipo_gasto, mes_referencia, media))
                    registros_criados += 1
            
            # Commit a cada mês
            conn.commit()
            print(f"   ✅ Criados: {registros_criados}, Atualizados: {registros_atualizados}")
            
            # Próximo mês
            mes_atual = mes_atual + relativedelta(months=1)
        
        print(f"\n🎉 Concluído!")
        print(f"   📝 Total de registros criados: {registros_criados}")
        print(f"   🔄 Total de registros atualizados: {registros_atualizados}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Populando médias históricas no budget_planning...")
    print("=" * 60)
    popular_medias_historico(user_id=1, ano_inicio=2024, ano_fim=2026)
