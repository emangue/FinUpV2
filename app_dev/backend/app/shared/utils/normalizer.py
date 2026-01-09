"""
Utilitários para normalização de texto e tokens

Fonte: https://github.com/emangue/FinUp/tree/main/app/utils/normalizer.py
"""
import re
import unicodedata
import math


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
    
    # Remove parcelas no formato XX/YY ou (XX/YY) do final
    estab = re.sub(r'\s*\(?\d{1,2}/\d{1,2}\)?\s*$', '', estabelecimento)
    
    # Normaliza
    estab = normalizar(estab)
    
    # Remove asteriscos
    estab = estab.replace('*', '')
    
    return estab.strip()


def tokensValidos(texto):
    """
    Extrai tokens válidos de um texto (igual ao n8n)
    
    Args:
        texto (str): Texto para extrair tokens
        
    Returns:
        list: Lista de tokens válidos
    """
    # Stop words (igual ao n8n)
    STOP_WORDS = {
        'BOLETO', 'PAGAMENTO', 'PAG', 'PIX', 'TED', 'MOBILE', 'TIT', 'INT',
        'OUTROS', 'BANCOS', 'PARA', 'AUTORIZACAO', 'TRANSACAO', 'LANCTO',
        'DEBITO', 'CREDITO', 'AJUSTE', 'COMPRA'
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


def intersecaoCount(tokens_a, tokens_b):
    """
    Conta interseção entre duas listas de tokens
    
    Args:
        tokens_a (list): Primeira lista de tokens
        tokens_b (list): Segunda lista de tokens
        
    Returns:
        int: Número de tokens em comum
    """
    set_a = set(tokens_a)
    count = 0
    for token in tokens_b:
        if token in set_a:
            count += 1
    return count


def toNumberFlexible(value):
    """
    Converte valor para número com flexibilidade (igual ao n8n)
    
    Args:
        value: Valor para converter (str, int, float)
        
    Returns:
        float: Número convertido ou 0 se inválido
    """
    if value is None:
        return 0
    
    # Se já é número, retorna
    if isinstance(value, (int, float)):
        return float(value)
    
    # Se é string, tenta converter
    try:
        raw = str(value).strip().replace(',', '.').upper()
        
        # Verifica notação K (ex: "1.5K" = 1500)
        k_match = re.match(r'^(\d+(?:\.\d+)?)\s*K$', raw)
        if k_match:
            return float(k_match.group(1)) * 1000
        
        # Conversão normal
        number = float(raw)
        return number if math.isfinite(number) else 0
    except:
        return 0


def detectar_parcela(estabelecimento, origem=''):
    """
    Detecta se há parcela no formato XX/YY no final do estabelecimento
    
    Args:
        estabelecimento (str): Nome do estabelecimento
        origem (str): Origem da transação (para validação contextual)
        
    Returns:
        dict or None: {'parcela': int, 'total': int} ou None
    """
    match = re.search(r'\s*\(?(\d{1,2})/(\d{1,2})\)?\s*$', estabelecimento)
    
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
    return round(float(valor), 2)


def fuzzy_match_titular(estabelecimento, titular_nome, threshold=0.60):
    """
    Verifica se o estabelecimento contém o nome do titular com matching fuzzy
    
    Usado para detectar TED/PIX/transferências envolvendo a própria pessoa,
    permitindo auto-ignorar essas transações no dashboard.
    
    Args:
        estabelecimento (str): Nome do estabelecimento/beneficiário
        titular_nome (str): Nome completo do titular da conta
        threshold (float): Limiar de similaridade (0-1), default 0.60 = 60%
        
    Returns:
        bool: True se há match acima do threshold
        
    Examples:
        >>> fuzzy_match_titular("TED ENVIADO PARA EDUARDO MANGUE", "Eduardo Mangue")
        True
        >>> fuzzy_match_titular("PIX RECEBIDO DE MANGUE E", "Eduardo Mangue")
        True
        >>> fuzzy_match_titular("TED MARIA SILVA", "Eduardo Mangue")
        False
    """
    if not estabelecimento or not titular_nome:
        return False
    
    # Normalizar ambos
    estab_norm = normalizar(estabelecimento)
    titular_norm = normalizar(titular_nome)
    
    # Palavras comuns a remover (não são significativas)
    palavras_ignorar = {
        'TED', 'PIX', 'DOC', 'TRANSF', 'TRANSFERENCIA', 'ENVIADO', 'RECEBIDO',
        'PARA', 'DE', 'CPF', 'CNPJ', 'BANCO', 'PAGAMENTO', 'SAQUE', 'DEPOSITO',
        'E', 'DA', 'DO', 'DOS', 'DAS', 'A', 'O', 'AS', 'OS'
    }
    
    # Extrair tokens válidos do estabelecimento
    tokens_estab = set(token for token in estab_norm.split() 
                       if len(token) >= 2 and token not in palavras_ignorar)
    
    # Extrair tokens do nome do titular
    tokens_titular = set(token for token in titular_norm.split() 
                         if len(token) >= 2 and token not in palavras_ignorar)
    
    if not tokens_estab or not tokens_titular:
        return False
    
    # Calcular overlap de tokens
    intersecao = tokens_estab & tokens_titular
    uniao = tokens_estab | tokens_titular
    
    # Similaridade de Jaccard
    similaridade = len(intersecao) / len(uniao) if uniao else 0
    
    # Ou calcular overlap direto nos tokens do titular (mais permissivo)
    overlap_titular = len(intersecao) / len(tokens_titular) if tokens_titular else 0
    
    # Aceitar se qualquer métrica passar o threshold
    return max(similaridade, overlap_titular) >= threshold


def tokens_validos_titular(nome):
    """
    Extrai tokens válidos de um nome de titular para matching
    
    Args:
        nome (str): Nome completo do titular
        
    Returns:
        set: Conjunto de tokens normalizados (mínimo 2 caracteres)
    """
    if not nome:
        return set()
    
    nome_norm = normalizar(nome)
    palavras_ignorar = {'E', 'DA', 'DO', 'DOS', 'DAS', 'DE', 'A', 'O', 'AS', 'OS'}
    
    return set(token for token in nome_norm.split() 
               if len(token) >= 2 and token not in palavras_ignorar)
