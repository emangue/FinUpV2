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
        # Verificar quais colunas existem primeiro
        cursor_sqlite.execute("PRAGMA table_info(generic_classification_rules)")
        colunas = [row[1] for row in cursor_sqlite.fetchall()]
        print(f"  Colunas SQLite: {', '.join(colunas)}")
        
        # Colunas do PRAGMA: id, nome_regra, descricao, keywords, grupo, subgrupo, tipo_gasto, prioridade, 
        # ativo, case_sensitive, match_completo, created_at, updated_at, created_by, total_matches, last_match_at
        cursor_sqlite.execute("""
            SELECT id, nome_regra, descricao, keywords, grupo, subgrupo, tipo_gasto, prioridade,
                   ativo, case_sensitive, match_completo, created_at, updated_at, created_by,
                   total_matches, last_match_at
            FROM generic_classification_rules ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        if not rows:
            print(f"  ⏭️  Tabela vazia, pulando...\n")
        else:
            cursor_pg.execute("TRUNCATE TABLE generic_classification_rules RESTART IDENTITY CASCADE")
            
            success_count = 0
            for row in rows:
                try:
                    cursor_pg.execute("""
                        INSERT INTO generic_classification_rules 
                        (id, nome_regra, descricao, keywords, grupo, subgrupo, tipo_gasto, prioridade,
                         ativo, case_sensitive, match_completo, created_at, updated_at, created_by,
                         total_matches, last_match_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                        bool(row[8]) if row[8] is not None else True,
                        bool(row[9]) if row[9] is not None else False,
                        bool(row[10]) if row[10] is not None else False,
                        row[11], row[12], row[13], row[14], row[15]
                    ))
                    success_count += 1
                    pg_conn.commit()  # Commit individual para evitar transaction aborted
                except Exception as e:
                    print(f"  ⚠️  Erro na regra {row[0]}: {e}")
                    pg_conn.rollback()
                    continue
            
            print(f"  ✅ {success_count}/{len(rows)} regras migradas\n")
        
        # 4. investimentos_cenarios
        print("📋 Corrigindo investimentos_cenarios...")
        # Verificar colunas do SQLite
        cursor_sqlite.execute("PRAGMA table_info(investimentos_cenarios)")
        colunas = [row[1] for row in cursor_sqlite.fetchall()]
        print(f"  Colunas SQLite: {', '.join(colunas)}")
        
        # Schema SQLite: id, user_id, nome_cenario, descricao, ativo, patrimonio_inicial, rendimento_mensal_pct, aporte_mensal, periodo_meses, created_at, updated_at
        # Schema PostgreSQL: id, user_id, nome_cenario, descricao, ativo, patrimonio_inicial, rendimento_mensal_pct, aporte_mensal, periodo_meses, created_at, updated_at
        cursor_sqlite.execute("""
            SELECT id, user_id, nome_cenario, descricao, ativo, patrimonio_inicial, 
                   rendimento_mensal_pct, aporte_mensal, periodo_meses, created_at, updated_at
            FROM investimentos_cenarios ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        if not rows:
            print(f"  ⏭️  Tabela vazia, pulando...\n")
        else:
            cursor_pg.execute("TRUNCATE TABLE investimentos_cenarios RESTART IDENTITY CASCADE")
            
            success_count = 0
            for row in rows:
                try:
                    cursor_pg.execute("""
                        INSERT INTO investimentos_cenarios 
                        (id, user_id, nome_cenario, descricao, ativo, patrimonio_inicial, 
                         rendimento_mensal_pct, aporte_mensal, periodo_meses, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row[0], row[1], row[2], row[3], 
                        bool(row[4]) if row[4] is not None else True,
                        row[5], row[6], row[7], row[8], row[9], row[10]
                    ))
                    success_count += 1
                    pg_conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Erro no cenário {row[0] if row else 'unknown'}: {e}")
                    print(f"     Row: {row}")
                    pg_conn.rollback()
                    continue
            
            print(f"  ✅ {success_count}/{len(rows)} cenários migrados\n")
        
        # 5. investimentos_portfolio
        print("📋 Corrigindo investimentos_portfolio...")
        # Verificar colunas SQLite
        cursor_sqlite.execute("PRAGMA table_info(investimentos_portfolio)")
        colunas = [row[1] for row in cursor_sqlite.fetchall()]
        print(f"  Colunas SQLite: {', '.join(colunas)}")
        
        # Schema PostgreSQL: id, user_id, balance_id, nome_produto, corretora, ano, anomes, tipo_investimento,
        #                   classe_ativo, emissor, percentual_cdi, data_aplicacao, data_vencimento,
        #                   quantidade, valor_unitario_inicial, valor_total_inicial, ativo, created_at, updated_at
        cursor_sqlite.execute("""
            SELECT id, user_id, balance_id, nome_produto, corretora, ano, anomes, tipo_investimento,
                   classe_ativo, emissor, percentual_cdi, data_aplicacao, data_vencimento,
                   quantidade, valor_unitario_inicial, valor_total_inicial, ativo, created_at, updated_at
            FROM investimentos_portfolio ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        if not rows:
            print(f"  ⏭️  Tabela vazia, pulando...\n")
        else:
            cursor_pg.execute("TRUNCATE TABLE investimentos_portfolio RESTART IDENTITY CASCADE")
            
            success_count = 0
            for row in rows:
                try:
                    cursor_pg.execute("""
                        INSERT INTO investimentos_portfolio 
                        (id, user_id, balance_id, nome_produto, corretora, ano, anomes, tipo_investimento,
                         classe_ativo, emissor, percentual_cdi, data_aplicacao, data_vencimento,
                         quantidade, valor_unitario_inicial, valor_total_inicial, ativo, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                        row[8], row[9], row[10], row[11], row[12],
                        row[13], row[14], row[15],
                        bool(row[16]) if row[16] is not None else True,
                        row[17], row[18]
                    ))
                    success_count += 1
                    pg_conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Erro no investimento {row[0] if row else 'unknown'}: {e}")
                    print(f"     Row: {row[:5]}...")
                    pg_conn.rollback()
                    continue
            
            print(f"  ✅ {success_count}/{len(rows)} investimentos migrados\n")
        
        # 6. investimentos_historico
        print("📋 Corrigindo investimentos_historico...")
        # Verificar colunas SQLite
        cursor_sqlite.execute("PRAGMA table_info(investimentos_historico)")
        colunas = [row[1] for row in cursor_sqlite.fetchall()]
        print(f"  Colunas SQLite: {', '.join(colunas)}")
        
        # Schema PostgreSQL: id, investimento_id, ano, mes, anomes, data_referencia,
        #                   quantidade, valor_unitario, valor_total, aporte_mes,
        #                   rendimento_mes, rendimento_acumulado, created_at, updated_at
        cursor_sqlite.execute("""
            SELECT id, investimento_id, ano, mes, anomes, data_referencia,
                   quantidade, valor_unitario, valor_total, aporte_mes,
                   rendimento_mes, rendimento_acumulado, created_at, updated_at
            FROM investimentos_historico ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        if not rows:
            print(f"  ⏭️  Tabela vazia, pulando...\n")
        else:
            cursor_pg.execute("TRUNCATE TABLE investimentos_historico RESTART IDENTITY CASCADE")
            
            success_count = 0
            for row in rows:
                try:
                    cursor_pg.execute("""
                        INSERT INTO investimentos_historico 
                        (id, investimento_id, ano, mes, anomes, data_referencia,
                         quantidade, valor_unitario, valor_total, aporte_mes,
                         rendimento_mes, rendimento_acumulado, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                          row[8], row[9], row[10], row[11], row[12], row[13]))
                    success_count += 1
                    pg_conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Erro no histórico {row[0] if row else 'unknown'}: {e}")
                    pg_conn.rollback()
                    continue
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} registros de histórico migrados\n")
        
        # 7. investimentos_aportes_extraordinarios
        print("📋 Corrigindo investimentos_aportes_extraordinarios...")
        # Verificar colunas SQLite
        cursor_sqlite.execute("PRAGMA table_info(investimentos_aportes_extraordinarios)")
        colunas = [row[1] for row in cursor_sqlite.fetchall()]
        print(f"  Colunas SQLite: {', '.join(colunas)}")
        
        # Schema PostgreSQL: id, cenario_id, mes_referencia, valor, descricao, created_at
        cursor_sqlite.execute("""
            SELECT id, cenario_id, mes_referencia, valor, descricao, created_at
            FROM investimentos_aportes_extraordinarios ORDER BY id
        """)
        rows = cursor_sqlite.fetchall()
        
        if not rows:
            print(f"  ⏭️  Tabela vazia, pulando...\n")
        else:
            cursor_pg.execute("TRUNCATE TABLE investimentos_aportes_extraordinarios RESTART IDENTITY CASCADE")
            
            success_count = 0
            for row in rows:
                try:
                    cursor_pg.execute("""
                        INSERT INTO investimentos_aportes_extraordinarios 
                        (id, cenario_id, mes_referencia, valor, descricao, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (row[0], row[1], row[2], row[3], row[4], row[5]))
                    success_count += 1
                    pg_conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Erro no aporte {row[0] if row else 'unknown'}: {e}")
                    pg_conn.rollback()
                    continue
            
            print(f"  ✅ {success_count}/{len(rows)} aportes migrados\n")
        
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
