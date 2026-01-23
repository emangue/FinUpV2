#!/usr/bin/env python3
"""
Script para corrigir problemas de schema entre SQLite e PostgreSQL
Resolve questões de case-sensitivity e tipos de dados
"""
import sqlite3
import psycopg2
import psycopg2.extras
from pathlib import Path

# Configurações
SQLITE_PATH = Path("/var/www/finup/app_dev/backend/database/financas_dev.db")
POSTGRES_DSN = "postgresql://finup_user:FinUp2026SecurePass@localhost:5432/finup_db"

def migrate_with_fixes():
    """Migra tabelas com correções de schema"""
    print("\n🔧 Corrigindo problemas de migração...\n")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    pg_conn = psycopg2.connect(POSTGRES_DSN)
    pg_conn.autocommit = False
    
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    try:
        # 1. base_marcacoes
        print("📋 Corrigindo base_marcacoes...")
        cursor_sqlite.execute("SELECT id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral FROM base_marcacoes ORDER BY id")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE base_marcacoes RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO base_marcacoes 
                (id, "GRUPO", "SUBGRUPO", "TipoGasto", "CategoriaGeral")
                VALUES (%s, %s, %s, %s, %s)
            """, (row[0], row[1], row[2], row[3], row[4]))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} registros migrados\n")
        
        # 2. journal_entries - TODAS as 29 colunas
        print("📋 Corrigindo journal_entries...")
        cursor_sqlite.execute("""
            SELECT id, user_id, Data, Estabelecimento, Valor, ValorPositivo, TipoTransacao,
                   TipoGasto, GRUPO, SUBGRUPO, IdTransacao, IdParcela, MesFatura, Ano,
                   arquivo_origem, banco_origem, tipodocumento, origem_classificacao,
                   IgnorarDashboard, created_at, NomeCartao, CategoriaGeral, upload_history_id,
                   categoria_orcamento_id, session_id, Mes, EstabelecimentoBase, parcela_atual, TotalParcelas
            FROM journal_entries ORDER BY id
        """)
        
        cursor_pg.execute("TRUNCATE TABLE journal_entries RESTART IDENTITY CASCADE")
        
        batch = []
        count = 0
        for row in cursor_sqlite:
            count += 1
            batch.append(row)
            
            if len(batch) >= 500:
                psycopg2.extras.execute_batch(cursor_pg, """
                    INSERT INTO journal_entries 
                    (id, user_id, "Data", "Estabelecimento", "Valor", "ValorPositivo", "TipoTransacao",
                     "TipoGasto", "GRUPO", "SUBGRUPO", "IdTransacao", "IdParcela", "MesFatura", "Ano",
                     arquivo_origem, banco_origem, tipodocumento, origem_classificacao,
                     "IgnorarDashboard", created_at, "NomeCartao", "CategoriaGeral", upload_history_id,
                     categoria_orcamento_id, session_id, "Mes", "EstabelecimentoBase", parcela_atual, "TotalParcelas")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, batch, page_size=500)
                pg_conn.commit()
                print(f"    → {count} registros...", end='\r')
                batch = []
        
        if batch:
            psycopg2.extras.execute_batch(cursor_pg, """
                INSERT INTO journal_entries 
                (id, user_id, "Data", "Estabelecimento", "Valor", "ValorPositivo", "TipoTransacao",
                 "TipoGasto", "GRUPO", "SUBGRUPO", "IdTransacao", "IdParcela", "MesFatura", "Ano",
                 arquivo_origem, banco_origem, tipodocumento, origem_classificacao,
                 "IgnorarDashboard", created_at, "NomeCartao", "CategoriaGeral", upload_history_id,
                 categoria_orcamento_id, session_id, "Mes", "EstabelecimentoBase", parcela_atual, "TotalParcelas")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, batch, page_size=500)
            pg_conn.commit()
        
        print(f"\n  ✅ {count} transações migradas\n")
        
        # 3. generic_classification_rules
        print("📋 Corrigindo generic_classification_rules...")
        cursor_sqlite.execute("""
            SELECT id, pattern, tipo_documento, categoria_geral, grupo, subgrupo, tipo_gasto, 
                   ordem, ativo, aplicar_automatico, case_sensitive, created_at
            FROM generic_classification_rules ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE generic_classification_rules RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO generic_classification_rules 
                (id, pattern, tipo_documento, categoria_geral, grupo, subgrupo, tipo_gasto, ordem,
                 ativo, aplicar_automatico, case_sensitive, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                bool(row[8]), bool(row[9]), bool(row[10]), row[11]
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} regras migradas\n")
        
        # 4. investimentos_cenarios
        print("📋 Corrigindo investimentos_cenarios...")
        cursor_sqlite.execute("""
            SELECT id, user_id, nome, descricao, ativo, valor_inicial, rentabilidade_anual_esperada,
                   anos_projecao, aporte_mensal_estimado, data_criacao, data_atualizacao
            FROM investimentos_cenarios ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_cenarios RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_cenarios 
                (id, user_id, nome, descricao, ativo, valor_inicial, rentabilidade_anual_esperada,
                 anos_projecao, aporte_mensal_estimado, data_criacao, data_atualizacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row[0], row[1], row[2], row[3], bool(row[4]), row[5], row[6],
                row[7], row[8], row[9], row[10]
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} cenários migrados\n")
        
        # 5. investimentos_portfolio
        print("📋 Corrigindo investimentos_portfolio...")
        cursor_sqlite.execute("""
            SELECT id, user_id, nome_ativo, tipo_ativo, valor_atual, quantidade, preco_medio,
                   data_aquisicao, data_venda, rentabilidade, valor_inicial, valor_investido,
                   ativo, data_criacao, data_atualizacao, instituicao, ticker, categoria,
                   objetivo_alocacao, notas
            FROM investimentos_portfolio ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_portfolio RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_portfolio 
                (id, user_id, nome_ativo, tipo_ativo, valor_atual, quantidade, preco_medio,
                 data_aquisicao, data_venda, rentabilidade, valor_inicial, valor_investido,
                 ativo, data_criacao, data_atualizacao, instituicao, ticker, categoria,
                 objetivo_alocacao, notas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11],
                bool(row[12]), row[13], row[14], row[15], row[16], row[17],
                row[18], row[19]
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} investimentos migrados\n")
        
        # 6. investimentos_historico
        print("📋 Corrigindo investimentos_historico...")
        cursor_sqlite.execute("""
            SELECT id, investimento_id, data_registro, valor, quantidade, operacao, observacoes,
                   rentabilidade_periodo, data_criacao
            FROM investimentos_historico ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_historico RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_historico 
                (id, investimento_id, data_registro, valor, quantidade, operacao, observacoes,
                 rentabilidade_periodo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} registros de histórico migrados\n")
        
        # 7. investimentos_aportes_extraordinarios
        print("📋 Corrigindo investimentos_aportes_extraordinarios...")
        cursor_sqlite.execute("""
            SELECT id, cenario_id, data_prevista, valor, descricao, data_criacao
            FROM investimentos_aportes_extraordinarios ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_aportes_extraordinarios RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_aportes_extraordinarios 
                (id, cenario_id, data_prevista, valor, descricao, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row[0], row[1], row[2], row[3], row[4], row[5]))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} aportes migrados\n")
        
        # Resetar sequences
        print("🔄 Resetando sequences...")
        sequences = [
            ('base_marcacoes_id_seq', 'base_marcacoes'),
            ('journal_entries_id_seq', 'journal_entries'),
            ('generic_classification_rules_id_seq', 'generic_classification_rules'),
            ('investimentos_cenarios_id_seq', 'investimentos_cenarios'),
            ('investimentos_portfolio_id_seq', 'investimentos_portfolio'),
            ('investimentos_historico_id_seq', 'investimentos_historico'),
            ('investimentos_aportes_extraordinarios_id_seq', 'investimentos_aportes_extraordinarios')
        ]
        
        for seq, table in sequences:
            cursor_pg.execute(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table}), 1))")
        
        pg_conn.commit()
        print("  ✅ Sequences resetadas\n")
        
        # Validação final
        print("🔍 Validando...")
        tables = [
            'base_marcacoes', 'journal_entries', 'generic_classification_rules',
            'investimentos_cenarios', 'investimentos_portfolio',
            'investimentos_historico', 'investimentos_aportes_extraordinarios'
        ]
        
        for table in tables:
            cursor_sqlite.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = cursor_sqlite.fetchone()[0]
            
            cursor_pg.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = cursor_pg.fetchone()[0]
            
            status = "✅" if sqlite_count == pg_count else "❌"
            print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
        
        print("\n✅ Correção concluída com sucesso!\n")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor_sqlite.close()
        cursor_pg.close()
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_with_fixes()
