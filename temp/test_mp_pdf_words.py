"""
Script de teste: extração de transações do extrato MP PDF.

Algoritmo ID-as-anchor (regra inline):
  1. Parsear texto via extract_text() linha a linha:
     - Linha com ID de operação (10+ dígitos) + data + valor  → "tx"
     - Demais linhas relevantes                                → "frag"
  2. Atribuir frags entre tx consecutivos:
     - 0 frags → nada
     - 1 frag + inline_atual VAZIO  → desc_before do tx atual
     - 1 frag + inline_atual CHEIO  → desc_after do tx anterior
     - 2+ frags → primeiro = desc_after do anterior; resto = desc_before do atual
  3. Montar descrição: desc_before + inline + desc_after
"""
import pdfplumber
import re
import pandas as pd
from pathlib import Path
from datetime import datetime


# ── Constantes ────────────────────────────────────────────────────────────────

_TX_RE = re.compile(
    r'(\d{2}-\d{2}-\d{4})'            # grupo 1: data DD-MM-YYYY
    r'\s*(.*?)\s*'                     # grupo 2: desc inline (non-greedy)
    r'(\d{10,})'                       # grupo 3: ID da operação (descartado)
    r'\s+R\$\s*(-?[\d.]+,\d{2})'      # grupo 4: valor
)

_IGNORE_EXACT = {
    'EXTRATO DE CONTA',
    'DETALHE DOS MOVIMENTOS',
    'Data Descrição ID da operação Valor Saldo',
}

_IGNORE_CONTAINS = [
    'CPF/CNPJ', 'Periodo:', 'Saldo inicial', 'Saldo final',
    'Entradas:', 'Saidas:', 'Você tem alguma', 'Você tem dúvida',
    'Mercado Pago Institui', 'www.mercadopago', 'Data de geração',
    'nosso SAC', 'ligue para 0800', 'protocolo do primeiro',
    'Av. das Nações', 'canais de consulta', 'CEP 06233',
    # artefatos de cabeçalho com fonte duplicada em algumas páginas
    'DDaattaa', 'IIdd ddaa',
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _convert_valor_br(valor_str: str) -> float:
    s = valor_str.strip()
    neg = s.startswith('-')
    if neg:
        s = s[1:]
    s = s.replace('.', '').replace(',', '.')
    try:
        return -float(s) if neg else float(s)
    except ValueError:
        return 0.0


def _is_ignorable(line: str) -> bool:
    if line in _IGNORE_EXACT:
        return True
    if re.match(r'^\d+/\d+$', line):   # paginação "1/9", "9/9" etc.
        return True
    return any(p in line for p in _IGNORE_CONTAINS)


# ── Extração principal ────────────────────────────────────────────────────────

def extract_transactions_text(texto: str):
    """
    Extrai lista de (data_iso, descricao, valor) do texto completo do PDF.

    Regra de atribuição de fragmentos (inline rule):
      - 1 frag, tx_atual sem inline  → desc_before do tx_atual
      - 1 frag, tx_atual com inline  → desc_after do tx_anterior
      - 2+ frags                     → primeiro=desc_after anterior; resto=desc_before atual
    """
    # 1. Classificar linhas
    entries = []   # ('tx', date, inline, id, valor) | ('frag', text)
    for raw_line in texto.split('\n'):
        line = raw_line.strip()
        if not line or _is_ignorable(line):
            continue
        m = _TX_RE.search(line)
        if m:
            entries.append(('tx', m.group(1), m.group(2).strip(), m.group(3), m.group(4)))
        else:
            entries.append(('frag', line))

    # 2. Atribuir fragmentos
    tx_indices = [i for i, e in enumerate(entries) if e[0] == 'tx']
    desc_before = {}
    desc_after  = {}

    for k, ti in enumerate(tx_indices):
        ti_prev      = tx_indices[k - 1] if k > 0 else -1
        frags        = [entries[j][1] for j in range(ti_prev + 1, ti)
                        if entries[j][0] == 'frag']
        inline_atual = entries[ti][2]

        if len(frags) == 0:
            pass
        elif len(frags) == 1:
            if not inline_atual:
                desc_before[ti] = frags[0]
            elif ti_prev >= 0:
                desc_after[ti_prev] = frags[0]
        else:  # 2+ frags
            if ti_prev >= 0:
                desc_after[ti_prev] = frags[0]
            desc_before[ti] = ' '.join(frags[1:])

    # Frags após o último tx → desc_after dele
    if tx_indices:
        last_ti    = tx_indices[-1]
        frags_tail = [entries[j][1] for j in range(last_ti + 1, len(entries))
                      if entries[j][0] == 'frag']
        if frags_tail:
            desc_after[last_ti] = frags_tail[0]

    # 3. Montar transações
    transacoes = []
    for ti in tx_indices:
        _, date_str, inline, _id, valor_str = entries[ti]
        parts     = [p for p in [desc_before.get(ti, ''), inline, desc_after.get(ti, '')] if p]
        full_desc = ' '.join(parts).strip()
        try:
            data_iso = datetime.strptime(date_str, '%d-%m-%Y').strftime('%d/%m/%Y')
        except ValueError:
            continue
        valor = _convert_valor_br(valor_str)
        if abs(valor) < 0.01:
            continue
        transacoes.append((data_iso, full_desc, valor))

    return transacoes


# ── Teste principal ──────────────────────────────────────────────────────────

def _load_xlsx(xlsx_path: Path):
    df = pd.read_excel(xlsx_path, header=None)
    txs = []
    for _, row in df.iloc[4:].iterrows():
        if pd.isna(row[0]) or pd.isna(row[1]) or pd.isna(row[3]):
            continue
        data_str  = str(row[0]).strip()
        desc_str  = str(row[1]).strip()
        valor_str = str(row[3]).strip().replace('.', '').replace(',', '.')
        try:
            data_iso = datetime.strptime(data_str, '%d-%m-%Y').strftime('%d/%m/%Y')
            valor    = float(valor_str)
        except Exception:
            continue
        if abs(valor) < 0.01:
            continue
        txs.append((data_iso, desc_str, valor))
    return txs


BASE  = Path("_arquivos_historicos/_csvs_historico/extrato/MP")
MESES = ['MP202508', 'MP202509', 'MP202510', 'MP202511', 'MP202512']

total_match    = 0
total_mismatch = 0

for mes in MESES:
    pdf_path  = BASE / f"{mes}.pdf"
    xlsx_path = BASE / f"{mes}.xlsx"

    with pdfplumber.open(pdf_path) as pdf:
        texto = '\n'.join(page.extract_text() or '' for page in pdf.pages)

    pdf_txs  = extract_transactions_text(texto)
    xlsx_txs = _load_xlsx(xlsx_path)

    print(f"\n{'='*72}")
    print(f"  {mes}  |  PDF={len(pdf_txs)}  XLSX={len(xlsx_txs)}")
    print(f"{'='*72}")

    match_count    = 0
    mismatch_count = 0

    for (dp, descp, vp), (dx, descx, vx) in zip(pdf_txs, xlsx_txs):
        ok = descp == descx and round(vp, 2) == round(vx, 2)
        if ok:
            match_count += 1
        else:
            mismatch_count += 1
            print(f"  {dp}  PDF: {descp!r:<55}  XLSX: {descx!r}  ❌")

    total_match    += match_count
    total_mismatch += mismatch_count
    print(f"\n  ✅ {match_count} match  ❌ {mismatch_count} mismatch")

print(f"\n{'#'*72}")
print(f"  TOTAL: ✅ {total_match} match  ❌ {total_mismatch} mismatch  "
      f"({total_match}/{total_match + total_mismatch})")
print(f"{'#'*72}")
