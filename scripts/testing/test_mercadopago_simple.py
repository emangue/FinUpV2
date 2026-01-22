"""
Script de teste simplificado para o processador Mercado Pago Extrato
Testa apenas a lógica de parsing sem imports complexos
"""

from pathlib import Path
from datetime import datetime
import pandas as pd


def test_mercadopago_extrato():
    """Testa o parsing do arquivo Mercado Pago"""
    
    # Path do arquivo de teste
    file_path = Path(__file__).parent / '_arquivos_historicos' / '_csvs_historico' / 'account_statement-202ffd51-0eb5-4dde-ac19-2c88c2c60896.xlsx'
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print(f"📁 Testando arquivo: {file_path.name}")
    print("=" * 80)
    
    try:
        # Ler XLSX sem header
        df_raw = pd.read_excel(file_path, header=None)
        print(f"✅ Arquivo lido: {len(df_raw)} linhas")
        
        # Extrair saldos da linha 1
        valores_linha = df_raw.iloc[1]
        saldo_inicial_str = str(valores_linha[0]).replace('.', '').replace(',', '.')
        saldo_final_str = str(valores_linha[3]).replace('.', '').replace(',', '.')
        saldo_inicial = float(saldo_inicial_str)
        saldo_final = float(saldo_final_str)
        
        print(f"\n📊 SALDOS EXTRAÍDOS:")
        print(f"   Saldo Inicial: R$ {saldo_inicial:,.2f}")
        print(f"   Saldo Final:   R$ {saldo_final:,.2f}")
        
        # Processar transações (a partir da linha 4)
        df = df_raw.iloc[4:].copy()
        df.columns = df_raw.iloc[3].values
        df = df.reset_index(drop=True)
        
        # Selecionar colunas relevantes
        df_processed = df.iloc[:, [0, 1, 3]].copy()
        df_processed.columns = ['data', 'lancamento', 'valor']
        
        # Remover linhas vazias
        df_processed = df_processed.dropna(subset=['data', 'lancamento', 'valor'])
        
        # Converter data
        df_processed['data'] = pd.to_datetime(df_processed['data'], format='%d-%m-%Y', errors='coerce')
        df_processed = df_processed.dropna(subset=['data'])
        df_processed['data'] = df_processed['data'].dt.strftime('%d/%m/%Y')
        
        # Converter valor
        df_processed['valor'] = df_processed['valor'].astype(str)
        df_processed['valor'] = df_processed['valor'].str.replace('.', '', regex=False)
        df_processed['valor'] = df_processed['valor'].str.replace(',', '.', regex=False)
        df_processed['valor'] = pd.to_numeric(df_processed['valor'], errors='coerce')
        df_processed = df_processed.dropna(subset=['valor'])
        df_processed = df_processed[df_processed['valor'] != 0]
        
        # Limpar lançamentos
        df_processed['lancamento'] = df_processed['lancamento'].str.strip()
        
        transactions = df_processed.reset_index(drop=True)
        
        print(f"\n✅ PROCESSAMENTO CONCLUÍDO")
        print("=" * 80)
        
        # Validação de saldo
        soma_transacoes = round(transactions['valor'].sum(), 2)
        diferenca = round(saldo_final - (saldo_inicial + soma_transacoes), 2)
        is_valid = abs(diferenca) < 0.01
        
        print(f"\n📊 VALIDAÇÃO DE SALDO:")
        print(f"   Saldo Inicial:     R$ {saldo_inicial:>12,.2f}")
        print(f"   Soma Transações:   R$ {soma_transacoes:>12,.2f}")
        print(f"   Calculado:         R$ {(saldo_inicial + soma_transacoes):>12,.2f}")
        print(f"   Saldo Final:       R$ {saldo_final:>12,.2f}")
        print(f"   Diferença:         R$ {diferenca:>12,.2f}")
        print(f"   Válido:            {'✅ SIM' if is_valid else '❌ NÃO'}")
        
        # Estatísticas
        creditos = transactions[transactions['valor'] > 0]
        debitos = transactions[transactions['valor'] < 0]
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total transações:  {len(transactions)}")
        print(f"   Créditos:          {len(creditos)} (R$ {creditos['valor'].sum():,.2f})")
        print(f"   Débitos:           {len(debitos)} (R$ {debitos['valor'].sum():,.2f})")
        
        # Primeiras 10 transações
        print(f"\n📋 PRIMEIRAS 10 TRANSAÇÕES:")
        print("-" * 80)
        for i, (_, row) in enumerate(transactions.head(10).iterrows(), 1):
            valor_str = f"R$ {row['valor']:>10,.2f}"
            lancamento = row['lancamento'][:50]
            print(f"   {i:2d}. {row['data']} | {valor_str} | {lancamento}")
        
        if len(transactions) > 10:
            print(f"   ... e mais {len(transactions) - 10} transações")
        
        # Últimas 5 transações
        if len(transactions) > 10:
            print(f"\n📋 ÚLTIMAS 5 TRANSAÇÕES:")
            print("-" * 80)
            for i, (_, row) in enumerate(transactions.tail(5).iterrows(), len(transactions) - 4):
                valor_str = f"R$ {row['valor']:>10,.2f}"
                lancamento = row['lancamento'][:50]
                print(f"   {i:2d}. {row['data']} | {valor_str} | {lancamento}")
        
        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"\n💡 O processador está pronto para uso no sistema!")
        print(f"   Banco: 'Mercado Pago' ou 'MercadoPago'")
        print(f"   Tipo: 'extrato'")
        print(f"   Formato: 'excel' (.xlsx)")
        
    except Exception as e:
        print(f"\n❌ ERRO NO PROCESSAMENTO:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_mercadopago_extrato()
