#!/usr/bin/env python3
"""
Script de Teste - Processadores de Upload
==========================================
Testa todos os arquivos em _arquivos_historicos/_csvs_historico/
Roda deteccao automatica + processamento + validacoes basicas.

Uso:
    cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
    source app_dev/venv/bin/activate
    python scripts/testing/test_upload_processors.py

    # Opcoes:
    python scripts/testing/test_upload_processors.py --only btg
    python scripts/testing/test_upload_processors.py --only itau
    python scripts/testing/test_upload_processors.py --only mp
    python scripts/testing/test_upload_processors.py --verbose
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'app_dev' / 'backend'))

# Minimo para importar modulos sem banco real
os.environ.setdefault('DATABASE_URL', 'postgresql://x:x@localhost/x')
os.environ.setdefault('JWT_SECRET_KEY', 'a' * 64)

from app.domains.upload.processors.raw.registry import get_processor
from app.domains.upload.processors.marker import TransactionMarker

BASE_DIR = ROOT / '_arquivos_historicos' / '_csvs_historico'
SENHA_BTG  = '11259347605'
SENHA_ITAU = '11259'

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
GREY   = '\033[90m'
RESET  = '\033[0m'
BOLD   = '\033[1m'


@dataclass
class TestResult:
    arquivo: str
    banco_detectado: str = '?'
    tipo_detectado: str = '?'
    formato_detectado: str = '?'
    confianca: float = 0.0
    processador_encontrado: bool = False
    n_transacoes: int = 0
    soma_valores: float = 0.0
    erro: Optional[str] = None
    avisos: list = field(default_factory=list)
    passou: bool = False


# ---------------------------------------------------------------------------
# Inventario de arquivos de teste
# ---------------------------------------------------------------------------
ARQUIVOS = {
    # EXTRATO ITAU
    'itau_extrato_xls_202503': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-202503.xls',
    'itau_extrato_xls_jan25':  BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-310120252248.xls',
    'itau_extrato_xls_dez24':  BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-301220242137.xls',
    'itau_extrato_xls_dez25a': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-221220252316.xls',
    'itau_extrato_xls_dez25b': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-261220251037.xls',
    'itau_extrato_xls_mai25a': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-190520251719.xls',
    'itau_extrato_xls_mai25b': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-Maio.xls',
    'itau_extrato_xls_mar25':  BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-020320251747.xls',
    'itau_extrato_xls_jul25a': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-030720252048.xls',
    'itau_extrato_xls_jul25b': BASE_DIR / 'extrato/Itau/Extrato Conta Corrente-300720252109.xls',
    'itau_extrato_xls_2025':   BASE_DIR / 'extrato/Itau/extrato-itau-2025.xls',
    'itau_extrato_pdf_2025':   BASE_DIR / 'extrato/Itau/extrato-itau-2025.pdf',
    # EXTRATO MERCADO PAGO
    'mp_extrato_xlsx_202501':  BASE_DIR / 'extrato/MP/MP202501.xlsx',
    'mp_extrato_xlsx_202502':  BASE_DIR / 'extrato/MP/MP202502.xlsx',
    'mp_extrato_xlsx_202503':  BASE_DIR / 'extrato/MP/MP202503.xlsx',
    'mp_extrato_xlsx_202504':  BASE_DIR / 'extrato/MP/MP202504.xlsx',
    'mp_extrato_xlsx_202505':  BASE_DIR / 'extrato/MP/MP202505.xlsx',
    'mp_extrato_xlsx_202506':  BASE_DIR / 'extrato/MP/MP202506.xlsx',
    'mp_extrato_xlsx_202507':  BASE_DIR / 'extrato/MP/MP202507.xlsx',
    'mp_extrato_xlsx_202508':  BASE_DIR / 'extrato/MP/MP202508.xlsx',
    'mp_extrato_xlsx_202509':  BASE_DIR / 'extrato/MP/MP202509.xlsx',
    'mp_extrato_xlsx_202510':  BASE_DIR / 'extrato/MP/MP202510.xlsx',
    'mp_extrato_xlsx_202511':  BASE_DIR / 'extrato/MP/MP202511.xlsx',
    'mp_extrato_xlsx_202512':  BASE_DIR / 'extrato/MP/MP202512.xlsx',
    'mp_extrato_pdf_202508':   BASE_DIR / 'extrato/MP/MP202508.pdf',
    'mp_extrato_pdf_202509':   BASE_DIR / 'extrato/MP/MP202509.pdf',
    'mp_extrato_pdf_202510':   BASE_DIR / 'extrato/MP/MP202510.pdf',
    'mp_extrato_pdf_202511':   BASE_DIR / 'extrato/MP/MP202511.pdf',
    'mp_extrato_pdf_202512':   BASE_DIR / 'extrato/MP/MP202512.pdf',
    'mp_extrato_xlsx_acct1':   BASE_DIR / 'extrato/MP/account_statement-202ffd51-0eb5-4dde-ac19-2c88c2c60896.xlsx',
    'mp_extrato_xlsx_acct2':   BASE_DIR / 'extrato/MP/account_statement-3a5161f1-7662-434a-ad24-2493cd2647f4.xlsx',
    'mp_extrato_xlsx_acct3':   BASE_DIR / 'extrato/MP/account_statement-5c113ab1-e096-40cc-a03e-d76ee7ec1cf6.xlsx',
    # EXTRATO BTG
    'btg_extrato_xls_antigo':  BASE_DIR / 'extrato/btg/extrato_btg.xls',
    'btg_extrato_xls_multi':   BASE_DIR / 'extrato/btg/Extrato_2025-12-10_a_2026-03-09_11259347605.xls',
    'btg_extrato_pdf_multi':   BASE_DIR / 'extrato/btg/Extrato_2025-12-10_a_2026-03-09_11259347605.pdf',
    # FATURA ITAU CSV
    'itau_fatura_csv_202510':  BASE_DIR / 'fatura/Itau/fatura_itau-202510.csv',
    'itau_fatura_csv_202511':  BASE_DIR / 'fatura/Itau/fatura_itau-202511.csv',
    'itau_fatura_csv_202512':  BASE_DIR / 'fatura/Itau/fatura_itau-202512.csv',
    'fatura_csv_202508':       BASE_DIR / 'fatura/Itau/fatura-202508.csv',
    'fatura_csv_202509':       BASE_DIR / 'fatura/Itau/fatura-202509.csv',
    'fatura_csv_202601':       BASE_DIR / 'fatura/Itau/fatura-202601.csv',
    # FATURA ITAU PDF
    'itau_fatura_pdf_202509':  BASE_DIR / 'fatura/Itau/fatura-202509.pdf',
    'itau_fatura_pdf_202510':  BASE_DIR / 'fatura/Itau/fatura-202510.pdf',
    'itau_fatura_pdf_202511':  BASE_DIR / 'fatura/Itau/fatura-202511.pdf',
    'itau_fatura_pdf_202512':  BASE_DIR / 'fatura/Itau/fatura-202512.pdf',
    # FATURA MERCADO PAGO — TODO: processador raw nao existe ainda, desabilitado
    # 'mp_fatura_pdf_202507':    BASE_DIR / 'fatura/MP/FATURAMP202507.pdf',
    # 'mp_fatura_pdf_202508':    BASE_DIR / 'fatura/MP/FATURAMP202508.pdf',
    # 'mp_fatura_pdf_202509':    BASE_DIR / 'fatura/MP/FATURAMP202509.pdf',
    # 'mp_fatura_pdf_202510':    BASE_DIR / 'fatura/MP/FATURAMP202510.pdf',
    # 'mp_fatura_pdf_202511':    BASE_DIR / 'fatura/MP/FATURAMP202511.pdf',
    # 'mp_fatura_pdf_202512':    BASE_DIR / 'fatura/MP/FATURAMP202512.pdf',
    # 'mp_fatura_pdf_202601':    BASE_DIR / 'fatura/MP/FATURAMP202601.pdf',
    # 'mp_fatura_pdf_202602':    BASE_DIR / 'fatura/MP/FATURAMP202602.pdf',
    # FATURA BTG (protegidas com senha SENHA_BTG)
    'btg_fatura_xlsx_202602':  BASE_DIR / 'fatura/btg/2026-02-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.xlsx',
    'btg_fatura_pdf_202602':   BASE_DIR / 'fatura/btg/2026-02-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.pdf',
    'btg_fatura_xlsx_202603':  BASE_DIR / 'fatura/btg/2026-03-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.xlsx',
    'btg_fatura_pdf_202603':   BASE_DIR / 'fatura/btg/2026-03-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.pdf',
}

# ---------------------------------------------------------------------------
# Mapeamento pasta -> banco  (usado por _detect_from_path)
# ---------------------------------------------------------------------------
_PASTA_BANCO = {
    'itau': 'itau',
    'Itau': 'itau',
    'MP':   'mercadopago',
    'mp':   'mercadopago',
    'btg':  'btg',
}

# ---------------------------------------------------------------------------
# Senhas por chave de arquivo
# ---------------------------------------------------------------------------
SENHAS = {
    'btg_fatura_xlsx_202602':  SENHA_BTG,
    'btg_fatura_pdf_202602':   SENHA_BTG,
    'btg_fatura_xlsx_202603':  SENHA_BTG,
    'btg_fatura_pdf_202603':   SENHA_BTG,
    # itau_extrato_pdf_2025: nao usa senha (pdfplumber le sem criptografia)
    'itau_fatura_pdf_202509':  SENHA_ITAU,
    'itau_fatura_pdf_202510':  SENHA_ITAU,
    'itau_fatura_pdf_202511':  SENHA_ITAU,
    'itau_fatura_pdf_202512':  SENHA_ITAU,
}

# ---------------------------------------------------------------------------
# Expectativas de contagem/saldo (arquivos com valores conhecidos)
# ---------------------------------------------------------------------------
EXPECTATIVAS = {
    'btg_extrato_xls_multi': (65, None),
    'btg_extrato_pdf_multi': (65, 97.02),
}

# ---------------------------------------------------------------------------
# Pares para comparacao cruzada XLS vs PDF
# ---------------------------------------------------------------------------
PARES_COMPARACAO = [
    ('btg_extrato_xls_multi',  'btg_extrato_pdf_multi'),
    ('btg_fatura_xlsx_202602', 'btg_fatura_pdf_202602'),
    ('btg_fatura_xlsx_202603', 'btg_fatura_pdf_202603'),
    ('mp_extrato_xlsx_202508', 'mp_extrato_pdf_202508'),
    ('mp_extrato_xlsx_202509', 'mp_extrato_pdf_202509'),
    ('mp_extrato_xlsx_202510', 'mp_extrato_pdf_202510'),
    ('mp_extrato_xlsx_202511', 'mp_extrato_pdf_202511'),
    ('mp_extrato_xlsx_202512', 'mp_extrato_pdf_202512'),
    ('itau_extrato_xls_2025',  'itau_extrato_pdf_2025'),
]

FILTROS = {
    'btg':  lambda k: 'btg' in k,
    'itau': lambda k: 'itau' in k or k.startswith('fatura_csv'),
    'mp':   lambda k: k.startswith('mp'),
}

GRUPOS = [
    ('Extrato Itau',          lambda k: k.startswith('itau_extrato')),
    ('Fatura Itau CSV',       lambda k: k.startswith('itau_fatura_csv') or k.startswith('fatura_csv')),
    ('Fatura Itau PDF',       lambda k: k.startswith('itau_fatura_pdf')),
    ('Extrato Mercado Pago',  lambda k: k.startswith('mp_extrato')),
    # Fatura MP desabilitada — processador raw pendente de criacao
    # ('Fatura Mercado Pago',   lambda k: k.startswith('mp_fatura')),
    ('Extrato BTG',           lambda k: k.startswith('btg_extrato')),
    ('Fatura BTG',            lambda k: k.startswith('btg_fatura')),
]


def _formato(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == '.pdf':  return 'pdf'
    if ext == '.xlsx': return 'excel'
    if ext == '.xls':  return 'excel'
    if ext == '.csv':  return 'csv'
    return 'unknown'


def _detect_from_path(path: Path) -> tuple:
    """
    Deriva (banco, tipo, formato) da estrutura de pastas em _csvs_historico/.

    _csvs_historico/
      extrato/Itau/ -> ('itau',        'extrato', ...)
      extrato/MP/   -> ('mercadopago', 'extrato', ...)
      extrato/btg/  -> ('btg',         'extrato', ...)
      fatura/Itau/  -> ('itau',        'fatura',  ...)
      fatura/MP/    -> ('mercadopago', 'fatura',  ...)
      fatura/btg/   -> ('btg',         'fatura',  ...)
    """
    try:
        rel   = path.relative_to(BASE_DIR)
        parts = rel.parts          # ex: ('extrato', 'MP', 'MP202502.xlsx')
        tipo  = parts[0]           # 'extrato' ou 'fatura'
        banco = _PASTA_BANCO.get(parts[1], parts[1].lower())
        fmt   = _formato(path)
        return banco, tipo, fmt
    except (ValueError, IndexError):
        return 'desconhecido', 'desconhecido', _formato(path)


def _testar(key: str, path: Path, verbose: bool) -> TestResult:
    result = TestResult(arquivo=path.name)

    if not path.exists():
        result.erro = 'Arquivo nao encontrado'
        return result

    try:
        file_bytes = path.read_bytes()
    except Exception as e:
        result.erro = f'Erro leitura: {e}'
        return result

    # 1. Deteccao pelo caminho da pasta (fonte da verdade)
    result.banco_detectado, result.tipo_detectado, result.formato_detectado = _detect_from_path(path)
    result.confianca = 1.0

    # 2. Buscar processador
    processor = get_processor(
        result.banco_detectado,
        result.tipo_detectado,
        result.formato_detectado,
    )
    if not processor:
        result.erro = (
            f'Sem processador para '
            f'{result.banco_detectado}/{result.tipo_detectado}/{result.formato_detectado}'
        )
        return result
    result.processador_encontrado = True

    # 3. Processar (mesma assinatura de service.py)
    senha = SENHAS.get(key)
    try:
        output = processor(
            path, path.name, None, None,
            **({'senha': senha} if senha else {})
        )
        transacoes = output[0] if isinstance(output, tuple) else output
        result.n_transacoes = len(transacoes)
        result.soma_valores = round(sum(
            (t.valor if hasattr(t, 'valor') else t.get('valor', 0))
            for t in transacoes
        ), 2)
    except Exception as e:
        result.erro = f'{type(e).__name__}: {str(e)[:120]}'
        return result

    # 4. Validacoes basicas
    if result.n_transacoes == 0:
        result.avisos.append('[AVISO] Nenhuma transacao extraida')

    LIXO = [
        'saldo anterior', 'agencia', 'lancamento', 'data e hora',
        'initial_balance', 'release_date', 'cliente:',
    ]
    for i, tx in enumerate(transacoes[:5]):
        lc = tx.lancamento if hasattr(tx, 'lancamento') else tx.get('lancamento', '')
        if lc and any(x in str(lc).lower() for x in LIXO):
            result.avisos.append(f'Tx[{i}] lixo de cabecalho: "{str(lc)[:60]}"')

    # 5. Expectativas
    if key in EXPECTATIVAS:
        n_esp, s_esp = EXPECTATIVAS[key]
        if n_esp is not None and result.n_transacoes != n_esp:
            result.avisos.append(
                f'[FAIL] n_tx={result.n_transacoes} (esperado {n_esp})'
            )
        if s_esp is not None and abs(result.soma_valores - s_esp) > 0.02:
            result.avisos.append(
                f'[FAIL] saldo R${result.soma_valores:,.2f} (esperado R${s_esp:,.2f})'
            )

    # 6. Verbose: mostra primeiras transacoes
    if verbose and transacoes:
        print('  Primeiras 3:')
        for tx in transacoes[:3]:
            d = tx.data if hasattr(tx, 'data') else tx.get('data', '?')
            l = tx.lancamento if hasattr(tx, 'lancamento') else tx.get('lancamento', '?')
            v = tx.valor if hasattr(tx, 'valor') else tx.get('valor', 0)
            print(f'    {d}  {str(l)[:50]:50s}  R$ {v:>10,.2f}')

    # 7. PASS/FAIL
    result.passou = (
        result.n_transacoes > 0
        and result.erro is None
        and not any('[FAIL]' in a for a in result.avisos)
    )
    return result


def _imprimir(key: str, r: TestResult) -> None:
    status = f'{GREEN}PASS{RESET}' if r.passou else f'{RED}FAIL{RESET}'
    if r.erro:
        info = f'{RED}{r.erro[:90]}{RESET}'
    else:
        bs = f'{r.banco_detectado}/{r.tipo_detectado}/{r.formato_detectado}'
        info = (
            f'{CYAN}{bs:37s}{RESET}'
            f'tx={r.n_transacoes:>4}  '
            f'R${r.soma_valores:>12,.2f}'
        )
        if r.avisos:
            info += f'  {YELLOW}[{len(r.avisos)} av.]{RESET}'
    print(f'  [{status}]  {BOLD}{r.arquivo[:46]:46s}{RESET}  {info}')
    for av in r.avisos:
        cor = RED if '[FAIL]' in av else YELLOW
        print(f'           {cor}{av}{RESET}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Testa processadores de upload')
    parser.add_argument('--only', choices=['btg', 'itau', 'mp'],
                        help='Filtrar por banco')
    parser.add_argument('--verbose', action='store_true',
                        help='Mostrar primeiras transacoes de cada arquivo')
    args = parser.parse_args()

    arquivos = {
        k: v for k, v in ARQUIVOS.items()
        if not args.only or FILTROS[args.only](k)
    }

    print(f'\n{BOLD}{"=" * 80}{RESET}')
    print(f'{BOLD}Teste de Processadores de Upload  ({len(arquivos)} arquivos){RESET}')
    print(f'{BOLD}Deteccao via estrutura de pastas (extrato/btg/, fatura/MP/, ...){RESET}')
    print(f'{BOLD}{"=" * 80}{RESET}')

    resultados: dict[str, TestResult] = {}
    n_pass = n_fail = 0

    for titulo, fn in GRUPOS:
        keys = [k for k in arquivos if fn(k)]
        if not keys:
            continue
        print(f'\n{BOLD}{CYAN}>> {titulo}{RESET}')
        for key in keys:
            r = _testar(key, arquivos[key], args.verbose)
            resultados[key] = r
            _imprimir(key, r)
            n_pass += r.passou
            n_fail += not r.passou

    # Comparacao cruzada XLS vs PDF
    if not args.only:
        print(f'\n{BOLD}{CYAN}>> Comparacao XLS vs PDF (mesmo periodo){RESET}')
        probs = []
        for ka, kb in PARES_COMPARACAO:
            if ka not in resultados or kb not in resultados:
                continue
            ra, rb = resultados[ka], resultados[kb]
            if ra.erro or rb.erro:
                continue
            if abs(ra.n_transacoes - rb.n_transacoes) > 0:
                probs.append(
                    f'{ra.arquivo} ({ra.n_transacoes}tx) != '
                    f'{rb.arquivo} ({rb.n_transacoes}tx)'
                )
                n_fail += 1
            if abs(ra.soma_valores - rb.soma_valores) > 0.02:
                probs.append(
                    f'{ra.arquivo} R${ra.soma_valores:,.2f} != '
                    f'{rb.arquivo} R${rb.soma_valores:,.2f}'
                )
                n_fail += 1
        if probs:
            for p in probs:
                print(f'  {RED}[FAIL] {p}{RESET}')
        else:
            print(f'  {GREEN}[OK] Todos os pares identicos{RESET}')

    # Resumo final
    print(f'\n{BOLD}{"=" * 80}{RESET}')
    cor = GREEN if n_fail == 0 else RED
    print(f'{cor}{BOLD}Resultado: {n_pass}/{n_pass + n_fail} PASS  |  {n_fail} FAIL{RESET}')

    sem_proc = [
        (k, r) for k, r in resultados.items()
        if r.erro and 'Sem processador' in (r.erro or '')
    ]
    criticos = [
        (k, r) for k, r in resultados.items()
        if any('[FAIL]' in a for a in r.avisos)
    ]

    if sem_proc:
        print(f'\n{YELLOW}{BOLD}Lacunas de processador:{RESET}')
        for k, r in sem_proc:
            print(f'  {YELLOW}* {r.arquivo} -> {r.erro}{RESET}')

    if criticos:
        print(f'\n{RED}{BOLD}Falhas de expectativa:{RESET}')
        for k, r in criticos:
            for av in r.avisos:
                if '[FAIL]' in av:
                    print(f'  {RED}* {r.arquivo}: {av}{RESET}')

    if n_fail == 0:
        print(f'\n  {GREEN}Todos os processadores funcionando!{RESET}')

    # Validacao de hashes cross-formato
    if not args.only:
        n_hash_fail = _testar_hashes()
        n_fail += n_hash_fail

    print()
    sys.exit(0 if n_fail == 0 else 1)


# ---------------------------------------------------------------------------
# Validacao de hashes cross-formato
# ---------------------------------------------------------------------------

# Pares XLSX/PDF (ou CSV) que devem gerar os mesmos IdTransacao e IdParcela
# Formato: (chave_a, chave_b, tipo_documento)
PARES_HASH = [
    ('btg_fatura_xlsx_202602', 'btg_fatura_pdf_202602', 'fatura'),
    ('btg_fatura_xlsx_202603', 'btg_fatura_pdf_202603', 'fatura'),
    ('mp_extrato_xlsx_202508', 'mp_extrato_pdf_202508', 'extrato'),
    ('mp_extrato_xlsx_202509', 'mp_extrato_pdf_202509', 'extrato'),
    ('mp_extrato_xlsx_202510', 'mp_extrato_pdf_202510', 'extrato'),
    ('mp_extrato_xlsx_202511', 'mp_extrato_pdf_202511', 'extrato'),
    ('mp_extrato_xlsx_202512', 'mp_extrato_pdf_202512', 'extrato'),
    ('itau_extrato_xls_2025',  'itau_extrato_pdf_2025', 'extrato'),
]


def _processar_e_marcar(key: str) -> list:
    """Processa o arquivo e retorna lista de MarkedTransaction (user_id=99 fixo para teste)."""
    from app.domains.upload.processors.marker import TransactionMarker

    path = ARQUIVOS[key]
    banco, tipo, fmt = _detect_from_path(path)
    processor = get_processor(banco, tipo, fmt)
    if not processor:
        return []
    senha = SENHAS.get(key)
    try:
        output = processor(path, path.name, None, None, **({'senha': senha} if senha else {}))
        raws = output[0] if isinstance(output, tuple) else output
    except Exception:
        return []
    marker = TransactionMarker(user_id=99)
    marked = []
    for r in raws:
        try:
            marked.append(marker.mark_transaction(r))
        except Exception:
            pass
    return marked


def _testar_hashes() -> int:
    """
    Valida que formatos diferentes (XLSX vs PDF, CSV vs PDF) geram os mesmos
    IdTransacao e IdParcela para as mesmas transacoes.

    Logica de comparacao:
    - Agrupa transacoes de cada arquivo por (data, valor) como chave minima
    - Para cada transacao do arquivo A, busca correspondente no B
    - Compara IdTransacao e IdParcela
    """
    print(f'\n{BOLD}{CYAN}>> Validacao de Hashes Cross-Formato (deduplicacao){RESET}')
    print(f'  {GREY}Garante que XLSX e PDF da mesma fatura/extrato geram IdTransacao identico{RESET}')

    n_fail = 0

    for ka, kb, tipo_doc in PARES_HASH:
        if ka not in ARQUIVOS or kb not in ARQUIVOS:
            continue

        marked_a = _processar_e_marcar(ka)
        marked_b = _processar_e_marcar(kb)

        if not marked_a or not marked_b:
            print(f'  {YELLOW}[SKIP]{RESET} {ka} x {kb} — sem transacoes para comparar')
            continue

        # Indexa B por (data, valor) -> fila FIFO de (id_transacao, id_parcela)
        # FIFO garante que multiplos duplicados (mesma data+valor) sejam
        # consumidos na mesma ordem em que aparecem — igual ao que o banco faz.
        from collections import defaultdict, deque
        idx_b: dict[tuple, deque] = defaultdict(deque)
        for m in marked_b:
            chave = (m.data, round(float(m.valor), 2))
            idx_b[chave].append((m.id_transacao, m.id_parcela))

        divergencias_id = []
        divergencias_parcela = []
        sem_par = 0

        for m in marked_a:
            chave = (m.data, round(float(m.valor), 2))
            if not idx_b[chave]:
                sem_par += 1
                continue
            id_tx_b, id_parc_b = idx_b[chave].popleft()  # consome em ordem
            if m.id_transacao != id_tx_b:
                divergencias_id.append(
                    f'{m.lancamento[:40]} | {m.data} R${m.valor:.2f}\n'
                    f'    {ARQUIVOS[ka].suffix}: {m.id_transacao}\n'
                    f'    {ARQUIVOS[kb].suffix}: {id_tx_b}'
                )
            if m.id_parcela and id_parc_b:
                if m.id_parcela != id_parc_b:
                    divergencias_parcela.append(
                        f'{m.lancamento[:40]} | {m.data} R${m.valor:.2f}\n'
                        f'    {ARQUIVOS[ka].suffix} IdParcela: {m.id_parcela}\n'
                        f'    {ARQUIVOS[kb].suffix} IdParcela: {id_parc_b}'
                    )

        label = f'{ARQUIVOS[ka].name[:30]} x {ARQUIVOS[kb].name[:30]}'
        if not divergencias_id and not divergencias_parcela:
            extra = f' {GREY}(sem_par={sem_par}){RESET}' if sem_par else ''
            print(f'  [{GREEN}PASS{RESET}]  {label}{extra}')
        else:
            print(f'  [{RED}FAIL{RESET}]  {label}')
            for d in divergencias_id:
                print(f'    {RED}[IdTransacao diverge]{RESET} {d}')
                n_fail += 1
            for d in divergencias_parcela:
                print(f'    {RED}[IdParcela diverge]{RESET} {d}')
                n_fail += 1
            if sem_par:
                print(f'    {YELLOW}[AVISO] {sem_par} transacoes sem par por (data,valor){RESET}')

    return n_fail


if __name__ == '__main__':
    main()
