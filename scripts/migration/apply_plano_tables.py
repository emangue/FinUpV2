#!/usr/bin/env python3
"""
Aplica tabelas do plano financeiro manualmente.
Use se alembic upgrade falhar com "overlaps".

Uso:
  cd app_dev/backend && source ../venv/bin/activate
  PYTHONPATH=. python ../../scripts/migration/apply_plano_tables.py
"""
import os
import sys
from pathlib import Path

# Carregar .env
backend = Path(__file__).resolve().parent.parent.parent / "app_dev" / "backend"
os.chdir(backend)
env_file = backend / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

sys.path.insert(0, str(backend))

from sqlalchemy import text
from app.core.database import engine

SQL = """
CREATE TABLE IF NOT EXISTS user_financial_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    renda_mensal_liquida FLOAT,
    idade_atual INTEGER,
    idade_aposentadoria INTEGER DEFAULT 65,
    patrimonio_atual FLOAT DEFAULT 0,
    taxa_retorno_anual FLOAT DEFAULT 0.08,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_user_financial_profile_user_id ON user_financial_profile(user_id);

CREATE TABLE IF NOT EXISTS plano_metas_categoria (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    grupo VARCHAR(100) NOT NULL,
    valor_meta FLOAT NOT NULL,
    ano INTEGER NOT NULL,
    mes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, grupo, ano, mes)
);
CREATE INDEX IF NOT EXISTS ix_plano_metas_categoria_user_id ON plano_metas_categoria(user_id);

CREATE TABLE IF NOT EXISTS plano_compromissos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    nome VARCHAR(200) NOT NULL,
    valor_mensal FLOAT NOT NULL,
    meses_restantes INTEGER,
    grupo VARCHAR(100),
    data_inicio DATE NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_plano_compromissos_user_id ON plano_compromissos(user_id);
"""

def main():
    with engine.connect() as conn:
        with conn.begin():
            for stmt in SQL.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    try:
                        conn.execute(text(stmt))
                        print("OK:", stmt[:60] + "...")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            print("SKIP (exists):", stmt[:50] + "...")
                        else:
                            raise
    print("Tabelas plano criadas/verificadas.")

if __name__ == "__main__":
    main()
