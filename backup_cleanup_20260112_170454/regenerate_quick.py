#!/usr/bin/env python3
import sqlite3
import shutil
from datetime import datetime

# Backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db_path = 'app_dev/backend/database/financas_dev.db'
backup_path = f'app_dev/backend/database/financas_dev_backup_{timestamp}.db'
shutil.copy2(db_path, backup_path)
print(f"📦 Backup: {backup_path}")

# Função hash FNV-1a 64-bit
def fnv1a_64_hash(text):
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("\n🔄 Regenerando IdTransacao v4.0.0...")
c.execute("SELECT id, Data, Estabelecimento, Valor FROM journal_entries ORDER BY id")
transacoes = c.fetchall()

total = len(transacoes)
modificados = 0
id_cache = {}  # Detectar duplicatas

for row in transacoes:
    id_row, data, estab, valor = row
    
    # Gerar hash base
    chave_base = f"{data}|{estab.upper().strip()}|{abs(valor):.2f}"
    hash_base = fnv1a_64_hash(chave_base)
    
    # Se duplicata, adicionar sequência
    novo_id = hash_base
    seq = 1
    while novo_id in id_cache:
        novo_id = fnv1a_64_hash(f"{chave_base}|{seq}")
        seq += 1
    
    id_cache[novo_id] = id_row
    
    # Atualizar
    c.execute("UPDATE journal_entries SET IdTransacao = ? WHERE id = ?", (novo_id, id_row))
    modificados += 1
    
    if modificados % 500 == 0:
        print(f"  Processadas: {modificados}/{total} ({100*modificados/total:.1f}%)")

conn.commit()
conn.close()

print(f"\n✅ {modificados} IdTransacao regenerados com sucesso!")
print("\n📋 Próximos passos:")
print("   1. cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4")
print("   2. ./quick_stop.sh && ./quick_start.sh")
