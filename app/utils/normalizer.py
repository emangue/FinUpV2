"""
Utilitários para normalização de texto e tokens
"""
import re
import unicodedata


def normalizar(texto):
    """
    Normaliza texto: remove acentos, caracteres especiais, converte para maiúsculas
    
    Args:
        texto (str): Texto para normalizar
        
    Returns:
        str: Texto normalizado
    """
    if not texto:
        return ""
    
    # Converte para string
    texto = str(texto)
    
    # Remove acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
    
    # Maiúsculas
    texto = texto.upper()
    
    # Remove caracteres especiais (mantém letras, números e espaços)
    texto = re.sub(r'[^A-Z0-9\s]', ' ', texto)
    
    # Remove espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()


def normalizar_estabelecimento(estabelecimento):
    """
    Normaliza nome do estabelecimento (remove parcelas XX/YY do final)
    
    Args:
        estabelecimento (str): Nome do estabelecimento
        
    Returns:
        str: Estabelecimento normalizado
    """
    if not estabelecimento:
        return ""
    
    # Remove parcelas no formato XX/YY do final
    estab = re.sub(r'\s*\d{1,2}/\d{1,2}\s*$', '', estabelecimento)
    
    # Normaliza
    estab = normalizar(estab)
    
    # Remove asteriscos
    estab = estab.replace('*', '')
    
    return estab.strip()


def tokens_validos(texto):
    """
    Extrai tokens válidos de um texto (remove stop words)
    
    Args:
        texto (str): Texto para extrair tokens
        
    Returns:
        list: Lista de tokens válidos
    """
    # Stop words (palavras a ignorar)
    STOP_WORDS = {
        'BOLETO', 'PAGAMENTO', 'PAG', 'PIX', 'TED', 'MOBILE', 'TIT', 'INT',
        'OUTROS', 'BANCOS', 'PARA', 'AUTORIZACAO', 'TRANSACAO', 'LANCTO',
        'DEBITO', 'CREDITO', 'AJUSTE', 'COMPRA', 'SALDO', 'DIA'
    }
    
    # Normaliza e quebra em palavras
    texto_norm = normalizar(texto)
    palavras = texto_norm.split()
    
    # Filtra: comprimento > 3 e não está em stop words
    tokens = [
        palavra for palavra in palavras
        if len(palavra) > 3 and palavra not in STOP_WORDS
    ]
    
    return tokens


def detectar_parcela(estabelecimento, origem=''):
    """
    Detecta se há parcela no formato XX/YY no final do estabelecimento
    
    Args:
        estabelecimento (str): Nome do estabelecimento
        origem (str): Origem da transação (para validação contextual)
        
    Returns:
        dict or None: {'parcela': int, 'total': int} ou None
    """
    match = re.search(r'\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    
    if not match:
        return None
    
    parcela = int(match.group(1))
    total = int(match.group(2))
    
    # Validação básica
    if not (1 <= parcela <= total <= 99):
        return None
    
    # Validação contextual para extratos
    # Em extratos, XX/YY com YY <= 12 e XX <= 31 pode ser data, não parcela
    eh_extrato = 'extrato' in origem.lower() or 'person' in origem.lower()
    if eh_extrato and total <= 12 and parcela <= 31:
        return None
    
    return {'parcela': parcela, 'total': total}


def get_faixa_valor(valor):
    """
    Determina faixa de valor para segmentação
    
    Args:
        valor (float): Valor da transação
        
    Returns:
        str: Faixa de valor
    """
    v = abs(float(valor))
    
    if v == 0:
        return "ZERO"
    elif v < 50:
        return "0-50"
    elif v < 100:
        return "50-100"
    elif v < 200:
        return "100-200"
    elif v < 500:
        return "200-500"
    elif v < 1000:
        return "500-1K"
    elif v < 2000:
        return "1K-2K"
    elif v < 5000:
        return "2K-5K"
    else:
        return "5K+"


def arredondar_2_decimais(valor):
    """
    Arredonda valor para 2 casas decimais
    
    Args:
        valor (float): Valor para arredondar
        
    Returns:
        float: Valor arredondado
    """
    return round(float(valor) + 0.00001, 2)
