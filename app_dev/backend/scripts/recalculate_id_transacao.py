"""
Script de migração: Recalcular IdTransacao de todas as transações
Usa algoritmo FNV-1a 64-bit consistente (generate_id_transacao)

Execução:
    cd app_dev/backend
    python scripts/recalculate_id_transacao.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.domains.transactions.models import JournalEntry
from app.shared.utils.hasher import generate_id_transacao
from sqlalchemy import func

def recalculate_all_ids():
    """
    Recalcula IdTransacao de todas as transações usando FNV-1a
    """
    db = SessionLocal()
    
    try:
        # Contar total
        total = db.query(func.count(JournalEntry.IdTransacao)).scalar()
        print(f"\n🔄 Recalculando IdTransacao de {total} transações...")
        print(f"   Algoritmo: FNV-1a 64-bit")
        print(f"   Formato: Data|Estabelecimento|Valor\n")
        
        # Processar em lotes
        batch_size = 1000
        offset = 0
        updated = 0
        errors = 0
        
        while offset < total:
            # Buscar lote
            transactions = db.query(JournalEntry).offset(offset).limit(batch_size).all()
            
            if not transactions:
                break
            
            for tx in transactions:
                try:
                    # Recalcular IdTransacao
                    new_id = generate_id_transacao(
                        data=tx.Data,
                        estabelecimento=tx.Estabelecimento,
                        valor=abs(tx.Valor)
                    )
                    
                    # Atualizar se diferente
                    if tx.IdTransacao != new_id:
                        old_id = tx.IdTransacao
                        tx.IdTransacao = new_id
                        updated += 1
                        
                        if updated <= 5:  # Mostrar primeiros 5
                            print(f"   ✅ {tx.Data} | {tx.Estabelecimento[:30]:30s} | R$ {abs(tx.Valor):8.2f}")
                            print(f"      Antigo: {old_id}")
                            print(f"      Novo:   {new_id}\n")
                    
                except Exception as e:
                    print(f"   ❌ Erro: {tx.Data} | {tx.Estabelecimento[:30]:30s} - {str(e)}")
                    errors += 1
            
            # Commit do lote
            db.commit()
            offset += batch_size
            
            # Progress
            progress = min(offset, total)
            print(f"   Progresso: {progress}/{total} ({progress*100//total}%) - {updated} atualizados, {errors} erros")
        
        print(f"\n✅ Concluído!")
        print(f"   Total processado: {total}")
        print(f"   Atualizados: {updated}")
        print(f"   Mantidos: {total - updated - errors}")
        print(f"   Erros: {errors}")
        
        if updated > 0:
            print(f"\n⚠️  IMPORTANTE: Reinicie os servidores para aplicar mudanças")
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MIGRAÇÃO: Recalcular IdTransacao (FNV-1a 64-bit)")
    print("="*80)
    
    response = input("\n⚠️  Isso irá atualizar TODOS os IdTransacao do journal_entries. Continuar? (s/N): ")
    
    if response.lower() == 's':
        recalculate_all_ids()
    else:
        print("\n❌ Operação cancelada.")
