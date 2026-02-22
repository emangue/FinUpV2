"""
Processador para Fatura BTG Pactual - PDF com senha

DEPLOY → ProjetoFinancasV5
  Destino: app/domains/upload/processors/raw/pdf/btg_fatura_pdf.py  (NOVO arquivo)
  Registry: adicionar entradas para ('btg pactual', 'fatura', 'pdf') e aliases

FORMATO DO PDF:
  - Protegido por senha (padrão: CPF sem pontos/traço)
  - Layout de duas colunas — texto extraído como string corrida
  - Transações nacionais:  "DD Mon Descrição R$ valor"
  - Transações internacionais: "DD Mon Descrição USD/EUR amount"
                               seguido de "Conversão para Real - R$ valor_brl"
  - Seções por cartão: "Lançamentos do cartão ... | Final XXXX"

RETORNO: Tuple[List[RawTransaction], BalanceValidation]
  - service.py trata nativamente via isinstance(result, tuple)
  - saldo_inicial=0.0 (fatura, sem saldo inicial)
  - saldo_final = total declarado no PDF ("valor a pagar de R$ X,XX")
  - is_valid = True se soma bate com o total (tolerância 1 centavo)

⚠️  RECOMENDAÇÃO: Use btg_fatura_xlsx.py quando o .xlsx estiver disponível.
O XLSX tem estrutura limpa com datas exatas, valores BRL e final do cartão separados.
O PDF é o fallback quando só houver o PDF.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pdfplumber

from ..base import RawTransaction, BalanceValidation

logger = logging.getLogger(__name__)

# Meses em português usados pelo BTG no PDF
_MESES_PT = {
    "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
    "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
}
_MESES_PATTERN = "|".join(_MESES_PT.keys())


def process_btg_fatura_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = "BTG Pactual",
    final_cartao: str = None,
    senha: Optional[str] = None,
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa fatura BTG Pactual em formato PDF (com ou sem senha).

    Assinatura compatível com o registry do V5:
        processor(file_path, nome_arquivo, nome_cartao, final_cartao)
    O parâmetro `senha` deve ser injetado via functools.partial no registry:
        partial(process_btg_fatura_pdf, senha=os.getenv('BTG_SENHA'))

    Args:
        file_path: Caminho do arquivo .pdf
        nome_arquivo: Nome original do arquivo
        nome_cartao: Nome do cartão para identificação
        final_cartao: Final do cartão (4 dígitos) — ignorado aqui, extraído do PDF
        senha: Senha de proteção do PDF (CPF sem pontos/traço)

    Returns:
        Tupla (List[RawTransaction], BalanceValidation).
        service.py detecta a tupla via isinstance e salva o balance_validation.
    """
    logger.info(f"Processando fatura BTG PDF: {nome_arquivo}" + (" [com senha]" if senha else ""))

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Extrair texto completo do PDF
    open_kwargs = {"password": senha} if senha else {}
    try:
        with pdfplumber.open(file_path, **open_kwargs) as pdf:
            logger.debug(f"PDF aberto: {len(pdf.pages)} páginas")
            texto_completo = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texto_completo += text + "\n"
    except Exception as e:
        raise Exception(f"Falha ao abrir PDF '{file_path.name}': {e}") from e

    # Extrair metadados da fatura
    mes_fatura = _extract_mes_fatura(nome_arquivo)
    ano_fatura, num_mes_fatura = _extract_ano_mes_fatura(texto_completo, nome_arquivo)
    data_criacao = datetime.now()

    # Capturar total declarado no PDF
    balance = BalanceValidation()
    balance.saldo_inicial = 0.0  # Fatura não tem saldo inicial
    balance.saldo_final = _extract_total_pdf(texto_completo)
    if balance.saldo_final is not None:
        logger.debug(f"Total declarado na fatura: R$ {balance.saldo_final:.2f}")
    else:
        logger.warning("Total da fatura não encontrado no PDF")

    # Extrair transações por seção de cartão
    transacoes_raw = _extract_all_transactions(texto_completo, ano_fatura, num_mes_fatura)

    transactions: List[RawTransaction] = []
    for data_str, descricao, valor, final_cartao_pdf, tipo_compra in transacoes_raw:
        transactions.append(
            RawTransaction(
                banco="BTG",
                tipo_documento="fatura",
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=data_str,
                lancamento=descricao,
                valor=valor,
                nome_cartao=nome_cartao,
                final_cartao=final_cartao_pdf,  # extraído do PDF por seção de cartão
                mes_fatura=mes_fatura,
            )
        )

    # Validar soma vs total declarado
    balance.soma_transacoes = round(sum(t.valor for t in transactions), 2)
    balance.validate()

    logger.info(f"✅ Fatura BTG PDF processada: {len(transactions)} transações")
    logger.info(
        f"{'✅' if balance.is_valid else '⚠️ ATENÇÃO'} Validação: "
        f"total declarado R$ {balance.saldo_final:.2f} | "
        f"soma extraída R$ {balance.soma_transacoes:.2f} | "
        f"diferença R$ {balance.diferenca:.2f}"
    )
    return transactions, balance


# ─── Extração de transações ────────────────────────────────────────────────────

def _extract_all_transactions(
    texto: str,
    ano_fatura: int,
    mes_fatura: int,
) -> List[Tuple[str, str, float, str, str]]:
    """
    Percorre o texto completo e extrai transações de todas as seções de cartão.

    Returns:
        Lista de (data_iso, descricao, valor, final_cartao, tipo_compra)
    """
    resultados = []

    regex_secao = re.compile(
        r'Lançamentos do cartão\s+\S+\s*\|[^|]+\|\s*Final\s+(\d{4})',
        re.IGNORECASE
    )

    secoes = list(regex_secao.finditer(texto))
    logger.debug(f"Seções de cartão encontradas: {len(secoes)}")

    for i, secao in enumerate(secoes):
        final_cartao = secao.group(1)
        inicio = secao.end()
        fim = secoes[i + 1].start() if i + 1 < len(secoes) else len(texto)
        bloco = texto[inicio:fim]

        transacoes_secao = _extract_transactions_from_block(
            bloco, final_cartao, ano_fatura, mes_fatura
        )
        resultados.extend(transacoes_secao)
        logger.debug(f"  Final {final_cartao}: {len(transacoes_secao)} transações")

    return resultados


def _extract_total_pdf(texto: str) -> Optional[float]:
    """
    Extrai o total a pagar declarado no PDF do BTG.
    Ex: 'Fevereiro no valor a pagar de R$ 646,76'
    """
    patterns = [
        r'valor a pagar de R\$\s*([\d.]+,[\d]{2})',
        r'Total a pagar\s+R\$\s*([\d.]+,[\d]{2})',
        r'no valor de R\$\s*([\d.]+,[\d]{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, texto, re.IGNORECASE)
        if match:
            return _convert_valor_br(match.group(1))
    return None


def _split_two_columns(texto: str) -> str:
    """
    O PDF BTG tem layout de duas colunas: duas transações — ou uma transação e
    informações de câmbio — podem aparecer na mesma linha de texto. Ex:
      '10 Jan Umbro (1/3) R$ 54,51 21 Jan Hostinger US$ 7,99'
      '10 Jan Netshoes (1/3) R$ 79,83 Cotação da moeda - R$ 5,70'

    Insere newlines nos três pontos de corte naturais:
      1. Valor (X,XX) seguido de DD Mon  → início de nova transação
      2. Antes de 'Cotação da moeda'     → info de câmbio da coluna direita
      3. Antes de 'Conversão para Real'  → conversão BRL da coluna direita
    """
    texto = re.compile(
        r'(\d{1,3}(?:\.\d{3})*,\d{2})\s+(?=\d{2}\s+(?:' + _MESES_PATTERN + r')\s+)'
    ).sub(r'\1\n', texto)
    texto = re.sub(r'(Cotação da moeda)', r'\n\1', texto)
    texto = re.sub(r'(Conversão para Real)', r'\n\1', texto)
    return texto


def _extract_transactions_from_block(
    bloco: str,
    final_cartao: str,
    ano_fatura: int,
    mes_fatura: int,
) -> List[Tuple[str, str, float, str, str]]:
    """
    Extrai transações de um bloco de texto de um cartão específico.

    Trata dois formatos:
      Nacional:       "DD Mon Descrição R$ valor"
      Internacional:  "DD Mon Descrição US$|EUR amount"
                      seguido de "Conversão para Real - R$ valor_brl"
    """
    bloco_normalizado = _split_two_columns(bloco)
    linhas = bloco_normalizado.split("\n")

    regex_nacional = re.compile(
        r'^(\d{2})\s+(' + _MESES_PATTERN + r')\s+(.+?)\s+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s*$'
    )
    regex_int_header = re.compile(
        r'^(\d{2})\s+(' + _MESES_PATTERN + r')\s+(.+?)\s+(?:US\$|USD|EUR|GBP|ARS)\s*[\d.,]+\s*$'
    )
    regex_conversao = re.compile(
        r'Conversão para Real\s*-?\s*R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})'
    )
    regex_cotacao = re.compile(r'Cotação da moeda', re.IGNORECASE)

    transacoes: List[Tuple[str, str, float, str, str]] = []
    pending_intl: Optional[dict] = None

    for linha in linhas:
        linha_strip = linha.strip()
        if not linha_strip:
            continue

        match_conv = regex_conversao.search(linha_strip)
        if match_conv and pending_intl:
            valor = _convert_valor_br(match_conv.group(1))
            transacoes.append((
                pending_intl["data"],
                pending_intl["desc"],
                valor,
                final_cartao,
                "Compra internacional",
            ))
            logger.debug(f"  Intl completada: {pending_intl['desc']} R$ {valor}")
            pending_intl = None
            continue

        if regex_cotacao.search(linha_strip):
            continue

        match_nac = regex_nacional.match(linha_strip)
        if match_nac:
            dd, mes_str, desc, valor_str = (
                match_nac.group(1), match_nac.group(2),
                match_nac.group(3).strip(), match_nac.group(4),
            )
            data_iso = _build_date(dd, mes_str, ano_fatura, mes_fatura)
            valor = _convert_valor_br(valor_str)
            tipo = _classify_tipo(desc)
            transacoes.append((data_iso, desc, valor, final_cartao, tipo))
            logger.debug(f"  Nacional: {data_iso} {desc} R$ {valor}")
            continue

        match_int = regex_int_header.match(linha_strip)
        if match_int:
            pending_intl = None
            dd, mes_str, desc = (
                match_int.group(1), match_int.group(2),
                match_int.group(3).strip(),
            )
            data_iso = _build_date(dd, mes_str, ano_fatura, mes_fatura)
            pending_intl = {"data": data_iso, "desc": desc}
            logger.debug(f"  Intl iniciada: {data_iso} {desc}")

    return transacoes


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_date(dd: str, mes_str: str, ano_fatura: int, mes_fatura: int) -> str:
    """Monta data ISO YYYY-MM-DD inferindo o ano correto."""
    num_mes = _MESES_PT.get(mes_str, 1)
    ano = ano_fatura - 1 if num_mes > mes_fatura else ano_fatura
    return f"{ano}-{num_mes:02d}-{int(dd):02d}"


def _convert_valor_br(valor_str: str) -> float:
    """Converte '1.234,56' ou 'R$ 1.234,56' para float."""
    valor_str = valor_str.strip().replace("R$", "").strip()
    negativo = valor_str.startswith("-")
    valor_str = valor_str.lstrip("-").strip()
    valor_str = valor_str.replace(".", "").replace(",", ".")
    try:
        valor = float(valor_str)
        return -valor if negativo else valor
    except ValueError:
        logger.warning(f"Não foi possível converter valor: {valor_str!r}")
        return 0.0


def _classify_tipo(descricao: str) -> str:
    """Classifica tipo de compra a partir da descrição."""
    desc_upper = descricao.upper()
    if "SEGURO" in desc_upper:
        return "Contratação Seguro"
    if re.search(r'\d+/\d+', descricao):
        return "Parcela sem juros"
    return "Compra à vista"


def _extract_mes_fatura(nome_arquivo: str) -> str:
    """Ex: '2026-02-01_Fatura_..._BTG.pdf' → '202602'"""
    match = re.search(r'(\d{4})-(\d{2})-\d{2}', nome_arquivo)
    if match:
        return match.group(1) + match.group(2)
    match = re.search(r'(\d{6})', nome_arquivo)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y%m")


def _extract_ano_mes_fatura(texto: str, nome_arquivo: str) -> Tuple[int, int]:
    """Extrai o ano e mês da fatura do texto do PDF ou do nome do arquivo."""
    meses_map = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    }
    match = re.search(
        r'fatura de (' + '|'.join(meses_map.keys()) + r') de (\d{4})',
        texto,
        re.IGNORECASE,
    )
    if match:
        mes = meses_map[match.group(1).lower()]
        ano = int(match.group(2))
        logger.debug(f"Fatura: {match.group(1)} {ano} → mês {mes}")
        return ano, mes

    match_arq = re.search(r'(\d{4})-(\d{2})-\d{2}', nome_arquivo)
    if match_arq:
        return int(match_arq.group(1)), int(match_arq.group(2))

    now = datetime.now()
    return now.year, now.month
