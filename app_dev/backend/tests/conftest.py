"""
Pytest conftest - Garante que modelos com relationships estejam no registry.
Evita KeyError 'UploadHistory' ao usar SessionLocal em testes/scripts.
"""
# Carregar antes de qualquer test que use SessionLocal
from app.domains.upload.history_models import UploadHistory  # noqa: F401
from app.domains.transactions.models import JournalEntry  # noqa: F401
