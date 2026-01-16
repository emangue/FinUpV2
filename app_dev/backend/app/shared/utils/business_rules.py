"""
Business Rules - Regras de Negócio Compartilhadas
Funções que implementam lógica de negócio usada por múltiplos domínios
"""

from typing import Optional


def determine_categoria_geral(
    grupo: Optional[str], 
    valor: float, 
    nome_cartao: Optional[str] = None
) -> Optional[str]:
    """
    Determina CategoriaGeral baseado em regras de negócio
    
    Regras (em ordem de prioridade):
    1. Cartão de Crédito → SEMPRE Despesa
    2. Transferência Entre Contas → Transferência
    3. Investimentos → Investimentos
    4. Valor positivo → Receita
    5. Valor negativo → Despesa
    
    Args:
        grupo: Grupo da transação (pode ser None)
        valor: Valor da transação (negativo = despesa, positivo = receita)
        nome_cartao: Nome do cartão (se for transação de cartão de crédito)
    
    Returns:
        'Despesa', 'Receita', 'Transferência', 'Investimentos', ou None
    """
    if not grupo:
        return None
    
    # Normalizar grupo para comparação
    grupo_lower = grupo.lower().strip()
    
    # Regra 1: Cartão de Crédito → SEMPRE Despesa
    if nome_cartao and nome_cartao.strip():
        return 'Despesa'
    
    # Regra 2: Transferência
    if 'transferencia' in grupo_lower or 'transferência' in grupo_lower:
        return 'Transferência'
    
    # Regra 3: Investimentos
    if 'investimento' in grupo_lower:
        return 'Investimentos'
    
    # Regra 4 e 5: Baseado no sinal do valor
    if valor >= 0:
        return 'Receita'
    else:
        return 'Despesa'
