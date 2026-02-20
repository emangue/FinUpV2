#!/usr/bin/env python3
"""
Diagnóstico: Por que Base Parcelas não marca transações no upload?

Executa: cd app_dev/backend && python -c "
import sys; sys.path.insert(0, '.');
exec(open('../../scripts/diagnostic/diagnosticar_base_parcelas_upload.py').read().split('# RUN')[1])
"
"""
import sqlite3
import hashlib
import re

DB_PATH = "app_dev/backend/database/financas_dev.db"

def normalizar_estabelecimento(estab):
    if not estab: return ""
    estab = re.sub(r'\s*\(?\d{1,2}/\d{1,2}\)?\s*$', '', estab)
    import unicodedata
    estab = unicodedata.normalize('NFD', estab)
    estab = ''.join(c for c in estab if unicodedata.category(c) != 'Mn')
    estab = estab.upper()
    estab = re.sub(r'[^A-Z0-9\s]', ' ', estab)
    estab = re.sub(r'\s+', ' ', estab)
    return estab.strip()

def extrair_parcela(lancamento):
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', lancamento)
    if match:
        p, t = int(match.group(2)), int(match.group(3))
        if 1 <= p <= t <= 99:
            return {'estabelecimento_base': match.group(1).strip(), 'parcela': p, 'total': t}
    return None

def calcular_id_parcela(estab_base, valor, total, user_id):
    estab_norm = normalizar_estabelecimento(estab_base)
    valor_arr = round(float(valor), 2)
    chave = f"{estab_norm}|{valor_arr:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]

# RUN
if __name__ == "__main__" or "diagnostic" in dir():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("=" * 60)
    print("DIAGNÓSTICO: Base Parcelas no Upload")
    print("=" * 60)
    
    # 1. Testar extração de parcela do CSV
    lancamento_teste = "PRODUTOS GLOBO    07/12"
    valor_teste = 59.9
    info = extrair_parcela(lancamento_teste)
    print(f"\n1. EXTRAÇÃO DE PARCELA (marker)")
    print(f"   Lancamento: '{lancamento_teste}'")
    print(f"   Resultado: {info}")
    if info:
        print(f"   ✓ Estabelecimento base: '{info['estabelecimento_base']}'")
        print(f"   ✓ Parcela: {info['parcela']}/{info['total']}")
    else:
        print(f"   ✗ FALHA: Parcela não detectada! Verificar regex no marker.py")
    
    # 2. Calcular IdParcela para user_id 1 e 4
    print(f"\n2. CÁLCULO IdParcela (valor={valor_teste})")
    for uid in [1, 4]:
        id_p = calcular_id_parcela("PRODUTOS GLOBO", valor_teste, 12, uid)
        print(f"   user_id={uid}: IdParcela = {id_p}")
    
    # 3. Verificar base_parcelas
    print(f"\n3. BASE_PARCELAS (PRODUTOS GLOBO)")
    rows = conn.execute("""
        SELECT user_id, id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas, qtd_pagas
        FROM base_parcelas WHERE estabelecimento_base LIKE '%GLOBO%'
    """).fetchall()
    for r in rows:
        print(f"   user_id={r[0]} | id_parcela={r[1]} | R${r[3]} | {r[4]}x | pagas={r[5]}")
    
    # 4. Match?
    print(f"\n4. VERIFICAÇÃO DE MATCH")
    id_gerado_1 = calcular_id_parcela("PRODUTOS GLOBO", 59.9, 12, 1)
    id_gerado_4 = calcular_id_parcela("PRODUTOS GLOBO", 59.9, 12, 4)
    ids_na_base = {r[1] for r in rows}
    if id_gerado_1 in ids_na_base:
        print(f"   ✓ user_id=1: IdParcela {id_gerado_1} EXISTE em base_parcelas")
    else:
        print(f"   ✗ user_id=1: IdParcela {id_gerado_1} NÃO encontrado em base_parcelas")
    if id_gerado_4 in ids_na_base:
        print(f"   ✓ user_id=4: IdParcela {id_gerado_4} EXISTE em base_parcelas")
    else:
        print(f"   ✗ user_id=4: IdParcela {id_gerado_4} NÃO encontrado em base_parcelas")
    
    # 5. Causas prováveis
    print(f"\n5. CAUSAS PROVÁVEIS SE NÃO MARCA")
    print("   a) user_id diferente: Você está logado com qual usuário? base_parcelas é por user_id.")
    print("   b) Primeiro upload: base_parcelas só é populada APÓS confirmar. 1º upload = vazio.")
    print("   c) Produção vs Local: meufinup.com.br usa banco diferente. base_parcelas em prod pode estar vazia.")
    print("   d) Formato Excel: Não há processador para fatura Excel. Use CSV ou PDF.")
    
    conn.close()
    print("\n" + "=" * 60)
