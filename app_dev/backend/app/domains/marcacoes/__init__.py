"""
Domínio Marcações - Gestão de Grupos e Subgrupos
"""
from app.domains.categories.models import BaseMarcacao  # Importar modelo existente
from .schemas import (
    MarcacaoCreate,
    MarcacaoResponse,
    MarcacaoListResponse,
    SubgrupoCreate,
    SubgrupoResponse,
    GrupoComSubgrupos
)
from .service import MarcacaoService
from .repository import MarcacaoRepository
from .router import router

__all__ = [
    "BaseMarcacao",
    "MarcacaoCreate",
    "MarcacaoResponse",
    "MarcacaoListResponse",
    "SubgrupoCreate",
    "SubgrupoResponse",
    "GrupoComSubgrupos",
    "MarcacaoService",
    "MarcacaoRepository",
    "router",
]
