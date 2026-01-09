"""
Script de migração: Recalcular IdTransacao de todas as transações usando SQL direto
Usa algoritmo FNV-1a 64-bit consistente

Execução:
    cd app_dev/backend
    source ../venv/bin/activate
    python scripts/recalculate_id_transacao_sql.py
"""

import sqlite3
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shared.utils.hasher import generate_id_transacao

DB_PATH = Path(__file__).parent.parent / "database" / "financas_dev.db"

def recalculate_all_ids():
    """
    Recalcula IdTransacao de todas as transações usando FNV-1a
    Para transações duplicadas, adiciona timestamp do created_at
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Contar total
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total = cursor.fetchone()[0]
        
        print(f"\n🔄 Recalculando IdTransacao de {total} transações...")
        print(f"   Algoritmo: FNV-1a 64-bit")
        print(f"   Formato: Data|Estabelecimento|Valor[|Timestamp se duplicado]\n")
        
        # Buscar todas as transações com rowid e created_at
        cursor.execute("""
            SELECT rowid, IdTransacao, Data, Estabelecimento, Valor, created_at 
            FROM journal_entries 
            ORDER BY rowid
        """)
        transactions = cursor.fetchall()
        
        updated = 0
        maintained = 0
        errors = 0
        seen_ids = {}  # Rastrear IDs já gerados
        
        for i, (rowid, old_id, data, estabelecimento, valor, created_at) in enumerate(transactions, 1):
            try:
                # Recalcular IdTransacao (primeira tentativa sem timestamp)
                new_id = generate_id_transacao(
                    data=data,
                    estabelecimento=estabelecimento,
                    valor=abs(valor)
                )
                
                # Se já existe esse ID, adicionar timestamp para diferenciar
                if new_id in seen_ids:
                    # Usar created_at ou timestamp sequencial
                    timestamp = created_at.replace('-', '').replace(':', '').replace(' ', '').replace('.', '')
                    new_id = generate_id_transacao(
                        data=data,
                        estabelecimento=estabelecimento,
                        valor=abs(valor),
                        timestamp_micro=timestamp
                    )
                    
                    if updated <= 5:
                        print(f"   🔄 Duplicata detectada: {estabelecimento[:30]:30s}")
                        print(f"      Adicionando timestamp: {timestamp[:20]}...\n")
                
                # Registrar ID como visto
                seen_ids[new_id] = rowid
                
                # Atualizar se diferente
                if old_id != new_id:
                    cursor.execute(
                        "UPDATE journal_entries SET IdTransacao = ? WHERE rowid = ?",
                        (new_id, rowid)
                    )
                    updated += 1
                    
                    if updated <= 5:  # Mostrar primeiros 5
                        print(f"   ✅ {data} | {estabelecimento[:30]:30s} | R$ {abs(valor):8.2f}")
                        print(f"      Antigo: {old_id}")
                        print(f"      Novo:   {new_id}\n")
                else:
                    maintained += 1
                
                # Progress a cada 1000
                if i % 1000 == 0:
                    conn.commit()
                    print(f"   Progresso: {i}/{total} ({i*100//total}%) - {updated} atualizados, {maintained} mantidos, {errors} erros")
                
            except Exception as e:
                print(f"   ❌ Erro: {data} | {estabelecimento[:30]:30s} - {str(e)}")
                errors += 1
        
        # Commit final
        conn.commit()
        
        print(f"\n✅ Concluído!")
        print(f"   Total processado: {total}")
        print(f"   Atualizados: {updated}")
        print(f"   Mantidos: {maintained}")
        print(f"   Erros: {errors}")
        
        if updated > 0:
            print(f"\n⚠️  IMPORTANTE: Reinicie os servidores para aplicar mudanças")
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MIGRAÇÃO: Recalcular IdTransacao (FNV-1a 64-bit)")
    print("="*80)
    
    response = input("\n⚠️  Isso irá atualizar TODOS os IdTransacao do journal_entries. Continuar? (s/N): ")
    
    if response.lower() == 's':
        recalculate_all_ids()
    else:
        print("\n❌ Operação cancelada.")
