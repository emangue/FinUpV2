"""add_user_id_base_grupos_marcacoes - Grupos por usuário

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-02-28

Adiciona user_id e is_padrao em base_grupos_config.
Adiciona user_id em base_marcacoes.
Atribui dados existentes a user_id=1.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = "g2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    is_sqlite = "sqlite" in str(conn.engine.url)

    # 1. base_grupos_config: add user_id, is_padrao
    op.add_column("base_grupos_config", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column(
        "base_grupos_config",
        sa.Column("is_padrao", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    conn.execute(text("UPDATE base_grupos_config SET user_id = 1 WHERE user_id IS NULL"))
    conn.execute(text("UPDATE base_grupos_config SET is_padrao = true WHERE user_id = 1"))
    op.alter_column("base_grupos_config", "user_id", nullable=False)

    if not is_sqlite:
        op.create_foreign_key(
            "fk_base_grupos_config_user_id", "base_grupos_config", "users", ["user_id"], ["id"]
        )

    # Trocar UNIQUE: drop (nome_grupo) → create (user_id, nome_grupo)
    # SQLite: unique está no index ix_base_grupos_config_nome_grupo
    # PostgreSQL: pode ser constraint ou index, usar DO block para evitar abort
    if is_sqlite:
        op.execute(text("DROP INDEX IF EXISTS ix_base_grupos_config_nome_grupo"))
    else:
        # PostgreSQL: drop constraint/index se existir (evita InFailedSqlTransaction)
        op.execute(text("""
            DO $$
            DECLARE r RECORD;
            BEGIN
                FOR r IN (SELECT conname FROM pg_constraint WHERE conrelid = 'base_grupos_config'::regclass AND contype = 'u')
                LOOP
                    EXECUTE format('ALTER TABLE base_grupos_config DROP CONSTRAINT IF EXISTS %I', r.conname);
                END LOOP;
                DROP INDEX IF EXISTS ix_base_grupos_config_nome_grupo;
            END $$;
        """))

    op.create_unique_constraint(
        "uq_base_grupos_config_user_nome", "base_grupos_config", ["user_id", "nome_grupo"]
    )
    op.create_index("ix_base_grupos_config_user_id", "base_grupos_config", ["user_id"], unique=False)

    # 2. base_marcacoes: add user_id
    op.add_column("base_marcacoes", sa.Column("user_id", sa.Integer(), nullable=True))
    conn.execute(text("UPDATE base_marcacoes SET user_id = 1 WHERE user_id IS NULL"))
    op.alter_column("base_marcacoes", "user_id", nullable=False)

    if not is_sqlite:
        op.create_foreign_key(
            "fk_base_marcacoes_user_id", "base_marcacoes", "users", ["user_id"], ["id"]
        )

    # Remover duplicatas (user_id, GRUPO, SUBGRUPO) antes de criar constraint
    if not is_sqlite:
        conn.execute(text("""
            DELETE FROM base_marcacoes a USING base_marcacoes b
            WHERE a.id > b.id AND a.user_id = b.user_id AND a."GRUPO" = b."GRUPO" AND a."SUBGRUPO" = b."SUBGRUPO"
        """))

    op.create_unique_constraint(
        "uq_base_marcacoes_user_grupo_sub", "base_marcacoes", ["user_id", "GRUPO", "SUBGRUPO"]
    )
    op.create_index("ix_base_marcacoes_user_id", "base_marcacoes", ["user_id"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    is_sqlite = "sqlite" in str(conn.engine.url)

    op.drop_index("ix_base_marcacoes_user_id", table_name="base_marcacoes")
    op.drop_constraint("uq_base_marcacoes_user_grupo_sub", "base_marcacoes", type_="unique")
    if not is_sqlite:
        op.drop_constraint("fk_base_marcacoes_user_id", "base_marcacoes", type_="foreignkey")
    op.drop_column("base_marcacoes", "user_id")

    op.drop_index("ix_base_grupos_config_user_id", table_name="base_grupos_config")
    op.drop_constraint("uq_base_grupos_config_user_nome", "base_grupos_config", type_="unique")
    if not is_sqlite:
        op.drop_constraint("fk_base_grupos_config_user_id", "base_grupos_config", type_="foreignkey")
    op.drop_column("base_grupos_config", "is_padrao")
    op.drop_column("base_grupos_config", "user_id")

    op.create_index("ix_base_grupos_config_nome_grupo", "base_grupos_config", ["nome_grupo"], unique=True)
