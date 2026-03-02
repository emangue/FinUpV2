"""
Testes T.01–T.06 — Grupos por usuário (plano admin-gestao-usuarios)

Requer: DATABASE_URL e JWT_SECRET_KEY no .env ou:
  DATABASE_URL=sqlite:///./database/financas_dev.db JWT_SECRET_KEY=test-secret pytest tests/test_grupos_por_usuario.py -v
"""
import os
import pytest
from datetime import datetime

# Configurar env antes de importar app (para SQLite local)
os.environ.setdefault("DATABASE_URL", "sqlite:///./database/financas_dev.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-for-pytest-min-32-chars")

from sqlalchemy.orm import Session
from app.core.database import SessionLocal

# Garantir que todos os modelos estejam carregados (evita KeyError em relationships)
from app.domains.upload.history_models import UploadHistory  # noqa: F401
from app.domains.users.service import UserService
from app.domains.users.schemas import UserCreate
from app.domains.users.repository import UserRepository
from app.domains.users.models import User
from app.domains.grupos.models import BaseGruposConfig, BaseGruposTemplate
from app.domains.categories.models import BaseMarcacao
from app.domains.transactions.models import JournalEntry


def get_expected_grupos_count(db: Session) -> int:
    """Quantidade de grupos no template (base_grupos_template) — dinâmico."""
    return db.query(BaseGruposTemplate).count()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()


class TestT01CriarUsuarioGrupos:
    """T.01: Criar usuário → base_grupos_config count = 14"""

    def test_criar_usuario_inicializa_grupos(self, db: Session):
        email = f"test_t01_{datetime.now().strftime('%H%M%S')}@teste.com"
        user_data = UserCreate(
            email=email,
            nome="Teste T01 Grupos",
            password="senha123",
            role="user",
        )
        service = UserService(db)
        user = service.create_user(user_data)
        assert user.id is not None

        expected = get_expected_grupos_count(db)
        count = db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).count()
        assert count == expected, f"Esperado {expected} grupos, obtido {count}"

        # Limpar
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user.id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()


class TestT02IdempotenteInicializar:
    """T.02: _inicializar_grupos_usuario duas vezes → ainda 14 grupos"""

    def test_inicializar_duas_vezes_nao_duplica(self, db: Session):
        email = f"test_t02_{datetime.now().strftime('%H%M%S')}@teste.com"
        user_data = UserCreate(
            email=email,
            nome="Teste T02 Idempotente",
            password="senha123",
            role="user",
        )
        service = UserService(db)
        user = service.create_user(user_data)

        # Chamar novamente (idempotente)
        service._inicializar_grupos_usuario(user.id)

        expected = get_expected_grupos_count(db)
        count = db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).count()
        assert count == expected, f"Esperado {expected} grupos após 2ª chamada, obtido {count}"

        # Limpar
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user.id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()


class TestT03GrupoIsoladoPorUsuario:
    """T.03: User A cria grupo 'MeuGrupo' → User B não vê em GET /grupos/"""

    def test_grupo_criado_por_a_nao_visivel_para_b(self, db: Session):
        from app.domains.grupos.service import GrupoService
        from app.domains.grupos.schemas import GrupoCreate

        # Criar User A e User B
        email_a = f"test_t03a_{datetime.now().strftime('%H%M%S')}@teste.com"
        email_b = f"test_t03b_{datetime.now().strftime('%H%M%S')}@teste.com"
        service_user = UserService(db)
        user_a = service_user.create_user(UserCreate(email=email_a, nome="User A", password="senha123", role="user"))
        user_b = service_user.create_user(UserCreate(email=email_b, nome="User B", password="senha123", role="user"))

        # User A cria grupo "MeuGrupo"
        grupo_service = GrupoService(db)
        grupo_create = GrupoCreate(
            nome_grupo="MeuGrupo",
            tipo_gasto_padrao="Ajustável",
            categoria_geral="Despesa",
        )
        grupo_service.create_grupo(user_a.id, grupo_create)

        # User B lista grupos — não deve ver "MeuGrupo"
        grupos_b = grupo_service.list_grupos(user_b.id)
        nomes_b = [g.nome_grupo for g in grupos_b.grupos]
        assert "MeuGrupo" not in nomes_b, "User B não deve ver grupo criado por User A"

        # User A deve ver "MeuGrupo"
        grupos_a = grupo_service.list_grupos(user_a.id)
        nomes_a = [g.nome_grupo for g in grupos_a.grupos]
        assert "MeuGrupo" in nomes_a, "User A deve ver seu grupo"

        # Limpar
        db.query(BaseGruposConfig).filter(BaseGruposConfig.nome_grupo == "MeuGrupo").delete(synchronize_session=False)
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user_a.id).delete()
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user_b.id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_a.id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_b.id).delete()
        db.query(User).filter(User.id.in_([user_a.id, user_b.id])).delete(synchronize_session=False)
        db.commit()


class TestT04PurgeZeraDados:
    """T.04: Purge → journal_entries e base_grupos_config/base_marcacoes zerados"""

    def test_purge_remove_todos_dados_do_usuario(self, db: Session):
        email = f"test_t04_{datetime.now().strftime('%H%M%S')}@teste.com"
        service = UserService(db)
        user = service.create_user(UserCreate(email=email, nome="Teste Purge", password="senha123", role="user"))

        expected = get_expected_grupos_count(db)
        count_grupos_antes = db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).count()
        assert count_grupos_antes == expected, f"Esperado {expected} grupos, obtido {count_grupos_antes}"

        # Purge (executado por admin id=1)
        service.purge_user(user.id, executado_por=1)

        count_grupos = db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).count()
        count_marcacoes = db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user.id).count()
        count_journal = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).count()

        assert count_grupos == 0, "base_grupos_config deve estar vazio"
        assert count_marcacoes == 0, "base_marcacoes deve estar vazio"
        assert count_journal == 0, "journal_entries deve estar vazio"


class TestT05PurgeUser1Proibido:
    """T.05: user_id=1 → DELETE /users/1/purge retorna 403"""

    def test_purge_user_1_retorna_403(self, db: Session):
        from fastapi import HTTPException

        service = UserService(db)

        with pytest.raises(HTTPException) as exc_info:
            service.purge_user(1, executado_por=1)

        assert exc_info.value.status_code == 403


class TestT06ReativarUsuario:
    """T.06: Reativar → usuário consegue logar normalmente"""

    def test_reativar_usuario_permite_login(self, db: Session):
        from app.domains.auth.password_utils import verify_password

        email = f"test_t06_{datetime.now().strftime('%H%M%S')}@teste.com"
        service = UserService(db)
        user = service.create_user(UserCreate(email=email, nome="Teste Reativar", password="senha123", role="user"))

        # Desativar
        service.delete_user(user.id)
        repo = UserRepository(db)
        u = repo.get_by_id(user.id)
        assert u.ativo == 0

        # Reativar
        service.reativar(user.id)
        u2 = UserRepository(db).get_by_id(user.id)
        assert u2.ativo == 1

        # Verificar que senha ainda funciona
        assert verify_password("senha123", u2.password_hash)

        # Limpar
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user.id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
