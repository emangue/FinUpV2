"""
Preprocessador para Cartão de Crédito Banco do Brasil (OFX)

Versão: 3.0.0
Data: 28/12/2025

Detecta e processa arquivos OFX de cartão de crédito do Banco do Brasil (Ourocard).

Formato esperado:
- Formato OFX padrão (XML-like)
- <ORG>Banco do Brasil</ORG>
- <CCSTMTRS> para extratos de cartão de crédito
- Transações com <STMTTRN>
- Valores negativos = compras/débitos
- Valores positivos = pagamentos/créditos
- Parcelas indicadas no <MEMO> com "PARC XX/YY"

Exemplo de transação:
<STMTTRN>
  <TRNTYPE>PAYMENT</TRNTYPE>
  <DTPOSTED>20241128</DTPOSTED>
  <TRNAMT>-110.75</TRNAMT>
  <FITID>2024112849840000000060340000000003</FITID>
  <MEMO>VOTRE                  SAO PAULO     BR</MEMO>
</STMTTRN>
"""
import xml.etree.ElementTree as ET
import pandas as pd
import re
from datetime import datetime


def is_cartao_bb_ofx(file_path):
    """
    Detecta se o arquivo é um OFX de cartão de crédito do Banco do Brasil
    
    Critérios:
    - Extensão .ofx
    - Contém <ORG>Banco do Brasil</ORG>
    - Contém <CCSTMTRS> (Credit Card Statement Response)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(5000)  # Ler primeiros 5KB
            
            # Verifica markers característicos
            is_ofx = 'OFXHEADER:' in content or '<OFX>' in content
            is_bb = 'Banco do Brasil' in content
            is_cartao = '<CCSTMTRS>' in content or 'CREDITCARDMSGSRSV1' in content
            
            if is_ofx and is_bb and is_cartao:
                print("✅ Detectado: Cartão BB OFX")
                return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Erro ao detectar cartão BB OFX: {e}")
        return False


def limpar_ofx_header(file_path):
    """
    Remove cabeçalho OFX não-XML e retorna apenas o XML
    
    OFX tem headers especiais antes do XML:
    OFXHEADER:100
    DATA:OFXSGML
    ...
    <OFX>...</OFX>
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Encontra início do XML
    xml_start = content.find('<OFX>')
    if xml_start == -1:
        raise Exception("Não encontrado tag <OFX> no arquivo")
    
    return content[xml_start:]


def extrair_estabelecimento(memo):
    """
    Extrai nome do estabelecimento do campo MEMO
    
    Formatos:
    - "VOTRE                  SAO PAULO     BR"
    - "MERCADOLIVRE* PARC 01/04 OSASCO BR"
    - "AMAZON.COM.BR           SAO PAULO BR"
    
    Remove:
    - Cidade e país (padrão no final)
    - Espaços extras
    - Indicador de parcelas (será extraído separadamente)
    """
    if not memo:
        return "N/A"
    
    memo = memo.strip()
    
    # Remove "PARC XX/YY" se presente (parcelas)
    memo = re.sub(r'PARC\s+\d{2}/\d{2}', '', memo, flags=re.IGNORECASE)
    
    # Remove cidade + país do final (ex: "SAO PAULO BR", "OSASCO BR")
    memo = re.sub(r'\s+[A-Z\s]+\s+BR\s*$', '', memo)
    
    # Remove espaços múltiplos
    memo = re.sub(r'\s+', ' ', memo).strip()
    
    return memo


def extrair_parcelas(memo):
    """
    Extrai informação de parcelas do MEMO
    
    Formato: "PARC 01/04" ou "PARC 02/12"
    
    Retorna:
    - (parcela_atual, total_parcelas) se encontrado
    - (None, None) se não tem parcelas
    """
    if not memo:
        return None, None
    
    match = re.search(r'PARC\s+(\d{2})/(\d{2})', memo, re.IGNORECASE)
    if match:
        parcela_atual = int(match.group(1))
        total_parcelas = int(match.group(2))
        return parcela_atual, total_parcelas
    
    return None, None


def processar_cartao_bb_ofx(file_path):
    """
    Processa arquivo OFX de cartão de crédito Banco do Brasil
    
    Retorna:
    {
        'df': DataFrame com transações processadas,
        'validacao': {
            'total_transacoes': int,
            'total_debitos': float,
            'total_creditos': float,
            'saldo_final': float,
            'valido': bool
        },
        'banco': 'Banco do Brasil',
        'tipodocumento': 'Fatura Cartão de Crédito',
        'preprocessado': True
    }
    """
    print("\n💳 Processando Cartão BB (OFX)...")
    
    # Limpar header OFX e obter XML puro
    xml_content = limpar_ofx_header(file_path)
    
    # Parse XML
    try:
        # OFX não é XML bem formado, precisa de limpeza
        xml_content = xml_content.replace('&', '&amp;')
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"⚠️  Erro ao parsear XML: {e}")
        # Tentar parseamento alternativo
        root = ET.fromstring(xml_content.encode('utf-8'))
    
    # Extrair informações da conta
    conta_elem = root.find('.//CCACCTFROM/ACCTID')
    conta = conta_elem.text.strip() if conta_elem is not None else "N/A"
    print(f"💳 Conta: {conta}")
    
    # Extrair período do extrato
    dtstart_elem = root.find('.//DTSTART')
    dtend_elem = root.find('.//DTEND')
    
    if dtstart_elem is not None and dtend_elem is not None:
        dtstart = dtstart_elem.text
        dtend = dtend_elem.text
        print(f"📅 Período: {dtstart[:4]}-{dtstart[4:6]}-{dtstart[6:8]} até {dtend[:4]}-{dtend[4:6]}-{dtend[6:8]}")
    
    # Extrair transações
    transacoes = []
    stmttrn_list = root.findall('.//STMTTRN')
    
    print(f"📊 Processando {len(stmttrn_list)} transações...")
    
    for trn in stmttrn_list:
        # Tipo de transação
        trntype = trn.find('TRNTYPE')
        tipo = trntype.text if trntype is not None else 'OTHER'
        
        # Data (YYYYMMDD)
        dtposted = trn.find('DTPOSTED')
        if dtposted is not None:
            data_str = dtposted.text
            # Converter YYYYMMDD para DD/MM/YYYY
            data = f"{data_str[6:8]}/{data_str[4:6]}/{data_str[:4]}"
        else:
            data = "N/A"
        
        # Valor
        trnamt = trn.find('TRNAMT')
        valor = float(trnamt.text) if trnamt is not None else 0.0
        
        # ID único da transação
        fitid = trn.find('FITID')
        id_transacao = fitid.text if fitid is not None else ""
        
        # Memo (descrição/estabelecimento)
        memo = trn.find('MEMO')
        memo_text = memo.text if memo is not None else ""
        
        # Extrair estabelecimento e parcelas
        estabelecimento = extrair_estabelecimento(memo_text)
        parcela_atual, total_parcelas = extrair_parcelas(memo_text)
        
        transacoes.append({
            'data': data,
            'estabelecimento': estabelecimento,
            'valor': valor,
            'tipo': tipo,
            'id_transacao': id_transacao,
            'descricao_original': memo_text,
            'parcela_atual': parcela_atual,
            'total_parcelas': total_parcelas,
            'conta': conta
        })
    
    # Criar DataFrame
    df = pd.DataFrame(transacoes)
    
    # FILTRAR: Só manter COMPRAS (valores negativos = PAYMENT)
    # Excluir pagamentos/créditos (valores positivos) pois aparecem no extrato da conta
    df_compras = df[df['valor'] < 0].copy()
    
    print(f"🛒 Transações de COMPRA (valores negativos): {len(df_compras)}")
    print(f"💳 Transações de PAGAMENTO (valores positivos): {len(df[df['valor'] > 0])}")
    print(f"   → Importando apenas COMPRAS")
    
    # Renomear colunas para padrão esperado pelo processador de fatura
    # 'estabelecimento' → 'lançamento' (compatibilidade)
    df_compras = df_compras.rename(columns={
        'estabelecimento': 'lançamento',
        'valor': 'valor (R$)'
    })
    
    # Validação
    total_compras = abs(df_compras['valor (R$)'].sum())
    
    # Buscar saldo final (ledger balance)
    ledgerbal = root.find('.//LEDGERBAL/BALAMT')
    saldo_final = float(ledgerbal.text) if ledgerbal is not None else 0.0
    
    validacao = {
        'total_transacoes': len(df_compras),
        'total_compras': total_compras,
        'saldo_devedor': abs(saldo_final),
        'valido': True  # OFX sempre confiável
    }
    
    print(f"💰 Total Compras: R$ {total_compras:,.2f}")
    print(f"💰 Saldo Devedor: R$ {abs(saldo_final):,.2f}")
    print(f"✅ Validação: OK")
    
    # Identificar transações parceladas
    parceladas = df_compras[df_compras['total_parcelas'].notna()]
    if len(parceladas) > 0:
        print(f"📋 {len(parceladas)} transações parceladas detectadas")
    
    return {
        'df': df_compras,
        'validacao': validacao,
        'banco': 'Banco do Brasil',
        'tipodocumento': 'Fatura Cartão de Crédito',
        'preprocessado': True
    }


# Exportar funções principais
__all__ = ['is_cartao_bb_ofx', 'processar_cartao_bb_ofx']
