"""
Base dataclass for raw transactions
Estrutura padronizada de transação após processamento bruto
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BalanceValidation:
    """
    Validação de saldo para extratos bancários
    Saldo Inicial + Soma Transações = Saldo Final
    """
    saldo_inicial: Optional[float] = None
    saldo_final: Optional[float] = None
    soma_transacoes: Optional[float] = None
    is_valid: Optional[bool] = None
    diferenca: Optional[float] = None
    
    def validate(self) -> bool:
        """Valida se saldo inicial + transações = saldo final"""
        if self.saldo_inicial is None or self.saldo_final is None or self.soma_transacoes is None:
            self.is_valid = None
            return False
        
        calculado = round(self.saldo_inicial + self.soma_transacoes, 2)
        self.diferenca = round(self.saldo_final - calculado, 2)
        self.is_valid = abs(self.diferenca) < 0.01  # Tolerância de 1 centavo
        return self.is_valid
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'saldo_inicial': self.saldo_inicial,
            'saldo_final': self.saldo_final,
            'soma_transacoes': self.soma_transacoes,
            'is_valid': self.is_valid,
            'diferenca': self.diferenca
        }


@dataclass
class RawTransaction:
    """
    Transação bruta após processamento inicial
    Todos os processadores devem retornar esta estrutura
    """
    
    # Campos obrigatórios
    banco: str                      # Nome do banco (Itaú, BTG, etc)
    tipo_documento: str             # 'fatura' ou 'extrato'
    nome_arquivo: str               # Nome do arquivo original
    data_criacao: datetime          # Quando o arquivo foi processado
    data: str                       # Data da transação (DD/MM/YYYY)
    lancamento: str                 # Descrição/estabelecimento
    valor: float                    # Valor da transação (positivo ou negativo)
    
    # Campos opcionais (específicos de fatura)
    nome_cartao: Optional[str] = None  # Ex: "Mastercard Black"
    final_cartao: Optional[str] = None # Ex: "4321"
    mes_fatura: Optional[str] = None   # Ex: "202601" (AAAAMM)
    
    def to_dict(self) -> dict:
        """Converte para dicionário para salvar no banco"""
        return {
            'banco': self.banco,
            'tipo_documento': self.tipo_documento,
            'nome_arquivo': self.nome_arquivo,
            'data_criacao': self.data_criacao,
            'data': self.data,
            'lancamento': self.lancamento,
            'valor': self.valor,
            'nome_cartao': self.nome_cartao,
            'cartao': self.final_cartao,
            'mes_fatura': self.mes_fatura,
        }
