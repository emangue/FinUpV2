import sys
import os
from collections import defaultdict
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import get_db_session, JournalEntry
from app.utils.hasher import generate_id_transacao

def fix_id_transacao():
    print("🔧 Atualizando IdTransacao para nova lógica de hash...")
    
    session = get_db_session()
    
    try:
        entries = session.query(JournalEntry).all()
        print(f"Processando {len(entries)} transações...")
        
        # Mapa de novos hashes para detectar colisões
        hash_map = defaultdict(list)
        
        for e in entries:
            new_hash = generate_id_transacao(e.Data, e.Estabelecimento, e.Valor)
            hash_map[new_hash].append(e)
            
        updated_count = 0
        duplicates_removed = 0
        
        for new_hash, items in hash_map.items():
            if len(items) > 1:
                # Duplicatas encontradas no banco!
                print(f"⚠ Encontradas {len(items)} duplicatas para hash {new_hash}")
                # Mantém o primeiro, remove os outros
                keep = items[0]
                keep.IdTransacao = new_hash
                updated_count += 1
                
                for remove in items[1:]:
                    print(f"  🗑 Removendo duplicado ID {remove.id} ({remove.Estabelecimento})")
                    session.delete(remove)
                    duplicates_removed += 1
            else:
                # Caso normal
                item = items[0]
                if item.IdTransacao != new_hash:
                    item.IdTransacao = new_hash
                    updated_count += 1
        
        session.commit()
        print(f"✅ Concluído!")
        print(f"  - Transações atualizadas: {updated_count}")
        print(f"  - Duplicatas removidas: {duplicates_removed}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_id_transacao()
