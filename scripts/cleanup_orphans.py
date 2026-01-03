import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import get_db_session, BaseParcelas, JournalEntry

def cleanup_orphans():
    print("🧹 Limpando contratos órfãos em BaseParcelas...")
    
    session = get_db_session()
    
    try:
        # Busca todos os IDs de parcela em uso
        used_ids = session.query(JournalEntry.IdParcela).distinct().all()
        used_ids = {id[0] for id in used_ids if id[0]}
        
        # Busca todos os contratos
        contratos = session.query(BaseParcelas).all()
        
        deleted = 0
        for c in contratos:
            if c.id_parcela not in used_ids:
                # print(f"  🗑 Deletando órfão: {c.estabelecimento_base} ({c.id_parcela})")
                session.delete(c)
                deleted += 1
        
        session.commit()
        print(f"✅ {deleted} contratos órfãos removidos.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    cleanup_orphans()
