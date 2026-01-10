#!/usr/bin/env python3
"""
Regenerar hashes v4.1.0 via SQL direto (sem ORM)
"""
import sqlite3
from pathlib import Path

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

# Hash recursivo v4.1.0
def generate_hash(data: str, estabelecimento: str, valor: float, seq: int) -> str:
    estab_upper = estabelecimento.upper().strip()
    valor_abs = abs(valor)
    chave = f"{data}|{estab_upper}|{valor_abs:.2f}"
    
    hash_atual = fnv1a_64_hash(chave)
    for _ in range(seq - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual

def main():
    db_path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("REGENERAÇÃO v4.1.0 (SQL Direto)")
    print("=" * 80)
    print()
    
    # 1. Buscar transações
    print("📊 Carregando...")
    cursor.execute("""
        SELECT id, Data, Estabelecimento, Valor
        FROM journal_entries
        ORDER BY id
    """)
    transactions = cursor.fetchall()
    print(f"   {len(transactions)} transações")
    print()
    
    # 2. Agrupar e numerar sequência
    print("🔄 Calculando hashes...")
    from collections import defaultdict
    grupos = defaultdict(list)
    
    for t in transactions:
        tid, data, estab, valor = t
        estab_upper = estab.upper().strip()
        valor_abs = abs(valor)
        chave = f"{data}|{estab_upper}|{valor_abs:.2f}"
        grupos[chave].append(t)
    
    # 3. Gerar updates
    updates = []
    for chave, grupo in grupos.items():
        for seq, t in enumerate(grupo, start=1):
            tid, data, estab, valor = t
            novo_hash = generate_hash(data, estab, valor, seq)
            updates.append((novo_hash, tid))
    
    print(f"   {len(updates)} atualizações")
    print()
    
    # 4. Confirmar
    resp = input("Continuar? (SIM): ")
    if resp != "SIM":
        print("Cancelado")
        return
    
    # 5. Aplicar
    print("💾 Aplicando...")
    cursor.executemany(
        "UPDATE journal_entries SET IdTransacao = ? WHERE id = ?",
        updates
    )
    conn.commit()
    
    print(f"✅ {len(updates)} hashes regenerados!")
    print("🎯 Sistema agora usa v4.1.0")
    
    conn.close()

if __name__ == "__main__":
    main()
