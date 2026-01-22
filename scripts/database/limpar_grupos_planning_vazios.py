"""
Validação e Limpeza de Grupos no Planning

Este script:
1. Lista todos os grupos em budget_planning
2. Verifica se cada grupo tem valores realizados em journal_entries
3. Lista grupos ÓRFÃOS (sem valores no histórico)
4. Permite limpar grupos órfãos do budget_planning

Autor: Sistema de Finanças V5
Data: 2026-01-15
"""

import sqlite3
from pathlib import Path
from datetime import datetime

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


def verificar_valores_realizados(conn, grupo):
    """Verifica se um grupo tem valores realizados em journal_entries (apenas Despesas)"""
    cursor = conn.cursor()
    
    # Buscar apenas transações de DESPESA desse grupo
    cursor.execute("""
        SELECT 
            COUNT(*) as total_transacoes,
            SUM(ABS(Valor)) as total_despesas,
            MIN(Ano) as ano_inicial,
            MAX(Ano) as ano_final
        FROM journal_entries
        WHERE user_id = ?
          AND GRUPO = ?
          AND CategoriaGeral = 'Despesa'
    """, (USER_ID, grupo))
    
    resultado = cursor.fetchone()
    
    return {
        'grupo': grupo,
        'total_transacoes': resultado['total_transacoes'],
        'total_despesas': round(resultado['total_despesas'] or 0, 2),
        'ano_inicial': resultado['ano_inicial'],
        'ano_final': resultado['ano_final'],
        'tem_valores': resultado['total_transacoes'] > 0 and resultado['total_despesas'] > 0
    }


def contar_registros_planning(conn, grupo):
    """Conta quantos registros de planning existem para um grupo"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(valor_planejado) as soma_planejado
        FROM budget_planning
        WHERE user_id = ?
          AND grupo = ?
    """, (USER_ID, grupo))
    
    resultado = cursor.fetchone()
    return {
        'total_registros': resultado['total'],
        'soma_planejado': round(resultado['soma_planejado'] or 0, 2)
    }


def analisar_grupos(excluir_grupo=None):
    """Analisa todos os grupos e identifica órfãos
    
    Args:
        excluir_grupo: Nome do grupo a excluir da lista de órfãos (manter sempre)
    """
    print("=" * 80)
    print("🔍 ANÁLISE DE GRUPOS NO BUDGET PLANNING")
    print("=" * 80)
    print(f"📁 Banco de dados: {DB_PATH}")
    print(f"👤 User ID: {USER_ID}")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    conn = conectar_banco()
    
    try:
        # Listar grupos
        grupos = listar_grupos_planning(conn)
        print(f"\n📊 Total de grupos únicos no planning: {len(grupos)}\n")
        
        # Analisar cada grupo
        grupos_com_valores = []
        grupos_orfaos = []
        
        for grupo in grupos:
            info_realizado = verificar_valores_realizados(conn, grupo)
            info_planning = contar_registros_planning(conn, grupo)
            
            info_completa = {
                **info_realizado,
                **info_planning
            }
            
            if info_realizado['tem_valores']:
                grupos_com_valores.append(info_completa)
            else:
                # Excluir grupo específico da lista de órfãos se solicitado
                if excluir_grupo and grupo == excluir_grupo:
                    grupos_com_valores.append(info_completa)
                else:
                    grupos_orfaos.append(info_completa)
        
        # Relatório: Grupos com valores
        print("✅ GRUPOS COM VALORES REALIZADOS NO HISTÓRICO")
        print("-" * 80)
        if grupos_com_valores:
            for info in grupos_com_valores:
                print(f"\n📌 {info['grupo']}")
                print(f"   Transações: {info['total_transacoes']}")
                print(f"   Total despesas: R$ {info['total_despesas']:,.2f}")
                print(f"   Período: {info['ano_inicial']} - {info['ano_final']}")
                print(f"   Planning: {info['total_registros']} registros (R$ {info['soma_planejado']:,.2f})")
        else:
            print("   Nenhum grupo encontrado (ERRO!)")
        
        # Relatório: Grupos órfãos
        print("\n" + "=" * 80)
        print("⚠️  GRUPOS ÓRFÃOS (SEM DESPESAS REALIZADAS)")
        print("-" * 80)
        if grupos_orfaos:
            print(f"Total de grupos órfãos: {len(grupos_orfaos)}\n")
            for info in grupos_orfaos:
                print(f"\n❌ {info['grupo']}")
                print(f"   Transações: {info['total_transacoes']} (ZERO)")
                print(f"   Planning: {info['total_registros']} registros (R$ {info['soma_planejado']:,.2f})")
        else:
            print("   ✅ Nenhum grupo órfão encontrado!")
        
        print("\n" + "=" * 80)
        print("📊 RESUMO")
        print("-" * 80)
        print(f"Total de grupos: {len(grupos)}")
        print(f"Grupos com valores: {len(grupos_com_valores)}")
        print(f"Grupos órfãos: {len(grupos_orfaos)}")
        
        return grupos_orfaos
        
    finally:
        conn.close()


def limpar_grupos_orfaos(grupos_orfaos):
    """Remove grupos órfãos do budget_planning"""
    if not grupos_orfaos:
        print("\n✅ Nenhum grupo órfão para limpar!")
        return
    
    print("\n" + "=" * 80)
    print("🧹 LIMPEZA DE GRUPOS ÓRFÃOS")
    print("=" * 80)
    
    nomes_grupos = [info['grupo'] for info in grupos_orfaos]
    total_registros = sum(info['total_registros'] for info in grupos_orfaos)
    
    print(f"\n⚠️  Serão removidos {len(nomes_grupos)} grupos:")
    for grupo in nomes_grupos:
        print(f"   - {grupo}")
    print(f"\n📊 Total de registros a serem deletados: {total_registros}")
    
    confirmacao = input("\n❓ Deseja continuar com a limpeza? (sim/não): ").strip().lower()
    
    if confirmacao != 'sim':
        print("❌ Limpeza cancelada pelo usuário.")
        return
    
    # Conectar ao banco
    conn = conectar_banco()
    
    try:
        cursor = conn.cursor()
        
        # Criar backup antes de deletar
        print("\n💾 Criando backup...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_table = f"budget_planning_backup_{timestamp}"
        
        cursor.execute(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM budget_planning
        """)
        print(f"   ✅ Backup criado: {backup_table}")
        
        # Deletar grupos órfãos
        print("\n🗑️  Deletando grupos órfãos...")
        placeholders = ','.join('?' * len(nomes_grupos))
        
        cursor.execute(f"""
            DELETE FROM budget_planning
            WHERE user_id = ?
              AND grupo IN ({placeholders})
        """, [USER_ID] + nomes_grupos)
        
        deletados = cursor.rowcount
        conn.commit()
        
        print(f"   ✅ {deletados} registros deletados com sucesso!")
        
        # Validar resultado
        print("\n🔍 Validando resultado...")
        cursor.execute("""
            SELECT COUNT(DISTINCT grupo) as total_grupos
            FROM budget_planning
            WHERE user_id = ?
        """, (USER_ID,))
        
        grupos_restantes = cursor.fetchone()['total_grupos']
        print(f"   ✅ Grupos restantes no planning: {grupos_restantes}")
        
        print("\n" + "=" * 80)
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"📊 Registros deletados: {deletados}")
        print(f"🗃️  Backup disponível: {backup_table}")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO ao deletar grupos: {e}")
        raise
        
    finally:
        conn.close()


def main():
    """Função principal"""
    print("\n🚀 Iniciando validação e limpeza de grupos órfãos...")
    print()
    
    try:
        # Análise mantendo grupo Outros
        grupos_orfaos = analisar_grupos(excluir_grupo="Outros")
        
        # Se houver grupos órfãos, perguntar se deseja limpar
        if grupos_orfaos:
            print("\n" + "=" * 80)
            limpar_grupos_orfaos(grupos_orfaos)
        
        print("\n🎯 Processo finalizado!\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {e}\n")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        raise


if __name__ == "__main__":
    main()
