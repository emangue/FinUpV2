"""
Utilitários para hash FNV-1a 64-bit

Versão: 3.0.0
Data: 21/03/2026
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

Histórico:
- 2.0.0: Migração de MD5 para FNV-1a 64-bit (correção bug colisão VPD)
- 2.1.0: Sistema de versionamento implementado
- 3.0.0: IdTransacao v5 — chave baseada em banco+tipo+data+valor (sem nome)
          Resolve deduplicação quebrada para BTG (descrição varia entre exports)
          Adiciona canonical mapping para migração de dados históricos
          BREAKING CHANGE: requer recálculo de todos os IdTransacao existentes
          Testes: scripts/testing/test_idtransacao_v5.py (23/23)
"""

import re
import unicodedata


# ──────────────────────────────────────────────────────────────────────────────
# Canonical mapping — normalização de nomes de banco
# Necessário para garantir mesmo hash independente de variações de grafia.
# Em uploads novos, service.py injeta o valor canônico do form.
# Usado também pela migração histórica (recalculate_id_transacao_v5.py).
# ──────────────────────────────────────────────────────────────────────────────

_BANCO_CANONICAL: dict = {
    # BTG
    'BTG':              'BTG',
    'BTGPACTUAL':       'BTG',       # 'BTG Pactual' → normaliza → 'BTGPACTUAL' → 'BTG'
    # Mercado Pago
    'MERCADOPAGO':      'MERCADOPAGO',  # 'Mercado Pago' e 'MercadoPago' → mesmo
    # Itaú
    'ITAU':             'ITAU',
    # Demais bancos suportados
    'BRADESCO':         'BRADESCO',
    'NUBANK':           'NUBANK',
    'SANTANDER':        'SANTANDER',
    'BB':               'BB',
    'BANCODOB':         'BB',
    'BANCODOBRASIL':    'BB',        # 'Banco do Brasil' → 'BB'
    'CAIXA':            'CAIXA',
    'XP':               'XP',
    'INTER':            'INTER',
    'C6':               'C6',
    'C6BANK':           'C6',        # 'C6 Bank' → 'C6'
    'SICOOB':           'SICOOB',
    'SICREDI':          'SICREDI',
    'OUTROS':           'OUTROS',
}


def _normalize_str(text: str) -> str:
    """
    Remove acentos, converte para maiúsculas, elimina tudo que não for A-Z0-9.

    Exemplos:
        'Itaú'         → 'ITAU'
        'Mercado Pago' → 'MERCADOPAGO'
        'BTG Pactual'  → 'BTGPACTUAL'
        'C6 Bank'      → 'C6BANK'
    """
    sem_acento = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Z0-9]', '', sem_acento.upper())


def get_canonical_banco(banco: str) -> str:
    """
    Retorna o nome canônico do banco para uso no hash v5.

    Fluxo: texto raw → _normalize_str → lookup em _BANCO_CANONICAL.
    Se não encontrado (banco novo), retorna o próprio _normalize_str como fallback.

    Exemplos:
        'BTG Pactual'     → 'BTG'
        'btg pactual'     → 'BTG'
        'Mercado Pago'    → 'MERCADOPAGO'
        'MercadoPago'     → 'MERCADOPAGO'
        'Itaú'            → 'ITAU'
        'Banco do Brasil' → 'BB'
        'BancoNovo'       → 'BANCONOVO'  (fallback seguro)
    """
    key = _normalize_str(banco)
    return _BANCO_CANONICAL.get(key, key)


def fnv1a_64_hash(text):
    """
    Gera hash FNV-1a 64-bit de uma string
    
    Args:
        text (str): Texto para gerar hash
        
    Returns:
        str: Hash em decimal (string)
    """
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    
    return str(h)


def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1) -> str:
    """
    Gera IdTransacao v5 usando hash FNV-1a 64-bit.

    ESTRATÉGIA v5 (BREAKING CHANGE vs v4.2.1):
    - Chave: user_id | banco_canonical | tipo | data | valor
    - Remove dependência do nome/descrição da transação
    - Imune a variações de texto entre exports do mesmo banco
    - Sequência diferencia múltiplas transações com mesma chave no arquivo

    Args:
        data          : Data no formato DD/MM/AAAA
        banco         : Nome do banco do form (ex: 'BTG Pactual', 'Mercado Pago')
        tipo_documento: 'extrato' ou 'fatura'
        valor         : Valor EXATO (com sinal — negativo para despesas)
        user_id       : ID do usuário (isolamento entre usuários)
        sequencia     : Posição no arquivo (1=primeira ocorrência, 2=segunda, ...)

    Returns:
        str: IdTransacao — hash FNV-1a 64-bit em decimal

    Exemplos:
        # Mesma transação BTG, duas descrições diferentes → mesmo hash ✅
        >>> generate_id_transacao('29/12/2025', 'BTG Pactual', 'extrato', 10520.01, 1)
        >>> generate_id_transacao('29/12/2025', 'BTG',         'extrato', 10520.01, 1)
        # Ambos retornam o mesmo valor (canonical 'BTG')

        # Dois saques de R$100 no mesmo dia → hashes diferentes por sequência ✅
        >>> generate_id_transacao('15/01/2026', 'Itaú', 'extrato', -100.00, 1, sequencia=1)
        >>> generate_id_transacao('15/01/2026', 'Itaú', 'extrato', -100.00, 1, sequencia=2)

    BREAKING CHANGE vs v4.2.1:
        Parâmetro 'estabelecimento' removido.
        Parâmetros 'banco' e 'tipo_documento' adicionados.
        Todos os IdTransacao existentes devem ser recalculados (migração).
    """
    banco_norm = get_canonical_banco(banco)       # 'BTG Pactual' → 'BTG'
    tipo_norm  = _normalize_str(tipo_documento)   # 'extrato' → 'EXTRATO'
    valor_str  = f"{float(valor):.2f}"            # -10520.01 → '-10520.01'

    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"

    hash_atual = fnv1a_64_hash(chave)

    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)

    return hash_atual


def generate_id_simples(data, estabelecimento, valor):
    """
    Gera ID simples (compatível com n8n)
    Inclui estabelecimento normalizado para evitar colisões
    
    Args:
        data (str): Data
        estabelecimento (str): Estabelecimento
        valor (float): Valor
        
    Returns:
        str: Hash simples
    """
    from app.shared.utils.normalizer import normalizar_estabelecimento
    
    # Normaliza estabelecimento para garantir consistência
    estab_norm = normalizar_estabelecimento(estabelecimento)
    
    # Inclui estabelecimento normalizado no hash
    str_concat = f"{data}{estab_norm}{valor:.2f}".replace(' ', '').replace('/', '').replace('-', '')
    
    # Hash simples (compatível com JavaScript)
    hash_val = 0
    for char in str_concat:
        hash_val = ((hash_val << 5) - hash_val) + ord(char)
        hash_val = hash_val & 0xFFFFFFFF  # Convert to 32bit integer
    
    # Retorna em decimal (consistente com journal_entries)
    return str(abs(hash_val))
