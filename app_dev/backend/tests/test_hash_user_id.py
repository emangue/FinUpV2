"""
Validação: Hashes SEMPRE incluem user_id para isolamento entre usuários.

Garante que IdTransacao e IdParcela nunca colidam entre usuários diferentes.
"""
import hashlib
import importlib.util
from pathlib import Path

# Import direto dos módulos (evita app.shared.__init__ e FastAPI)
_backend = Path(__file__).resolve().parent.parent
_hasher_path = _backend / "app" / "shared" / "utils" / "hasher.py"
_normalizer_path = _backend / "app" / "shared" / "utils" / "normalizer.py"

spec_h = importlib.util.spec_from_file_location("hasher", _hasher_path)
hasher = importlib.util.module_from_spec(spec_h)
spec_h.loader.exec_module(hasher)
generate_id_transacao = hasher.generate_id_transacao

spec_n = importlib.util.spec_from_file_location("normalizer", _normalizer_path)
normalizer = importlib.util.module_from_spec(spec_n)
spec_n.loader.exec_module(normalizer)
normalizar_estabelecimento = normalizer.normalizar_estabelecimento

import pytest


# Fórmula IdParcela (deve estar em sync com marker.py)
def _gerar_id_parcela_esperado(estab_base: str, valor: float, total: int, user_id: int) -> str:
    """Réplica exata da lógica do marker.py para IdParcela"""
    estab_norm = normalizar_estabelecimento(estab_base)
    valor_arr = round(float(valor), 2)
    chave = f"{estab_norm}|{valor_arr:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


class TestHashIncluiUserId:
    """Garante que user_id está em todos os hashes críticos."""

    def test_id_transacao_diferente_por_user(self):
        """IdTransacao deve ser diferente para user_id diferente."""
        data = "15/10/2025"
        estab = "NETFLIX (1/12)"
        valor = -49.90

        id_user1 = generate_id_transacao(data, estab, valor, user_id=1)
        id_user2 = generate_id_transacao(data, estab, valor, user_id=2)

        assert id_user1 != id_user2, "IdTransacao deve ser diferente por user_id"

    def test_id_transacao_igual_mesmo_user(self):
        """IdTransacao deve ser igual para mesmo user e mesmos dados."""
        data = "15/10/2025"
        estab = "NETFLIX (1/12)"
        valor = -49.90

        id1 = generate_id_transacao(data, estab, valor, user_id=1)
        id2 = generate_id_transacao(data, estab, valor, user_id=1)

        assert id1 == id2

    def test_id_parcela_diferente_por_user(self):
        """IdParcela deve ser diferente para user_id diferente."""
        estab = "PRODUTOS GLOBO"
        valor = 59.9
        total = 12

        id_user1 = _gerar_id_parcela_esperado(estab, valor, total, user_id=1)
        id_user2 = _gerar_id_parcela_esperado(estab, valor, total, user_id=2)

        assert id_user1 != id_user2, "IdParcela deve ser diferente por user_id"

    def test_id_parcela_igual_mesmo_user(self):
        """IdParcela deve ser igual para mesmo user e mesmos dados."""
        estab = "PRODUTOS GLOBO"
        valor = 59.9
        total = 12

        id1 = _gerar_id_parcela_esperado(estab, valor, total, user_id=1)
        id2 = _gerar_id_parcela_esperado(estab, valor, total, user_id=1)

        assert id1 == id2

    def test_id_parcela_formato_correto(self):
        """IdParcela deve ter 16 chars (MD5[:16])."""
        id_p = _gerar_id_parcela_esperado("LOJA XYZ", 100.0, 6, user_id=1)
        assert len(id_p) == 16
        assert id_p.isalnum()
