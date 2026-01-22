"""
Script de teste para o processador Mercado Pago Extrato
"""

import sys
from pathlib import Path

# Adicionar path do backend ao sys.path
backend_path = Path(__file__).parent / 'app_dev' / 'backend'
sys.path.insert(0, str(backend_path))

from app.domains.upload.processors.raw.excel.mercadopago_extrato import (
    process_mercadopago_extrato
)


def test_mercadopago_extrato():
    """Testa o processador de extrato Mercado Pago"""
    
    # Path do arquivo de teste
    file_path = Path(__file__).parent / '_arquivos_historicos' / '_csvs_historico' / 'account_statement-202ffd51-0eb5-4dde-ac19-2c88c2c60896.xlsx'
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print(f"📁 Testando arquivo: {file_path.name}")
    print("=" * 80)
    
    try:
        # Processar arquivo
        transactions, balance = process_mercadopago_extrato(
            file_path=file_path,
            nome_arquivo=file_path.name
        )
        
        # Exibir resultados
        print(f"\n✅ PROCESSAMENTO CONCLUÍDO")
        print("=" * 80)
        
        # Validação de saldo
        print(f"\n📊 VALIDAÇÃO DE SALDO:")
        print(f"   Saldo Inicial:     R$ {balance.saldo_inicial:,.2f}")
        print(f"   Soma Transações:   R$ {balance.soma_transacoes:,.2f}")
        print(f"   Saldo Final:       R$ {balance.saldo_final:,.2f}")
        print(f"   Diferença:         R$ {balance.diferenca:,.2f}")
        print(f"   Válido:            {'✅ SIM' if balance.is_valid else '❌ NÃO'}")
        
        # Estatísticas
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total transações:  {len(transactions)}")
        
        creditos = [t for t in transactions if t.valor > 0]
        debitos = [t for t in transactions if t.valor < 0]
        
        print(f"   Créditos:          {len(creditos)} (R$ {sum(t.valor for t in creditos):,.2f})")
        print(f"   Débitos:           {len(debitos)} (R$ {sum(t.valor for t in debitos):,.2f})")
        
        # Primeiras 10 transações
        print(f"\n📋 PRIMEIRAS 10 TRANSAÇÕES:")
        print("-" * 80)
        for i, t in enumerate(transactions[:10], 1):
            valor_str = f"R$ {t.valor:>10,.2f}"
            print(f"   {i:2d}. {t.data} | {valor_str} | {t.lancamento[:50]}")
        
        if len(transactions) > 10:
            print(f"   ... e mais {len(transactions) - 10} transações")
        
        # Últimas 5 transações
        if len(transactions) > 10:
            print(f"\n📋 ÚLTIMAS 5 TRANSAÇÕES:")
            print("-" * 80)
            for i, t in enumerate(transactions[-5:], len(transactions) - 4):
                valor_str = f"R$ {t.valor:>10,.2f}"
                print(f"   {i:2d}. {t.data} | {valor_str} | {t.lancamento[:50]}")
        
        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO NO PROCESSAMENTO:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_mercadopago_extrato()
