"""
Processador bruto para Extrato Itaú PDF
Extrai transações e saldos de PDFs de extrato do Itaú e gera a mesma estrutura que itau_extrato.py
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import pdfplumber

logger = logging.getLogger(__name__)


class RawTransaction:
    """Classe para armazenar transação bruta"""
    def __init__(self, banco, tipo_documento, nome_arquivo, data_criacao, 
                 data, lancamento, valor, nome_cartao, final_cartao, mes_fatura):
        self.banco = banco
        self.tipo_documento = tipo_documento
        self.nome_arquivo = nome_arquivo
        self.data_criacao = data_criacao
        self.data = data
        self.lancamento = lancamento
        self.valor = valor
        self.nome_cartao = nome_cartao
        self.final_cartao = final_cartao
        self.mes_fatura = mes_fatura


class BalanceValidation:
    """Classe para validação de saldo"""
    def __init__(self):
        self.saldo_inicial = None
        self.saldo_final = None
        self.soma_transacoes = None
        self.diferenca = None
        self.is_valid = False
    
    def validate(self):
        """Valida se saldo inicial + transações = saldo final"""
        if self.saldo_inicial is not None and self.saldo_final is not None and self.soma_transacoes is not None:
            saldo_calculado = round(self.saldo_inicial + self.soma_transacoes, 2)
            self.diferenca = round(self.saldo_final - saldo_calculado, 2)
            # Tolerância de 0.01 por causa de arredondamentos
            self.is_valid = abs(self.diferenca) < 0.01


def process_itau_extrato_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa extrato Itaú PDF
    
    Args:
        file_path: Caminho do arquivo PDF
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Tupla (Lista de RawTransaction, BalanceValidation)
    """
    logger.info(f"Processando extrato Itaú PDF: {nome_arquivo}")
    
    try:
        # Extrair texto de todas as páginas
        with pdfplumber.open(file_path) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() + "\n"
        
        logger.debug(f"PDF lido: {len(pdf.pages)} páginas")
        
        # Extrair saldos
        balance = _extract_balance_info(texto_completo)
        logger.info(f"Saldos extraídos: Inicial={balance.saldo_inicial}, Final={balance.saldo_final}")
        
        # Extrair transações do texto
        transacoes = _extract_transactions_from_text(texto_completo)
        logger.info(f"Extrato PDF preprocessado: {len(transacoes)} transações")
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for data, lancamento, valor in transacoes:
            transaction = RawTransaction(
                banco='Itaú',
                tipo_documento='extrato',
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=data,
                lancamento=lancamento,
                valor=valor,
                nome_cartao=None,
                final_cartao=None,
                mes_fatura=None,
            )
            transactions.append(transaction)
        
        # Calcular soma das transações e validar
        balance.soma_transacoes = round(sum(t.valor for t in transactions), 2)
        balance.validate()
        
        logger.info(f"✅ Extrato Itaú PDF processado: {len(transactions)} transações")
        logger.info(f"📊 Validação de saldo: {balance.is_valid} (diferença: {balance.diferenca})")
        
        return transactions, balance
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato Itaú PDF: {str(e)}", exc_info=True)
        raise


def _extract_balance_info(texto: str) -> BalanceValidation:
    """
    Extrai saldo inicial e final do texto do PDF
    
    Args:
        texto: Texto completo do PDF
        
    Returns:
        BalanceValidation com saldos extraídos
    """
    balance = BalanceValidation()
    linhas = texto.split('\n')
    
    for linha in linhas:
        linha_upper = linha.upper().strip()
        
        # Procurar saldo anterior (inicial)
        if 'SALDO ANTERIOR' in linha_upper:
            # Extrair valor (geralmente ao final da linha)
            match = re.search(r'([-]?\d+[\d.,]*\d+)$', linha)
            if match:
                valor_str = match.group(1)
                try:
                    balance.saldo_inicial = _convert_valor_br(valor_str)
                    logger.debug(f"Saldo inicial encontrado: {balance.saldo_inicial}")
                except ValueError:
                    pass
        
        # Procurar saldo final (último SALDO TOTAL DISPONÍVEL DIA)
        if 'SALDO TOTAL' in linha_upper and 'DIA' in linha_upper:
            # Extrair valor (geralmente ao final da linha)
            match = re.search(r'([-]?\d+[\d.,]*\d+)$', linha)
            if match:
                valor_str = match.group(1)
                try:
                    balance.saldo_final = _convert_valor_br(valor_str)
                    logger.debug(f"Saldo final atualizado: {balance.saldo_final}")
                except ValueError:
                    pass
    
    return balance


def _extract_transactions_from_text(texto: str) -> List[Tuple[str, str, float]]:
    """
    Extrai transações do texto do PDF
    
    Formato esperado:
    DD/MM/YYYY LANÇAMENTO VALOR (pode ser negativo)
    
    Returns:
        Lista de tuplas (data, lancamento, valor)
    """
    transacoes = []
    linhas = texto.split('\n')
    
    for linha in linhas:
        linha = linha.strip()
        
        # Ignorar linhas vazias, cabeçalhos e linhas de saldo
        if not linha:
            continue
        
        linha_upper = linha.upper()
        if any(palavra in linha_upper for palavra in [
            'DATA LANÇAMENTOS VALOR',
            'SALDO ANTERIOR',
            'SALDO TOTAL',
            'PERÍODO DE VISUALIZAÇÃO',
            'EMITIDO EM',
            'LANÇAMENTOS'
        ]):
            continue
        
        # Padrão: DD/MM/YYYY TEXTO VALOR
        # Exemplo: "15/01/2025 TED 033.1730.EMANUEL G L 12.896,00"
        # Exemplo: "15/01/2025 PIX TRANSF JOAO BA15/01 -400,00"
        match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([-]?\d+[\d.,]*\d+)$', linha)
        
        if match:
            data = match.group(1)
            lancamento = match.group(2).strip()
            valor_str = match.group(3)
            
            # Converter valor
            valor = _convert_valor_br(valor_str)
            
            # Ignorar valores zero
            if valor != 0:
                transacoes.append((data, lancamento, valor))
                logger.debug(f"Transação extraída: {data} | {lancamento} | {valor}")
    
    return transacoes


def _convert_valor_br(valor_str: str) -> float:
    """
    Converte valor no formato brasileiro (1.234,56 ou -1.234,56) para float
    """
    valor_str = valor_str.strip()
    
    # Preservar sinal negativo
    negativo = valor_str.startswith('-')
    valor_str = valor_str.lstrip('-')
    
    # Formato brasileiro: remover ponto (milhar) e trocar vírgula por ponto (decimal)
    if ',' in valor_str:
        valor_str = valor_str.replace('.', '')  # Remove separador de milhar
        valor_str = valor_str.replace(',', '.')  # Troca vírgula por ponto
    
    try:
        valor = float(valor_str)
        return -valor if negativo else valor
    except ValueError:
        logger.warning(f"Não foi possível converter valor: {valor_str}")
        return 0.0


# Teste standalone
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    # Testar com arquivo de exemplo
    file_path = Path('extrato-itau-2025.pdf')
    if file_path.exists():
        transactions, balance = process_itau_extrato_pdf(
            file_path=file_path,
            nome_arquivo='extrato-itau-2025.pdf'
        )
        
        print(f"\n✅ Total de transações: {len(transactions)}")
        print(f"💰 Saldo inicial: R$ {balance.saldo_inicial:.2f}")
        print(f"💰 Soma transações: R$ {balance.soma_transacoes:.2f}")
        print(f"💰 Saldo final: R$ {balance.saldo_final:.2f}")
        print(f"✅ Validação: {balance.is_valid} (diferença: {balance.diferenca})")
        print("\n📋 Primeiras 10 transações:")
        for t in transactions[:10]:
            print(f"  {t.data} | {t.lancamento[:50]:50s} | R$ {t.valor:10.2f}")
