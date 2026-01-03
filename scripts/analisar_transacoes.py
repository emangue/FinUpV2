import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import get_db_session, JournalEntry, BasePadrao
from app.utils.normalizer import normalizar_estabelecimento

session = get_db_session()

estabelecimentos = [
    'POUSADA CANTOS E C (1/4)',
    'IBERIA LINEA075252 (5/10)',
    'EBN *VPD TRAVEL (10/10)',
    'AZULEH87JC (12/12)'
]

print('=' * 80)
print('🔍 ANÁLISE DE TRANSAÇÕES NÃO CLASSIFICADAS')
print('=' * 80)

for estab_raw in estabelecimentos:
    print(f'\n📍 Estabelecimento: {estab_raw}')
    print('-' * 80)
    
    estab_norm = normalizar_estabelecimento(estab_raw)
    print(f'   Normalizado: {estab_norm}')
    
    # Busca em base_padroes
    padroes = session.query(BasePadrao).filter(
        BasePadrao.padrao_estabelecimento.like(f'%{estab_norm}%')
    ).all()
    
    if padroes:
        print(f'\n   ✅ EM BASE_PADROES:')
        for p in padroes:
            print(f'      Padrão: {p.padrao_estabelecimento}')
            print(f'      Grupo: {p.GRUPO} | Subgrupo: {p.SUBGRUPO} | Tipo: {p.TipoGasto}')
            print(f'      Confiança: {p.confianca} | Contagem: {p.contagem}')
    else:
        print(f'   ❌ NÃO em base_padroes')
    
    # Busca em journal_entries
    entries = session.query(JournalEntry).filter(
        JournalEntry.Estabelecimento.like(f'%{estab_norm}%'),
        JournalEntry.GRUPO.isnot(None)
    ).limit(3).all()
    
    if entries:
        print(f'\n   ✅ EM JOURNAL_ENTRIES:')
        for e in entries:
            print(f'      Estab: {e.Estabelecimento}')
            print(f'      Grupo: {e.GRUPO} | Subgrupo: {e.SUBGRUPO}')
            print(f'      IdParcela: {e.IdParcela}')
    else:
        print(f'   ❌ NÃO em journal_entries')

session.close()
