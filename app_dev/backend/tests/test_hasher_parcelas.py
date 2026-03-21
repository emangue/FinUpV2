"""
Testes para generate_id_transacao v5.1 — suporte a parcelas.

Sprint 3 — fix dedup parcelas
PRD: docs/features/upload-banco-manual/01-PRD/PRD_parcelas_v5_1.md
"""
import importlib.util
from pathlib import Path
import pytest

_backend  = Path(__file__).resolve().parent.parent
_hasher_p = _backend / "app" / "shared" / "utils" / "hasher.py"
spec = importlib.util.spec_from_file_location("hasher", _hasher_p)
hasher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hasher)
generate_id_transacao = hasher.generate_id_transacao

# ─── Dados de referência (AIRBNB real do DB) ──────────────────────────────────
_DATA  = "19/01/2026"
_BANCO = "itau"
_TIPO  = "fatura"
_VALOR = -1011.21
_UID   = 1


class TestHasherParcelas:

    def test_parcela_1_difere_de_parcela_2(self):
        """Parcelas 1/6 e 2/6 da mesma compra → IdTransacao diferentes."""
        id_p1 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/6")
        id_p2 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="2/6")
        assert id_p1 != id_p2, "Parcela 1/6 e 2/6 devem ter IdTransacao distintos"

    def test_todas_parcelas_diferentes(self):
        """Parcelas 1..6 de mesma compra → todos IdTransacao únicos."""
        ids = {
            generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela=f"{i}/6")
            for i in range(1, 7)
        }
        assert len(ids) == 6, "Todas as 6 parcelas devem ter IdTransacao único"

    def test_sem_parcela_backward_compat(self):
        """Sem parcela → hash idêntico ao v5 (mesma chave sem parcela)."""
        id_v5  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID)
        id_v51 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela=None)
        assert id_v5 == id_v51, "parcela=None deve produzir hash idêntico ao v5"

    def test_parcela_none_nao_colapsa_com_1_1(self):
        """parcela=None e parcela='1/1' devem gerar hashes diferentes."""
        id_none = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID)
        id_1_1  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/1")
        assert id_none != id_1_1, "None e '1/1' não devem colapsar"

    def test_mesma_parcela_idempotente(self):
        """Mesma chamada com mesma parcela → hash idêntico (determinístico)."""
        id_a = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="3/12")
        id_b = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="3/12")
        assert id_a == id_b

    def test_parcela_formato_variado(self):
        """Formatos '1/12' e '01/12' são strings distintas → hashes diferentes."""
        id_1_12  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/12")
        id_01_12 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="01/12")
        # Formatos diferentes são strings distintas (marker.py normaliza antes de chamar)
        assert id_1_12 != id_01_12, "Formatos '1/12' e '01/12' devem ser distintos"

    def test_user_id_isolamento_com_parcela(self):
        """Com parcela, user_id diferente ainda gera IdTransacao diferente."""
        id_u1 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, 1, parcela="2/6")
        id_u2 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, 2, parcela="2/6")
        assert id_u1 != id_u2, "user_id deve isolar hashes mesmo com parcela"

    def test_hash_e_inteiro(self):
        """IdTransacao deve ser um inteiro (FNV-1a 64-bit como string decimal)."""
        id_p = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/6")
        assert str(id_p).isdigit() or isinstance(id_p, int), \
            "IdTransacao deve ser inteiro decimal"
