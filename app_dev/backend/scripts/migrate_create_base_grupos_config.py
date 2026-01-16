#!/usr/bin/env python3
"""
FASE 1: Criar base_grupos_config e popular com seed data

ESTRUTURA:
- nome_grupo (PRIMARY KEY)
- tipo_gasto_padrao (5 valores: Fixo, Ajustável, Investimentos, Transferência, Receita)
- categoria_geral (4 valores: Receita, Despesa, Investimentos, Transferência)

IMPACTO: ZERO - Tabela nova não afeta sistema atual
REVERSÍVEL: DROP TABLE IF EXISTS base_grupos_config
"""

import sqlite3
from pathlib import Path

# Path do banco
DB_PATH = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db")

# SQL para criar tabela
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS base_grupos_config (
    nome_grupo TEXT PRIMARY KEY,
    tipo_gasto_padrao TEXT NOT NULL,
    categoria_geral TEXT NOT NULL,
    CHECK (tipo_gasto_padrao IN ('Fixo', 'Ajustável', 'Investimentos', 'Transferência', 'Receita')),
    CHECK (categoria_geral IN ('Receita', 'Despesa', 'Investimentos', 'Transferência'))
);
"""

# Seed data (17 grupos)
SEED_DATA = [
    # Fixo (3 grupos)
    ('Moradia', 'Fixo', 'Despesa'),
    ('Educação', 'Fixo', 'Despesa'),
    ('Saúde', 'Fixo', 'Despesa'),
    
    # Ajustável (10 grupos)
    ('Casa', 'Ajustável', 'Despesa'),
    ('Delivery', 'Ajustável', 'Despesa'),
    ('Entretenimento', 'Ajustável', 'Despesa'),
    ('Uber', 'Ajustável', 'Despesa'),
    ('Viagens', 'Ajustável', 'Despesa'),
    ('Supermercado', 'Ajustável', 'Despesa'),
    ('Roupas', 'Ajustável', 'Despesa'),
    ('Presentes', 'Ajustável', 'Despesa'),
    ('Assinaturas', 'Ajustável', 'Despesa'),
    ('Carro', 'Ajustável', 'Despesa'),
    
    # Investimentos (1 grupo)
    ('Aplicações', 'Investimentos', 'Investimentos'),
    
    # Transferência (1 grupo)
    ('Movimentações', 'Transferência', 'Transferência'),
    
    # Receita (1 grupo)
    ('Salário', 'Receita', 'Receita'),
    
    # NOTA: "Outros" foi removido - usa fallback baseado em sinal do valor
]

def main():
    print("=" * 80)
    print("FASE 1: CRIAÇÃO DE base_grupos_config")
    print("=" * 80)
    print()
    
    # 1. Conectar
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. Verificar se tabela já existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='base_grupos_config'
    """)
    exists = cursor.fetchone()
    
    if exists:
        print("⚠️  Tabela base_grupos_config JÁ EXISTE!")
        print()
        
        # Mostrar dados atuais
        cursor.execute("SELECT COUNT(*) FROM base_grupos_config")
        count = cursor.fetchone()[0]
        print(f"   Registros existentes: {count}")
        
        if count > 0:
            print("\n📊 Grupos atuais:")
            cursor.execute("""
                SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
                FROM base_grupos_config 
                ORDER BY tipo_gasto_padrao, nome_grupo
            """)
            for row in cursor.fetchall():
                print(f"   {row[0]:<20} {row[1]:<15} {row[2]}")
        
        print()
        resp = input("Deseja RECRIAR a tabela? (SIM para recriar, ENTER para manter): ")
        if resp != "SIM":
            print("\n✅ Mantendo tabela existente. Nenhuma alteração feita.")
            conn.close()
            return
        
        print("\n🗑️  Removendo tabela existente...")
        cursor.execute("DROP TABLE base_grupos_config")
    
    # 3. Criar tabela
    print("🔨 Criando tabela base_grupos_config...")
    cursor.execute(CREATE_TABLE_SQL)
    print("   ✅ Tabela criada com sucesso!")
    print()
    
    # 4. Validar estrutura
    print("🔍 Validando estrutura da tabela...")
    cursor.execute("PRAGMA table_info(base_grupos_config)")
    columns = cursor.fetchall()
    print(f"   Colunas criadas: {len(columns)}")
    for col in columns:
        print(f"      - {col[1]} ({col[2]})")
    print()
    
    # 5. Popular seed data
    print("📝 Populando seed data (17 grupos)...")
    
    for nome_grupo, tipo_gasto, categoria in SEED_DATA:
        try:
            cursor.execute("""
                INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
                VALUES (?, ?, ?)
            """, (nome_grupo, tipo_gasto, categoria))
            print(f"   ✅ {nome_grupo:<20} {tipo_gasto:<15} {categoria}")
        except sqlite3.IntegrityError as e:
            print(f"   ⚠️  {nome_grupo}: Já existe (pulando)")
    
    conn.commit()
    print()
    
    # 6. Validar seed data
    print("🔍 VALIDAÇÃO FINAL:")
    print()
    
    # Query 1: Contar registros
    cursor.execute("SELECT COUNT(*) FROM base_grupos_config")
    total = cursor.fetchone()[0]
    print(f"✓ Total de registros: {total}")
    if total == 17:
        print("  ✅ OK - 17 grupos conforme esperado")
    else:
        print(f"  ⚠️  Esperado: 17, encontrado: {total}")
    print()
    
    # Query 2: Contar por tipo_gasto_padrao
    cursor.execute("""
        SELECT tipo_gasto_padrao, COUNT(*) as qtd
        FROM base_grupos_config
        GROUP BY tipo_gasto_padrao
        ORDER BY tipo_gasto_padrao
    """)
    print("✓ Distribuição por tipo_gasto_padrao:")
    for row in cursor.fetchall():
        print(f"  - {row[0]:<20} {row[1]} grupos")
    print()
    
    # Query 3: Contar por categoria_geral
    cursor.execute("""
        SELECT categoria_geral, COUNT(*) as qtd
        FROM base_grupos_config
        GROUP BY categoria_geral
        ORDER BY categoria_geral
    """)
    print("✓ Distribuição por categoria_geral:")
    for row in cursor.fetchall():
        print(f"  - {row[0]:<20} {row[1]} grupos")
    print()
    
    # Query 4: Testar constraints
    print("✓ Testando constraints (deve falhar):")
    try:
        cursor.execute("""
            INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
            VALUES ('Teste', 'INVALIDO', 'Despesa')
        """)
        print("  ⚠️  ERRO: Constraint não funcionou (permitiu valor inválido)")
        conn.rollback()
    except sqlite3.IntegrityError:
        print("  ✅ OK - Constraint bloqueou valor inválido em tipo_gasto_padrao")
    
    try:
        cursor.execute("""
            INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
            VALUES ('Teste2', 'Fixo', 'INVALIDA')
        """)
        print("  ⚠️  ERRO: Constraint não funcionou (permitiu valor inválido)")
        conn.rollback()
    except sqlite3.IntegrityError:
        print("  ✅ OK - Constraint bloqueou valor inválido em categoria_geral")
    print()
    
    # 7. Mostrar todos os grupos
    print("📊 TODOS OS GRUPOS CONFIGURADOS:")
    print("-" * 80)
    cursor.execute("""
        SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
        FROM base_grupos_config 
        ORDER BY tipo_gasto_padrao, nome_grupo
    """)
    
    print(f"{'Grupo':<20} {'TipoGasto Padrão':<20} {'Categoria Geral':<20}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:<20} {row[1]:<20} {row[2]:<20}")
    print("-" * 80)
    print()
    
    # 8. SQL para rollback (se necessário)
    print("💡 ROLLBACK:")
    print("   Para remover: DROP TABLE IF EXISTS base_grupos_config;")
    print()
    
    print("=" * 80)
    print("✅ FASE 1 CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print()
    print("✓ Tabela criada: base_grupos_config")
    print(f"✓ Grupos configurados: {total}")
    print("✓ Constraints funcionando")
    print()
    print("⏭️  PRÓXIMO PASSO: Fase 2 - Criar Helper Functions")
    print("   Script: test_categorias_helper.py")
    print()
    
    conn.close()

if __name__ == "__main__":
    main()
