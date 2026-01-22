from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adicionar o diretório do app ao PYTHONPATH
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

# Importar settings e Base do app
from app.core.config import settings
from app.core.database import Base

# Importar TODOS os modelos para garantir que sejam registrados no Base.metadata
from app.domains.transactions.models import JournalEntry, BaseParcelas
from app.domains.users.models import User
from app.domains.categories.models import BaseMarcacao
from app.domains.grupos.models import BaseGruposConfig
from app.domains.cards.models import Cartao
from app.domains.exclusoes.models import TransacaoExclusao
from app.domains.upload.models import PreviewTransacao
from app.domains.patterns.models import BasePadroes
from app.domains.screen_visibility.models import ScreenVisibility
from app.domains.budget.models import (
    BudgetGeral, BudgetPlanning,
    BudgetCategoriaConfig, BudgetGeralHistorico
)
from app.domains.compatibility.models import BankFormatCompatibility
from app.domains.classification.models import GenericClassificationRules
from app.domains.investimentos.models import (
    InvestimentoPortfolio, InvestimentoHistorico,
    InvestimentoCenario, AporteExtraordinario, InvestimentoPlanejamento
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Configurar sqlalchemy.url com a URL do settings (suporta SQLite ou PostgreSQL)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Usar Base.metadata do app (todos os modelos importados acima)
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
