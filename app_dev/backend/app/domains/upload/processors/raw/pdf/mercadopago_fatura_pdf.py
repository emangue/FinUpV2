"""
Processador para Fatura Mercado Pago — PDF
Usa OCR (easyocr + PyMuPDF) para extrair texto legível das páginas.

O PDF do Mercado Pago usa fontes com mapeamento de caracteres corrompido:
as descrições ficam ilegíveis com extração de texto convencional.
OCR resolve isso renderizando cada página como imagem primeiro.

DEPENDÊNCIAS (adicionar ao requirements.txt):
    easyocr>=1.7.0         # OCR engine (instala PyTorch automaticamente)
    PyMuPDF>=1.24.0        # renderização de PDF para imagem (fitz)

NOTA DE PERFORMANCE:
    - Primeira execução: download de modelos easyocr (~100MB em ~/.EasyOCR/)
    - Por página: ~3-8s (CPU) dependendo do hardware
    - Por fatura: ~15-40s (5-7 páginas úteis)

RETORNO: Tuple[List[RawTransaction], BalanceValidation]
    - saldo_inicial=0.0 (fatura, sem saldo inicial)
    - saldo_final = "Total a pagar" da capa da fatura
    - is_valid = True se soma das compras bate com o total
"""

import io
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF

from ..base import RawTransaction, BalanceValidation

logger = logging.getLogger(__name__)

# ─── Cache do leitor OCR (inicialização pesada: ~5s + download na primeira vez)
_ocr_reader = None


def _get_reader():
    """Retorna o leitor OCR inicializado (singleton)."""
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        logger.info("Inicializando easyocr (pode demorar na primeira execução)...")
        _ocr_reader = easyocr.Reader(['pt', 'en'], gpu=False, verbose=False)
        logger.info("easyocr pronto.")
    return _ocr_reader


# ─── Regex de apoio ────────────────────────────────────────────────────────────

# Data no formato DD/MM (início de linha de transação)
_RE_DATE = re.compile(r'^(\d{2})/(\d{2})$')

# Valor monetário: "R$ 1.234,56" ou "R$1.234,56"
_RE_VALUE = re.compile(r'R\$\s*([\d.]+,\d{2})')

# Final do cartão: "5966]" ou "'5966]" ou "*5966]"
_RE_FINAL_CARTAO = re.compile(r"['\*\[]?(\d{4})\]")

# Total a pagar na capa: "Total a pagar" + valor ou "R$ 1.234,56" isolado
_RE_TOTAL_CAPA = re.compile(r'R\$\s*([\d.]+,\d{2})', re.IGNORECASE)

# Linhas a ignorar (conversão cambial)
_SKIP_PATTERNS = [
    re.compile(r'BRL\s*\d*\s*=\s*USD'),
    re.compile(r'USD\s*\d*\s*=\s*R\$'),
    re.compile(r'BRL\s+[\d.]+'),
]


def process_mercadopago_fatura_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = "Mercado Pago",
    final_cartao: str = None,
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa fatura Mercado Pago em formato PDF via OCR.

    Assinatura compatível com o registry do V5:
        processor(file_path, nome_arquivo, nome_cartao, final_cartao)

    Args:
        file_path: Caminho do arquivo .pdf
        nome_arquivo: Nome original do arquivo (usado para extrair mes_fatura)
        nome_cartao: Nome do cartão para identificação (padrão: 'Mercado Pago')
        final_cartao: Ignorado — extraído do próprio PDF por seção de cartão

    Returns:
        Tupla (List[RawTransaction], BalanceValidation).
        service.py detecta a tupla via isinstance e salva o balance_validation.
    """
    logger.info(f"Processando fatura Mercado Pago PDF via OCR: {nome_arquivo}")
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    doc = fitz.open(str(file_path))
    logger.debug(f"PDF aberto: {doc.page_count} páginas")

    # ── Extrair metadados da fatura ───────────────────────────────────────────
    mes_fatura = _extract_mes_fatura(nome_arquivo)
    ano_fatura, num_mes_fatura = _extract_ano_mes_from_cover(doc, nome_arquivo)
    data_criacao = datetime.now()

    # ── Total a pagar (da capa — página 1) ───────────────────────────────────
    balance = BalanceValidation()
    balance.saldo_inicial = 0.0
    balance.saldo_final = _extract_total_capa(doc[0])
    if balance.saldo_final:
        logger.debug(f"Total a pagar: R$ {balance.saldo_final:.2f}")
    else:
        logger.warning("Total a pagar não encontrado na capa")

    # ── OCR em cada página de transações ──────────────────────────────────────
    reader = _get_reader()
    transactions: List[RawTransaction] = []

    for page_num in range(1, doc.page_count):
        page = doc[page_num]

        # Verificar rapidamente se é página de parcelamento (ignorar)
        quick_text = page.get_text('text')
        if _is_installment_page(quick_text):
            logger.debug(f"Pág {page_num + 1}: página de parcelamento — ignorada")
            continue

        logger.debug(f"Pág {page_num + 1}: rodando OCR...")
        rows = _ocr_page_to_rows(reader, page)
        page_transactions = _parse_rows(
            rows, nome_arquivo, nome_cartao, mes_fatura,
            ano_fatura, num_mes_fatura, data_criacao
        )
        transactions.extend(page_transactions)
        logger.debug(f"Pág {page_num + 1}: {len(page_transactions)} transações extraídas")

    doc.close()

    # ── Validação ─────────────────────────────────────────────────────────────
    balance.soma_transacoes = round(sum(t.valor for t in transactions), 2)
    balance.validate()

    logger.info(f"✅ Fatura Mercado Pago PDF: {len(transactions)} transações")
    if balance.saldo_final:
        logger.info(
            f"{'✅' if balance.is_valid else '⚠️ ATENÇÃO'} Validação: "
            f"total declarado R$ {balance.saldo_final:.2f} | "
            f"soma extraída R$ {balance.soma_transacoes:.2f} | "
            f"diferença R$ {balance.diferenca:.2f}"
        )

    return transactions, balance


# ─── OCR: renderizar página e agrupar por linha ────────────────────────────────

def _ocr_page_to_rows(reader, page) -> List[List[Tuple]]:
    """
    Renderiza página como imagem, aplica OCR e agrupa resultados por linha.

    Returns:
        Lista de linhas. Cada linha é uma lista de (bbox, text, conf)
        ordenada da esquerda para a direita.
    """
    # Renderizar em 3x (≈216 DPI) — resolução suficiente para OCR preciso
    mat = fitz.Matrix(3.0, 3.0)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes('png')

    results = reader.readtext(img_bytes, detail=1, paragraph=False)

    # Agrupar por y (centro da bbox), tolerância de 25px na imagem 3x
    return _group_by_row(results, y_tolerance=25)


def _group_by_row(results, y_tolerance: int = 25) -> List[List[Tuple]]:
    """Agrupa elementos OCR pelo eixo Y (mesma linha visual)."""
    items = list(enumerate(results))
    items_sorted = sorted(items, key=lambda x: x[1][0][0][1])  # sort by y_top
    used = [False] * len(results)
    rows = []

    for i, (orig_i, (bbox, text, conf)) in enumerate(items_sorted):
        if used[orig_i]:
            continue
        y_center = (bbox[0][1] + bbox[2][1]) / 2
        row = [(bbox, text, conf)]
        used[orig_i] = True

        for j, (orig_j, (bbox2, text2, conf2)) in enumerate(items_sorted):
            if used[orig_j]:
                continue
            y2_center = (bbox2[0][1] + bbox2[2][1]) / 2
            if abs(y_center - y2_center) < y_tolerance:
                row.append((bbox2, text2, conf2))
                used[orig_j] = True

        # Ordenar da esquerda para direita dentro da linha
        row.sort(key=lambda x: x[0][0][0])
        rows.append(row)

    return rows


# ─── Parser de linhas OCR ──────────────────────────────────────────────────────

def _parse_rows(
    rows: List[List[Tuple]],
    nome_arquivo: str,
    nome_cartao: str,
    mes_fatura: str,
    ano_fatura: int,
    num_mes_fatura: int,
    data_criacao: datetime,
) -> List[RawTransaction]:
    """
    Interpreta as linhas OCR de uma página e extrai transações.

    Lógica:
    - "Cartão Visa [***XXXX]" → atualiza final_cartao corrente
    - "Movimentações na fatura" → entra em modo 'pagamentos' (skip)
    - Linha com DD/MM no início → transação
      - "Pagamento da fatura de..." → ignorada (crédito de pagamento)
      - BRL/USD info → ignorada (conversão cambial)
      - Demais → RawTransaction
    """
    transactions: List[RawTransaction] = []
    current_final_cartao = ""
    in_payment_section = False  # seção de pagamentos/créditos no topo

    for row in rows:
        texts = [text.strip() for _, text, conf in row if conf > 0.3 and text.strip()]
        if not texts:
            continue

        joined = " ".join(texts)

        # ── Detectar seção de cartão ──────────────────────────────────────────
        if "Cartão Visa" in joined or "Cartao Visa" in joined:
            match = _RE_FINAL_CARTAO.search(joined)
            if match:
                current_final_cartao = match.group(1)
                logger.debug(f"Cartão detectado: *{current_final_cartao}")
            in_payment_section = False  # reset: agora é seção de compras
            continue

        # ── Detectar seção de movimentações globais (pagamentos/créditos) ─────
        if "Movimentações na fatura" in joined or "Movimentacoes na fatura" in joined:
            in_payment_section = True
            continue

        # ── Ignorar cabeçalhos e separadores ─────────────────────────────────
        if any(h in joined for h in [
            "Data", "Movimentações", "Valor em R$", "Detalhes de consumo",
            "Detalhes do consumo", "mercado", "pago", "Emanuel", "Vencimento"
        ]):
            if not _RE_DATE.match(texts[0]):
                continue

        # ── Linhas de total (ex: "Total R$ 241,34") ──────────────────────────
        if texts[0].lower() == "total":
            continue

        # ── Verificar se primeira palavra é uma data DD/MM ────────────────────
        date_match = _RE_DATE.match(texts[0])
        if not date_match:
            continue

        dd, mm = date_match.group(1), date_match.group(2)

        # ── Ignorar linhas de conversão cambial ───────────────────────────────
        if any(p.search(joined) for p in _SKIP_PATTERNS):
            logger.debug(f"Linha FX ignorada: {joined}")
            continue

        # ── Extrair valor (último elemento que parece valor) ──────────────────
        valor = None
        value_texts_idx = []
        for idx, (bbox, text, conf) in enumerate(row):
            m = _RE_VALUE.search(text)
            if m:
                valor = _parse_value(m.group(1))
                value_texts_idx.append(idx)

        if valor is None:
            logger.debug(f"Linha sem valor: {joined}")
            continue

        # ── Extrair descrição (tudo entre data e valor) ───────────────────────
        last_value_idx = max(value_texts_idx) if value_texts_idx else len(row) - 1
        desc_parts = []
        for idx, (bbox, text, conf) in enumerate(row):
            if idx == 0:  # skip data
                continue
            if idx >= last_value_idx:  # skip valor
                break
            t = text.strip()
            if t and conf > 0.3:
                desc_parts.append(t)

        descricao = " ".join(desc_parts).strip()
        if not descricao:
            descricao = "Mercado Pago"

        # ── Ignorar pagamentos de fatura ──────────────────────────────────────
        if in_payment_section or "Pagamento da fatura" in descricao:
            logger.debug(f"Pagamento ignorado: {descricao}")
            continue

        # ── Inferir ano correto da transação ──────────────────────────────────
        num_mes = int(mm)
        if num_mes > num_mes_fatura:
            ano_transacao = ano_fatura - 1
        else:
            ano_transacao = ano_fatura

        data_iso = f"{ano_transacao}-{mm}-{dd}"

        transactions.append(RawTransaction(
            banco="Mercado Pago",
            tipo_documento="fatura",
            nome_arquivo=nome_arquivo,
            data_criacao=data_criacao,
            data=data_iso,
            lancamento=descricao,
            valor=valor,
            nome_cartao=nome_cartao,
            final_cartao=current_final_cartao,
            mes_fatura=mes_fatura,
        ))
        logger.debug(f"  ✓ {data_iso} | {descricao[:40]} | R$ {valor:.2f} | cartão *{current_final_cartao}")

    return transactions


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_installment_page(text: str) -> bool:
    """Retorna True se a página é sobre parcelamento (não tem transações)."""
    return (
        "Parcele a fatura" in text or
        ("parcelamento" in text.lower() and "Cartão Visa" not in text and "Data" not in text)
    )


def _extract_total_capa(page) -> Optional[float]:
    """
    Extrai o 'Total a pagar' da capa (página 1) usando texto nativo do PDF.
    O campo fica logo após 'Total a pagar' e antes do vencimento.
    """
    text = page.get_text('text')
    # Linha típica: "R$ 241,34\n04/08/2025 R$ 35.000,00"
    # Tentamos capturar o primeiro valor R$ após "Total a pagar"
    match = re.search(r'Total a pagar\s*[\n\r]*(?:Vence em.*?[\n\r]*)?\s*(R\$\s*[\d.]+,\d{2})', text, re.IGNORECASE | re.DOTALL)
    if match:
        return _parse_value(match.group(1).replace('R$', '').strip())

    # Fallback: capturar o primeiro valor grande isolado na página
    # (o total fica bem destacado na capa)
    matches = _RE_TOTAL_CAPA.findall(text)
    # Filtrar valores > 0 e pegar o primeiro (normalmente é o total)
    for m in matches:
        v = _parse_value(m)
        if v and v > 0:
            return v
    return None


def _extract_ano_mes_from_cover(doc, nome_arquivo: str) -> Tuple[int, int]:
    """
    Extrai ano e mês da fatura da capa (página 1) ou do nome do arquivo.
    Ex: "Essa é sua fatura de julho" + "Emitido em: 30/07/2025" → (2025, 7)
    """
    meses_map = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    }
    text = doc[0].get_text('text')

    # "Emitido em: 30/07/2025" → ano=2025, mês=7
    match_emitido = re.search(r'Emitido em:\s*(\d{2})/(\d{2})/(\d{4})', text, re.IGNORECASE)
    if match_emitido:
        mes = int(match_emitido.group(2))
        ano = int(match_emitido.group(3))
        logger.debug(f"Fatura: emitido em {match_emitido.group(0)} → mês {mes}/{ano}")
        return ano, mes

    # "fatura de julho" → mês a partir do nome do mês
    match_mes = re.search(
        r'fatura de (' + '|'.join(meses_map.keys()) + r')',
        text, re.IGNORECASE
    )
    if match_mes:
        mes_nome = match_mes.group(1).lower()
        mes = meses_map[mes_nome]
        # Buscar o ano no mesmo texto
        match_ano = re.search(r'(\d{4})', text)
        ano = int(match_ano.group(1)) if match_ano else datetime.now().year
        logger.debug(f"Fatura: {mes_nome} {ano}")
        return ano, mes

    # Fallback: nome do arquivo (ex: "FaturaMercadoPago202507.pdf")
    match_arq = re.search(r'(\d{4})(\d{2})', nome_arquivo)
    if match_arq:
        return int(match_arq.group(1)), int(match_arq.group(2))

    now = datetime.now()
    return now.year, now.month


def _extract_mes_fatura(nome_arquivo: str) -> str:
    """
    Extrai mês da fatura do nome do arquivo.
    Ex: 'FaturaMercadoPago202507.pdf' → '202507'
    """
    match = re.search(r'(\d{6})', nome_arquivo)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y%m")


def _parse_value(value_str: str) -> float:
    """Converte '1.234,56' ou 'R$ 1.234,56' para float."""
    value_str = value_str.strip().replace("R$", "").replace(" ", "")
    value_str = value_str.replace(".", "").replace(",", ".")
    try:
        return float(value_str)
    except ValueError:
        logger.warning(f"Não foi possível converter valor: {value_str!r}")
        return 0.0
