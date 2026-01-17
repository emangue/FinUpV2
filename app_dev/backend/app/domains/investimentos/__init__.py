"""
Domínio Investimentos - Gestão de portfólio de investimentos.

Exports dos componentes principais.
"""
from .models import (
    InvestimentoPortfolio,
    InvestimentoHistorico,
    InvestimentoCenario,
    AporteExtraordinario,
    InvestimentoPlanejamento
)
from .schemas import (
    InvestimentoPortfolioCreate,
    InvestimentoPortfolioUpdate,
    InvestimentoPortfolioResponse,
    InvestimentoHistoricoCreate,
    InvestimentoHistoricoResponse,
    InvestimentoCenarioCreate,
    InvestimentoCenarioResponse,
    InvestimentoPlanejamentoCreate,
    InvestimentoPlanejamentoResponse,
    PortfolioResumo,
    SimulacaoCompleta
)
from .service import InvestimentoService
from .repository import InvestimentoRepository
from .router import router

__all__ = [
    # Models
    "InvestimentoPortfolio",
    "InvestimentoHistorico",
    "InvestimentoCenario",
    "AporteExtraordinario",
    "InvestimentoPlanejamento",
    # Schemas
    "InvestimentoPortfolioCreate",
    "InvestimentoPortfolioUpdate",
    "InvestimentoPortfolioResponse",
    "InvestimentoHistoricoCreate",
    "InvestimentoHistoricoResponse",
    "InvestimentoCenarioCreate",
    "InvestimentoCenarioResponse",
    "InvestimentoPlanejamentoCreate",
    "InvestimentoPlanejamentoResponse",
    "PortfolioResumo",
    "SimulacaoCompleta",
    # Service & Repository
    "InvestimentoService",
    "InvestimentoRepository",
    # Router
    "router",
]
