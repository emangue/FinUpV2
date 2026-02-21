"""
Schemas Pydantic do domínio Investimentos.
"""
from datetime import datetime, date
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator


# ============================================================================
# PORTFOLIO SCHEMAS
# ============================================================================

class InvestimentoPortfolioBase(BaseModel):
    """Schema base para investimento no portfólio"""
    balance_id: str = Field(..., max_length=100)
    nome_produto: str = Field(..., max_length=255)
    corretora: str = Field(..., max_length=100)
    tipo_investimento: str = Field(..., max_length=50)
    classe_ativo: Optional[str] = Field(None, max_length=50)
    emissor: Optional[str] = Field(None, max_length=100)
    ano: Optional[int] = None
    anomes: Optional[int] = None
    percentual_cdi: Optional[float] = None
    data_aplicacao: Optional[date] = None
    data_vencimento: Optional[date] = None
    quantidade: float = 1.0
    valor_unitario_inicial: Optional[Decimal] = None
    valor_total_inicial: Optional[Decimal] = None


class InvestimentoPortfolioCreate(InvestimentoPortfolioBase):
    """Schema para criação de investimento. user_id é preenchido pelo backend."""
    user_id: Optional[int] = None


class InvestimentoPortfolioUpdate(BaseModel):
    """Schema para atualização de investimento"""
    nome_produto: Optional[str] = None
    corretora: Optional[str] = None
    tipo_investimento: Optional[str] = None
    classe_ativo: Optional[str] = None
    emissor: Optional[str] = None
    ano: Optional[int] = None
    anomes: Optional[int] = None
    percentual_cdi: Optional[float] = None
    data_aplicacao: Optional[date] = None
    data_vencimento: Optional[date] = None
    quantidade: Optional[float] = None
    valor_unitario_inicial: Optional[Decimal] = None
    valor_total_inicial: Optional[Decimal] = None
    ativo: Optional[bool] = None


class InvestimentoPortfolioResponse(InvestimentoPortfolioBase):
    """Schema de resposta de investimento"""
    id: int
    user_id: int
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class InvestimentoComHistoricoResponse(InvestimentoPortfolioResponse):
    """Resposta com valores do histórico do mês (usado para ativos/passivos)"""
    valor_total_mes: Optional[Decimal] = None
    valor_unitario_mes: Optional[Decimal] = None
    quantidade_mes: Optional[float] = None


# ============================================================================
# HISTORICO SCHEMAS
# ============================================================================

class InvestimentoHistoricoBase(BaseModel):
    """Schema base para histórico mensal"""
    ano: int = Field(..., ge=2000, le=2100)
    mes: int = Field(..., ge=1, le=12)
    anomes: int = Field(..., ge=200001, le=210012)
    data_referencia: date
    quantidade: Optional[float] = None
    valor_unitario: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    aporte_mes: Decimal = Decimal('0.00')
    rendimento_mes: Optional[Decimal] = None
    rendimento_acumulado: Optional[Decimal] = None


class InvestimentoHistoricoCreate(InvestimentoHistoricoBase):
    """Schema para criação de histórico"""
    investimento_id: int


class InvestimentoHistoricoUpdate(BaseModel):
    """Schema para atualização de histórico"""
    quantidade: Optional[float] = None
    valor_unitario: Optional[Decimal] = None
    valor_total: Optional[Decimal] = None
    aporte_mes: Optional[Decimal] = None
    rendimento_mes: Optional[Decimal] = None
    rendimento_acumulado: Optional[Decimal] = None


class InvestimentoHistoricoResponse(InvestimentoHistoricoBase):
    """Schema de resposta de histórico"""
    id: int
    investimento_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# CENARIO SCHEMAS
# ============================================================================

class AporteExtraordinarioBase(BaseModel):
    """Schema base para aporte extraordinário"""
    mes_referencia: int = Field(..., ge=1)
    valor: Decimal = Field(..., gt=0)
    descricao: Optional[str] = Field(None, max_length=255)


class AporteExtraordinarioCreate(AporteExtraordinarioBase):
    """Schema para criação de aporte extraordinário"""
    pass


class AporteExtraordinarioResponse(AporteExtraordinarioBase):
    """Schema de resposta de aporte extraordinário"""
    id: int
    cenario_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvestimentoCenarioBase(BaseModel):
    """Schema base para cenário de simulação"""
    nome_cenario: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    patrimonio_inicial: Decimal = Field(..., ge=0)
    rendimento_mensal_pct: Decimal = Field(..., ge=-0.5, le=1.0)  # -50% a 100%
    aporte_mensal: Decimal = Field(default=Decimal('0.00'), ge=0)
    periodo_meses: int = Field(default=120, ge=1, le=600)  # Até 50 anos


class InvestimentoCenarioCreateIn(InvestimentoCenarioBase):
    """Schema do body da requisição - SEM user_id (injetado pelo router)."""
    aportes_extraordinarios: List[AporteExtraordinarioCreate] = []
    idade_atual: Optional[int] = None
    idade_aposentadoria: Optional[int] = None
    renda_mensal_alvo: Optional[Decimal] = None
    inflacao_aa: Optional[Decimal] = None
    retorno_aa: Optional[Decimal] = None
    anomes_inicio: Optional[int] = None
    principal: Optional[bool] = None
    extras_json: Optional[str] = None


class InvestimentoCenarioCreate(InvestimentoCenarioCreateIn):
    """Schema completo para criação (com user_id injetado pelo router)."""
    user_id: int  # Obrigatório após injetar no router


class InvestimentoCenarioUpdate(BaseModel):
    """Schema para atualização de cenário"""
    nome_cenario: Optional[str] = None
    descricao: Optional[str] = None
    patrimonio_inicial: Optional[Decimal] = None
    rendimento_mensal_pct: Optional[Decimal] = None
    aporte_mensal: Optional[Decimal] = None
    periodo_meses: Optional[int] = None
    ativo: Optional[bool] = None
    idade_atual: Optional[int] = None
    idade_aposentadoria: Optional[int] = None
    renda_mensal_alvo: Optional[Decimal] = None
    inflacao_aa: Optional[Decimal] = None
    retorno_aa: Optional[Decimal] = None
    anomes_inicio: Optional[int] = None
    principal: Optional[bool] = None
    extras_json: Optional[str] = None


class InvestimentoCenarioResponse(InvestimentoCenarioBase):
    """Schema de resposta de cenário"""
    id: int
    user_id: int
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime]
    aportes_extraordinarios: List[AporteExtraordinarioResponse] = []
    idade_atual: Optional[int] = None
    idade_aposentadoria: Optional[int] = None
    renda_mensal_alvo: Optional[Decimal] = None
    inflacao_aa: Optional[Decimal] = None
    retorno_aa: Optional[Decimal] = None
    anomes_inicio: Optional[int] = None
    principal: Optional[bool] = None
    extras_json: Optional[str] = None

    class Config:
        from_attributes = True


class CenarioProjecaoItem(BaseModel):
    """Item de projeção mensal"""
    mes_num: int
    anomes: int
    patrimonio: Decimal
    aporte: Decimal = Field(default=Decimal('0'), description='Aporte planejado do mês (usado como meta/plano)')


# ============================================================================
# PLANEJAMENTO SCHEMAS
# ============================================================================

class InvestimentoPlanejamentoBase(BaseModel):
    """Schema base para planejamento mensal"""
    ano: int = Field(..., ge=2000, le=2100)
    mes: int = Field(..., ge=1, le=12)
    anomes: int = Field(..., ge=200001, le=210012)
    meta_aporte_mensal: Optional[Decimal] = None
    meta_rendimento_pct: Optional[Decimal] = None
    meta_patrimonio: Optional[Decimal] = None
    aporte_realizado: Optional[Decimal] = None
    rendimento_realizado: Optional[Decimal] = None
    patrimonio_realizado: Optional[Decimal] = None


class InvestimentoPlanejamentoCreate(InvestimentoPlanejamentoBase):
    """Schema para criação de planejamento"""
    user_id: int


class InvestimentoPlanejamentoUpdate(BaseModel):
    """Schema para atualização de planejamento"""
    meta_aporte_mensal: Optional[Decimal] = None
    meta_rendimento_pct: Optional[Decimal] = None
    meta_patrimonio: Optional[Decimal] = None
    aporte_realizado: Optional[Decimal] = None
    rendimento_realizado: Optional[Decimal] = None
    patrimonio_realizado: Optional[Decimal] = None


class InvestimentoPlanejamentoResponse(InvestimentoPlanejamentoBase):
    """Schema de resposta de planejamento"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# SCHEMAS AGREGADOS/CONSULTA
# ============================================================================

class InvestimentoComHistorico(InvestimentoPortfolioResponse):
    """Investimento com histórico completo"""
    historico: List[InvestimentoHistoricoResponse] = []


class PortfolioResumo(BaseModel):
    """Resumo consolidado do portfólio"""
    total_investido: Decimal
    valor_atual: Decimal
    rendimento_total: Decimal
    rendimento_percentual: float
    quantidade_produtos: int
    produtos_ativos: int


class RendimentoMensal(BaseModel):
    """Rendimento de um mês específico"""
    ano: int
    mes: int
    anomes: int
    rendimento_mes: Decimal
    patrimonio_final: Decimal
    aporte_mes: Decimal


class PatrimonioMensal(BaseModel):
    """Patrimônio (ativos, passivos, PL) de um mês específico"""
    ano: int
    mes: int
    anomes: int
    ativos: float
    passivos: float
    patrimonio_liquido: float


class ProjecaoCenario(BaseModel):
    """Projeção mensal de um cenário"""
    mes: int
    patrimonio: Decimal
    rendimento_mes: Decimal
    aporte_mes: Decimal
    aporte_extraordinario: Decimal


class SimulacaoCompleta(BaseModel):
    """Simulação completa com todas as projeções"""
    cenario: InvestimentoCenarioResponse
    projecoes: List[ProjecaoCenario]
    patrimonio_final: Decimal
    rendimento_total: Decimal
    total_aportes: Decimal
