#!/usr/bin/env python3
"""
Corrige id_parcela na VM para formato com user_id no hash.
Executar na VM: python3 fix_id_parcela_vm.py
Ou via SSH: ssh host 'cd /var/www/finup && python3 -' < fix_id_parcela_vm.py
"""
import sqlite3
import hashlib
import re
import unicodedata
import os

# Detectar path do banco
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "..", "app_dev", "backend", "database", "financas_dev.db")
DB_PATH = os.path.normpath(DB_PATH)

def normalizar_estabelecimento(texto):
    """Igual ao marker.py / app.shared.utils"""
    if not texto:
        return ""
    estab = re.sub(r'\s*\(?\d{1,2}/\d{1,2}\)?\s*$', '', str(texto))
    estab = unicodedata.normalize('NFD', estab)
    estab = ''.join(c for c in estab if unicodedata.category(c) != 'Mn')
    estab = estab.upper()
    estab = re.sub(r'[^A-Z0-9\s]', ' ', estab)
    estab = re.sub(r'\s+', ' ', estab)
    return estab.replace('*', '').strip()

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco não encontrado: {DB_PATH}")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT id, id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas, user_id FROM base_parcelas").fetchall()
    
    print(f"📦 Encontradas {len(rows)} parcelas")
    
    updates = []
    for r in rows:
        user_id = r['user_id']
        if user_id is None:
            print(f"  ⚠️ id={r['id']} sem user_id, pulando")
            continue
        
        estab_norm = normalizar_estabelecimento(r['estabelecimento_base'])
        valor = float(r['valor_parcela'])
        total = int(r['qtd_parcelas'])
        chave = f"{estab_norm}|{valor:.2f}|{total}|{user_id}"
        novo_id = hashlib.md5(chave.encode()).hexdigest()[:16]
        
        if r['id_parcela'] != novo_id:
            updates.append((novo_id, r['id']))
            print(f"  🔄 id={r['id']} | {r['estabelecimento_base'][:35]:35} | user={user_id} | {r['id_parcela']} → {novo_id}")
    
    if updates:
        for novo_id, row_id in updates:
            conn.execute("UPDATE base_parcelas SET id_parcela = ? WHERE id = ?", (novo_id, row_id))
        conn.commit()
        print(f"\n✅ {len(updates)} parcelas atualizadas")
    else:
        print("\n✅ Todas as parcelas já estão corretas")
    
    conn.close()
    return 0

if __name__ == "__main__":
    exit(main())
