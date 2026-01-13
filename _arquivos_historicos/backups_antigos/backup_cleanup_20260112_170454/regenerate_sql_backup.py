#!/usr/bin/env python3
"""
Regenerar hashes v4.1.0 via SQL direto (SEM parcela no hash)

CORREÇÃO CRÍTICA:
- Extrair parcela do estabelecimento
- Gerar hash usando estabelecimento_base (SEM parcela)
- "LOJA (1/12)" e "LOJA 01/12" → ambos viram hash("LOJA")
"""
import sqlite3
import re
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

# Extrair parcela (copiado de marker.py)
def extrair_estabelecimento_base(estabelecimento: str) -> str:
    """
    Extrai estabelecimento base removendo parcela
    
    Formatos suportados:
    - "LOJA (1/12)" → "LOJA"
    - "LOJA 01/12" → "LOJA"
    - "LOJA" → "LOJA"
    """
    # Formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        return match.group(1).strip()
    
    # Formato sem parênteses: "LOJA 3/12" ou "LOJA3/12"
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        return match.group(1).strip()
    
    # Sem parcela
    return estabelecimento.strip()

# Hash recursivo v4.1.0
def generate_hash(data: str, estabelecimento: str, valor: float, seq: int, tipo_doc: str = 'fatura') -> str:
    """
    ESTRATÉGIA CONDICIONAL:
    - extrato: usa estabelecimento COMPLETO
    - fatura: usa estabelecimento_base (sem parcela)
    """
    # Extrair base apenas para faturas
    if tipo_doc == 'extrato':
        estab_para_hash = estabelecimento  # Completo
    else:
        estab_para_hash = extrair_estabelecimento_base(estabelecimento)  # Sem parcela
    
    estab_upper = estab_para_hash.upper().strip()
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
        SELECT id, Data, Estabelecimento, Valor, tipodocumento
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
        tid, data, estab, valor, tipo_doc = t
        # ESTRATÉGIA CONDICIONAL por tipo_documento:
        # - extrato: usa estabelecimento COMPLETO
        # - fatura: usa estabelecimento_base (sem parcela)
        if tipo_doc == 'extrato':
            estab_para_hash = estab  # Completo (PIX TRANSF EMANUEL15/10)
        else:
            estab_para_hash = extrair_estabelecimento_base(estab)  # Sem parcela (LOJA)
        
        estab_upper = estab_para_hash.upper().strip()
        valor_abs = abs(valor)
        chave = f"{data}|{estab_upper}|{valor_abs:.2f}"
        grupos[chave].append(t)
    
    # 3. Gerar updates
    updates = []
    for chave, grupo in grupos.items():
        for seq, t in enumerate(grupo, start=1):
            tid, data, estab, valor, tipo_doc = t
            novo_hash = generate_hash(data, estab, valor, seq, tipo_doc)
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
