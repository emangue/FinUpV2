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
print('🔍 BUSCANDO TRANSAÇÕES POR SIMILARIDADE')
print('=' * 80)

for estab_raw in estabelecimentos:
    print(f'\n📍 Estabelecimento: {estab_raw}')
    print('-' * 80)
    
    estab_norm = normalizar_estabelecimento(estab_raw)
    print(f'   Normalizado: {estab_norm}')
    
    # Quebra em palavras para buscar por partes
    palavras = estab_norm.split()
    
    for palavra in palavras:
        if len(palavra) >= 4:  # Só palavras com 4+ caracteres
            print(f'\n   🔍 Buscando por: "{palavra}"')
            
            # Busca em journal_entries
            entries = session.query(JournalEntry).filter(
                JournalEntry.Estabelecimento.like(f'%{palavra}%'),
                JournalEntry.GRUPO.isnot(None)
            ).limit(5).all()
            
            if entries:
                print(f'   ✅ ENCONTRADAS {len(entries)} TRANSAÇÕES SIMILARES:')
                for e in entries:
                    print(f'      - {e.Estabelecimento}')
                    print(f'        Grupo: {e.GRUPO} | Subgrupo: {e.SUBGRUPO}')
                    print(f'        Data: {e.Data} | Valor: R$ {e.Valor:.2f}')
                    print(f'        IdParcela: {e.IdParcela}')
                    print()
            
            # Busca em base_padroes
            padroes = session.query(BasePadrao).filter(
                BasePadrao.padrao_estabelecimento.like(f'%{palavra}%')
            ).limit(3).all()
            
            if padroes:
                print(f'   ✅ ENCONTRADOS {len(padroes)} PADRÕES SIMILARES:')
                for p in padroes:
                    print(f'      - {p.padrao_estabelecimento}')
                    print(f'        Grupo: {p.grupo_sugerido} | Subgrupo: {p.subgrupo_sugerido}')
                    print(f'        Confiança: {p.confianca} | Contagem: {p.contagem}')
                    print(f'        Valor Médio: R$ {p.valor_medio:.2f} | Exemplos: {p.exemplos}')
                    print()

session.close()