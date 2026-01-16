#!/usr/bin/env python3
"""
FASE 3: MIGRAÇÃO JOURNAL ENTRIES - TipoGasto 22→5 valores
===========================================================

⚠️  SCRIPT CRÍTICO - Modifica 4.153+ transações no banco de dados!

Este script atualiza a coluna TipoGasto em journal_entries de 22 valores
para 5 valores (Fixo, Ajustável, Investimentos, Transferência, Receita)
baseado no mapeamento GRUPO → base_grupos_config.

BACKUP AUTOMÁTICO:
- Cria backup antes de qualquer modificação
- Arquivo: financas_dev.db.backup_antes_fase3_YYYYMMDD_HHMMSS

PROCESSO:
1. Valida dependências (base_grupos_config existe)
2. Cria backup do banco
3. Mostra preview da migração (quantas linhas de cada tipo)
4. Aguarda confirmação do usuário
5. Executa migração
6. Valida resultado (deve ter apenas 5 valores)

ROLLBACK (se necessário):
    cp financas_dev.db.backup_antes_fase3_YYYYMMDD_HHMMSS financas_dev.db
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def criar_backup():
    """Cria backup do banco antes da migração"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"financas_dev.db.backup_antes_fase3_{timestamp}"
    
    print(f"🔒 Criando backup: {backup_path.name}")
    shutil.copy2(DB_PATH, backup_path)
    
    backup_size = backup_path.stat().st_size / 1024 / 1024
    print(f"   ✅ Backup criado: {backup_size:.2f} MB")
    
    return backup_path


def validar_dependencias(conn):
    """Valida que base_grupos_config existe"""
    cursor = conn.cursor()
    
    print("🔍 Validando dependências...")
    
    # 1. Verificar se base_grupos_config existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='base_grupos_config'
    """)
    
    if not cursor.fetchone():
        print("   ❌ ERRO: Tabela base_grupos_config não existe!")
        print("   Execute primeiro: python scripts/migrate_create_base_grupos_config.py")
        return False
    
    # 2. Verificar se tem 17 grupos
    cursor.execute("SELECT COUNT(*) FROM base_grupos_config")
    total_grupos = cursor.fetchone()[0]
    
    if total_grupos != 17:
        print(f"   ⚠️  AVISO: base_grupos_config tem {total_grupos} grupos (esperado: 17)")
    else:
        print(f"   ✅ base_grupos_config OK ({total_grupos} grupos)")
    
    # 3. Verificar se journal_entries existe
    cursor.execute("""
        SELECT COUNT(*) FROM journal_entries
    """)
    total_entries = cursor.fetchone()[0]
    print(f"   ✅ journal_entries OK ({total_entries:,} transações)")
    
    return True


def preview_migracao(conn):
    """Mostra preview da migração"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 PREVIEW DA MIGRAÇÃO")
    print("="*80)
    
    # 1. TipoGasto atual (antes)
    print("\n1️⃣  VALORES ATUAIS DE TipoGasto (22 valores):")
    print("-" * 80)
    
    cursor.execute("""
        SELECT TipoGasto, COUNT(*) as total
        FROM journal_entries
        GROUP BY TipoGasto
        ORDER BY total DESC
    """)
    
    valores_antes = []
    total_antes = 0
    for tipo, count in cursor.fetchall():
        valores_antes.append(tipo)
        total_antes += count
        print(f"   {tipo:30s} → {count:5,} transações")
    
    print(f"\n   📊 Total de valores únicos: {len(valores_antes)}")
    print(f"   📊 Total de transações: {total_antes:,}")
    
    # 2. Mapeamento GRUPO → TipoGasto novo
    print("\n2️⃣  MAPEAMENTO GRUPO → NOVO TipoGasto:")
    print("-" * 80)
    
    cursor.execute("""
        SELECT 
            j.GRUPO,
            j.TipoGasto as tipo_atual,
            c.tipo_gasto_padrao as tipo_novo,
            COUNT(*) as total
        FROM journal_entries j
        LEFT JOIN base_grupos_config c ON j.GRUPO = c.nome_grupo
        GROUP BY j.GRUPO, j.TipoGasto, c.tipo_gasto_padrao
        ORDER BY total DESC
    """)
    
    grupos_sem_config = []
    preview_data = []
    
    for grupo, tipo_atual, tipo_novo, count in cursor.fetchall():
        preview_data.append((grupo, tipo_atual, tipo_novo, count))
        
        # Formatar valores None
        grupo_str = grupo if grupo else 'NULL'
        tipo_atual_str = tipo_atual if tipo_atual else 'NULL'
        tipo_novo_str = tipo_novo if tipo_novo else 'NULL'
        
        if tipo_novo is None:
            grupos_sem_config.append((grupo, count))
            print(f"   ⚠️  {grupo_str:20s} ({tipo_atual_str:15s}) → NULL ({count:5,} transações)")
        elif tipo_atual != tipo_novo:
            print(f"   🔄 {grupo_str:20s} ({tipo_atual_str:15s}) → {tipo_novo_str:15s} ({count:5,} transações)")
        else:
            print(f"   ✅ {grupo_str:20s} ({tipo_atual_str:15s}) → {tipo_novo_str:15s} ({count:5,} transações) [sem mudança]")
    
    # 3. Valores após migração
    print("\n3️⃣  VALORES APÓS MIGRAÇÃO (5 valores esperados):")
    print("-" * 80)
    
    cursor.execute("""
        SELECT 
            c.tipo_gasto_padrao as tipo_novo,
            COUNT(*) as total
        FROM journal_entries j
        LEFT JOIN base_grupos_config c ON j.GRUPO = c.nome_grupo
        GROUP BY c.tipo_gasto_padrao
        ORDER BY total DESC
    """)
    
    valores_depois = {}
    total_depois = 0
    for tipo_novo, count in cursor.fetchall():
        valores_depois[tipo_novo] = count
        total_depois += count
        
        if tipo_novo is None:
            print(f"   ⚠️  NULL (sem grupo config)      → {count:5,} transações")
        else:
            print(f"   ✅ {tipo_novo:30s} → {count:5,} transações")
    
    print(f"\n   📊 Total de valores únicos: {len([k for k in valores_depois.keys() if k is not None])}")
    print(f"   📊 Total de transações: {total_depois:,}")
    
    # 4. Avisos
    print("\n4️⃣  VALIDAÇÕES:")
    print("-" * 80)
    
    if grupos_sem_config:
        print(f"   ⚠️  {len(grupos_sem_config)} grupos SEM configuração em base_grupos_config:")
        for grupo, count in grupos_sem_config:
            print(f"       - {grupo} ({count:,} transações)")
        print("   ⚠️  Essas transações ficarão com TipoGasto = NULL")
        return False, grupos_sem_config
    else:
        print("   ✅ Todos os grupos têm configuração")
    
    if None in valores_depois:
        print(f"   ⚠️  {valores_depois[None]:,} transações ficarão com TipoGasto NULL")
        return False, []
    else:
        print("   ✅ Nenhuma transação ficará com NULL")
    
    if len([k for k in valores_depois.keys() if k is not None]) != 5:
        print(f"   ⚠️  Valores únicos após migração: {len([k for k in valores_depois.keys() if k is not None])} (esperado: 5)")
    else:
        print("   ✅ Valores únicos após migração: 5 (correto)")
    
    return True, []


def executar_migracao(conn):
    """Executa a migração do TipoGasto"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🚀 EXECUTANDO MIGRAÇÃO")
    print("="*80)
    
    # Update TipoGasto baseado em base_grupos_config
    print("\n1️⃣  Atualizando TipoGasto em journal_entries...")
    
    cursor.execute("""
        UPDATE journal_entries
        SET TipoGasto = (
            SELECT tipo_gasto_padrao 
            FROM base_grupos_config 
            WHERE nome_grupo = journal_entries.GRUPO
        )
        WHERE EXISTS (
            SELECT 1 
            FROM base_grupos_config 
            WHERE nome_grupo = journal_entries.GRUPO
        )
    """)
    
    linhas_atualizadas = cursor.rowcount
    print(f"   ✅ {linhas_atualizadas:,} linhas atualizadas")
    
    # Commit
    conn.commit()
    print("   ✅ Commit realizado")
    
    return linhas_atualizadas


def validar_resultado(conn):
    """Valida que apenas 5 valores existem após migração"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("✅ VALIDAÇÃO DO RESULTADO")
    print("="*80)
    
    # 1. Valores únicos
    cursor.execute("""
        SELECT TipoGasto, COUNT(*) as total
        FROM journal_entries
        WHERE TipoGasto IS NOT NULL
        GROUP BY TipoGasto
        ORDER BY total DESC
    """)
    
    valores_finais = {}
    for tipo, count in cursor.fetchall():
        valores_finais[tipo] = count
    
    print("\n1️⃣  VALORES FINAIS DE TipoGasto:")
    print("-" * 80)
    for tipo, count in valores_finais.items():
        print(f"   ✅ {tipo:30s} → {count:5,} transações")
    
    # 2. Verificar NULLs
    cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE TipoGasto IS NULL")
    nulls = cursor.fetchone()[0]
    
    if nulls > 0:
        print(f"\n   ⚠️  {nulls:,} transações com TipoGasto NULL")
    else:
        print("\n   ✅ Nenhuma transação com NULL")
    
    # 3. Total
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    total = cursor.fetchone()[0]
    print(f"   ✅ Total de transações: {total:,}")
    
    # 4. Validação final
    print("\n2️⃣  VALIDAÇÕES FINAIS:")
    print("-" * 80)
    
    sucesso = True
    
    if len(valores_finais) == 5:
        print("   ✅ 5 valores únicos (correto)")
    else:
        print(f"   ❌ {len(valores_finais)} valores únicos (esperado: 5)")
        sucesso = False
    
    valores_esperados = {'Fixo', 'Ajustável', 'Investimentos', 'Transferência', 'Receita'}
    valores_encontrados = set(valores_finais.keys())
    
    if valores_encontrados == valores_esperados:
        print("   ✅ Valores corretos: Fixo, Ajustável, Investimentos, Transferência, Receita")
    else:
        faltando = valores_esperados - valores_encontrados
        extras = valores_encontrados - valores_esperados
        if faltando:
            print(f"   ⚠️  Valores faltando: {faltando}")
        if extras:
            print(f"   ⚠️  Valores extras: {extras}")
        sucesso = False
    
    if nulls == 0:
        print("   ✅ Sem valores NULL")
    else:
        print(f"   ⚠️  {nulls:,} valores NULL")
        sucesso = False
    
    return sucesso


def main():
    """Executa a migração completa"""
    print("="*80)
    print("FASE 3: MIGRAÇÃO JOURNAL ENTRIES - TipoGasto 22→5")
    print("="*80)
    print(f"Banco: {DB_PATH}")
    print()
    
    if not DB_PATH.exists():
        print(f"❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return 1
    
    # Conectar
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 1. Validar dependências
        if not validar_dependencias(conn):
            return 1
        
        # 2. Preview
        valido, grupos_sem_config = preview_migracao(conn)
        
        if not valido:
            print("\n" + "="*80)
            print("⚠️  AVISOS ENCONTRADOS NO PREVIEW")
            print("="*80)
            
            if grupos_sem_config:
                print("\nAlguns grupos não têm configuração em base_grupos_config.")
                print("Essas transações ficarão com TipoGasto = NULL.")
                print("\nOpções:")
                print("1. Adicionar grupos faltantes em base_grupos_config")
                print("2. Continuar mesmo assim (não recomendado)")
                
                resposta = input("\nContinuar mesmo assim? (sim/não): ").strip().lower()
                if resposta not in ['sim', 's', 'yes', 'y']:
                    print("❌ Migração cancelada pelo usuário")
                    return 1
        
        # 3. Confirmação
        print("\n" + "="*80)
        print("⚠️  CONFIRMAÇÃO FINAL")
        print("="*80)
        print("Esta operação vai modificar TODAS as transações do banco.")
        print("Um backup será criado automaticamente antes da execução.")
        print()
        
        resposta = input("Confirma execução da migração? (sim/não): ").strip().lower()
        
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Migração cancelada pelo usuário")
            return 1
        
        # 4. Criar backup
        backup_path = criar_backup()
        
        # 5. Executar migração
        linhas_atualizadas = executar_migracao(conn)
        
        # 6. Validar resultado
        sucesso = validar_resultado(conn)
        
        # 7. Resultado final
        print("\n" + "="*80)
        if sucesso:
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print("⚠️  MIGRAÇÃO CONCLUÍDA COM AVISOS")
        print("="*80)
        
        print(f"\n📊 Resumo:")
        print(f"   - Linhas atualizadas: {linhas_atualizadas:,}")
        print(f"   - Backup criado: {backup_path.name}")
        print(f"   - Valores únicos: 5 (Fixo, Ajustável, Investimentos, Transferência, Receita)")
        
        print("\n⏭️  PRÓXIMO PASSO: Fase 4 - Migração Budget Planning")
        print("   Script: migrate_budget_planning_tipo_gasto.py")
        
        if not sucesso:
            print("\n⚠️  ROLLBACK (se necessário):")
            print(f"   cp {backup_path.name} financas_dev.db")
        
        return 0 if sucesso else 1
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
