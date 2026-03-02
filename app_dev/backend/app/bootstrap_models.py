"""
Bootstrap para carregar modelos com relationships no registry SQLAlchemy.
Use em scripts standalone que importam SessionLocal sem passar por main.py.

Exemplo:
    from app.bootstrap_models import ensure_models_loaded
    ensure_models_loaded()
    from app.core.database import SessionLocal
    ...
"""
from app.domains.upload.history_models import UploadHistory  # noqa: F401
from app.domains.transactions.models import JournalEntry  # noqa: F401


def ensure_models_loaded() -> None:
    """Garante que UploadHistory e JournalEntry estejam no registry (evita KeyError)."""
    pass  # Import no topo já carrega os modelos
