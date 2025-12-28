"""
Processador de Lógica de Negócio para Extrato de Conta Corrente

Versão: 3.0.0
Data: 27/12/2025
Status: stable

ATENÇÃO: Este arquivo foi SIMPLIFICADO.
- Transformação de dados específicos do banco → movida para preprocessors (utils/)
- Este arquivo contém APENAS lógica de negócio:
  * Classificação por sinal de valor (Receitas vs Despesas)
  * Metadados de negócio (DT_Fatura, TransacaoFutura, etc)
  * Normalização de estabelecimento

DataFrame de entrada já vem padronizado com:
- Colunas: ['data', 'lançamento', 'valor (R$)']
- Valores em formato float

Histórico:
- 3.0.0: Simplificação - preprocessamento movido para utils/
"""
import pandas as pd
from datetime import datetime
from app.utils.hasher import generate_id_transacao
from app.utils.normalizer import normalizar_estabelecimento, arredondar_2_decimais


def processar_extrato_conta(df, banco='Genérico', tipodocumento='Extrato', origem='Extrato', file_name=''):
    """
    Processa DataFrame de extrato de conta (já preprocessado)
    
    IMPORTANTE: Este processador espera que o DataFrame já venha padronizado
    pelo preprocessador do banco específico (extrato_itau.py, extrato_btg.py, etc).
    
    Args:
        df (DataFrame): DataFrame PADRONIZADO com ['data', 'lançamento', 'valor (R$)']
        banco (str): Nome do banco ('Itaú', 'BTG', 'Mercado Pago', etc)
        tipodocumento (str): 'Extrato'
        origem (str): Nome da origem para registro
        file_name (str): Nome do arquivo para referência
        
    Returns:
        list: Lista de transações processadas com metadados de negócio
    """
    print(f"\n🏦 Processando lógica de negócio - Extrato de Conta: {banco}")
    
    try:
        transacoes = []
        hash_counter = {}  # Contador para hashes duplicados no mesmo arquivo
        
        for idx, row in df.iterrows():
            data_br = row['data']
            estabelecimento_raw = str(row['lançamento']).strip()
            valor = float(row['valor (R$)'])
            
            # Ignora valores zero
            if valor == 0:
                continue
            
            # Extrai ano/mês da data
            try:
                dt = datetime.strptime(data_br, '%d/%m/%Y')
                ano = dt.year
                mes = f"{dt.month:02d}"
                dt_fatura = f"{ano}{mes}"
            except:
                # Fallback: mês atual
                now = datetime.now()
                ano = now.year
                mes = f"{now.month:02d}"
                dt_fatura = f"{ano}{mes}"
            
            # Define tipo de transação baseado no sinal
            if valor > 0:
                tipo_transacao = 'Receitas'
            else:
                tipo_transacao = 'Despesas'
            
            # Normaliza estabelecimento
            estabelecimento_norm = normalizar_estabelecimento(estabelecimento_raw)
            
            # Gera ID usando FNV-1a
            id_base = generate_id_transacao(data_br, estabelecimento_raw, valor)
            
            # Se o hash já existe no arquivo atual, adiciona sufixo
            if id_base in hash_counter:
                hash_counter[id_base] += 1
                id_transacao = f"{id_base}_{hash_counter[id_base]}"
            else:
                hash_counter[id_base] = 0
                id_transacao = id_base
            
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
                'banco': banco,
                'tipodocumento': tipodocumento,
                'forma_classificacao': 'Não Classificada',
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
        
        print(f"✓ {len(transacoes)} transações processadas")
        return transacoes
        
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"❌ ERRO AO PROCESSAR EXTRATO")
        print(f"{'='*60}")
        print(f"📄 Arquivo: {file_name}")
        print(f"🏦 Banco: {banco}")
        print(f"📋 Tipo: {tipodocumento}")
        print(f"⚠️  Erro: {type(e).__name__}")
        print(f"💬 Mensagem: {str(e)}")
        print(f"\n🔍 Traceback:")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        raise
