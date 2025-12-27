"""
Processador Genérico de Fatura de Cartão de Crédito
Aceita qualquer CSV/XLSX de fatura com mapeamento de colunas
"""
import pandas as pd
import re
from datetime import datetime
from app.utils.hasher import generate_id_transacao
from app.utils.normalizer import normalizar_estabelecimento, detectar_parcela, arredondar_2_decimais


def processar_fatura_cartao(df, mapeamento, origem='Fatura', file_name=''):
    """
    Processa DataFrame de fatura de cartão de crédito
    
    Args:
        df (DataFrame): DataFrame com os dados da fatura
        mapeamento (dict): {'data': col, 'estabelecimento': col, 'valor': col}
        origem (str): Nome da origem (ex: 'Fatura Itaú', 'Fatura Nubank')
        file_name (str): Nome do arquivo para extrair mês/ano
        
    Returns:
        list: Lista de transações processadas
    """
    print(f"\n💳 Processando Fatura de Cartão: {origem}")
    
    # Guarda os nomes originais das colunas
    col_data = mapeamento['data']
    col_estabelecimento = mapeamento['estabelecimento']
    col_valor = mapeamento['valor']
    
    try:
        df_trabalho = df.copy()
        transacoes = []
        contador_seq = 0
        hash_counter = {}  # Contador para hashes duplicados no mesmo arquivo
        
        # Tenta extrair ano/mês do nome do arquivo (formato: algo-AAAAMM.extensão)
        match = re.search(r'-(\d{4})(\d{2})', file_name)
        if match:
            ano_fatura = int(match.group(1))
            mes_fatura = match.group(2)
            dt_fatura = f"{ano_fatura}{mes_fatura}"
        else:
            # Fallback: usa data da primeira linha
            try:
                first_date = pd.to_datetime(df_trabalho['data'].iloc[0])
                ano_fatura = first_date.year
                mes_fatura = f"{first_date.month:02d}"
                dt_fatura = f"{ano_fatura}{mes_fatura}"
            except:
                # Última opção: mês atual
                now = datetime.now()
                ano_fatura = now.year
                mes_fatura = f"{now.month:02d}"
                dt_fatura = f"{ano_fatura}{mes_fatura}"
        
        # Detecta e agrupa parcelas
        parcelas_map = {}
        
        for idx, row in df_trabalho.iterrows():
            contador_seq += 1
            
            # Extrai dados usando os nomes originais das colunas
            data_raw = row[col_data]
            estabelecimento_raw = str(row[col_estabelecimento]).strip()
            valor_raw = row[col_valor]
            
            # Ignora pagamentos/estornos comuns
            if any(termo in estabelecimento_raw.upper() for termo in [
                'PAGAMENTO EFETUADO', 'PAGAMENTO RECEBIDO', 'CRÉDITO FATURA'
            ]):
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
            except:
                # Se falhar, usa data atual
                dt = datetime.now()
                data_br = dt.strftime('%d/%m/%Y')
                ano = dt.year
            
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
            
            # IMPORTANTE: Inverte sinal para padronizar
            # CSV: despesas positivas, estornos negativos
            # Banco: despesas negativas, estornos positivos
            valor = -valor
            
            # Detecta parcela
            parcela_info = detectar_parcela(estabelecimento_raw, origem)
            
            if parcela_info:
                # Tem parcela - remove a parte XX/YY do estabelecimento
                parcela_atual = parcela_info['parcela']
                total_parcelas = parcela_info['total']
                # Remove " 01/12" do final do estabelecimento
                estabelecimento_base = re.sub(r'\s*\d{1,2}/\d{1,2}\s*$', '', estabelecimento_raw).strip()
                
                # Cria chave para agrupar - inclui valor para diferenciar compras distintas
                # FIX: Adiciona valor na chave para evitar misturar compras diferentes
                # com mesmo estabelecimento e quantidade de parcelas
                chave = f"{estabelecimento_base}_{total_parcelas}_{abs(valor):.2f}"
                
                if chave not in parcelas_map:
                    parcelas_map[chave] = {
                        'estabelecimento': estabelecimento_base,
                        'total_parcelas': total_parcelas,
                        'linhas': []
                    }
                
                parcelas_map[chave]['linhas'].append({
                    'parcela': parcela_atual,
                    'data': data_br,
                    'valor': valor,
                    'ano': ano,
                    'estabelecimento_original': estabelecimento_raw
                })
            else:
                # Não tem parcela - adiciona direto
                # Gera ID base consistente com o banco de dados (FNV-1a)
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
                    'IdParcela': None,  # Transações sem parcela não têm IdParcela
                    'Data': data_br,
                    'Estabelecimento': estabelecimento_raw,
                    'Valor': arredondar_2_decimais(valor),
                    'ValorPositivo': abs(arredondar_2_decimais(valor)),
                    'TipoTransacao': 'Cartão de Crédito',
                    'TipoTransacaoAjuste': 'Cartão de Crédito',
                    'Ano': ano,
                    'DT_Fatura': dt_fatura,
                    'NomeTitular': None,
                    'DataPostagem': data_br,
                    'origem': origem,
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
        
        # Processa parcelas agrupadas
        parcelas_processadas = 0
        for chave, info in parcelas_map.items():
            linhas_parcelas = info['linhas']
            total_parcelas = info['total_parcelas']
            estabelecimento_base = info['estabelecimento']
            
            # Ordena por número de parcela
            linhas_parcelas.sort(key=lambda x: x['parcela'])
            
            # Gera IdParcela único para todas as parcelas desta compra
            # Baseia-se no estabelecimento + valor unitário + total de parcelas
            # Usa hash simples sem data pois queremos agrupar todas as parcelas
            valor_primeira_parcela = linhas_parcelas[0]['valor'] if linhas_parcelas else 0
            import hashlib
            
            # FIX: Normaliza estabelecimento para garantir mesmo hash independente de maiúsculas/minúsculas
            estab_norm_hash = normalizar_estabelecimento(estabelecimento_base)
            chave_parcela = f"{estab_norm_hash}|{abs(valor_primeira_parcela):.2f}|{total_parcelas}"
            id_parcela = hashlib.md5(chave_parcela.encode()).hexdigest()[:16]
            
            parcelas_processadas += len(linhas_parcelas)
            
            # Gera uma transação para cada parcela
            for parcela_data in linhas_parcelas:
                contador_seq += 1
                parcela_num = parcela_data['parcela']
                
                # Reconstrói nome com parcela para gerar ID correto
                nome_com_parcela = f"{estabelecimento_base} ({parcela_num}/{total_parcelas})"
                
                # ID base único com parcela (consistente com banco de dados)
                id_base = generate_id_transacao(parcela_data['data'], nome_com_parcela, parcela_data['valor'])
                
                # Se o hash já existe no arquivo atual, adiciona sufixo
                if id_base in hash_counter:
                    hash_counter[id_base] += 1
                    id_transacao = f"{id_base}_{hash_counter[id_base]}"
                else:
                    hash_counter[id_base] = 0
                    id_transacao = id_base
                
                # Verifica se é futura
                try:
                    data_trans = datetime.strptime(parcela_data['data'], '%d/%m/%Y')
                    eh_futura = data_trans > datetime.now()
                except:
                    eh_futura = False
                
                # VALIDAÇÃO CRÍTICA: IdParcela NUNCA pode ser None para transações parceladas
                if not id_parcela:
                    raise ValueError(f"IdParcela está None para transação parcelada: {estabelecimento_base} ({parcela_num}/{total_parcelas})")
                
                transacoes.append({
                    'IdTransacao': id_transacao,
                    'IdParcela': id_parcela,  # SEMPRE gerado para parcelas
                    'parcela_atual': parcela_num,  # Adiciona número da parcela para deduplicação
                    'Data': parcela_data['data'],
                    'Estabelecimento': f"{estabelecimento_base} ({parcela_num}/{total_parcelas})",
                    'Valor': arredondar_2_decimais(parcela_data['valor']),
                    'ValorPositivo': abs(arredondar_2_decimais(parcela_data['valor'])),
                    'TipoTransacao': 'Cartão de Crédito',
                    'TipoTransacaoAjuste': 'Cartão de Crédito',
                    'Ano': parcela_data['ano'],
                    'DT_Fatura': dt_fatura,
                    'NomeTitular': None,
                    'DataPostagem': parcela_data['data'],
                    'origem': origem,
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
        
        print(f"✓ {len(transacoes)} transações extraídas da fatura")
        if parcelas_processadas > 0:
            print(f"  ⚡ {parcelas_processadas} transações parceladas com IdParcela gerado")
        return transacoes
        
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"❌ ERRO DETALHADO AO PROCESSAR FATURA")
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
