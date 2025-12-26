"""
Processador de Fatura Itaú (CSV)
"""
import pandas as pd
import re
from datetime import datetime
from utils.hasher import generate_id_simples
from utils.normalizer import normalizar_estabelecimento, detectar_parcela, arredondar_2_decimais


def processar_fatura_itau(file_path, file_name):
    """
    Processa arquivo CSV de Fatura do Itaú
    
    Args:
        file_path (str): Caminho do arquivo
        file_name (str): Nome do arquivo
        
    Returns:
        list: Lista de transações processadas
    """
    print(f"\n📄 Processando Fatura Itaú: {file_name}")
    
    try:
        # Lê CSV
        df = pd.read_csv(file_path)
        
        # Valida colunas necessárias
        required_cols = ['data', 'lançamento', 'valor']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV deve conter colunas: {required_cols}")
        
        transacoes = []
        contador_seq = 0  # Contador para garantir IDs únicos
        
        # Extrai ano/mês do nome do arquivo (fatura_itau-202512.csv)
        match = re.search(r'fatura_itau-(\d{4})(\d{2})', file_name)
        if match:
            ano_fatura = int(match.group(1))
            mes_fatura = match.group(2)
            dt_fatura = f"{ano_fatura}{mes_fatura}"
        else:
            # Fallback: usa data da primeira linha
            first_date = pd.to_datetime(df['data'].iloc[0])
            ano_fatura = first_date.year
            mes_fatura = f"{first_date.month:02d}"
            dt_fatura = f"{ano_fatura}{mes_fatura}"
        
        # Detecta parcelas e agrupa
        parcelas_map = {}  # {estabelecimento_base: {total_parcelas: [linhas]}}
        
        for idx, row in df.iterrows():
            contador_seq += 1  # Incrementa contador
            data_iso = row['data']  # YYYY-MM-DD
            lancamento = str(row['lançamento']).strip()
            valor = float(row['valor'])
            
            # Ignora pagamentos da fatura
            if 'PAGAMENTO EFETUADO' in lancamento.upper():
                continue
            
            # Converte data para DD/MM/AAAA
            try:
                dt = datetime.strptime(data_iso, '%Y-%m-%d')
                data_br = dt.strftime('%d/%m/%Y')
                ano = dt.year
            except:
                continue
            
            # Inverte o sinal do valor da fatura
            valor = -valor
            
            # Detecta parcela
            parcela_info = detectar_parcela(lancamento, 'Fatura Itaú')
            
            if parcela_info:
                # Tem parcela
                parcela_atual = parcela_info['parcela']
                total_parcelas = parcela_info['total']
                
                # Remove parcela do nome
                estabelecimento_base = normalizar_estabelecimento(lancamento)
                valor_parcela = abs(valor)
                valor_total = arredondar_2_decimais(valor_parcela * total_parcelas)
                
                # Agrupa para detectar menor parcela
                key = f"{estabelecimento_base}|{valor_parcela:.2f}|{total_parcelas}"
                if key not in parcelas_map:
                    parcelas_map[key] = []
                
                parcelas_map[key].append({
                    'data': data_br,
                    'estabelecimento': lancamento,
                    'valor': valor,
                    'ano': ano,
                    'parcela_atual': parcela_atual,
                    'total_parcelas': total_parcelas,
                    'estabelecimento_base': estabelecimento_base,
                    'valor_total': valor_total,
                    'seq': contador_seq  # Adiciona sequencial
                })
            else:
                # Sem parcela
                # Adiciona contador sequencial para garantir unicidade
                id_transacao = f"{generate_id_simples(data_br, lancamento, valor)}_{contador_seq}"
                
                transacoes.append({
                    'IdTransacao': id_transacao,
                    'Data': data_br,
                    'Estabelecimento': lancamento,
                    'Valor': valor,
                    'ValorPositivo': abs(valor),
                    'TipoTransacao': 'Cartão de Crédito',
                    'TipoTransacaoAjuste': 'Cartão de Crédito',
                    'Ano': ano,
                    'DT_Fatura': dt_fatura,
                    'NomeTitular': None,
                    'DataPostagem': data_br,
                    'origem': 'Fatura Itaú',
                    'MarcacaoIA': None,
                    'ValidarIA': None,
                    'TipoGasto': None,
                    'GRUPO': None,
                    'SUBGRUPO': None,
                    'TransacaoFutura': 'NÃO',
                    'TipoLancamento': 'Nacional',
                    'CartaoCodigo8': None,
                    'FinalCartao': None
                })
        
        # Processa parcelas agrupadas
        for key, parcelas_list in parcelas_map.items():
            # Encontra menor parcela
            menor_parcela = min(p['parcela_atual'] for p in parcelas_list)
            
            for parcela_data in parcelas_list:
                eh_futura = parcela_data['parcela_atual'] > menor_parcela
                
                # Adiciona contador sequencial para garantir unicidade
                id_transacao = f"{generate_id_simples(parcela_data['data'], parcela_data['estabelecimento'], parcela_data['valor'])}_{parcela_data['seq']}"
                
                transacoes.append({
                    'IdTransacao': id_transacao,
                    'Data': parcela_data['data'],
                    'Estabelecimento': parcela_data['estabelecimento'],
                    'Valor': parcela_data['valor'],
                    'ValorPositivo': abs(parcela_data['valor']),
                    'TipoTransacao': 'Cartão de Crédito',
                    'TipoTransacaoAjuste': 'Cartão de Crédito',
                    'Ano': parcela_data['ano'],
                    'DT_Fatura': dt_fatura,
                    'NomeTitular': None,
                    'DataPostagem': parcela_data['data'],
                    'origem': 'Fatura Itaú',
                    'MarcacaoIA': None,
                    'ValidarIA': None,
                    'TipoGasto': None,
                    'GRUPO': None,
                    'SUBGRUPO': None,
                    'TransacaoFutura': 'SIM' if eh_futura else 'NÃO',
                    'TipoLancamento': 'Nacional',
                    'CartaoCodigo8': None,
                    'FinalCartao': None
                })
        
        print(f"✓ {len(transacoes)} transações extraídas")
        return transacoes
        
    except Exception as e:
        print(f"❌ Erro ao processar fatura: {e}")
        raise
