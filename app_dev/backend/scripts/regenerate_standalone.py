#!/usr/bin/env python3
"""
Regenera IdTransacao - Versão Standalone (sem imports complexos)
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Hash FNV-1a 64-bit standalone
def fnv1a_64_hash(text):
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)

def generate_id_transacao_v4(data, estabelecimento, valor):
    """Hash v4.0.0 - Simplificado"""
    estab_upper = str(estabelecimento).upper().strip()
    valor_abs = abs(float(valor))
    chave = f"{data}|{estab_upper}|{valor_abs:.2f}"
    return fnv1a_64_hash(chave)

def regenerar():
    db_path = Path(__file__).parent.parent / "database" / "financas_dev.db"
    
    print("="*60)
    print("🔄 REGENERAÇÃO DE IdTransacao - v4.0.0 (Standalone)")
    print("="*60)
    print()
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"financas_dev_backup_{timestamp}.db"
    print(f"📦 Backup: {backup_path.name}")
    shutil.copy2(db_path, backup_path)
    print("✅ Backup criado!")
    print()
    
    # Conectar
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Buscar todas
        cursor.execute('SELECT id, Data, Estabelecimento, Valor, IdTransacao FROM journal_entries')
        rows = cursor.fetchall()
        total = len(rows)
        
        print(f"📊 {total} transações encontradas")
        print()
        
        resposta = input("🔹 Continuar? (SIM): ")
        if resposta.strip().upper() != "SIM":
            print("❌ Cancelado")
            return
        
        print()
        print("🔄 Processando...")
        print("-" * 60)
        
        modificados = 0
        amostras = []
        
        for i, (id_row, data, estab, valor, id_antigo) in enumerate(rows, 1):
            # Gerar novo ID
            id_novo = generate_id_transacao_v4(data, estab, valor)
            
            if id_antigo != id_novo:
                # Atualizar
                cursor.execute(
                    'UPDATE journal_entries SET IdTransacao = ? WHERE id = ?',
                    (id_novo, id_row)
                )
                modificados += 1
                
                if len(amostras) < 5:
                    amostras.append({
                        'data': data,
                        'estab': estab[:40],
                        'valor': valor,
                        'antigo': id_antigo,
                        'novo': id_novo
                    })
            
            if i % 500 == 0 or i == total:
                print(f"  {i}/{total} ({(i/total)*100:.1f}%)")
        
        print()
        print("="*60)
        print("📊 RESUMO")
        print("="*60)
        print(f"Total:       {total}")
        print(f"Modificadas: {modificados}")
        print(f"Sem mudança: {total - modificados}")
        print()
        
        if amostras:
            print("🔍 AMOSTRAS:")
            print("-" * 60)
            for a in amostras:
                print(f"\n{a['data']} | {a['estab']} | R$ {a['valor']:.2f}")
                print(f"  Antigo: {a['antigo']}")
                print(f"  Novo:   {a['novo']}")
        
        print()
        print("-" * 60)
        
        if modificados > 0:
            resposta = input(f"\n🔹 Confirmar {modificados} alterações? (SIM): ")
            if resposta.strip().upper() == "SIM":
                conn.commit()
                print()
                print(f"✅ {modificados} IdTransacao atualizados!")
                print()
                print("📋 Próximos passos:")
                print("   1. Limpar preview: DELETE FROM preview_transacoes;")
                print("   2. Fazer novo upload")
                print("   3. Rodar: ./validar_upload.sh")
            else:
                conn.rollback()
                print("❌ Rollback")
        else:
            print("ℹ️  Nenhuma modificação")
            
    finally:
        conn.close()
        print()
        print("🏁 Finalizado")

if __name__ == "__main__":
    regenerar()
