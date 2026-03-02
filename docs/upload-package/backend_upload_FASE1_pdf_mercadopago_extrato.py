"""
Processador para Extrato MercadoPago PDF
Extrai transações de extratos do MercadoPago em PDF
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import pdfplumber

logger = logging.getLogger(__name__)


class BalanceValidation:
    """Classe para validação de saldos"""
    def __init__(self):
        self.saldo_inicial = 0.0
        self.saldo_final = 0.0
        self.soma_transacoes = 0.0
        self.is_valid = False
        self.diferenca = 0.0
    
    def validate(self):
        """Valida se saldo inicial + transações = saldo final"""
        esperado = self.saldo_inicial + self.soma_transacoes
        self.diferenca = abs(esperado - self.saldo_final)
        self.is_valid = self.diferenca < 0.01  # Tolerância de 1 centavo


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


def process_mercadopago_extrato_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa extrato MercadoPago PDF e extrai transações
    
    Args:
        file_path: Caminho do arquivo PDF
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Tupla (Lista de RawTransaction, BalanceValidation)
    """
    logger.info(f"Processando extrato MercadoPago PDF: {nome_arquivo}")
    
    try:
        with pdfplumber.open(file_path) as pdf:
            logger.debug(f"PDF aberto: {len(pdf.pages)} páginas")
            
            # Extrair texto de todas as páginas
            texto_completo = ""
            for page_num, page in enumerate(pdf.pages, 1):
                texto = page.extract_text()
                if texto:
                    texto_completo += texto + "\n"
                    logger.debug(f"Página {page_num}: {len(texto)} caracteres")
            
            # Extrair saldos
            balance = _extract_balance_info(texto_completo)
            logger.info(f"Saldos extraídos: Inicial={balance.saldo_inicial}, Final={balance.saldo_final}")
            
            # Extrair transações
            transacoes_raw = _extract_transactions_from_text(texto_completo)
            
            # Converter para RawTransaction
            transacoes = []
            data_criacao = datetime.now()
            
            for data, descricao, valor in transacoes_raw:
                transaction = RawTransaction(
                    banco='MercadoPago',
                    tipo_documento='extrato',
                    nome_arquivo=nome_arquivo,
                    data_criacao=data_criacao,
                    data=data,
                    lancamento=descricao,
                    valor=valor,
                    nome_cartao=None,
                    final_cartao=None,
                    mes_fatura=None,
                )
                transacoes.append(transaction)
            
            # Calcular soma das transações e validar
            balance.soma_transacoes = round(sum(t.valor for t in transacoes), 2)
            balance.validate()
            
            logger.info(f"✅ Extrato MercadoPago PDF processado: {len(transacoes)} transações")
            logger.info(f"📊 Validação de saldo: {balance.is_valid} (diferença: {balance.diferenca})")
            
            return transacoes, balance
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato MercadoPago PDF: {str(e)}", exc_info=True)
        raise


def _extract_balance_info(texto: str) -> BalanceValidation:
    """
    Extrai saldo inicial e final do texto do PDF
    
    Formato esperado:
    Saldo inicial: R$ XXX,XX Saldo final: R$ XXX,XX
    """
    balance = BalanceValidation()
    
    linhas = texto.split('\n')
    
    for linha in linhas:
        # Procurar linha com saldo inicial e final
        # Formato: "Saldo inicial: R$ 213,15 Saldo final: R$ 126,39"
        if 'Saldo inicial' in linha and 'Saldo final' in linha:
            # Extrair saldo inicial
            match_inicial = re.search(r'Saldo inicial:\s*R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})', linha)
            if match_inicial:
                balance.saldo_inicial = _convert_valor_br(match_inicial.group(1))
                logger.debug(f"Saldo inicial encontrado: {balance.saldo_inicial}")
            
            # Extrair saldo final
            match_final = re.search(r'Saldo final:\s*R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})', linha)
            if match_final:
                balance.saldo_final = _convert_valor_br(match_final.group(1))
                logger.debug(f"Saldo final encontrado: {balance.saldo_final}")
            
            break
    
    return balance


def _extract_transactions_from_text(texto: str) -> List[Tuple[str, str, float]]:
    """
    Extrai transações do texto do PDF
    
    O PDF do MercadoPago tem formato variável:
    - Formato 1: Data Descrição ID Valor Saldo (tudo em uma linha)
    - Formato 2: Data ID Valor Saldo (sem descrição na linha, vem antes ou depois)
    - Linhas seguintes podem ter descrição complementar ou nome de pessoa
    
    Estratégia: Capturar todas as linhas com data + ID + valor + saldo
    """
    transacoes = []
    linhas = texto.split('\n')
    
    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()
        
        # Ignorar linhas vazias
        if not linha:
            i += 1
            continue
        
        # Ignorar cabeçalhos, seções e paginação
        if any(x in linha for x in ['EXTRATO DE CONTA', 'DETALHE DOS MOVIMENTOS', 'Data Descrição ID', '/9']):
            i += 1
            continue
        
        # Tentar capturar transação
        # Regex flexível: DD-MM-YYYY [descrição opcional] (ID numérico 10+ dígitos) R$ valor R$ saldo
        # Descrição pode estar ausente na linha principal
        pattern = r'^(\d{2}-\d{2}-\d{4})\s+(.+?)\s+(\d{10,})\s+R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\s+R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})$'
        match = re.match(pattern, linha)
        
        # Se não matchou, tentar padrão sem descrição: DD-MM-YYYY ID valor saldo
        if not match:
            pattern_sem_desc = r'^(\d{2}-\d{2}-\d{4})\s+(\d{10,})\s+R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\s+R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})$'
            match_sem_desc = re.match(pattern_sem_desc, linha)
            if match_sem_desc:
                data_str = match_sem_desc.group(1)
                descricao = ""  # Sem descrição na linha principal
                id_operacao = match_sem_desc.group(2)
                valor_str = match_sem_desc.group(3)
                saldo_str = match_sem_desc.group(4)
                match = True  # Marcar como matchado
            else:
                match = False
        else:
            # Match com descrição
            data_str = match.group(1)  # DD-MM-YYYY
            descricao = match.group(2).strip()
            id_operacao = match.group(3)
            valor_str = match.group(4)
            saldo_str = match.group(5)
        
        if match:
            
            # Coletar linhas de contexto anterior (podem ser parte da descrição)
            # Voltar até 2 linhas para pegar descrições que vêm antes
            descricoes_extras = []
            for j in range(max(0, i-2), i):
                linha_anterior = linhas[j].strip()
                # Se não é data, não é cabeçalho, não é paginação e não está vazia
                if linha_anterior and not re.match(r'^\d{2}-\d{2}-\d{4}', linha_anterior):
                    if not any(x in linha_anterior for x in ['EXTRATO', 'DETALHE', 'Data Descrição', 'Valor Saldo', '/9']):
                        descricoes_extras.append(linha_anterior)
            
            # Adicionar descrições extras antes
            if descricoes_extras:
                descricao = ' '.join(descricoes_extras) + ' ' + descricao
            
            # Verificar se as próximas linhas são continuação da descrição
            linhas_seguintes = []
            j = i + 1
            while j < len(linhas):
                proxima_linha = linhas[j].strip()
                if not proxima_linha:
                    j += 1
                    continue
                # Se começa com data, é nova transação - parar
                if re.match(r'^\d{2}-\d{2}-\d{4}', proxima_linha):
                    break
                # Se é cabeçalho ou paginação - parar
                if any(x in proxima_linha for x in ['EXTRATO', 'DETALHE', 'Data Descrição', 'Valor Saldo', '/9']):
                    break
                # É continuação da descrição
                linhas_seguintes.append(proxima_linha)
                j += 1
            
            # Adicionar descrições extras depois
            if linhas_seguintes:
                descricao += ' ' + ' '.join(linhas_seguintes)
                i = j - 1  # Pular as linhas processadas
            
            # Limpar descrição
            descricao = ' '.join(descricao.split())  # Normalizar espaços
            
            # Converter data para DD/MM/YYYY
            try:
                data_obj = datetime.strptime(data_str, '%d-%m-%Y')
                data_iso = data_obj.strftime('%d/%m/%Y')
            except ValueError:
                logger.warning(f"Data inválida: {data_str}")
                i += 1
                continue
            
            # Converter valor brasileiro para float
            valor = _convert_valor_br(valor_str)
            
            # Ignorar valores zero
            if abs(valor) < 0.01:
                i += 1
                continue
            
            transacoes.append((data_iso, descricao, valor))
            logger.debug(f"Transação extraída: {data_iso} | {descricao} | {valor}")
        
        i += 1
    
    logger.debug(f"Total de transações extraídas: {len(transacoes)}")
    
    return transacoes


def _convert_valor_br(valor_str: str) -> float:
    """
    Converte valor no formato brasileiro para float
    Exemplo: "1.234,56" -> 1234.56
             "-234,56" -> -234.56
    """
    # Remover espaços
    valor_str = valor_str.strip()
    
    # Verificar se é negativo
    is_negative = valor_str.startswith('-')
    if is_negative:
        valor_str = valor_str[1:]
    
    # Remover pontos (separador de milhar) e substituir vírgula por ponto
    valor_str = valor_str.replace('.', '').replace(',', '.')
    
    try:
        valor = float(valor_str)
        return -valor if is_negative else valor
    except ValueError:
        logger.warning(f"Erro ao converter valor: {valor_str}")
        return 0.0


if __name__ == "__main__":
    # Teste rápido
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        pdf_path = Path('MP202512.pdf')
    
    if pdf_path.exists():
        transacoes, balance = process_mercadopago_extrato_pdf(pdf_path, str(pdf_path))
        
        print(f'\n✅ Total de transações: {len(transacoes)}')
        print(f'💰 Saldo inicial: R$ {balance.saldo_inicial:,.2f}')
        print(f'💰 Soma transações: R$ {balance.soma_transacoes:,.2f}')
        print(f'💰 Saldo final: R$ {balance.saldo_final:,.2f}')
        print(f'✅ Validação: {balance.is_valid} (diferença: {balance.diferenca})')
        
        print(f'\n📋 Primeiras 10 transações:')
        for i, t in enumerate(transacoes[:10], 1):
            print(f'  {i:2}. {t.data} | {t.lancamento:<50} | R$ {t.valor:>10,.2f}')
    else:
        print(f'❌ Arquivo não encontrado: {pdf_path}')
