import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import get_db_session, JournalEntry

def enforce_credit_card_only():
    print("🔒 Garantindo que apenas Cartão de Crédito tenha parcelas...")
    
    session = get_db_session()
    
    try:
        # Busca transações que NÃO são Cartão de Crédito mas TÊM IdParcela
        invalidas = session.query(JournalEntry).filter(
            JournalEntry.IdParcela.isnot(None),
            JournalEntry.IdParcela != '',
            JournalEntry.TipoTransacao != 'Cartão de Crédito'
        ).all()
        
        if not invalidas:
            print("✅ Nenhuma transação inválida encontrada.")
            return
            
        print(f"⚠ Encontradas {len(invalidas)} transações inválidas (não-cartão com parcela).")
        
        for t in invalidas:
            # print(f"  - Removendo parcela de: {t.Estabelecimento} ({t.TipoTransacao})")
            t.IdParcela = None
            
        session.commit()
        print(f"✅ {len(invalidas)} transações corrigidas.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    enforce_credit_card_only()
