"""
📄 PROCESSADOR BTG PACTUAL - EXTRATO DE CONTA CORRENTE (Formato PDF)

=== FORMATO ===
PDF de múltiplas páginas gerado pelo JasperReports 6.16.0.
Cada página repete o cabeçalho completo (Cliente, CPF, Agência...).
Transações no formato: DD/MM/YYYY HHhMM Categoria Transação Descrição ±R$ X.XXX,XX

=== PADRÕES DE FRAGMENTAÇÃO ===
O JasperReports pode quebrar linhas longas em múltiplas linhas:

Padrão A (Crédito e Financiamento simples):
    'Crédito e'
    'DD/MM/YYYY HHhMM Transação Descrição -R$ valor'
    'Financiamento'

Padrão B (Crédito e Financiamento com descrição transbordada):
    'Crédito e [início da descrição]'
    'DD/MM/YYYY HHhMM Transação -R$ valor'
    'Financiamento [fim da descrição]'

Padrão C (Transação transborda ANTES da data):
    '[texto da coluna Transação]'
    'DD/MM/YYYY HHhMM Categoria Descrição -R$ valor'   ← linha completa

Padrão D (Transação transborda antes E depois — sanduíche):
    '[início da coluna Transação]'
    'DD/MM/YYYY HHhMM Categoria Descrição -R$ valor'   ← linha completa
    '[fim da coluna Transação]'

=== ESTRATÉGIA (máquina de estados) ===
- Flag `credito_e_context` ativa quando linha começa com 'Crédito e' sem data
- Padrões C e D: a linha de data já é completa → overflow antes/depois é ignorado
- Padrões A e B: injetar 'Crédito e Financiamento - ' no início do lançamento

=== LINHAS IGNORADAS ===
- Cabeçalho: 'Olá', 'Este é o extrato', 'Extrato de conta', 'Cliente:', 'CPF:',
             'Agência:', 'Conta:', 'Período', 'Lançamentos:', 'Data e hora'
- Rodapé: 'Ouvidoria', '©BTG'
- Saldo Diário: 'Saldo Diário'
- Overflows de coluna (Padrões C e D): ignorados pois linha de data já é completa

=== RESULTADO ESPERADO (arquivo de referência) ===
- Arquivo: Extrato_2025-12-10_a_2026-03-09_11259347605.pdf
- 65 transações (mesmo período do XLS)
- Saldo R$ 97,02
- 3 transações de 'Crédito e Financiamento': -R$ 17.064,96 / -11.348,77 / -31,31

=== HISTÓRICO ===
- V1 (16/03/2026): criado após análise laboratorial do PDF de 3 páginas
  Analista: diagnóstico em docs/features/upload-btg-extrato/DIAGNOSTICO_BTG_EXTRATO_XLS.md
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List

import pdfplumber

try:
    from ..base import RawTransaction
except ImportError:
    # Para testes standalone
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class RawTransaction:
        banco: str
        tipo_documento: str
        nome_arquivo: str
        data_criacao: datetime
        data: str
        lancamento: str
        valor: float
        nome_cartao: Optional[str] = None
        final_cartao: Optional[str] = None
        mes_fatura: Optional[str] = None

logger = logging.getLogger(__name__)

# Regex: linha de transação começa com DD/MM/YYYY HHhMM
_RE_DATE_LINE = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+\d{2}h\d{2}\s+')

# Regex: extrai valor do final da linha  →  -R$ 1.234,56  ou  R$ 1.234,56
_RE_VALOR_END = re.compile(r'(-?R\$\s*[\d\.]+,\d{2})\s*$')

# Palavras-chave que identificam linhas de cabeçalho/rodapé — ignorar
_SKIP_KEYWORDS = [
    'Olá',
    'Este é o extrato',
    'Extrato de conta',
    'Cliente:',
    'CPF:',
    'Agência:',
    'Conta:',
    'Período',
    'Lançamentos:',
    'Data e hora',
    'Ouvidoria',
    '©BTG',
    'CNPJ',
    'www.btgpactual',
    'btgpactual.com',
]


def _parse_valor(valor_str: str) -> float:
    """
    Converte 'R$ 1.234,56' ou '-R$ 1.234,56' para float.
    Remove R$, espaços e pontos de milhar. Substitui vírgula decimal por ponto.
    """
    # Preservar sinal negativo
    negativo = valor_str.strip().startswith('-')
    # Remover tudo exceto dígitos, vírgula e ponto
    limpo = re.sub(r'[R$\s-]', '', valor_str)       # → "1.234,56"
    limpo = limpo.replace('.', '').replace(',', '.')  # → "1234.56"
    resultado = float(limpo)
    return -resultado if negativo else resultado


def process_btg_extrato_pdf(
    file_path: Path,
    banco: str,
    tipo_documento: str,
    user_email: str,
) -> List[RawTransaction]:
    """
    Processa PDF de extrato BTG Pactual (multi-página JasperReports).

    Args:
        file_path:      Caminho do arquivo .pdf
        banco:          Nome do banco (ex: 'BTG Pactual')
        tipo_documento: 'extrato'
        user_email:     Email do usuário (não usado na extração, mantido por interface)

    Returns:
        Lista de RawTransaction — uma por transação real (sem Saldo Diário)
    """
    transacoes: List[RawTransaction] = []
    nome_arquivo = file_path.name
    data_criacao = datetime.now()

    with pdfplumber.open(file_path) as pdf:
        n_paginas = len(pdf.pages)
        logger.info(f"📄 PDF BTG extrato: {n_paginas} página(s) — {nome_arquivo}")

        for num_pagina, page in enumerate(pdf.pages, 1):
            texto = page.extract_text()
            if not texto:
                logger.warning(f"⚠️  Página {num_pagina} sem texto extraível")
                continue

            lines = texto.splitlines()
            # Flag de estado: próxima data-line pertence à categoria "Crédito e Financiamento"
            credito_e_context = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # ── Cabeçalho / rodapé ─────────────────────────────────────────
                if any(kw in line for kw in _SKIP_KEYWORDS):
                    continue

                # ── Saldo Diário (não é transação real) ────────────────────────
                if 'Saldo Diário' in line:
                    continue

                # ── Padrão A/B: início de "Crédito e Financiamento" ────────────
                # Linha começa com "Crédito e" mas NÃO é linha de data
                if line.startswith('Crédito e') and not _RE_DATE_LINE.match(line):
                    credito_e_context = True
                    # A categoria será injetada na próxima data-line
                    continue

                # ── Padrão A/B: sufixo "Financiamento" após a data-line ────────
                # Linha começa com "Financiamento" mas NÃO é linha de data
                if line.startswith('Financiamento') and not _RE_DATE_LINE.match(line):
                    if credito_e_context:
                        credito_e_context = False  # contexto consumido
                    continue

                # ── Linha de transação: começa com DD/MM/YYYY HHhMM ────────────
                m_date = _RE_DATE_LINE.match(line)
                if m_date:
                    m_valor = _RE_VALOR_END.search(line)
                    if not m_valor:
                        logger.warning(f"⚠️  Linha de data sem valor detectado: {repr(line[:80])}")
                        continue

                    data_str = line[:10]                              # 'DD/MM/YYYY'
                    meio = line[m_date.end() : m_valor.start()].strip()
                    valor = _parse_valor(m_valor.group(1))

                    if valor == 0.0:
                        continue

                    # Injetar categoria "Crédito e Financiamento" se contexto ativo
                    if credito_e_context:
                        lancamento = f"Crédito e Financiamento - {meio}"
                        # NÃO resetar context aqui — espera "Financiamento" na linha seguinte
                    else:
                        lancamento = meio

                    transacoes.append(RawTransaction(
                        banco=banco,
                        tipo_documento=tipo_documento,
                        nome_arquivo=nome_arquivo,
                        data_criacao=data_criacao,
                        data=data_str,
                        lancamento=lancamento,
                        valor=valor,
                        nome_cartao=None,
                        final_cartao=None,
                        mes_fatura=None,
                    ))
                    continue

                # ── Overflow (Padrões C e D) ───────────────────────────────────
                # Qualquer outra linha não-data, não-skip, não-Crédito-e:
                # é overflow da coluna Transação; a linha de data correspondente
                # já contém Categoria + Descrição suficientes → ignorar.

    saldo = sum(t.valor for t in transacoes)
    logger.info(
        f"✅ PDF BTG extrato: {len(transacoes)} transações | "
        f"saldo R$ {saldo:,.2f}"
    )
    return transacoes
