#!/usr/bin/env python3
"""
Script de Migração - Otimização de Colunas
Version: 1.0.0
Date: 2026-01-03

Executa migração completa do schema de journal_entries:
- Fase 1: Criar colunas novas
- Fase 2: Popular tipodocumento
- Fase 3: Merge origem_classificacao
- Fase 4: Padronizar banco_origem
- Fase 5: Renomear colunas
"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = 'app/financas.db'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def execute_query(cursor, query, description):
    """Executa query e reporta resultado"""
    try:
        log(f"Executando: {description}")
        cursor.execute(query)
        affected = cursor.rowcount
        log(f"  ✅ {description}: {affected} registros afetados")
        return True
    except Exception as e:
        log(f"  ❌ ERRO em {description}: {e}")
        return False

def main():
    log("=" * 80)
    log("INICIANDO MIGRAÇÃO - Otimização de Colunas")
    log("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # ===================================================================
        # FASE 1: CRIAR NOVAS COLUNAS
        # ===================================================================
        log("\n📋 FASE 1: Criar novas colunas")
        log("-" * 80)
        
        execute_query(cursor, 
            "ALTER TABLE journal_entries ADD COLUMN arquivo_origem TEXT",
            "Criar coluna arquivo_origem")
        
        execute_query(cursor,
            "ALTER TABLE journal_entries ADD COLUMN origem_classificacao VARCHAR(50)",
            "Criar coluna origem_classificacao")
        
        conn.commit()
        log("✅ Fase 1 completa")
        
        # ===================================================================
        # FASE 2: POPULAR TIPODOCUMENTO (CRÍTICO!)
        # ===================================================================
        log("\n📋 FASE 2: Popular tipodocumento via TipoTransacao")
        log("-" * 80)
        
        execute_query(cursor,
            """UPDATE journal_entries 
               SET tipodocumento = 'Cartão' 
               WHERE TipoTransacao = 'Cartão de Crédito'""",
            "Popular tipodocumento = 'Cartão'")
        
        execute_query(cursor,
            """UPDATE journal_entries 
               SET tipodocumento = 'Extrato' 
               WHERE TipoTransacao IN ('Receitas', 'Despesas')""",
            "Popular tipodocumento = 'Extrato'")
        
        conn.commit()
        log("✅ Fase 2 completa - tipodocumento populado!")
        
        # ===================================================================
        # FASE 3: MERGE ORIGEM_CLASSIFICACAO
        # ===================================================================
        log("\n📋 FASE 3: Merge MarcacaoIA + forma_classificacao")
        log("-" * 80)
        
        # 3.1 Base Padrões
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Automática - Base Padrões'
               WHERE MarcacaoIA = 'Base_Padroes' 
                 AND (forma_classificacao IS NULL OR forma_classificacao LIKE 'Automática%')""",
            "Classificar Base Padrões")
        
        # 3.2 Histórico
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Automática - Histórico'
               WHERE MarcacaoIA = 'Historico' 
                 AND (forma_classificacao IS NULL OR forma_classificacao LIKE 'Automática%')""",
            "Classificar Histórico")
        
        # 3.3 Parcela
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Automática - Parcela'
               WHERE MarcacaoIA = 'Parcela_Fatura'""",
            "Classificar Parcela")
        
        # 3.4 Palavras-chave
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Automática - Palavras-chave'
               WHERE MarcacaoIA = 'Palavras_Chave'""",
            "Classificar Palavras-chave")
        
        # 3.5 Fatura
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Automática - Fatura'
               WHERE MarcacaoIA = 'Fatura'""",
            "Classificar Fatura")
        
        # 3.6 Semi-Automática (foi automática mas editada)
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Semi-Automática'
               WHERE MarcacaoIA IS NOT NULL 
                 AND MarcacaoIA != 'Manual'
                 AND MarcacaoIA != 'Manual (Lote)'
                 AND forma_classificacao LIKE 'Semi-Automática%'""",
            "Classificar Semi-Automática")
        
        # 3.7 Manual Lote
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Manual - Lote'
               WHERE MarcacaoIA = 'Manual (Lote)'""",
            "Classificar Manual Lote")
        
        # 3.8 Manual
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Manual'
               WHERE (MarcacaoIA = 'Manual' OR forma_classificacao LIKE 'Manual%')
                 AND origem_classificacao IS NULL""",
            "Classificar Manual")
        
        # 3.9 Ignorada
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Ignorada'
               WHERE MarcacaoIA = 'Ignorada' OR forma_classificacao = 'Ignorada'""",
            "Classificar Ignorada")
        
        # 3.10 Não Classificada (resto)
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem_classificacao = 'Não Classificada'
               WHERE origem_classificacao IS NULL""",
            "Classificar Não Classificada")
        
        conn.commit()
        log("✅ Fase 3 completa - origem_classificacao populada!")
        
        # ===================================================================
        # FASE 4: POPULAR arquivo_origem E PADRONIZAR banco_origem
        # ===================================================================
        log("\n📋 FASE 4: Popular arquivo_origem e padronizar banco_origem")
        log("-" * 80)
        
        # 4.1 arquivo_origem com nome de arquivos
        execute_query(cursor,
            """UPDATE journal_entries 
               SET arquivo_origem = origem 
               WHERE origem LIKE '%-%' OR origem LIKE '%.%'""",
            "Popular arquivo_origem com nomes de arquivos")
        
        # 4.2 arquivo_origem = 'dado_historico' para resto
        execute_query(cursor,
            """UPDATE journal_entries 
               SET arquivo_origem = 'dado_historico'
               WHERE arquivo_origem IS NULL""",
            "Popular arquivo_origem = 'dado_historico'")
        
        # 4.3 Padronizar Itaú
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem = 'Itaú'
               WHERE origem IN (
                   'Itau Person', 'Itaú Person', 'ITAU', 'itau',
                   'Extrato - extrato_itau.xls',
                   'Fatura - fatura_itau-202508.csv',
                   'Fatura - fatura_itau-202509.csv',
                   'Fatura - fatura_itau-202510.csv',
                   'Fatura - fatura_itau-202511.csv',
                   'Fatura - fatura_itau-202512.csv'
               )""",
            "Padronizar banco_origem = 'Itaú'")
        
        # 4.4 Padronizar Mercado Pago
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem = 'Mercado Pago'
               WHERE origem LIKE '%Mercado Pago%'""",
            "Padronizar banco_origem = 'Mercado Pago'")
        
        # 4.5 Padronizar BTG
        execute_query(cursor,
            """UPDATE journal_entries 
               SET origem = 'BTG'
               WHERE origem LIKE '%BTG%'""",
            "Padronizar banco_origem = 'BTG'")
        
        conn.commit()
        log("✅ Fase 4 completa - arquivo_origem e banco_origem padronizados!")
        
        # ===================================================================
        # FASE 5: RENOMEAR COLUNAS
        # ===================================================================
        log("\n📋 FASE 5: Renomear colunas")
        log("-" * 80)
        
        # SQLite não suporta ALTER TABLE RENAME COLUMN diretamente em versões antigas
        # Vamos verificar a versão primeiro
        cursor.execute("SELECT sqlite_version()")
        sqlite_version = cursor.fetchone()[0]
        log(f"SQLite version: {sqlite_version}")
        
        # Renomear origem → banco_origem
        try:
            execute_query(cursor,
                "ALTER TABLE journal_entries RENAME COLUMN origem TO banco_origem",
                "Renomear origem → banco_origem")
        except Exception as e:
            log(f"  ⚠️  Aviso: Não foi possível renomear coluna (SQLite antigo): {e}")
            log(f"  ℹ️  Solução: Criar coluna nova e copiar dados")
            execute_query(cursor,
                "ALTER TABLE journal_entries ADD COLUMN banco_origem TEXT",
                "Criar coluna banco_origem")
            execute_query(cursor,
                "UPDATE journal_entries SET banco_origem = origem",
                "Copiar dados origem → banco_origem")
        
        # Renomear DT_Fatura → MesFatura
        try:
            execute_query(cursor,
                "ALTER TABLE journal_entries RENAME COLUMN DT_Fatura TO MesFatura",
                "Renomear DT_Fatura → MesFatura")
        except Exception as e:
            log(f"  ⚠️  Aviso: Não foi possível renomear coluna: {e}")
            log(f"  ℹ️  Solução: Criar coluna nova e copiar dados")
            execute_query(cursor,
                "ALTER TABLE journal_entries ADD COLUMN MesFatura TEXT",
                "Criar coluna MesFatura")
            execute_query(cursor,
                "UPDATE journal_entries SET MesFatura = DT_Fatura",
                "Copiar dados DT_Fatura → MesFatura")
        
        conn.commit()
        log("✅ Fase 5 completa - colunas renomeadas!")
        
        # ===================================================================
        # VALIDAÇÃO FINAL
        # ===================================================================
        log("\n📊 VALIDAÇÃO FINAL")
        log("=" * 80)
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total = cursor.fetchone()[0]
        log(f"Total de registros: {total}")
        
        # Verificar tipodocumento
        cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE tipodocumento IS NULL")
        null_tipodoc = cursor.fetchone()[0]
        log(f"tipodocumento NULL: {null_tipodoc} ({100*null_tipodoc/total:.1f}%)")
        
        cursor.execute("SELECT tipodocumento, COUNT(*) FROM journal_entries GROUP BY tipodocumento")
        log("Distribuição tipodocumento:")
        for tipo, count in cursor.fetchall():
            log(f"  - {tipo}: {count} ({100*count/total:.1f}%)")
        
        # Verificar origem_classificacao
        cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE origem_classificacao IS NULL")
        null_origem_class = cursor.fetchone()[0]
        log(f"\norigem_classificacao NULL: {null_origem_class}")
        
        cursor.execute("SELECT origem_classificacao, COUNT(*) FROM journal_entries GROUP BY origem_classificacao ORDER BY COUNT(*) DESC")
        log("Distribuição origem_classificacao:")
        for origem, count in cursor.fetchall():
            log(f"  - {origem}: {count} ({100*count/total:.1f}%)")
        
        # Verificar arquivo_origem
        cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE arquivo_origem IS NULL")
        null_arquivo = cursor.fetchone()[0]
        log(f"\narquivo_origem NULL: {null_arquivo}")
        
        cursor.execute("SELECT arquivo_origem, COUNT(*) FROM journal_entries GROUP BY arquivo_origem ORDER BY COUNT(*) DESC LIMIT 10")
        log("Top 10 arquivo_origem:")
        for arquivo, count in cursor.fetchall():
            log(f"  - {arquivo}: {count}")
        
        # Verificar banco_origem
        cursor.execute("SELECT DISTINCT banco_origem FROM journal_entries ORDER BY banco_origem")
        bancos = [row[0] for row in cursor.fetchall()]
        log(f"\nBancos únicos ({len(bancos)}): {', '.join(bancos)}")
        
        log("\n" + "=" * 80)
        log("✅ MIGRAÇÃO COMPLETA COM SUCESSO!")
        log("=" * 80)
        
        return True
        
    except Exception as e:
        log(f"\n❌ ERRO DURANTE MIGRAÇÃO: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
