#!/usr/bin/env python3
"""
Regenerar hashes v4.2.1 (normalização condicional por tipo de documento)

ESTRATÉGIA v4.2.1:
- FATURA: Normaliza formato de parcela ("LOJA 01/05" → "LOJA (1/5)")
- EXTRATO: Mantém original ("JOAO BA04/10" não é parcela!)
- user_id + valor EXATO (com sinal)
- Hash recursivo para duplicados
"""
import sqlite3
import re
from pathlib import Path
from typing import Optional

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

def extrair_parcela_do_estabelecimento(estabelecimento: str) -> Optional[dict]:
    """
    Extrai informação de parcela do estabelecimento
    Suporta formatos: "LOJA (3/12)" ou "LOJA 3/12"
    """
    # Formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    # Formato sem parênteses: "LOJA 3/12" OU "LOJA3/12"
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    return None

def normalizar_formato_parcela(estabelecimento: str) -> str:
    """
    Normaliza formato de parcela para padrão único: "LOJA (X/Y)"
    Converte "LOJA 01/05" → "LOJA (1/5)"
    """
    info = extrair_parcela_do_estabelecimento(estabelecimento)
    
    if info:
        # Reconstruir com formato padrão (X/Y sem zeros à esquerda)
        return f"{info['estabelecimento_base']} ({info['parcela']}/{info['total']})"
    
    # Sem parcela, retorna original
    return estabelecimento

# Hash recursivo v4.2.1
def generate_hash(data: str, estabelecimento: str, valor: float, user_id: int, seq: int) -> str:
    """
    v4.2.1: user_id + estabelecimento COMPLETO + valor EXATO
    Garante isolamento entre usuários e parcelas únicas
    """
    estab_upper = estabelecimento.upper().strip()
    valor_exato = float(valor)  # SEM abs - mantém sinal
    chave = f"{user_id}|{data}|{estab_upper}|{valor_exato:.2f}"
    
    hash_atual = fnv1a_64_hash(chave)
    for _ in range(seq - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual

def main():
    db_path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("REGENERAÇÃO v4.2.1 (com user_id + estabelecimento completo + valor exato)")
    print("=" * 80)
    print()
    
    # 1. Buscar transações (INCLUINDO tipodocumento para normalização condicional)
    print("📊 Carregando...")
    cursor.execute("""
        SELECT id, Data, Estabelecimento, Valor, arquivo_origem, user_id, tipodocumento
        FROM journal_entries
        ORDER BY user_id, arquivo_origem, id
    """)
    transactions = cursor.fetchall()
    print(f"   {len(transactions)} transações")
    print()
    
    # 2. Agrupar GLOBALMENTE por user + chave (não por arquivo!)
    # CORREÇÃO: Transações idênticas em arquivos diferentes devem ter sequência incremental
    print("🔄 Calculando hashes v4.2.1 (user_id + agrupamento GLOBAL)...")
    from collections import defaultdict
    grupos_global = defaultdict(lambda: defaultdict(int))
    
    updates = []
    for t in transactions:
        tid, data, estab, valor, arquivo, user_id, tipo_doc = t
        
        # v4.2.1 CONDICIONAL: Normalizar apenas FATURAS
        # - FATURA: "LOJA 01/05" → "LOJA (1/5)"
        # - EXTRATO: "JOAO BA04/10" mantém original (BA04 é parte do nome!)
        tipo_doc_lower = tipo_doc.lower() if tipo_doc else ''
        is_fatura = 'fatura' in tipo_doc_lower or 'cartao' in tipo_doc_lower or 'cartão' in tipo_doc_lower
        
        if is_fatura:
            # Fatura: normalizar formato de parcela
            estab_normalizado = normalizar_formato_parcela(estab)
        else:
            # Extrato: manter original
            estab_normalizado = estab
        
        estab_upper = estab_normalizado.upper().strip()
        valor_exato = float(valor)  # SEM abs
        chave_unica = f"{data}|{estab_upper}|{valor_exato:.2f}"
        
        # Controle de sequência GLOBAL por usuário
        grupos_global[user_id][chave_unica] += 1
        sequencia = grupos_global[user_id][chave_unica]
        
        # Gerar hash (user_id + estabelecimento normalizado se fatura + valor exato)
        novo_hash = generate_hash(data, estab_normalizado, valor, user_id, sequencia)
        updates.append((novo_hash, tid))
    
    print(f"   {len(updates)} atualizações")
    print()
    
    # 3. Confirmar
    resp = input("Continuar? (SIM): ")
    if resp != "SIM":
        print("Cancelado")
        return
    
    # 4. Aplicar
    print("💾 Aplicando...")
    cursor.executemany(
        "UPDATE journal_entries SET IdTransacao = ? WHERE id = ?",
        updates
    )
    conn.commit()
    
    print(f"✅ {len(updates)} hashes regenerados!")
    print("🎯 Sistema agora usa v4.2.1 (user_id + estabelecimento completo + valor exato)")
    
    conn.close()

if __name__ == "__main__":
    main()
