"""
TRECHO PARA COLAR NO registry.py DO V5
=======================================
Substitui/complementa o arquivo:
  app/domains/upload/processors/raw/registry.py

1. Adicionar estes imports junto aos demais imports existentes:
"""

# ── IMPORTS A ADICIONAR ────────────────────────────────────────────────────────

import os
from functools import partial

# Novos processadores (adicionar após os imports existentes)
from .pdf.btg_fatura_pdf import process_btg_fatura_pdf
from .excel.btg_fatura_xlsx import process_btg_fatura_xlsx
from .pdf.mercadopago_fatura_pdf import process_mercadopago_fatura_pdf

# Atualizado (já existe, mas agora aceita `senha`)
# from .pdf.itau_fatura_pdf import process_itau_fatura_pdf  <- já está lá

# ── VARIÁVEIS DE SENHA (adicionar após os imports) ────────────────────────────

_ITAU_SENHA = os.getenv("ITAU_PDF_SENHA")  # CPF sem pontos/traço
_BTG_SENHA  = os.getenv("BTG_PDF_SENHA")   # CPF sem pontos/traço


# ── ENTRADAS A ADICIONAR/ATUALIZAR NO DICT PROCESSORS ────────────────────────
#
# Localizar o dict PROCESSORS e:
#   1. Atualizar a entrada ('itau', 'fatura', 'pdf')
#   2. Adicionar as entradas BTG fatura e Mercado Pago fatura abaixo
#

PROCESSORS_DELTA = {

    # ── ITAÚ (atualizar entrada existente) ────────────────────────────────────
    # Era: ('itau', 'fatura', 'pdf'): process_itau_fatura_pdf,
    # Vira:
    ("itau", "fatura", "pdf"): (
        partial(process_itau_fatura_pdf, senha=_ITAU_SENHA)
        if _ITAU_SENHA
        else process_itau_fatura_pdf
    ),

    # ── BTG PACTUAL (novas entradas) ──────────────────────────────────────────
    # XLSX — preferido (dados mais limpos, final_cartao por linha)
    ("btg", "fatura", "excel"): (
        partial(process_btg_fatura_xlsx, senha=_BTG_SENHA)
        if _BTG_SENHA
        else process_btg_fatura_xlsx
    ),
    ("btg pactual", "fatura", "excel"): (
        partial(process_btg_fatura_xlsx, senha=_BTG_SENHA)
        if _BTG_SENHA
        else process_btg_fatura_xlsx
    ),
    # PDF — fallback quando só houver o PDF
    ("btg", "fatura", "pdf"): (
        partial(process_btg_fatura_pdf, senha=_BTG_SENHA)
        if _BTG_SENHA
        else process_btg_fatura_pdf
    ),
    ("btg pactual", "fatura", "pdf"): (
        partial(process_btg_fatura_pdf, senha=_BTG_SENHA)
        if _BTG_SENHA
        else process_btg_fatura_pdf
    ),

    # ── MERCADO PAGO (novas entradas) ─────────────────────────────────────────
    # PDF usa OCR (easyocr + PyMuPDF) — PDF tem fonte corrompida, texto nativo ilegível
    ("mercado pago", "fatura", "pdf"): process_mercadopago_fatura_pdf,
    ("mercadopago",  "fatura", "pdf"): process_mercadopago_fatura_pdf,
}

# Nota: _normalize_bank_name("BTG Pactual") -> "btg pactual" (com espaço)
#        _normalize_bank_name("Mercado Pago") -> "mercado pago"
