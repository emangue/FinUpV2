import sys
import os
import hashlib
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import get_db_session, JournalEntry
from app.utils.normalizer import normalizar_estabelecimento, detectar_parcela

def fix_hashes():
    print("🔧 Corrigindo hashes de IdParcela (Case Sensitivity)...")
    
    session = get_db_session()
    
    try:
        entries = session.query(JournalEntry).filter(
            JournalEntry.IdParcela.isnot(None),
            JournalEntry.IdParcela != ''
        ).all()
        
        print(f"Processando {len(entries)} transações parceladas...")
        
        updated = 0
        
        for e in entries:
            # Detecta info da parcela para pegar o total
            info = detectar_parcela(e.Estabelecimento)
            
            if not info:
                # Tenta fallback manual se detectar_parcela falhar (ex: formato diferente)
                # Mas se já tem IdParcela, deveria ter passado na detecção original
                continue
                
            total = info['total']
            
            # Normaliza nome (remove parcela e uppercase)
            # Isso garante que "Azul Seguros" e "AZUL SEGUROS" gerem o mesmo hash
            estab_norm = normalizar_estabelecimento(e.Estabelecimento)
            
            # Recalcula hash usando a NOVA lógica (com estab normalizado)
            chave = f"{estab_norm}|{abs(e.Valor):.2f}|{total}"
            novo_hash = hashlib.md5(chave.encode()).hexdigest()[:16]
            
            if e.IdParcela != novo_hash:
                # print(f"  📝 {e.Estabelecimento}: {e.IdParcela} -> {novo_hash}")
                e.IdParcela = novo_hash
                updated += 1
        
        session.commit()
        print(f"✅ {updated} transações atualizadas com hashes normalizados.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_hashes()
