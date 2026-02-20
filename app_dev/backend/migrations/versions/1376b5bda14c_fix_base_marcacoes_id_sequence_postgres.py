"""fix_base_marcacoes_id_sequence_postgres

Revision ID: 1376b5bda14c
Revises: 599d728bc4da
Create Date: 2026-02-15 19:14:44.093197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1376b5bda14c'
down_revision: Union[str, Sequence[str], None] = '599d728bc4da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    PostgreSQL: base_marcacoes.id precisa de sequence para auto-increment.
    A migration 599d728bc4da criou a tabela com id INTEGER NOT NULL sem DEFAULT.
    SQLite auto-incrementa; PostgreSQL não - precisa de SERIAL ou sequence.
    """
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS base_marcacoes_id_seq"))
        op.execute(sa.text(
            "ALTER TABLE base_marcacoes ALTER COLUMN id SET DEFAULT nextval('base_marcacoes_id_seq')"
        ))
        result = conn.execute(sa.text("SELECT COALESCE(MAX(id), 1) FROM base_marcacoes"))
        max_id = result.scalar()
        op.execute(sa.text(f"SELECT setval('base_marcacoes_id_seq', {max_id})"))


def downgrade() -> None:
    """Remove default do id (PostgreSQL)"""
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute(sa.text("ALTER TABLE base_marcacoes ALTER COLUMN id DROP DEFAULT"))
        op.execute(sa.text("DROP SEQUENCE IF EXISTS base_marcacoes_id_seq"))
