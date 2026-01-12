#!/usr/bin/env python3
"""Regenera IdTransacao v4.0.0 recriando tabela"""
import sqlite3
import shutil
from datetime import datetime

def fnv1a_64_hash(text):
    h = 0xcbf29ce484222325
    for c in text:
        h = ((h ^ ord(c)) * 0x100000001b3) & ((1 << 64) - 1)
    return str(h)

# Paths
db_path = 'app_dev/backend/database/financas_dev.db'
backup_source = 'app_dev/backend/database/financas_dev_backup_20260110_141400.db'

# Restaurar do backup limpo
print(f"📦 Restaurando de: {backup_source}")
shutil.copy2(backup_source, db_path)

# Conectar
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("\n🔄 Regenerando IdTransacao v4.0.0...")

# Desabilitar foreign keys
c.execute("PRAGMA foreign_keys = OFF")

# Criar nova tabela sem UNIQUE
c.execute("""
CREATE TABLE journal_entries_new (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    Data TEXT,
    Estabelecimento TEXT,
    Valor REAL,
    ValorPositivo REAL,
    TipoTransacao TEXT,
    TipoGasto TEXT,
    GRUPO TEXT,
    SUBGRUPO TEXT,
    CategoriaGeral TEXT,
    IdTransacao TEXT,
    IdParcela TEXT,
    arquivo_origem TEXT,
    banco_origem TEXT,
    tipodocumento TEXT,
    origem_classificacao TEXT,
    upload_history_id INTEGER,
    MesFatura TEXT,
    Ano INTEGER,
    created_at DATETIME,
    NomeCartao TEXT,
    IgnorarDashboard INTEGER DEFAULT 0
)
""")

# Copiar dados com novo IdTransacao
c.execute("SELECT * FROM journal_entries ORDER BY id")
rows = c.fetchall()
total = len(rows)
id_cache = {}

print(f"Total: {total} transações\n")

for i, row in enumerate(rows, 1):
    # Gerar novo IdTransacao
    chave_base = f"{row['Data']}|{row['Estabelecimento'].upper().strip()}|{abs(row['Valor']):.2f}"
    novo_id = fnv1a_64_hash(chave_base)
    
    # Se duplicata, adicionar sequência
    seq = 1
    while novo_id in id_cache:
        novo_id = fnv1a_64_hash(f"{chave_base}|{seq}")
        seq += 1
    id_cache[novo_id] = True
    
    # Inserir
    c.execute("""
        INSERT INTO journal_entries_new VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row['id'], row['user_id'], row['Data'], row['Estabelecimento'],
        row['Valor'], row['ValorPositivo'], row['TipoTransacao'], row['TipoGasto'],
        row['GRUPO'], row['SUBGRUPO'], row['CategoriaGeral'], novo_id,
        row['IdParcela'], row['arquivo_origem'], row['banco_origem'], row['tipodocumento'],
        row['origem_classificacao'], row['upload_history_id'], row['MesFatura'],
        row['Ano'], row['created_at'], row['NomeCartao'], row['IgnorarDashboard']
    ))
    
    if i % 500 == 0:
        print(f"  Processadas: {i}/{total} ({100*i/total:.1f}%)")

# Substituir tabela
c.execute("DROP TABLE journal_entries")
c.execute("ALTER TABLE journal_entries_new RENAME TO journal_entries")

# Recriar índices
print("\n📊 Recriando índices...")
c.execute("CREATE UNIQUE INDEX idx_journal_entries_id_transacao ON journal_entries(IdTransacao)")

conn.commit()
conn.close()

print(f"\n✅ {total} IdTransacao regenerados com sucesso!")
print("\n📋 Próximos passos:")
print("   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4")
print("   ./quick_stop.sh && ./quick_start.sh")
