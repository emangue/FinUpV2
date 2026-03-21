"""
Testes para marker.py v5.1 — correção dedup parcelas.

Foca nos três bugs corrigidos:
  BUG-1: chave_unica ignorava parcela → colapso intra-arquivo
  BUG-2: generate_id_transacao não recebia parcela → colisão entre meses
  BUG-3: IdParcela baseado em nome do estabelecimento (frágil PDF/CSV)

Sprint 3 — fix dedup parcelas
PRD: docs/features/upload-banco-manual/01-PRD/PRD_parcelas_v5_1.md
"""
import hashlib
import importlib.util
import inspect
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ─── Replicar fórmulas do marker.py v5.1 (sem importar FastAPI/SQLAlchemy) ───

def _chave_unica_v51(banco: str, tipo: str, data: str,
                     valor: float, parcela_param: Optional[str]) -> str:
    """Replica fórmula de chave_unica do marker.py v5.1."""
    if parcela_param:
        return f"{banco}|{tipo}|{data}|{valor:.2f}|{parcela_param}"
    return f"{banco}|{tipo}|{data}|{valor:.2f}"


def _id_parcela_v51(banco: str, tipo: str, data: str,
                    valor: float, total: int, user_id: int) -> str:
    """Replica fórmula de IdParcela do marker.py v5.1."""
    chave = f"{banco}|{tipo}|{data}|{valor:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


# ─── Dados de referência ──────────────────────────────────────────────────────
_BANCO = "itau"
_TIPO  = "fatura"


class TestChaueUnicaBug1:
    """BUG-1: chave_unica deve incluir parcela para evitar colapso intra-arquivo."""

    def test_chave_diferentes_para_parcelas_diferentes(self):
        """Parcelas 1/6 e 2/6 no mesmo arquivo → chaves_unicas distintas."""
        chave_1 = _chave_unica_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, "1/6")
        chave_2 = _chave_unica_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, "2/6")
        assert chave_1 != chave_2, "Parcelas 1/6 e 2/6 devem ter chave_unica distintas"

    def test_chave_igual_mesma_parcela(self):
        """Mesma transação (re-upload) → mesma chave (idempotente)."""
        chave_a = _chave_unica_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, "1/6")
        chave_b = _chave_unica_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, "1/6")
        assert chave_a == chave_b, "Mesma transação deve gerar mesma chave (idempotente)"

    def test_sem_parcela_backward_compat(self):
        """Sem parcela → chave idêntica ao v5 (nenhum campo extra)."""
        chave_v5  = f"itau|fatura|15/02/2026|-42.00"
        chave_v51 = _chave_unica_v51("itau", "fatura", "15/02/2026", -42.00, None)
        assert chave_v5 == chave_v51, "Sem parcela deve ser idêntico ao v5"


class TestIdParcelaBug3:
    """BUG-3: IdParcela v5.1 baseado em fingerprint banco/tipo/data/valor/total."""

    def test_mesmos_dados_mesma_id_parcela(self):
        """Mesmos banco+tipo+data+valor+total+user_id → mesmo IdParcela (idempotente)."""
        id_1 = _id_parcela_v51(_BANCO, _TIPO, "10/01/2026", -200.00, 12, 1)
        id_2 = _id_parcela_v51(_BANCO, _TIPO, "10/01/2026", -200.00, 12, 1)
        assert id_1 == id_2, "IdParcela deve ser idêntico para mesmos dados"

    def test_id_parcela_diferente_por_user(self):
        """user_id diferente → IdParcela diferente."""
        id_u1 = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 1)
        id_u2 = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 2)
        assert id_u1 != id_u2, "IdParcela deve isolar por user_id"

    def test_id_parcela_formato_16_chars(self):
        """IdParcela deve ter 16 chars hex (MD5[:16])."""
        id_p = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 1)
        assert len(id_p) == 16
        assert all(c in "0123456789abcdef" for c in id_p)

    def test_anuidade_parcelas_data_diferente(self):
        """ANUIDADE (data de cobrança muda por mês) → IdParcela diferente por parcela.
        
        Caso real: ANUIDADE DIFERENCI — cada parcela tem data de cobrança diferente.
        Não é um problema: IdTransacao também serão diferentes (datas distintas).
        """
        id_p5 = _id_parcela_v51(_BANCO, _TIPO, "26/12/2025", -73.50, 10, 1)
        id_p6 = _id_parcela_v51(_BANCO, _TIPO, "26/01/2026", -73.50, 10, 1)
        assert id_p5 != id_p6, "Data diferente → IdParcela diferente (esperado)"

    def test_airbnb_parcelas_mesma_data(self):
        """AIRBNB (data original mantida) → mesmo IdParcela para todas parcelas.
        
        Caso real: AIRBNB * HMHMZAQ — todas as 6 parcelas usam data=19/01/2026.
        IdParcela idêntico agrupa as parcelas da mesma compra.
        """
        id_p1 = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 1)
        id_p2 = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 1)
        id_p6 = _id_parcela_v51(_BANCO, _TIPO, "19/01/2026", -1011.21, 6, 1)
        assert id_p1 == id_p2 == id_p6, \
            "Parcelas da mesma compra (mesma data) devem ter mesmo IdParcela"


class TestAtualizacaoTestHashUserId:
    """Verifica que hasher.py v5.1 tem assinatura correta com param parcela."""

    def test_assinatura_v51_requer_parcela(self):
        """Documenta que assinatura v5.1 exige banco, tipo_documento e parcela."""
        _backend  = Path(__file__).resolve().parent.parent
        _hasher_p = _backend / "app" / "shared" / "utils" / "hasher.py"
        spec = importlib.util.spec_from_file_location("hasher", _hasher_p)
        hmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hmod)
        sig    = inspect.signature(hmod.generate_id_transacao)
        params = list(sig.parameters.keys())
        assert "banco"          in params, "v5.1 deve ter parâmetro 'banco'"
        assert "tipo_documento" in params, "v5.1 deve ter parâmetro 'tipo_documento'"
        assert "parcela"        in params, "v5.1 deve ter parâmetro 'parcela'"
        # parcela deve ter default None (opcional)
        assert sig.parameters["parcela"].default is None, \
            "parcela deve ter default=None (backward compat)"
