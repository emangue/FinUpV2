"""
Processador de Extrato Mercado Pago (XLSX)
"""
import pandas as pd
import re
from datetime import datetime
from app.utils.hasher import fnv1a_64_hash
from app.utils.normalizer import normalizar_estabelecimento


def processar_mercado_pago(file_path, file_name):
    """
    Processa arquivo XLSX de Extrato Mercado Pago
    
    Args:
        file_path (str): Caminho do arquivo
        file_name (str): Nome do arquivo
        
    Returns:
        list: Lista de transações processadas
    """
    print(f"\n📄 Processando Mercado Pago: {file_name}")
    
    try:
        # Lê XLSX
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Converte para texto
        texto = ''
        for col in df.columns:
            texto += '\n' + df[col].astype(str).str.cat(sep='\n')
        
        transacoes = []
        
        # Extrai nome do titular
        nome_titular = None
        match_tit = re.search(r'EXTRATO DE CONTA\s+([^<]+?)\s+CPF', texto, re.IGNORECASE)
        if match_tit:
            nome_titular = match_tit.group(1).strip().replace('\n', ' ')
            nome_titular = re.sub(r'\s+', ' ', nome_titular)
        
        # Quebra em linhas
        linhas = texto.replace('\r', '').split('\n')
        linhas = [l.strip() for l in linhas if l.strip()]
        
        contador_seq = 0  # Contador para garantir IDs únicos
        hash_counter = {}  # Contador para hashes duplicados no mesmo arquivo
        i = 0
        while i < len(linhas):
            contador_seq += 1  # Incrementa contador
            # Procura data: dd-mm-aaaa
            match_data = re.match(r'^(\d{2})-(\d{2})-(\d{4})$', linhas[i])
            if not match_data:
                i += 1
                continue
            
            dd, mm, yyyy = match_data.groups()
            data_br = f"{dd}/{mm}/{yyyy}"
            
            # Agrega bloco de descrição até linha com R$
            bloco = []
            j = i + 1
            while j < len(linhas) and not re.match(r'^\d{2}-\d{2}-\d{4}$', linhas[j]):
                bloco.append(linhas[j])
                if 'R$' in linhas[j]:
                    break
                j += 1
            
            bloco_str = ' '.join(bloco)
            bloco_str = re.sub(r'\s+', ' ', bloco_str).strip()
            
            # Extrai ID da operação
            match_id = re.search(r'(\d{6,})\s+R\$\s*-?\d', bloco_str)
            id_operacao = match_id.group(1) if match_id else None
            
            # Extrai valor (primeiro R$ antes do saldo)
            match_valor = re.search(r'R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})', bloco_str)
            if match_valor:
                valor_str = match_valor.group(1)
                valor = float(valor_str.replace('.', '').replace(',', '.'))
            else:
                i = j + 1
                continue
            
            # Estabelecimento (remove ID e valores)
            estabelecimento = re.sub(r'\b\d{6,}\b.*$', '', bloco_str)
            estabelecimento = re.sub(r'R\$.*$', '', estabelecimento)
            estabelecimento = re.sub(r'\s+', ' ', estabelecimento).strip()
            
            if not estabelecimento:
                i = j + 1
                continue
            
            # Define tipo
            tipo_transacao = 'Receitas' if valor > 0 else 'Despesas'
            
            # Gera ID base via hash FNV-1a
            estab_norm = normalizar_estabelecimento(estabelecimento)
            chave = f"{data_br}|{estab_norm}|{valor:.2f}"
            id_base = fnv1a_64_hash(chave)
            
            # Se o hash já existe no arquivo atual, adiciona sufixo
            if id_base in hash_counter:
                hash_counter[id_base] += 1
                id_transacao = f"{id_base}_{hash_counter[id_base]}"
            else:
                hash_counter[id_base] = 0
                id_transacao = id_base
            
            transacoes.append({
                'IdTransacao': id_transacao,
                'IdOperacao': id_operacao,
                'Data': data_br,
                'Estabelecimento': estabelecimento,
                'Valor': valor,
                'ValorPositivo': abs(valor),
                'TipoTransacao': tipo_transacao,
                'TipoTransacaoAjuste': tipo_transacao,
                'Ano': int(yyyy),
                'DT_Fatura': f"{yyyy}{mm}",
                'NomeTitular': nome_titular,
                'DataPostagem': None,
                'origem': 'MP',
                'MarcacaoIA': None,
                'ValidarIA': None,
                'TipoGasto': None,
                'GRUPO': None,
                'SUBGRUPO': None,
                'TransacaoFutura': 'NÃO',
                'TipoLancamento': None,
                'CartaoCodigo8': None,
                'FinalCartao': None
            })
            
            i = j + 1
        
        print(f"✓ {len(transacoes)} transações extraídas")
        return transacoes
        
    except Exception as e:
        print(f"❌ Erro ao processar Mercado Pago: {e}")
        raise
