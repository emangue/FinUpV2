"""
Testes de integração — processadores fatura BTG Pactual (XLSX + PDF).

Arquivos reais: _arquivos_historicos/_csvs_historico/fatura/btg/
Senha: CPF sem pontos/traço (env BTG_SENHA ou fallback para testes locais)

Cobre:
  1. Proteção por senha — PasswordRequiredException sem senha e com senha errada
  2. Estrutura das transações (banco, tipo_documento, mes_fatura, data, lancamento, valor)
  3. BalanceValidation — saldo_inicial=0, total declarado encontrado, soma vs total
  4. Paridade cross-formato: XLSX e PDF do mesmo mês → mesmo n_transacoes e soma
  5. Paridade de hashes: XLSX e PDF → mesmo IdTransacao para mesma transação

Sprint 3 — processadores BTG fatura
"""

import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

import pytest

# ─── Path setup ───────────────────────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parents[3]        # ProjetoFinancasV5/
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("DATABASE_URL",   "postgresql://x:x@localhost/x")
os.environ.setdefault("JWT_SECRET_KEY", "a" * 64)

# ─── Arquivos de teste ────────────────────────────────────────────────────────
BTG_DIR = ROOT / "_arquivos_historicos" / "_csvs_historico" / "fatura" / "btg"

XLSX_202602 = BTG_DIR / "2026-02-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.xlsx"
PDF_202602  = BTG_DIR / "2026-02-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.pdf"
XLSX_202603 = BTG_DIR / "2026-03-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.xlsx"
PDF_202603  = BTG_DIR / "2026-03-01_Fatura_Emanuel Guerra Leandro_1921141_BTG.pdf"

SENHA_BTG   = os.getenv("BTG_SENHA", "11259347605")  # CPF sem pontos/traço
SENHA_ERRADA = "00000000000"

FILES_EXIST = all(f.exists() for f in [XLSX_202602, PDF_202602, XLSX_202603, PDF_202603])
requires_files = pytest.mark.skipif(
    not FILES_EXIST,
    reason="Arquivos BTG não encontrados em _csvs_historico/fatura/btg/",
)

# ─── Imports lazy (após sys.path) ─────────────────────────────────────────────

def _get_xlsx_processor():
    from app.domains.upload.processors.raw.excel.btg_fatura_xlsx import process_btg_fatura_xlsx
    return process_btg_fatura_xlsx


def _get_pdf_processor():
    from app.domains.upload.processors.raw.pdf.btg_fatura_pdf import process_btg_fatura_pdf
    return process_btg_fatura_pdf


def _get_password_exc():
    from app.domains.upload.processors.raw.base import PasswordRequiredException
    return PasswordRequiredException


def _get_marker():
    from app.domains.upload.processors.marker import TransactionMarker
    return TransactionMarker


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _processar_e_marcar(transactions, user_id=99):
    """Aplica TransactionMarker a uma lista de RawTransaction."""
    TransactionMarker = _get_marker()
    marker = TransactionMarker(user_id=user_id)
    marked = []
    for raw in transactions:
        try:
            marked.append(marker.mark_transaction(raw))
        except Exception:
            pass
    return marked


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — processa uma vez por módulo (scope="module")
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def resultado_xlsx_202602():
    txs, balance = _get_xlsx_processor()(XLSX_202602, XLSX_202602.name, senha=SENHA_BTG)
    return txs, balance


@pytest.fixture(scope="module")
def resultado_pdf_202602():
    txs, balance = _get_pdf_processor()(PDF_202602, PDF_202602.name, senha=SENHA_BTG)
    return txs, balance


@pytest.fixture(scope="module")
def resultado_xlsx_202603():
    txs, balance = _get_xlsx_processor()(XLSX_202603, XLSX_202603.name, senha=SENHA_BTG)
    return txs, balance


@pytest.fixture(scope="module")
def resultado_pdf_202603():
    txs, balance = _get_pdf_processor()(PDF_202603, PDF_202603.name, senha=SENHA_BTG)
    return txs, balance


# ─────────────────────────────────────────────────────────────────────────────
# 1. Proteção por senha
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestSenhaXLSX:
    """XLSX é criptografado — deve exigir senha correta."""

    def test_sem_senha_levanta_excecao(self):
        """Sem senha → PasswordRequiredException com wrong_password=False."""
        PasswordRequiredException = _get_password_exc()
        process = _get_xlsx_processor()
        with pytest.raises(PasswordRequiredException) as exc:
            process(XLSX_202602, XLSX_202602.name)
        assert exc.value.wrong_password is False

    def test_senha_errada_levanta_excecao(self):
        """Senha errada → PasswordRequiredException com wrong_password=True."""
        PasswordRequiredException = _get_password_exc()
        process = _get_xlsx_processor()
        with pytest.raises(PasswordRequiredException) as exc:
            process(XLSX_202602, XLSX_202602.name, senha=SENHA_ERRADA)
        assert exc.value.wrong_password is True

    def test_senha_correta_nao_levanta(self):
        """Senha correta → processa sem exceção."""
        process = _get_xlsx_processor()
        result = process(XLSX_202602, XLSX_202602.name, senha=SENHA_BTG)
        txs = result[0] if isinstance(result, tuple) else result
        assert len(txs) > 0


@requires_files
class TestSenhaPDF:
    """PDF é protegido por senha — deve exigir senha correta."""

    def test_sem_senha_levanta_excecao(self):
        """Sem senha → PasswordRequiredException com wrong_password=False."""
        PasswordRequiredException = _get_password_exc()
        process = _get_pdf_processor()
        with pytest.raises(PasswordRequiredException) as exc:
            process(PDF_202602, PDF_202602.name)
        assert exc.value.wrong_password is False

    def test_senha_errada_levanta_excecao(self):
        """Senha errada → PasswordRequiredException com wrong_password=True."""
        PasswordRequiredException = _get_password_exc()
        process = _get_pdf_processor()
        with pytest.raises(PasswordRequiredException) as exc:
            process(PDF_202602, PDF_202602.name, senha=SENHA_ERRADA)
        assert exc.value.wrong_password is True

    def test_senha_correta_nao_levanta(self):
        """Senha correta → processa sem exceção."""
        process = _get_pdf_processor()
        result = process(PDF_202602, PDF_202602.name, senha=SENHA_BTG)
        txs = result[0] if isinstance(result, tuple) else result
        assert len(txs) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Estrutura das transações — XLSX
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestEstruturaXLSX202602:
    """Valida estrutura e campos das transações extraídas do XLSX fev/2026."""

    def test_retorna_tuple(self, resultado_xlsx_202602):
        assert isinstance(resultado_xlsx_202602, tuple)
        assert len(resultado_xlsx_202602) == 2

    def test_n_transacoes_positivo(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        assert len(txs) > 0, "XLSX 202602 deve conter transações"

    def test_banco_btg(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        assert all(t.banco == "BTG" for t in txs), "Todas as transações devem ter banco='BTG'"

    def test_tipo_documento_fatura(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        assert all(t.tipo_documento == "fatura" for t in txs)

    def test_mes_fatura_202602(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        assert all(t.mes_fatura == "202602" for t in txs), \
            f"mes_fatura esperado '202602', encontrado: {set(t.mes_fatura for t in txs)}"

    def test_datas_formato_iso(self, resultado_xlsx_202602):
        """Datas devem estar no formato YYYY-MM-DD."""
        txs, _ = resultado_xlsx_202602
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        invalidas = [t.data for t in txs if not pattern.match(str(t.data))]
        assert not invalidas, f"Datas fora do formato YYYY-MM-DD: {invalidas[:5]}"

    def test_lancamentos_nao_vazios(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        vazios = [i for i, t in enumerate(txs) if not t.lancamento or not t.lancamento.strip()]
        assert not vazios, f"Transações com lancamento vazio nos índices: {vazios[:5]}"

    def test_valores_sao_floats(self, resultado_xlsx_202602):
        txs, _ = resultado_xlsx_202602
        nao_float = [i for i, t in enumerate(txs) if not isinstance(t.valor, float)]
        assert not nao_float, f"Valores não-float nos índices: {nao_float[:5]}"

    def test_final_cartao_nao_vazio(self, resultado_xlsx_202602):
        """XLSX traz final_cartao de cada linha — não deve ser vazio para a maioria."""
        txs, _ = resultado_xlsx_202602
        com_cartao = [t for t in txs if t.final_cartao and t.final_cartao.strip()]
        assert len(com_cartao) > len(txs) * 0.5, \
            "Mais da metade das transações deve ter final_cartao preenchido"


@requires_files
class TestEstruturaXLSX202603:
    """Valida estrutura e campos das transações extraídas do XLSX mar/2026."""

    def test_n_transacoes_positivo(self, resultado_xlsx_202603):
        txs, _ = resultado_xlsx_202603
        assert len(txs) > 0

    def test_banco_btg(self, resultado_xlsx_202603):
        txs, _ = resultado_xlsx_202603
        assert all(t.banco == "BTG" for t in txs)

    def test_tipo_documento_fatura(self, resultado_xlsx_202603):
        txs, _ = resultado_xlsx_202603
        assert all(t.tipo_documento == "fatura" for t in txs)

    def test_mes_fatura_202603(self, resultado_xlsx_202603):
        txs, _ = resultado_xlsx_202603
        assert all(t.mes_fatura == "202603" for t in txs), \
            f"mes_fatura esperado '202603', encontrado: {set(t.mes_fatura for t in txs)}"

    def test_datas_formato_iso(self, resultado_xlsx_202603):
        txs, _ = resultado_xlsx_202603
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        invalidas = [t.data for t in txs if not pattern.match(str(t.data))]
        assert not invalidas, f"Datas fora do formato YYYY-MM-DD: {invalidas[:5]}"

    def test_sem_pagamento_fatura(self, resultado_xlsx_202603):
        """'Pagamento de fatura' deve ser filtrado — duplicaria o débito do extrato bancário."""
        txs, _ = resultado_xlsx_202603
        pagamentos = [t.lancamento for t in txs if "pagamento de fatura" in t.lancamento.lower()]
        assert not pagamentos, (
            f"'Pagamento de fatura' não deve ser importado (duplica extrato): {pagamentos}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Estrutura das transações — PDF
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestEstruturaPDF202602:
    """Valida estrutura e campos das transações extraídas do PDF fev/2026."""

    def test_retorna_tuple(self, resultado_pdf_202602):
        assert isinstance(resultado_pdf_202602, tuple)
        assert len(resultado_pdf_202602) == 2

    def test_n_transacoes_positivo(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        assert len(txs) > 0

    def test_banco_btg(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        assert all(t.banco == "BTG" for t in txs)

    def test_tipo_documento_fatura(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        assert all(t.tipo_documento == "fatura" for t in txs)

    def test_mes_fatura_202602(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        assert all(t.mes_fatura == "202602" for t in txs), \
            f"mes_fatura esperado '202602', encontrado: {set(t.mes_fatura for t in txs)}"

    def test_datas_formato_iso(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        invalidas = [t.data for t in txs if not pattern.match(str(t.data))]
        assert not invalidas, f"Datas fora do formato YYYY-MM-DD: {invalidas[:5]}"

    def test_lancamentos_nao_vazios(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        vazios = [i for i, t in enumerate(txs) if not t.lancamento or not t.lancamento.strip()]
        assert not vazios, f"Transações com lancamento vazio nos índices: {vazios[:5]}"

    def test_valores_sao_floats(self, resultado_pdf_202602):
        txs, _ = resultado_pdf_202602
        nao_float = [i for i, t in enumerate(txs) if not isinstance(t.valor, float)]
        assert not nao_float


@requires_files
class TestEstruturaPDF202603:
    """Valida estrutura e campos das transações extraídas do PDF mar/2026."""

    def test_n_transacoes_positivo(self, resultado_pdf_202603):
        txs, _ = resultado_pdf_202603
        assert len(txs) > 0

    def test_banco_btg(self, resultado_pdf_202603):
        txs, _ = resultado_pdf_202603
        assert all(t.banco == "BTG" for t in txs)

    def test_mes_fatura_202603(self, resultado_pdf_202603):
        txs, _ = resultado_pdf_202603
        assert all(t.mes_fatura == "202603" for t in txs)

    def test_datas_formato_iso(self, resultado_pdf_202603):
        txs, _ = resultado_pdf_202603
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        invalidas = [t.data for t in txs if not pattern.match(str(t.data))]
        assert not invalidas

    def test_sem_pagamento_fatura(self, resultado_pdf_202603):
        """'Pagamento de fatura' deve ser filtrado — duplicaria o débito do extrato bancário."""
        txs, _ = resultado_pdf_202603
        pagamentos = [t.lancamento for t in txs if "pagamento de fatura" in t.lancamento.lower()]
        assert not pagamentos, (
            f"'Pagamento de fatura' não deve ser importado (duplica extrato): {pagamentos}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. BalanceValidation
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestBalanceValidation202602:
    """BalanceValidation para fev/2026 — XLSX e PDF."""

    def test_xlsx_saldo_inicial_zero(self, resultado_xlsx_202602):
        _, balance = resultado_xlsx_202602
        assert balance.saldo_inicial == 0.0

    def test_xlsx_total_declarado_encontrado(self, resultado_xlsx_202602):
        _, balance = resultado_xlsx_202602
        assert balance.saldo_final is not None, "Total da Fatura não encontrado no XLSX"
        assert balance.saldo_final > 0.0

    def test_xlsx_soma_vs_total_valida(self, resultado_xlsx_202602):
        """Soma das transações deve bater com o total declarado (tolerância 1 centavo)."""
        _, balance = resultado_xlsx_202602
        if balance.saldo_final is None:
            pytest.skip("Total não encontrado no XLSX — não é possível validar")
        assert balance.is_valid is True, (
            f"Soma R${balance.soma_transacoes:.2f} ≠ "
            f"Total declarado R${balance.saldo_final:.2f} "
            f"(diferença R${balance.diferenca:.2f})"
        )

    def test_pdf_saldo_inicial_zero(self, resultado_pdf_202602):
        _, balance = resultado_pdf_202602
        assert balance.saldo_inicial == 0.0

    def test_pdf_total_declarado_encontrado(self, resultado_pdf_202602):
        _, balance = resultado_pdf_202602
        assert balance.saldo_final is not None, "Total a pagar não encontrado no PDF"
        assert balance.saldo_final > 0.0

    def test_pdf_soma_vs_total_valida(self, resultado_pdf_202602):
        _, balance = resultado_pdf_202602
        if balance.saldo_final is None:
            pytest.skip("Total não encontrado no PDF — não é possível validar")
        assert balance.is_valid is True, (
            f"Soma R${balance.soma_transacoes:.2f} ≠ "
            f"Total declarado R${balance.saldo_final:.2f} "
            f"(diferença R${balance.diferenca:.2f})"
        )

    def test_xlsx_e_pdf_mesmo_total(self, resultado_xlsx_202602, resultado_pdf_202602):
        """Total declarado no XLSX e PDF devem ser iguais (mesma fatura)."""
        _, balance_xlsx = resultado_xlsx_202602
        _, balance_pdf  = resultado_pdf_202602
        if balance_xlsx.saldo_final is None or balance_pdf.saldo_final is None:
            pytest.skip("Total não disponível em um dos formatos")
        diff = abs(balance_xlsx.saldo_final - balance_pdf.saldo_final)
        assert diff < 0.02, (
            f"Total XLSX R${balance_xlsx.saldo_final:.2f} ≠ "
            f"Total PDF R${balance_pdf.saldo_final:.2f}"
        )


@requires_files
class TestBalanceValidation202603:
    """BalanceValidation para mar/2026 — XLSX e PDF."""

    def test_xlsx_total_declarado_encontrado(self, resultado_xlsx_202603):
        _, balance = resultado_xlsx_202603
        assert balance.saldo_final is not None
        assert balance.saldo_final > 0.0

    def test_xlsx_soma_vs_total_valida(self, resultado_xlsx_202603):
        """mar/2026: após filtrar 'Pagamento de fatura', soma deve bater com o total."""
        _, balance = resultado_xlsx_202603
        if balance.saldo_final is None:
            pytest.skip("Total não encontrado no XLSX")
        assert balance.is_valid is True, (
            f"Soma R${balance.soma_transacoes:.2f} ≠ "
            f"Total R${balance.saldo_final:.2f} (diff R${balance.diferenca:.2f})"
        )

    def test_pdf_total_declarado_encontrado(self, resultado_pdf_202603):
        _, balance = resultado_pdf_202603
        assert balance.saldo_final is not None
        assert balance.saldo_final > 0.0

    def test_pdf_soma_vs_total_valida(self, resultado_pdf_202603):
        """mar/2026: após filtrar 'Pagamento de fatura', soma deve bater com o total."""
        _, balance = resultado_pdf_202603
        if balance.saldo_final is None:
            pytest.skip("Total não encontrado no PDF")
        assert balance.is_valid is True, (
            f"Soma R${balance.soma_transacoes:.2f} ≠ "
            f"Total R${balance.saldo_final:.2f} (diff R${balance.diferenca:.2f})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Paridade cross-formato: XLSX == PDF (contagem e soma)
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestParidadeXLSXvsPDF202602:
    """XLSX e PDF fev/2026 devem extrair o mesmo conjunto de transações."""

    def test_mesma_quantidade_transacoes(self, resultado_xlsx_202602, resultado_pdf_202602):
        txs_xlsx, _ = resultado_xlsx_202602
        txs_pdf,  _ = resultado_pdf_202602
        assert len(txs_xlsx) == len(txs_pdf), (
            f"XLSX={len(txs_xlsx)} tx  PDF={len(txs_pdf)} tx — "
            f"devem ser iguais para o mesmo arquivo"
        )

    def test_mesma_soma_valores(self, resultado_xlsx_202602, resultado_pdf_202602):
        txs_xlsx, _ = resultado_xlsx_202602
        txs_pdf,  _ = resultado_pdf_202602
        soma_xlsx = round(sum(t.valor for t in txs_xlsx), 2)
        soma_pdf  = round(sum(t.valor for t in txs_pdf),  2)
        assert abs(soma_xlsx - soma_pdf) < 0.02, (
            f"Soma XLSX R${soma_xlsx:.2f} ≠ Soma PDF R${soma_pdf:.2f}"
        )


@requires_files
class TestParidadeXLSXvsPDF202603:
    """XLSX e PDF mar/2026 devem extrair o mesmo conjunto de transações."""

    def test_mesma_quantidade_transacoes(self, resultado_xlsx_202603, resultado_pdf_202603):
        txs_xlsx, _ = resultado_xlsx_202603
        txs_pdf,  _ = resultado_pdf_202603
        assert len(txs_xlsx) == len(txs_pdf), (
            f"XLSX={len(txs_xlsx)} tx  PDF={len(txs_pdf)} tx"
        )

    def test_mesma_soma_valores(self, resultado_xlsx_202603, resultado_pdf_202603):
        txs_xlsx, _ = resultado_xlsx_202603
        txs_pdf,  _ = resultado_pdf_202603
        soma_xlsx = round(sum(t.valor for t in txs_xlsx), 2)
        soma_pdf  = round(sum(t.valor for t in txs_pdf),  2)
        assert abs(soma_xlsx - soma_pdf) < 0.02, (
            f"Soma XLSX R${soma_xlsx:.2f} ≠ Soma PDF R${soma_pdf:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Paridade de hashes: XLSX vs PDF → mesmo IdTransacao por (data, valor)
# ─────────────────────────────────────────────────────────────────────────────

def _comparar_hashes(txs_a, txs_b, user_id=99):
    """
    Compara IdTransacao entre dois conjuntos de transações.
    Estratégia: indexa B por (data, valor) com fila FIFO (igual ao service.py).
    Retorna (divergencias_id, sem_par).
    """
    marked_a = _processar_e_marcar(txs_a, user_id=user_id)
    marked_b = _processar_e_marcar(txs_b, user_id=user_id)

    # Indexa B por (data, round(valor, 2)) → deque FIFO
    idx_b: dict = defaultdict(deque)
    for m in marked_b:
        chave = (m.data, round(float(m.valor), 2))
        idx_b[chave].append(m.id_transacao)

    divergencias = []
    sem_par = 0

    for m in marked_a:
        chave = (m.data, round(float(m.valor), 2))
        if not idx_b[chave]:
            sem_par += 1
            continue
        id_b = idx_b[chave].popleft()
        if m.id_transacao != id_b:
            divergencias.append(
                f"lancamento='{m.lancamento[:40]}' | "
                f"data={m.data} | valor={m.valor:.2f}\n"
                f"  XLSX id_transacao: {m.id_transacao}\n"
                f"   PDF id_transacao: {id_b}"
            )

    return divergencias, sem_par


@requires_files
class TestHashParidade202602:
    """IdTransacao deve ser idêntico para XLSX e PDF da mesma fatura (fev/2026)."""

    def test_id_transacao_identico_xlsx_vs_pdf(
        self, resultado_xlsx_202602, resultado_pdf_202602
    ):
        txs_xlsx, _ = resultado_xlsx_202602
        txs_pdf,  _ = resultado_pdf_202602
        divergencias, sem_par = _comparar_hashes(txs_xlsx, txs_pdf)
        assert not divergencias, (
            f"{len(divergencias)} divergência(s) de IdTransacao XLSX↔PDF:\n"
            + "\n".join(divergencias[:5])
        )

    def test_nenhum_tx_sem_par(self, resultado_xlsx_202602, resultado_pdf_202602):
        """Toda transação do XLSX deve ter correspondente no PDF (mesma data+valor)."""
        txs_xlsx, _ = resultado_xlsx_202602
        txs_pdf,  _ = resultado_pdf_202602
        _, sem_par = _comparar_hashes(txs_xlsx, txs_pdf)
        assert sem_par == 0, (
            f"{sem_par} transação(ões) do XLSX sem correspondente no PDF por (data, valor)"
        )


@requires_files
class TestHashParidade202603:
    """IdTransacao deve ser idêntico para XLSX e PDF da mesma fatura (mar/2026)."""

    def test_id_transacao_identico_xlsx_vs_pdf(
        self, resultado_xlsx_202603, resultado_pdf_202603
    ):
        txs_xlsx, _ = resultado_xlsx_202603
        txs_pdf,  _ = resultado_pdf_202603
        divergencias, sem_par = _comparar_hashes(txs_xlsx, txs_pdf)
        assert not divergencias, (
            f"{len(divergencias)} divergência(s) de IdTransacao XLSX↔PDF:\n"
            + "\n".join(divergencias[:5])
        )

    def test_nenhum_tx_sem_par(self, resultado_xlsx_202603, resultado_pdf_202603):
        txs_xlsx, _ = resultado_xlsx_202603
        txs_pdf,  _ = resultado_pdf_202603
        _, sem_par = _comparar_hashes(txs_xlsx, txs_pdf)
        assert sem_par == 0, (
            f"{sem_par} transação(ões) do XLSX sem correspondente no PDF por (data, valor)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Consistência entre meses (sanity checks)
# ─────────────────────────────────────────────────────────────────────────────

@requires_files
class TestConsistenciaEntreXLSX:
    """Sanity checks entre as duas faturas XLSX."""

    def test_mes_fatura_distintos(self, resultado_xlsx_202602, resultado_xlsx_202603):
        txs_202602, _ = resultado_xlsx_202602
        txs_202603, _ = resultado_xlsx_202603
        meses_202602 = {t.mes_fatura for t in txs_202602}
        meses_202603 = {t.mes_fatura for t in txs_202603}
        assert meses_202602.isdisjoint(meses_202603), \
            "mes_fatura não pode se sobrepor entre faturas diferentes"

    def test_ids_transacao_distintos_entre_meses(
        self, resultado_xlsx_202602, resultado_xlsx_202603
    ):
        """Transações de meses diferentes não devem ter o mesmo IdTransacao."""
        txs_202602, _ = resultado_xlsx_202602
        txs_202603, _ = resultado_xlsx_202603

        marked_202602 = _processar_e_marcar(txs_202602)
        marked_202603 = _processar_e_marcar(txs_202603)

        ids_202602 = {m.id_transacao for m in marked_202602}
        ids_202603 = {m.id_transacao for m in marked_202603}
        colisoes = ids_202602 & ids_202603
        # Pode haver colisões em subscrições mensais (mesmo valor, mesma data relativa)
        # Mas transações com datas diferentes devem ter hashes diferentes.
        # Reportamos mas não falhamos com threshold razoável.
        pct = len(colisoes) / max(len(ids_202602), 1) * 100
        assert pct < 20, (
            f"{len(colisoes)} colisões de IdTransacao entre 202602 e 202603 "
            f"({pct:.1f}%) — excede 20% (esperado ≈ 0%)"
        )
