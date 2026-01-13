#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend')

from app.domains.upload.processors.raw.itau_extrato import process_itau_extrato

arquivo = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/_csvs_historico/extrato_itau.xls'

print(f"Testando processamento: {arquivo}")
print()

try:
    transactions, balance = process_itau_extrato(arquivo, 'extrato_itau.xls')
    print(f"✅ Transações processadas: {len(transactions)}")
    print()
    
    # Verificar se tem transação futura (29/12/2025)
    tem_futura = False
    for t in transactions:
        if '29/12/2025' in t.data:
            print(f"❌ ERRO: Transação futura detectada: {t.data} - {t.lancamento} - {t.valor}")
            tem_futura = True
    
    if not tem_futura:
        print("✅ Nenhuma transação futura detectada!")
    
    print()
    print(f"Saldo inicial: {balance.saldo_inicial}")
    print(f"Saldo final: {balance.saldo_final}")
    print(f"Soma transações: {balance.soma_transacoes}")
    print(f"Validação: {'✅ Válido' if balance.is_valid else f'⚠️ Diferença: {balance.diferenca}'}")
    
    # Mostrar últimas 3 transações
    print()
    print("Últimas 3 transações:")
    for t in transactions[-3:]:
        print(f"  {t.data} - {t.lancamento} - R$ {t.valor}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
