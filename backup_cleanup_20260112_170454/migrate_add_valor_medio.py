"""
Script de migração: Adiciona coluna valor_medio_3_meses e popula histórico
Data: 2026-01-11

Funcionalidade:
1. Adiciona coluna valor_medio_3_meses na tabela budget_planning
2. Calcula média dos últimos 3 meses para cada tipo_gasto
3. Popula todos os meses existentes com valor_planejado=0 e média calculada
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adicionar path do app ao sys.path
sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.core.config import settings

DB_PATH = settings.DATABASE_PATH


def calcular_media_3_meses(conn, user_id: int, tipo_gasto: str, mes_referencia: str):
    """
    Calcula média dos últimos 3 meses anteriores ao mes_referencia
    
    Args:
        conn: Conexão SQLite
        user_id: ID do usuário
        tipo_gasto: Tipo de gasto
        mes_referencia: Mês no formato YYYY-MM
        
    Returns:
        float: Média calculada
    """
    # Converter mes_referencia para datetime
    ano, mes = map(int, mes_referencia.split('-'))
    
    # Calcular os 3 meses anteriores
    meses_anteriores = []
    for i in range(1, 4):  # 3 meses atrás
        m = mes - i
        a = ano
        if m < 1:
            m += 12
            a -= 1
        meses_anteriores.append(f"{a:04d}-{m:02d}")
    
    print(f"  Calculando média para {tipo_gasto} | Mês: {mes_referencia} | Meses anteriores: {meses_anteriores}")
    
    # Buscar transações dos 3 meses anteriores
    # Data em journal_entries está no formato dd/mm/yyyy
    cursor = conn.cursor()
    
    # Query para cada mês anterior
    somas_por_mes = {}
    for mes_ant in meses_anteriores:
        ano_busca, mes_busca = mes_ant.split('-')
        
        # Buscar transações deste mês
        query = """
        SELECT Data, Valor
        FROM journal_entries
        WHERE user_id = ?
          AND TipoGasto = ?
          AND CategoriaGeral = 'Despesa'
          AND Valor < 0
          AND substr(Data, 7, 4) || '-' || substr(Data, 4, 2) = ?
        """
        
        cursor.execute(query, (user_id, tipo_gasto, mes_ant))
        transacoes = cursor.fetchall()
        
        if transacoes:
            soma_mes = sum(abs(valor) for _, valor in transacoes)
            somas_por_mes[mes_ant] = soma_mes
            print(f"    {mes_ant}: R$ {soma_mes:.2f} ({len(transacoes)} transações)")
    
    # Calcular média (soma / qtd_meses_com_dados)
    if somas_por_mes:
        total = sum(somas_por_mes.values())
        qtd_meses = len(somas_por_mes)
        media = total / qtd_meses
        print(f"    → Média: R$ {media:.2f} (total: R$ {total:.2f} / {qtd_meses} meses)")
        return round(media, 2)
    else:
        print(f"    → Sem dados históricos (média = 0)")
        return 0.0


def adicionar_coluna(conn):
    """Adiciona coluna valor_medio_3_meses se não existir"""
    cursor = conn.cursor()
    
    # Verificar se coluna já existe
    cursor.execute("PRAGMA table_info(budget_planning)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'valor_medio_3_meses' in columns:
        print("✅ Coluna valor_medio_3_meses já existe")
        return
    
    print("📝 Adicionando coluna valor_medio_3_meses...")
    cursor.execute("""
        ALTER TABLE budget_planning 
        ADD COLUMN valor_medio_3_meses REAL NOT NULL DEFAULT 0.0
    """)
    conn.commit()
    print("✅ Coluna adicionada com sucesso")


def popular_historico(conn):
    """
    Popula tabela budget_planning com histórico de todos os meses
    valor_planejado = 0 (sem planejamento ainda)
    valor_medio_3_meses = calculado do journal_entries
    """
    cursor = conn.cursor()
    
    # Buscar todos os tipos de gasto únicos de Despesa
    cursor.execute("""
        SELECT DISTINCT TipoGasto
        FROM journal_entries
        WHERE CategoriaGeral = 'Despesa'
          AND TipoGasto IS NOT NULL
          AND TipoGasto != 'Pagamento Fatura'
        ORDER BY TipoGasto
    """)
    tipos_gasto = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Encontrados {len(tipos_gasto)} tipos de gasto únicos")
    
    # Buscar todos os meses únicos no journal_entries
    cursor.execute("""
        SELECT DISTINCT substr(Data, 7, 4) || '-' || substr(Data, 4, 2) as mes_ref
        FROM journal_entries
        WHERE CategoriaGeral = 'Despesa'
          AND Data IS NOT NULL
        ORDER BY mes_ref
    """)
    meses = [row[0] for row in cursor.fetchall()]
    
    print(f"📅 Encontrados {len(meses)} meses únicos: {meses[:3]}...{meses[-3:]}")
    
    user_id = 1  # Usuário padrão
    total_inseridos = 0
    total_atualizados = 0
    
    print(f"\n🔄 Processando {len(tipos_gasto)} tipos × {len(meses)} meses = {len(tipos_gasto) * len(meses)} combinações\n")
    
    for tipo_gasto in tipos_gasto:
        print(f"📌 Tipo: {tipo_gasto}")
        
        for mes_ref in meses:
            # Verificar se já existe registro
            cursor.execute("""
                SELECT id, valor_medio_3_meses
                FROM budget_planning
                WHERE user_id = ? AND tipo_gasto = ? AND mes_referencia = ?
            """, (user_id, tipo_gasto, mes_ref))
            
            existing = cursor.fetchone()
            
            # Calcular média dos 3 meses anteriores
            media = calcular_media_3_meses(conn, user_id, tipo_gasto, mes_ref)
            
            if existing:
                # Atualizar apenas valor_medio_3_meses
                budget_id, media_atual = existing
                if media_atual != media:
                    cursor.execute("""
                        UPDATE budget_planning
                        SET valor_medio_3_meses = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (media, datetime.now(), budget_id))
                    total_atualizados += 1
                    print(f"  ✏️  Atualizado: média {media_atual:.2f} → {media:.2f}")
            else:
                # Inserir novo registro com valor_planejado = 0
                cursor.execute("""
                    INSERT INTO budget_planning 
                    (user_id, tipo_gasto, mes_referencia, valor_planejado, valor_medio_3_meses, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, tipo_gasto, mes_ref, 0.0, media, datetime.now(), datetime.now()))
                total_inseridos += 1
                print(f"  ➕ Inserido: planejado=0, média={media:.2f}")
        
        print()  # Linha em branco entre tipos
    
    conn.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ Migração concluída!")
    print(f"   📥 Registros inseridos: {total_inseridos}")
    print(f"   ✏️  Registros atualizados: {total_atualizados}")
    print(f"   📊 Total processado: {total_inseridos + total_atualizados}")
    print(f"{'='*60}\n")


def main():
    """Executa migração completa"""
    print(f"\n{'='*60}")
    print(f"🚀 MIGRAÇÃO: Adicionar valor_medio_3_meses")
    print(f"{'='*60}")
    print(f"Database: {DB_PATH}")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 1. Adicionar coluna
        adicionar_coluna(conn)
        
        # 2. Popular histórico
        popular_historico(conn)
        
        print("✅ Migração concluída com sucesso!\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante migração: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()
