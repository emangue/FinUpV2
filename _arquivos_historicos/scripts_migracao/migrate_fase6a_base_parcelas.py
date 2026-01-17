"""
Script de Migração: Fase 6A - Base Parcelas
Atualiza tipo_gasto_sugerido de 9 valores compostos → 5 valores simplificados

Versão: 1.0.0
Data: 15/01/2026
Status: Fase 6A - Auxiliary Tables (Base Parcelas)

REGRA: Usa base_grupos_config para mapear grupo_sugerido → tipo_gasto_padrao
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

# Path do banco
DB_PATH = Path(__file__).parent / "app_dev" / "backend" / "database" / "financas_dev.db"


def get_stats_before():
    """Levanta estatísticas dos valores atuais"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT tipo_gasto_sugerido, COUNT(*) as total
        FROM base_parcelas
        GROUP BY tipo_gasto_sugerido
        ORDER BY total DESC
    """)
    
    stats = cursor.fetchall()
    conn.close()
    
    return stats


def migrate_base_parcelas(dry_run=True):
    """
    Migra base_parcelas usando mapeamento via base_grupos_config
    
    Estratégia:
    1. Para cada registro em base_parcelas:
       - Buscar grupo_sugerido → base_grupos_config.tipo_gasto_padrao
       - Atualizar tipo_gasto_sugerido com o valor encontrado
    
    Args:
        dry_run: Se True, apenas simula (não altera banco)
    """
    print("="*80)
    print("📦 MIGRAÇÃO FASE 6A - BASE PARCELAS")
    print("="*80)
    print()
    
    if dry_run:
        print("⚠️  MODO DRY RUN - Apenas simulação (sem alterações)")
    else:
        print("🚀 MODO REAL - Banco será modificado!")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Estatísticas ANTES
        print("📊 ESTATÍSTICAS ANTES DA MIGRAÇÃO:")
        print("-" * 80)
        
        stats_before = get_stats_before()
        for tipo, count in stats_before:
            print(f"   {tipo:50} {count:>4} registros")
        print()
        
        # 2. Buscar TODOS os registros de base_parcelas
        cursor.execute("""
            SELECT id, user_id, grupo_sugerido, tipo_gasto_sugerido, categoria_geral_sugerida
            FROM base_parcelas
        """)
        
        parcelas = cursor.fetchall()
        print(f"📋 Total de registros: {len(parcelas)}")
        print()
        
        if not parcelas:
            print("⚠️  Nenhum registro encontrado em base_parcelas")
            return
        
        # 3. Processar cada registro
        print("🔄 PROCESSANDO REGISTROS:")
        print("-" * 80)
        
        updates = []
        stats_mudancas = {}
        stats_sem_mudanca = 0
        stats_sem_grupo = 0
        stats_grupo_nao_encontrado = 0
        
        for parcela_id, user_id, grupo_sugerido, tipo_gasto_atual, categoria_geral_atual in parcelas:
            # Caso 1: Sem grupo sugerido
            if not grupo_sugerido or grupo_sugerido.strip() == '':
                stats_sem_grupo += 1
                continue
            
            # Buscar tipo_gasto_padrao E categoria_geral via base_grupos_config
            cursor.execute("""
                SELECT tipo_gasto_padrao, categoria_geral
                FROM base_grupos_config
                WHERE nome_grupo = ? COLLATE NOCASE
            """, (grupo_sugerido,))
            
            result = cursor.fetchone()
            
            # Caso 2: Grupo não encontrado em base_grupos_config
            if not result:
                print(f"  ⚠️  ID {parcela_id}: Grupo '{grupo_sugerido}' não encontrado em config")
                stats_grupo_nao_encontrado += 1
                continue
            
            tipo_gasto_novo, categoria_geral_nova = result
            
            # Caso 3: Já está correto (ambos os campos)
            if tipo_gasto_atual == tipo_gasto_novo and categoria_geral_atual == categoria_geral_nova:
                stats_sem_mudanca += 1
                continue
            
            # Caso 4: Precisa atualizar
            updates.append((tipo_gasto_novo, categoria_geral_nova, parcela_id))
            
            # Estatísticas de mudança
            mudanca_tipo = f"{tipo_gasto_atual} → {tipo_gasto_novo}" if tipo_gasto_atual != tipo_gasto_novo else f"{tipo_gasto_novo} (mantido)"
            mudanca_cat = f"{categoria_geral_atual or 'NULL'} → {categoria_geral_nova}" if categoria_geral_atual != categoria_geral_nova else f"{categoria_geral_nova} (mantido)"
            chave = f"{mudanca_tipo} | {mudanca_cat}"
            stats_mudancas[chave] = stats_mudancas.get(chave, 0) + 1
            
            # Mostrar primeiros 10 exemplos
            if len(updates) <= 10:
                print(f"  ✏️  ID {parcela_id}:")
                print(f"      Grupo: {grupo_sugerido}")
                print(f"      TipoGasto: {tipo_gasto_atual} → {tipo_gasto_novo}")
                print(f"      CategoriaGeral: {categoria_geral_atual or 'NULL'} → {categoria_geral_nova}")
        
        print()
        print("=" * 80)
        print("📊 RESUMO DA MIGRAÇÃO:")
        print("=" * 80)
        print()
        print(f"  📦 Total de registros: {len(parcelas)}")
        print(f"  ✅ Atualizações necessárias: {len(updates)}")
        print(f"  ➡️  Já corretos: {stats_sem_mudanca}")
        print(f"  ⚠️  Sem grupo sugerido: {stats_sem_grupo}")
        print(f"  ⚠️  Grupo não encontrado: {stats_grupo_nao_encontrado}")
        print()
        
        if stats_mudancas:
            print("📋 MUDANÇAS POR TIPO:")
            print("-" * 80)
            for mudanca, count in sorted(stats_mudancas.items(), key=lambda x: x[1], reverse=True):
                print(f"   {mudanca:60} {count:>4}x")
            print()
        
        # 4. Aplicar updates (se não for dry run)
        if updates:
            if not dry_run:
                print("💾 APLICANDO MUDANÇAS NO BANCO...")
                cursor.executemany(
                    "UPDATE base_parcelas SET tipo_gasto_sugerido = ?, categoria_geral_sugerida = ? WHERE id = ?",
                    updates
                )
                conn.commit()
                print("   ✅ Mudanças aplicadas com sucesso!")
                print()
                
                # Estatísticas DEPOIS
                print("📊 ESTATÍSTICAS APÓS MIGRAÇÃO:")
                print("-" * 80)
                stats_after = get_stats_before()
                for tipo, count in stats_after:
                    print(f"   {tipo:50} {count:>4} registros")
                print()
            else:
                print("⚠️  DRY RUN - Nenhuma mudança aplicada")
                print("   Para aplicar: execute com --apply")
                print()
        else:
            print("✅ Nenhuma atualização necessária - todos os registros já estão corretos!")
            print()
    
    except Exception as e:
        conn.rollback()
        print(f"❌ ERRO: {str(e)}")
        raise
    
    finally:
        conn.close()
    
    print("=" * 80)
    print("✅ MIGRAÇÃO CONCLUÍDA")
    print("=" * 80)


def main():
    """Executa migração com confirmação"""
    import sys
    
    # Verificar se foi passado --apply
    apply = '--apply' in sys.argv
    
    if not apply:
        # Dry run
        migrate_base_parcelas(dry_run=True)
        print()
        print("💡 Para aplicar as mudanças, execute:")
        print("   python migrate_fase6a_base_parcelas.py --apply")
    else:
        # Confirmação
        print("⚠️  ATENÇÃO: Esta operação irá modificar o banco de dados!")
        print()
        resposta = input("Deseja continuar? Digite 'SIM' para confirmar: ").strip()
        
        if resposta == 'SIM':
            migrate_base_parcelas(dry_run=False)
        else:
            print("❌ Operação cancelada pelo usuário")
            sys.exit(1)


if __name__ == '__main__':
    main()
