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
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg2.connect(POSTGRES_DSN)
    pg_conn.autocommit = False
    
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    try:
        # 1. base_marcacoes - Mapeamento correto de colunas (COM ASPAS!)
        print("📋 Corrigindo base_marcacoes...")
        cursor_sqlite.execute("SELECT * FROM base_marcacoes")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE base_marcacoes RESTART IDENTITY CASCADE")
        
        for row in rows:
            # PostgreSQL precisa de aspas duplas para case-sensitive!
            cursor_pg.execute("""
                INSERT INTO base_marcacoes 
                (id, "GRUPO", "SUBGRUPO", "TipoGasto", "CategoriaGeral")
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row['id'], row['GRUPO'], row['SUBGRUPO'], row['TipoGasto'], row['CategoriaGeral']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} registros migrados\n")
        
        # 2. journal_entries - Migrar TODAS as 29 colunas do SQLite
        print("📋 Corrigindo journal_entries...")
        cursor_sqlite.execute("SELECT * FROM journal_entries")
        
        cursor_pg.execute("TRUNCATE TABLE journal_entries RESTART IDENTITY CASCADE")
        
        batch = []
        count = 0
        for row in cursor_sqlite:
            count += 1
            # SQLite tem 29 colunas (índices 0-28):
            # 0:id, 1:user_id, 2:Data, 3:Estabelecimento, 4:Valor, 5:ValorPositivo, 6:TipoTransacao,
            # 7:TipoGasto, 8:GRUPO, 9:SUBGRUPO, 10:IdTransacao, 11:IdParcela, 12:MesFatura, 13:Ano,
            # 14:arquivo_origem, 15:banco_origem, 16:tipodocumento, 17:origem_classificacao,
            # 18:IgnorarDashboard, 19:created_at, 20:NomeCartao, 21:CategoriaGeral,
            # 22:upload_history_id, 23:categoria_orcamento_id, 24:session_id, 25:Mes,
            # 26:EstabelecimentoBase, 27:parcela_atual, 28:TotalParcelas
            
            batch.append((
                row[0],   # id
                row[1],   # user_id
                row[2],   # Data
                row[3],   # Estabelecimento
                row[4],   # Valor
                row[5],   # ValorPositivo
                row[6],   # TipoTransacao
                row[7],   # TipoGasto
                row[8],   # GRUPO
                row[9],   # SUBGRUPO
                row[10],  # IdTransacao
                row[11],  # IdParcela
                row[12],  # MesFatura
                row[13],  # Ano
                row[14],  # arquivo_origem
                row[15],  # banco_origem
                row[16],  # tipodocumento
                row[17],  # origem_classificacao
                row[18],  # IgnorarDashboard
                row[19],  # created_at
                row[20],  # NomeCartao
                row[21],  # CategoriaGeral
                row[22],  # upload_history_id
                row[23],  # categoria_orcamento_id
                row[24],  # session_id
                row[25],  # Mes
                row[26],  # EstabelecimentoBase
                row[27],  # parcela_atual
                row[28],  # TotalParcelas
            ))
            
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
        
        # 3. generic_classification_rules - Converter integer para boolean
        print("📋 Corrigindo generic_classification_rules...")
        cursor_sqlite.execute("SELECT * FROM generic_classification_rules")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE generic_classification_rules RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO generic_classification_rules 
                (id, pattern, tipo_documento, categoria_geral, grupo, subgrupo, tipo_gasto, ordem,
                 ativo, aplicar_automatico, case_sensitive, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['id'], row['pattern'], row['tipo_documento'], row['categoria_geral'],
                row['grupo'], row['subgrupo'], row['tipo_gasto'], row['ordem'],
                bool(row['ativo']), bool(row['aplicar_automatico']),
                bool(row['case_sensitive']), row['created_at']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} regras migradas\n")
        
        # 4. investimentos_cenarios - Converter integer para boolean
        print("📋 Corrigindo investimentos_cenarios...")
        cursor_sqlite.execute("SELECT * FROM investimentos_cenarios")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_cenarios RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_cenarios 
                (id, user_id, nome, descricao, ativo, valor_inicial, rentabilidade_anual_esperada,
                 anos_projecao, aporte_mensal_estimado, data_criacao, data_atualizacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['id'], row['user_id'], row['nome'], row['descricao'],
                bool(row['ativo']), row['valor_inicial'], row['rentabilidade_anual_esperada'],
                row['anos_projecao'], row['aporte_mensal_estimado'],
                row['data_criacao'], row['data_atualizacao']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} cenários migrados\n")
        
        # 5. investimentos_portfolio - Converter integer para boolean
        print("📋 Corrigindo investimentos_portfolio...")
        cursor_sqlite.execute("SELECT * FROM investimentos_portfolio")
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
                row['id'], row['user_id'], row['nome_ativo'], row['tipo_ativo'],
                row['valor_atual'], row['quantidade'], row['preco_medio'],
                row['data_aquisicao'], row['data_venda'], row['rentabilidade'],
                row['valor_inicial'], row['valor_investido'],
                bool(row['ativo']), row['data_criacao'], row['data_atualizacao'],
                row['instituicao'], row['ticker'], row['categoria'],
                row['objetivo_alocacao'], row['notas']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} investimentos migrados\n")
        
        # 6. investimentos_historico - Depende de portfolio
        print("📋 Corrigindo investimentos_historico...")
        cursor_sqlite.execute("SELECT * FROM investimentos_historico")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_historico RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_historico 
                (id, investimento_id, data_registro, valor, quantidade, operacao, observacoes,
                 rentabilidade_periodo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['id'], row['investimento_id'], row['data_registro'], row['valor'],
                row['quantidade'], row['operacao'], row['observacoes'],
                row['rentabilidade_periodo'], row['data_criacao']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} registros de histórico migrados\n")
        
        # 7. investimentos_aportes_extraordinarios - Depende de cenarios
        print("📋 Corrigindo investimentos_aportes_extraordinarios...")
        cursor_sqlite.execute("SELECT * FROM investimentos_aportes_extraordinarios")
        rows = cursor_sqlite.fetchall()
        
        cursor_pg.execute("TRUNCATE TABLE investimentos_aportes_extraordinarios RESTART IDENTITY CASCADE")
        
        for row in rows:
            cursor_pg.execute("""
                INSERT INTO investimentos_aportes_extraordinarios 
                (id, cenario_id, data_prevista, valor, descricao, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row['id'], row['cenario_id'], row['data_prevista'], row['valor'],
                row['descricao'], row['data_criacao']
            ))
        
        pg_conn.commit()
        print(f"  ✅ {len(rows)} aportes migrados\n")
        
        # Resetar sequences
        print("🔄 Resetando sequences...")
        cursor_pg.execute("""
            SELECT setval('base_marcacoes_id_seq', COALESCE((SELECT MAX(id) FROM base_marcacoes), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('journal_entries_id_seq', COALESCE((SELECT MAX(id) FROM journal_entries), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('generic_classification_rules_id_seq', 
                         COALESCE((SELECT MAX(id) FROM generic_classification_rules), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('investimentos_cenarios_id_seq', 
                         COALESCE((SELECT MAX(id) FROM investimentos_cenarios), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('investimentos_portfolio_id_seq', 
                         COALESCE((SELECT MAX(id) FROM investimentos_portfolio), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('investimentos_historico_id_seq', 
                         COALESCE((SELECT MAX(id) FROM investimentos_historico), 1))
        """)
        cursor_pg.execute("""
            SELECT setval('investimentos_aportes_extraordinarios_id_seq', 
                         COALESCE((SELECT MAX(id) FROM investimentos_aportes_extraordinarios), 1))
        """)
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
        raise
    finally:
        cursor_sqlite.close()
        cursor_pg.close()
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_with_fixes()
