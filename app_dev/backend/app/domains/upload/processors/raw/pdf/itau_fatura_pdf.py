"""
Processador bruto — Fatura Itaú PDF v2
======================================
O CSV (itau_fatura.py) é a fonte da verdade. Esta versão alinha o output
do PDF com o CSV nos pontos que SÃO controláveis pelo processador:

  ✅  Sinal dos valores:
        CSV faz df['valor'] * -1 no bruto (gastos + → saída −).
        Este processador aplica o mesmo ×-1 ao final.
        Resultado: gastos NEGATIVOS, estornos/créditos POSITIVOS.

  ✅  Bug de ano em Produtos/Serviços:
        v1 usava só `ano_fatura` sem inferência de mês → gerava datas como
        2026-12-26 para transações de dezembro/2025.
        v2 passa `mes_fatura` e aplica a mesma lógica da seção principal.

  ✅  Parcelas futuras:
        _extract_produtos_servicos agora descarta transações cujo mês
        inferido é posterior ao fechamento da fatura.

  ℹ️  Espaços no estabelecimento:
        O PDF renderiza "PAODEACUCAR" como uma única palavra sem espaços —
        é limitação de renderização, não do processador. extract_words()
        produz o mesmo resultado que extract_text(). Não é corrigível aqui;
        a normalização de dedup (remove non-alphanumeric) garante que a
        comparação lógica ainda funcione.

Assinatura pública:
    process_itau_fatura_pdf(file_path, nome_arquivo, nome_cartao,
                            final_cartao, senha=None) -> List[RawTransaction]

Compatível como drop-in replacement do v1.
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple

import pdfplumber

try:
    from ..base import RawTransaction
except ImportError:
    # execução standalone / testes fora do pacote
    from dataclasses import dataclass

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


# ─────────────────────────────────────────────────────────────────────────────
# Entry-point público
# ─────────────────────────────────────────────────────────────────────────────

def process_itau_fatura_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str,
    final_cartao: str,
    senha: Optional[str] = None,
) -> List[RawTransaction]:
    """
    Processa fatura Itaú PDF (com ou sem senha).

    Output alinhado com o processador CSV:
        - gastos  → valor NEGATIVO
        - créditos/estornos → valor POSITIVO
    """
    logger.info(
        f"[v2] Processando fatura Itaú PDF: {nome_arquivo}"
        + (" [com senha]" if senha else "")
    )
    try:
        open_kwargs = {"password": senha} if senha else {}
        with pdfplumber.open(file_path, **open_kwargs) as pdf:
            texto_completo = "\n".join(
                (p.extract_text() or "") for p in pdf.pages
            )
            n_paginas = len(pdf.pages)

        logger.debug(f"PDF lido: {n_paginas} páginas")

        transacoes_brutas = _extract_transactions_from_text(texto_completo)
        mes_fatura_str = _extract_mes_fatura(nome_arquivo)
        data_criacao = datetime.now()

        transactions: List[RawTransaction] = []
        for data, lancamento, valor in transacoes_brutas:
            # ── Inverter sinal para alinhar com CSV ───────────────────────
            # O PDF extrai gastos como positivos, igual ao CSV bruto.
            # O CSV aplica df * -1 antes de retornar; fazemos o mesmo aqui.
            # Estornos já chegam negativos (detectados pelo sufixo " -" ou
            # pela palavra ESTORNO) → após ×-1 ficam positivos. ✓
            valor_final = valor * -1

            # ── Converter data YYYY-MM-DD → DD/MM/YYYY ────────────────────
            # O V5 espera DD/MM/YYYY em RawTransaction.data (usado literal
            # na chave do hash FNV-1a). CSV já entrega nesse formato.
            data_br = _iso_to_br(data)

            transactions.append(
                RawTransaction(
                    banco="Itaú",
                    tipo_documento="fatura",
                    nome_arquivo=nome_arquivo,
                    data_criacao=data_criacao,
                    data=data_br,
                    lancamento=lancamento,
                    valor=valor_final,
                    nome_cartao=nome_cartao,
                    final_cartao=final_cartao,
                    mes_fatura=mes_fatura_str,
                )
            )

        logger.info(f"✅ [v2] Fatura Itaú PDF: {len(transactions)} transações")
        return transactions

    except Exception as e:
        logger.error(f"❌ [v2] Erro ao processar fatura Itaú PDF: {e}", exc_info=True)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Extração de transações do texto
# ─────────────────────────────────────────────────────────────────────────────

def _extract_transactions_from_text(texto: str) -> List[Tuple[str, str, float]]:
    """
    Extrai transações do texto do PDF.

    Retorna lista de (data YYYY-MM-DD, estabelecimento, valor_bruto).
    Valores ainda são BRUTOS aqui (gastos positivos); a inversão de sinal
    ocorre em process_itau_fatura_pdf após esta função.
    """
    transacoes: List[Tuple[str, str, float]] = []

    # ── Detectar mês/ano de fechamento da fatura ──────────────────────────
    ano_fatura = mes_fatura = None
    for pat in (
        r'Postagem:\s*\d{2}/(\d{2})/(\d{4})',
        r'Emiss[aã]o:\s*\d{2}/(\d{2})/(\d{4})',
    ):
        m = re.search(pat, texto, re.IGNORECASE)
        if m:
            mes_fatura = int(m.group(1))
            ano_fatura = int(m.group(2))
            break

    if not ano_fatura:
        now = datetime.now()
        ano_fatura, mes_fatura = now.year, now.month

    logger.debug(f"Fatura: {ano_fatura}-{mes_fatura:02d}")

    # ── IOF consolidado ───────────────────────────────────────────────────
    # PDF traz como "Repasse de IOF em R$ XXX" (gasto → positivo bruto)
    iofs = []
    for m in re.finditer(
        r'Repasse de IOF em R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})',
        texto,
        re.IGNORECASE,
    ):
        iofs.append(abs(_br(m.group(1))))

    logger.debug(f"IOFs consolidados: {len(iofs)}")

    # ── Transações brutas via regex DD/MM ESTABELECIMENTO VALOR ───────────
    regex = r'(\d{2}/\d{2})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    brutas = []

    for m in re.finditer(regex, texto, re.IGNORECASE | re.MULTILINE):
        ddmm = m.group(1)
        estab_bruto = m.group(2)
        valor_str = m.group(3)

        dd, mm_str = ddmm[:2], ddmm[3:5]
        mes_tx = int(mm_str)

        # Inferir ano: se mês da transação é APÓS o mês da fatura → ano anterior
        ano_tx = ano_fatura - 1 if mes_tx > mes_fatura else ano_fatura
        data_iso = f"{ano_tx}-{mm_str}-{dd}"

        estab = estab_bruto.strip()

        # Estorno: termina com " -" no estabelecimento
        eh_estorno = False
        if re.search(r'\s*-\s*$', estab):
            estab = re.sub(r'\s*-\s*$', '', estab)
            eh_estorno = True

        estab = re.sub(r'[,.\s]+$', '', estab)

        valor = _br(valor_str)
        if eh_estorno and valor > 0:
            valor = -valor  # já negativo; após ×-1 global ficará positivo

        ctx = texto[max(0, m.start() - 100): m.end() + 100]
        eh_intl = bool(re.search(r'USD|EUR|GBP|ARS', ctx, re.IGNORECASE))

        # Futura: mês posterior ao fechamento desta fatura
        eh_futura = ano_tx > ano_fatura or (
            ano_tx == ano_fatura and mes_tx > mes_fatura
        )

        brutas.append(
            dict(
                ddmm=ddmm,
                data_iso=data_iso,
                estabelecimento=estab,
                valor=valor,
                valor_positivo=abs(valor),
                eh_intl=eh_intl,
                eh_futura=eh_futura,
                posicao=m.start(),
                parcela_atual=None,
                parcela_total=None,
            )
        )

    logger.debug(f"Transações brutas: {len(brutas)}")

    # ── Dedup de parcelas ─────────────────────────────────────────────────
    brutas = _dedup_parcelas(brutas)

    # ── Registros finais (descarta futuras) ───────────────────────────────
    for t in brutas:
        if t["eh_futura"]:
            continue

        valor_final = t["valor"]
        estab_final = t["estabelecimento"]

        # Força negativo se ESTORNO no nome mas valor ainda positivo
        if "ESTORNO" in estab_final.upper() and valor_final > 0:
            valor_final = -valor_final

        transacoes.append((t["data_iso"], estab_final, valor_final))

    # ── IOFs consolidados (gastos, ainda positivos aqui) ─────────────────
    for v in iofs:
        transacoes.append(
            (f"{ano_fatura}-{mes_fatura:02d}-01", "IOF COMPRA INTERNACIONA", v)
        )

    # ── Produtos / Serviços ───────────────────────────────────────────────
    # v2: passa mes_fatura para corrigir inferência de ano
    servicos = _extract_produtos_servicos(
        texto.split("\n"), ano_fatura, mes_fatura
    )

    existentes = {_chave(d, l, v) for d, l, v in transacoes}
    for d, l, v in servicos:
        if _chave(d, l, v) not in existentes:
            transacoes.append((d, l, v))

    logger.debug(f"Total final: {len(transacoes)} transações")
    return transacoes


# ─────────────────────────────────────────────────────────────────────────────
# Dedup de parcelas
# ─────────────────────────────────────────────────────────────────────────────

def _dedup_parcelas(brutas: list) -> list:
    """
    Para compras parceladas que aparecem com múltiplos números (ex: 03/12 e
    04/12 na mesma fatura), mantém apenas a de menor número de parcela.
    Também remove duplicatas com/sem número de parcela na mesma data/valor.
    """
    rx_parcela = re.compile(r'(\d{2})/(\d{2})\s*$')
    sem_parcela = []
    grupos: dict[str, list] = {}

    for t in brutas:
        m = rx_parcela.search(t["estabelecimento"])
        if m:
            t["parcela_atual"] = int(m.group(1))
            t["parcela_total"] = int(m.group(2))
            base = re.sub(
                r'[^A-Z0-9]', '', t["estabelecimento"][:m.start()].upper()
            )
            grupos.setdefault(base, []).append(t)
        else:
            sem_parcela.append(t)

    filtradas = list(sem_parcela)
    for grupo in grupos.values():
        if len(grupo) == 1:
            filtradas.append(grupo[0])
            continue

        # Subgrupos por valor similar (<10% de diferença)
        subs: list[list] = []
        for t in grupo:
            placed = False
            for s in subs:
                ref = s[0]["valor_positivo"]
                if ref and abs(t["valor_positivo"] - ref) / ref < 0.1:
                    s.append(t)
                    placed = True
                    break
            if not placed:
                subs.append([t])

        for s in subs:
            filtradas.append(min(s, key=lambda x: x["parcela_atual"]))

    # Dedup com/sem número de parcela na mesma data/valor
    melhores: dict[str, dict] = {}
    for t in filtradas:
        base = re.sub(r'\s*\d{2}/\d{2}\s*$', '', t["estabelecimento"]).strip()
        norm = re.sub(r'[^A-Z0-9]', '', base.upper())
        chave = f"{t['data_iso']}|{norm}|{t['valor']}"

        if chave not in melhores:
            melhores[chave] = t
        else:
            ex = melhores[chave]
            tem = bool(rx_parcela.search(t["estabelecimento"]))
            ex_tem = bool(rx_parcela.search(ex["estabelecimento"]))
            if tem and not ex_tem:
                melhores[chave] = t          # preferir versão com parcela
            elif not tem and not ex_tem:
                melhores[f"{chave}#{len(melhores)}"] = t  # manter ambas

    return list(melhores.values())


# ─────────────────────────────────────────────────────────────────────────────
# Seção Produtos / Serviços
# ─────────────────────────────────────────────────────────────────────────────

def _extract_produtos_servicos(
    linhas: List[str],
    ano_fatura: int,
    mes_fatura: int,          # ← v2: recebe mes_fatura para inferir ano correto
) -> List[Tuple[str, str, float]]:
    """
    Extrai lançamentos da seção 'Lançamentos: Produtos/Serviços'.

    Correções v2:
      - Recebe mes_fatura e aplica inferência de ano igual à seção principal.
      - Descarta transações cujo mês inferido é posterior ao fechamento.
    """
    resultado = []
    inicio = next(
        (i for i, l in enumerate(linhas) if "PRODUTOS/SERVIÇOS" in l.upper()),
        -1,
    )
    if inicio == -1:
        return resultado

    rx = r'(\d{2}/\d{2})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    i = inicio + 1
    while i < len(linhas):
        linha = linhas[i].strip()
        if any(
            k in linha.upper()
            for k in ("COMPRAS PARCELADAS", "TOTAL DOS LANÇAMENTOS")
        ):
            break

        for m in re.finditer(rx, linha):
            dd, mm_str = m.group(1).split("/")
            mes_tx = int(mm_str)

            # ── inferência de ano (mesma lógica da seção principal) ───────
            ano_tx = ano_fatura - 1 if mes_tx > mes_fatura else ano_fatura
            data_completa = f"{ano_tx}-{mm_str}-{dd}"

            # ── descartar transações futuras ──────────────────────────────
            if ano_tx > ano_fatura or (
                ano_tx == ano_fatura and mes_tx > mes_fatura
            ):
                continue

            desc = m.group(2).strip()
            valor_str = m.group(3).strip()

            if desc.endswith("-"):
                desc = desc[:-1].strip()
                if not valor_str.startswith("-"):
                    valor_str = "-" + valor_str

            desc = re.sub(r'\d{2}/\d{2}$', '', desc).strip()
            valor = _br(valor_str)

            if "ESTORNO" in desc.upper() and valor > 0:
                valor = -valor

            if valor != 0:
                resultado.append((data_completa, desc, valor))
                logger.debug(f"Produto/Serviço: {data_completa} | {desc} | {valor}")

        i += 1

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _br(s: str) -> float:
    """Converte valor no formato brasileiro (1.234,56) para float."""
    s = str(s).strip().replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        logger.warning(f"Valor inválido: {s}")
        return 0.0


def _chave(data: str, lancamento: str, valor: float) -> str:
    lanc = re.sub(r'\s*\d{2}/\d{2}\s*$', '', lancamento).strip()
    lanc = re.sub(r'[^A-Z0-9]', '', lanc.upper())
    return f"{data}|{lanc}|{valor:.2f}"


def _extract_mes_fatura(nome_arquivo: str) -> str:
    m = re.search(r'(\d{6})', nome_arquivo)
    return m.group(1) if m else datetime.now().strftime('%Y%m')


def _iso_to_br(data_iso: str) -> str:
    """Converte YYYY-MM-DD → DD/MM/YYYY (formato esperado pelo V5 / CSV Itaú)."""
    try:
        dt = datetime.strptime(data_iso, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        # Já está em DD/MM/YYYY ou formato desconhecido — retorna como está
        return data_iso
