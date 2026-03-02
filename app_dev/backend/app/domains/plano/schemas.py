"""Schemas do domínio Plano"""
from pydantic import BaseModel, Field
from typing import Optional


class RendaUpdate(BaseModel):
    renda_mensal_liquida: float = Field(..., ge=0)


class PerfilUpdate(BaseModel):
    """PUT /plano/perfil - renda, aporte, idade, aposentadoria, patrimônio, taxa"""
    renda_mensal_liquida: Optional[float] = Field(None, ge=0)
    aporte_planejado: Optional[float] = Field(None, ge=0)
    idade_atual: Optional[int] = Field(None, ge=18, le=120)
    idade_aposentadoria: Optional[int] = Field(None, ge=18, le=120)
    patrimonio_atual: Optional[float] = Field(None, ge=0)
    taxa_retorno_anual: Optional[float] = Field(None, ge=0, le=1)
    crescimento_renda: Optional[float] = Field(None, ge=0, le=100)  # % a.a.
    reajuste_mes: Optional[int] = Field(None, ge=1, le=12)
    reajuste_ano: Optional[int] = Field(None, ge=2000, le=2100)
    crescimento_gastos: Optional[float] = Field(None, ge=0, le=100)  # % a.a. inflação dos gastos


class OrcamentoItem(BaseModel):
    grupo: str
    gasto: float
    meta: Optional[float]
    percentual: Optional[float]
    status: str  # ok, alerta, excedido


class MetaCreate(BaseModel):
    valor_meta: float = Field(..., ge=0)
    ano: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)


class ExpectativaCreate(BaseModel):
    """POST /plano/expectativas"""
    descricao: str = Field(..., max_length=200)
    valor: float = Field(..., ge=0)
    grupo: Optional[str] = Field(None, max_length=100)
    subgrupo: Optional[str] = Field(None, max_length=100)
    tipo_lancamento: str = Field("debito", pattern="^(debito|credito)$")
    mes_referencia: str = Field(..., pattern=r"^\d{4}-\d{2}$")  # YYYY-MM (mês de início)
    tipo_expectativa: str = Field("sazonal_plano", pattern="^(sazonal_plano|renda_plano|parcela_futura)$")
    recorrencia: Optional[str] = Field("unico", pattern="^(unico|bimestral|trimestral|semestral|anual)$")
    parcelas: Optional[int] = Field(1, ge=1, le=24)  # 1 = à vista, 2-24 = parcelado
    # Evolução anual do valor (para recorrências como anual/semestral)
    evoluir: Optional[bool] = Field(False)
    evolucao_valor: Optional[float] = Field(None, ge=0)  # valor do incremento (% ou R$)
    evolucao_tipo: Optional[str] = Field("percentual", pattern="^(percentual|nominal)$")


class ExpectativaResponse(BaseModel):
    id: int
    descricao: Optional[str]
    valor: float
    grupo: Optional[str]
    tipo_lancamento: str
    mes_referencia: str
    tipo_expectativa: str
    status: str

    class Config:
        from_attributes = True
