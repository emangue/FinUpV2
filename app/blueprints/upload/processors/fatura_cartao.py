"""
Processador de Lógica de Negócio para Fatura de Cartão de Crédito

Versão: 3.0.0
Data: 27/12/2025
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

ATENÇÃO: Este arquivo foi SIMPLIFICADO.
- Transformação de dados específicos do banco → movida para preprocessors (utils/)
- Este arquivo contém APENAS lógica de negócio:
  * Detecção e agrupamento de parcelas
  * Geração de IdParcela único
  * Inversão de sinal de valores
  * Classificação de tipo de transação
  * Metadados de negócio (DT_Fatura, TransacaoFutura, etc)

DataFrame de entrada já vem padronizado com:
- Colunas: ['data', 'lançamento', 'valor (R$)']
- Valores em formato float

Histórico:
- 2.0.0: Otimização de performance (bulk insert, correção N+1 query)
- 2.1.0: Sistema de versionamento implementado
- 3.0.0: Simplificação - preprocessamento movido para utils/
"""
import pandas as pd
import re
from datetime import datetime
from app.utils.hasher import generate_id_transacao
from app.utils.normalizer import normalizar_estabelecimento, detectar_parcela, arredondar_2_decimais


def processar_fatura_cartao(df, banco='Genérico', tipodocumento='Fatura Cartão de Crédito', origem='Fatura', file_name=''):
    """
    Processa DataFrame de fatura de cartão (já preprocessado)
    
    IMPORTANTE: Este processador espera que o DataFrame já venha padronizado
    pelo preprocessador do banco específico (fatura_itau.py, etc).
    
    Args:
        df (DataFrame): DataFrame PADRONIZADO com ['data', 'lançamento', 'valor (R$)']
        banco (str): Nome do banco ('Itaú', 'BTG', 'Nubank', etc)
        tipodocumento (str): 'Fatura Cartão de Crédito'
        origem (str): Nome da origem para registro
        file_name (str): Nome do arquivo para extrair mês/ano
        
    Returns:
        list: Lista de transações processadas com metadados de negócio
    """
    print(f"\n💳 Processando lógica de negócio - Fatura de Cartão: {banco}")
    
    try:
        transacoes = []
        hash_counter = {}  # Contador para hashes duplicados no mesmo arquivo
        
        # Extrai ano/mês do nome do arquivo (formato: algo-AAAAMM.extensão)
        match = re.search(r'-(\d{4})(\d{2})', file_name)
        if match:
            ano_fatura = int(match.group(1))
            mes_fatura = match.group(2)
            dt_fatura = f"{ano_fatura}{mes_fatura}"
        else:
            # Fallback: usa data da primeira linha
            try:
                first_date = pd.to_datetime(df['data'].iloc[0], format='%d/%m/%Y')
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
        
        for idx, row in df.iterrows():
            data_br = row['data']
            estabelecimento_raw = str(row['lançamento']).strip()
            valor = float(row['valor (R$)'])
            
            # Ignora valores zero
            if valor == 0:
                continue
            
            # Extrai ano da data
            try:
                dt = datetime.strptime(data_br, '%d/%m/%Y')
                ano = dt.year
            except:
                ano = ano_fatura
            
            # IMPORTANTE: Inverte sinal para padronizar
            # Preprocessador retorna valores positivos, mas banco precisa negativos
            valor = -abs(valor)
            
            # Detecta parcela
            parcela_info = detectar_parcela(estabelecimento_raw, origem)
            
            if parcela_info:
                # Tem parcela - remove a parte XX/YY do estabelecimento
                parcela_atual = parcela_info['parcela']
                total_parcelas = parcela_info['total']
                # Remove " 01/12" do final do estabelecimento
                estabelecimento_base = re.sub(r'\s*\d{1,2}/\d{1,2}\s*$', '', estabelecimento_raw).strip()
                
                # Cria chave para agrupar - inclui valor para diferenciar compras distintas
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
                # Gera ID base consistente (FNV-1a)
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
                    'Ano': ano,
                    'MesFatura': dt_fatura,
                    'DataPostagem': data_br,
                    'banco_origem': banco,
                    'tipodocumento': tipodocumento,
                    'origem_classificacao': 'Não Classificada',
                    'arquivo_origem': file_name,
                    'TipoGasto': None,
                    'GRUPO': None,
                    'SUBGRUPO': None
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
            valor_primeira_parcela = linhas_parcelas[0]['valor'] if linhas_parcelas else 0
            import hashlib
            
            # Normaliza estabelecimento para garantir mesmo hash
            estab_norm_hash = normalizar_estabelecimento(estabelecimento_base)
            chave_parcela = f"{estab_norm_hash}|{abs(valor_primeira_parcela):.2f}|{total_parcelas}"
            id_parcela = hashlib.md5(chave_parcela.encode()).hexdigest()[:16]
            
            parcelas_processadas += len(linhas_parcelas)
            
            # Gera uma transação para cada parcela
            for parcela_data in linhas_parcelas:
                parcela_num = parcela_data['parcela']
                
                # Reconstrói nome com parcela para gerar ID correto
                nome_com_parcela = f"{estabelecimento_base} ({parcela_num}/{total_parcelas})"
                
                # ID base único com parcela
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
                    'parcela_atual': parcela_num,  # Para deduplicação
                    'Data': parcela_data['data'],
                    'Estabelecimento': f"{estabelecimento_base} ({parcela_num}/{total_parcelas})",
                    'Valor': arredondar_2_decimais(parcela_data['valor']),
                    'ValorPositivo': abs(arredondar_2_decimais(parcela_data['valor'])),
                    'TipoTransacao': 'Cartão de Crédito',
                    'Ano': parcela_data['ano'],
                    'MesFatura': dt_fatura,
                    'DataPostagem': parcela_data['data'],
                    'banco_origem': banco,
                    'tipodocumento': tipodocumento,
                    'origem_classificacao': 'Não Classificada',
                    'arquivo_origem': file_name,
                    'TipoGasto': None,
                    'GRUPO': None,
                    'SUBGRUPO': None
                })
        
        print(f"✓ {len(transacoes)} transações processadas")
        if parcelas_processadas > 0:
            print(f"  ⚡ {parcelas_processadas} transações parceladas com IdParcela")
        return transacoes
        
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print(f"❌ ERRO AO PROCESSAR FATURA")
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
