"""
Processador de Extrato Itaú (XLS)
"""
import pandas as pd
import re
from datetime import datetime
from utils.hasher import generate_id_simples
from utils.normalizer import normalizar


def processar_extrato_itau(file_path, file_name):
    """
    Processa arquivo XLS de Extrato do Itaú
    
    Args:
        file_path (str): Caminho do arquivo
        file_name (str): Nome do arquivo
        
    Returns:
        list: Lista de transações processadas
    """
    print(f"\n📄 Processando Extrato Itaú: {file_name}")
    
    try:
        # Lê XLS (formato antigo)
        df = pd.read_excel(file_path, engine='xlrd')
        
        # Converte tudo para texto
        texto = ''
        for col in df.columns:
            texto += ' ' + df[col].astype(str).str.cat(sep=' ')
        
        transacoes = []
        contador_seq = 0  # Contador para garantir IDs únicos
        
        # Extrai nome do titular (padrão: NOME CPF)
        nome_titular = None
        match_nome = re.search(r'([A-Z][A-Z\s]+?)\s+\d{3}\.\d{3}\.\d{3}-\d{2}', texto)
        if match_nome:
            nome_titular = match_nome.group(1).strip()
        
        # Regex para transações: DD/MM/AAAA Estabelecimento Valor
        regex = re.compile(
            r'((\d{2})/(\d{2})/(\d{4}))\s+([A-Za-z0-9\s*./ \-]+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})|-?\d+(?:[.,]\d{2}))$',
            re.MULTILINE
        )
        
        for match in regex.finditer(texto):
            contador_seq += 1  # Incrementa contador
            data_completa = match.group(1)  # DD/MM/AAAA
            dia = match.group(2)
            mes = match.group(3)
            ano = match.group(4)
            estabelecimento = match.group(5).strip()
            valor_str = match.group(6)
            
            # Ignora saldo do dia
            if 'SALDO DO DIA' in estabelecimento.upper():
                continue
            
            # Converte valor
            valor = float(valor_str.replace('.', '').replace(',', '.'))
            
            # Define tipo
            if valor > 0:
                tipo_transacao = 'Receitas'
            elif valor < 0:
                tipo_transacao = 'Despesas'
            else:
                tipo_transacao = '(Espaços em branco)'
            
            # Gera ID com contador sequencial para garantir unicidade
            id_transacao = f"{generate_id_simples(data_completa, estabelecimento, valor)}_{contador_seq}"
            
            # Verifica se é futura
            try:
                data_trans = datetime.strptime(data_completa, '%d/%m/%Y')
                data_atual = datetime.now()
                eh_futura = data_trans > data_atual
            except:
                eh_futura = False
            
            transacoes.append({
                'IdTransacao': id_transacao,
                'Data': data_completa,
                'Estabelecimento': estabelecimento,
                'Valor': valor,
                'ValorPositivo': abs(valor),
                'TipoTransacao': tipo_transacao,
                'TipoTransacaoAjuste': tipo_transacao,
                'Ano': int(ano),
                'DT_Fatura': f"{ano}{mes}",
                'NomeTitular': nome_titular,
                'DataPostagem': None,
                'origem': 'Itaú Person',
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
        
        print(f"✓ {len(transacoes)} transações extraídas")
        return transacoes
        
    except Exception as e:
        print(f"❌ Erro ao processar extrato: {e}")
        raise
