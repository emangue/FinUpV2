#!/usr/bin/env python3
"""Teste de debug do marker"""

from app.domains.upload.processors.raw.base import RawTransaction
from app.domains.upload.processors.marker import TransactionMarker

# Criar marker novo
marker = TransactionMarker()
print('Estado inicial:', marker.seen_transactions)
print()

# Primeira transação
raw1 = RawTransaction(
    banco='itau', tipo_documento='extrato', nome_arquivo='test.xls',
    data_criacao='2026-01-10', data='15/10/2025',
    lancamento='PIX TRANSF EMANUEL15/10', valor=-1000.0,
    nome_cartao=None, final_cartao=None, mes_fatura=None
)

marked1 = marker.mark_transaction(raw1)
print(f'Trans 1: {marked1.lancamento}')
print(f'IdTransacao: {marked1.id_transacao}')
print(f'Estado após trans1: {marker.seen_transactions}')
print()

# Segunda transação (mesmo dia, mesmo estabelecimento, mesmo valor - duplicata real)
raw2 = RawTransaction(
    banco='itau', tipo_documento='extrato', nome_arquivo='test.xls',
    data_criacao='2026-01-10', data='15/10/2025',
    lancamento='PIX TRANSF EMANUEL15/10', valor=-1000.0,
    nome_cartao=None, final_cartao=None, mes_fatura=None
)

marked2 = marker.mark_transaction(raw2)
print(f'Trans 2: {marked2.lancamento}')
print(f'IdTransacao: {marked2.id_transacao}')
print(f'Estado após trans2: {marker.seen_transactions}')
print()

print('Hashes gerados:')
print(f'Trans 1 (seq 1): {marked1.id_transacao}')
print(f'Trans 2 (seq 2): {marked2.id_transacao}')
print(f'Esperado seq 1: 16634046522838173011')
print(f'Esperado seq 2: 8119916638940476640')
