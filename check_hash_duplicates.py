#!/usr/bin/env python3
"""
Verifica quais transações estão gerando IdTransacao duplicado
"""
import sqlite3
from pathlib import Path
from collections import defaultdict

# Hash FNV-1a
def fnv1a_64_hash(text: str) -> str:
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)

def generate_hash(data: str, estabelecimento: str, valor: float, seq: int) -> str:
    estab_upper = estabelecimento.upper().strip()
    valor_exato = float(valor)
    chave = f"{data}|{estab_upper}|{valor_exato:.2f}"
    
    hash_atual = fnv1a_64_hash(chave)
    for _ in range(seq - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual

db_path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, Data, Estabelecimento, Valor, arquivo_origem, user_id
    FROM journal_entries
    ORDER BY user_id, arquivo_origem, id
""")
transactions = cursor.fetchall()

grupos_arquivo = defaultdict(lambda: defaultdict(int))
hash_map = {}  # hash -> lista de ids

for t in transactions:
    tid, data, estab, valor, arquivo, user_id = t
    
    estab_upper = estab.upper().strip()
    valor_exato = float(valor)
    chave_unica = f"{data}|{estab_upper}|{valor_exato:.2f}"
    
    chave_arquivo = f"{user_id}_{arquivo}"
    grupos_arquivo[chave_arquivo][chave_unica] += 1
    sequencia = grupos_arquivo[chave_arquivo][chave_unica]
    
    novo_hash = generate_hash(data, estab, valor, sequencia)
    
    if novo_hash not in hash_map:
        hash_map[novo_hash] = []
    hash_map[novo_hash].append((tid, data, estab, valor, arquivo, sequencia))

# Encontrar duplicatas
duplicatas = {h: ids for h, ids in hash_map.items() if len(ids) > 1}

if duplicatas:
    print(f"\n🚨 Encontradas {len(duplicatas)} hashes duplicadas!\n")
    for hash_val, transacoes in list(duplicatas.items())[:5]:  # Mostrar primeiras 5
        print(f"Hash: {hash_val}")
        for tid, data, estab, valor, arquivo, seq in transacoes:
            print(f"  ID {tid}: {data} | {estab} | {valor} | arquivo={arquivo} | seq={seq}")
        print()
else:
    print("✅ Nenhuma duplicata encontrada!")

conn.close()
