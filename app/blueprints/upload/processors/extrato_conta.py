"""
Processador Genérico de Extrato de Conta Corrente
Aceita qualquer CSV/XLSX de extrato com mapeamento de colunas
"""
import pandas as pd
import re
from datetime import datetime
from utils.hasher import generate_id_simples
from utils.normalizer import normalizar_estabelecimento, arredondar_2_decimais


def processar_extrato_conta(df, mapeamento, origem='Extrato', file_name=''):
    """
    Processa DataFrame de extrato de conta corrente
    
    Args:
        df (DataFrame): DataFrame com os dados do extrato
        mapeamento (dict): {'data': col, 'estabelecimento': col, 'valor': col}
        origem (str): Nome da origem (ex: 'Extrato Itaú', 'Extrato Nubank')
        file_name (str): Nome do arquivo para referência
        
    Returns:
        list: Lista de transações processadas
    """
    print(f"\n🏦 Processando Extrato de Conta: {origem}")
    
    # Guarda os nomes originais das colunas
    col_data = mapeamento['data']
    col_estabelecimento = mapeamento['estabelecimento']
    col_valor = mapeamento['valor']
    
    try:
        df_trabalho = df.copy()
        transacoes = []
        contador_seq = 0
        
        for idx, row in df_trabalho.iterrows():
            contador_seq += 1
            
            # Extrai dados usando os nomes originais das colunas
            data_raw = row[col_data]
            estabelecimento_raw = str(row[col_estabelecimento]).strip()
            valor_raw = row[col_valor]
            
            # Ignora linhas de saldo ou resumo
            if any(termo in estabelecimento_raw.upper() for termo in [
                'SALDO DO DIA', 'SALDO ANTERIOR', 'SALDO FINAL', 'TOTAL'
            ]):
                continue
            
            # Ignora se estabelecimento estiver vazio
            if not estabelecimento_raw or estabelecimento_raw == 'nan':
                continue
            
            # Converte data para DD/MM/AAAA
            try:
                if isinstance(data_raw, str):
                    # Tenta vários formatos
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                        try:
                            dt = datetime.strptime(data_raw, fmt)
                            break
                        except:
                            continue
                    else:
                        dt = pd.to_datetime(data_raw)
                else:
                    dt = pd.to_datetime(data_raw)
                
                data_br = dt.strftime('%d/%m/%Y')
                ano = dt.year
                mes = f"{dt.month:02d}"
                dt_fatura = f"{ano}{mes}"
            except:
                print(f"⚠️  Data inválida na linha {idx}: {data_raw}")
                continue
            
            # Converte valor
            try:
                if isinstance(valor_raw, str):
                    # Remove pontos de milhar e substitui vírgula por ponto
                    valor = float(valor_raw.replace('.', '').replace(',', '.'))
                else:
                    valor = float(valor_raw)
            except:
                print(f"⚠️  Valor inválido na linha {idx}: {valor_raw}")
                continue
            
            # Define tipo de transação baseado no sinal
            if valor > 0:
                tipo_transacao = 'Receitas'
            elif valor < 0:
                tipo_transacao = 'Despesas'
            else:
                # Valor zero - ignora
                continue
            
            # Normaliza estabelecimento
            estabelecimento_norm = normalizar_estabelecimento(estabelecimento_raw)
            
            # Gera ID único
            id_transacao = f"{generate_id_simples(data_br, estabelecimento_norm, valor)}_{contador_seq}"
            
            # Verifica se é futura
            try:
                data_trans = datetime.strptime(data_br, '%d/%m/%Y')
                eh_futura = data_trans > datetime.now()
            except:
                eh_futura = False
            
            transacoes.append({
                'IdTransacao': id_transacao,
                'Data': data_br,
                'Estabelecimento': estabelecimento_raw,
                'Valor': arredondar_2_decimais(valor),
                'ValorPositivo': abs(arredondar_2_decimais(valor)),
                'TipoTransacao': tipo_transacao,
                'TipoTransacaoAjuste': tipo_transacao,
                'Ano': ano,
                'DT_Fatura': dt_fatura,
                'NomeTitular': None,
                'DataPostagem': None,
                'origem': origem,
                'MarcacaoIA': None,
                'ValidarIA': None,
                'TipoGasto': None,
                'GRUPO': None,
                'SUBGRUPO': None,
                'TransacaoFutura': 'SIM' if eh_futura else 'NÃO',
                'TipoLancamento': None,
                'CartaoCodigo8': None,
                'FinalCartao': None
            })
        
        print(f"✓ {len(transacoes)} transações extraídas do extrato")
        return transacoes
        
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"❌ ERRO DETALHADO AO PROCESSAR EXTRATO")
        print(f"{'='*60}")
        print(f"📄 Arquivo: {file_name}")
        print(f"📋 Mapeamento recebido: {mapeamento}")
        print(f"📊 Colunas disponíveis no DataFrame: {list(df.columns)}")
        print(f"⚠️  Tipo do erro: {type(e).__name__}")
        print(f"💬 Mensagem: {str(e)}")
        print(f"\n🔍 Traceback completo:")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        raise
