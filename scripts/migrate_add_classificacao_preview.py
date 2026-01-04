"""
Migração: Adiciona colunas de classificação em preview_transacoes
Data: 04/01/2026

Adiciona campos para salvar classificação automática durante o preview:
- GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
- origem_classificacao, ValidarIA, MarcacaoIA
- IdTransacao, IdParcela, EstabelecimentoBase
- TipoTransacao, ValorPositivo
"""

import sqlite3
import sys
from pathlib import Path

# Caminho do banco
backend_path = Path(__file__).parent.parent / 'app_dev' / 'backend'
db_path = backend_path / 'database' / 'financas_dev.db'

print(f"📁 Banco de dados: {db_path}")

if not db_path.exists():
    print(f"❌ Banco não encontrado em: {db_path}")
    sys.exit(1)

# Conectar ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n🔄 Iniciando migração...")

# Lista de colunas a adicionar
colunas_novas = [
    # Campos de identificação
    ("IdTransacao", "TEXT"),
    ("IdParcela", "TEXT"),
    ("EstabelecimentoBase", "TEXT"),
    
    # Campos de valor e tipo
    ("ValorPositivo", "REAL"),
    ("TipoTransacao", "TEXT"),  # Débito/Crédito
    
    # Campos de classificação
    ("GRUPO", "TEXT"),
    ("SUBGRUPO", "TEXT"),
    ("TipoGasto", "TEXT"),
    ("CategoriaGeral", "TEXT"),
    
    # Campos de origem da classificação
    ("origem_classificacao", "TEXT"),  # IdParcela, Base_Padroes, etc
    ("ValidarIA", "TEXT"),  # Revisar, OK
    ("MarcacaoIA", "TEXT"),  # Manual, Automático, etc
    
    # Campos de parcela
    ("ParcelaAtual", "INTEGER"),
    ("TotalParcelas", "INTEGER"),
    ("TemParcela", "INTEGER"),  # 0 ou 1 (boolean)
    
    # Flags
    ("IgnorarDashboard", "INTEGER DEFAULT 0"),  # 0 ou 1
]

# Verificar quais colunas já existem
cursor.execute("PRAGMA table_info(preview_transacoes)")
colunas_existentes = {row[1] for row in cursor.fetchall()}

print(f"\n📋 Colunas existentes: {len(colunas_existentes)}")

# Adicionar colunas que não existem
colunas_adicionadas = 0
for nome_coluna, tipo_coluna in colunas_novas:
    if nome_coluna not in colunas_existentes:
        try:
            sql = f"ALTER TABLE preview_transacoes ADD COLUMN {nome_coluna} {tipo_coluna}"
            cursor.execute(sql)
            print(f"  ✅ Coluna adicionada: {nome_coluna} ({tipo_coluna})")
            colunas_adicionadas += 1
        except sqlite3.OperationalError as e:
            print(f"  ⚠️  Erro ao adicionar {nome_coluna}: {e}")
    else:
        print(f"  ⏭️  Coluna já existe: {nome_coluna}")

# Commit
conn.commit()

print(f"\n✅ Migração concluída!")
print(f"   {colunas_adicionadas} colunas adicionadas")
print(f"   {len(colunas_existentes) + colunas_adicionadas} colunas totais")

# Verificar estrutura final
cursor.execute("PRAGMA table_info(preview_transacoes)")
colunas_final = cursor.fetchall()

print(f"\n📊 Estrutura final da tabela preview_transacoes:")
for col in colunas_final:
    print(f"   {col[1]:25} {col[2]:15} {'NOT NULL' if col[3] else ''}")

conn.close()

print("\n🎯 Próximos passos:")
print("   1. Atualizar modelo PreviewTransacao em app/models/__init__.py")
print("   2. Modificar endpoint /process-classify para salvar classificações")
print("   3. Testar fluxo completo de upload → preview → confirmar")
