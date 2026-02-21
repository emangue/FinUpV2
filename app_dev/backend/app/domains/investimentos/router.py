"""
Router do domínio Investimentos.
Endpoints FastAPI isolados aqui.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id, get_current_user_id
from .service import InvestimentoService
from . import schemas


router = APIRouter(prefix="/investimentos", tags=["Investimentos"])


# ============================================================================
# PORTFOLIO ENDPOINTS
# ============================================================================

@router.post("/", response_model=schemas.InvestimentoPortfolioResponse, status_code=201)
def create_investimento(
    data: schemas.InvestimentoPortfolioCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria novo investimento no portfólio"""
    data.user_id = user_id
    service = InvestimentoService(db)

    try:
        return service.create_investimento(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[schemas.InvestimentoComHistoricoResponse])
def list_investimentos(
    tipo_investimento: Optional[str] = Query(None, description="Filtrar por tipo"),
    ativo: Optional[bool] = Query(True, description="Apenas ativos"),
    anomes: Optional[int] = Query(None, description="Filtrar por mês (YYYYMM)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista investimentos do usuário"""
    service = InvestimentoService(db)
    return service.list_investimentos(
        user_id=user_id,
        tipo_investimento=tipo_investimento,
        ativo=ativo,
        anomes=anomes,
        skip=skip,
        limit=limit
    )


@router.get("/resumo", response_model=schemas.PortfolioResumo)
def get_portfolio_resumo(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna resumo consolidado do portfólio"""
    service = InvestimentoService(db)
    return service.get_portfolio_resumo(user_id)


@router.get("/distribuicao-tipo")
def get_distribuicao_por_tipo(
    classe_ativo: Optional[str] = Query(None, description="Filtrar por classe: Ativo ou Passivo"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna distribuição do portfólio por tipo de investimento"""
    service = InvestimentoService(db)
    return service.get_distribuicao_por_tipo(user_id, classe_ativo)


# Timeline - rotas específicas ANTES de /{investimento_id} para evitar conflito
@router.get("/timeline/rendimentos", response_model=List[schemas.RendimentoMensal])
def get_rendimentos_timeline(
    ano_inicio: int = Query(..., ge=2000, le=2100),
    ano_fim: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna série temporal de rendimentos mensais"""
    service = InvestimentoService(db)
    return service.get_rendimentos_timeline(user_id, ano_inicio, ano_fim)


@router.get("/timeline/patrimonio", response_model=List[schemas.PatrimonioMensal])
def get_patrimonio_timeline(
    ano_inicio: int = Query(..., ge=2000, le=2100),
    ano_fim: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna série temporal de ativos, passivos e PL por mês"""
    service = InvestimentoService(db)
    return service.get_patrimonio_timeline(user_id, ano_inicio, ano_fim)


@router.post("/copiar-mes-anterior")
def copiar_mes_anterior(
    anomes_destino: int = Query(..., description="Mês destino YYYYMM"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Copia todos investimentos do mês anterior para o mês destino"""
    service = InvestimentoService(db)
    count = service.copiar_mes_anterior(user_id, anomes_destino)
    return {"copiados": count, "anomes_destino": anomes_destino}


# ============================================================================
# CENARIOS - Rotas ANTES de /{investimento_id} para evitar conflito (cenarios ≠ id)
# ============================================================================

@router.post("/cenarios", response_model=schemas.InvestimentoCenarioResponse, status_code=201)
def create_cenario(
    data: schemas.InvestimentoCenarioCreateIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria novo cenário de simulação. user_id vem do token de autenticação."""
    full_data = schemas.InvestimentoCenarioCreate(**data.model_dump(), user_id=user_id)
    service = InvestimentoService(db)
    return service.create_cenario(full_data)


@router.get("/cenarios", response_model=List[schemas.InvestimentoCenarioResponse])
def list_cenarios(
    ativo: Optional[str] = Query(default="true", description="Apenas cenários ativos (true/false)"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista cenários do usuário"""
    ativo_bool = ativo.lower() in ("true", "1", "yes") if ativo else True
    service = InvestimentoService(db)
    return service.list_cenarios(user_id, ativo_bool)


@router.get("/cenarios/principal/aporte-mes")
def get_aporte_principal_por_mes(
    year: int = Query(..., description="Ano (ex: 2026)"),
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Retorna aporte planejado (regular + extraordinário) do cenário principal para o mês.
    Usa CenarioProjecao quando disponível (inclui aportes extraordinários).
    """
    service = InvestimentoService(db)
    aporte = service.get_aporte_principal_por_mes(user_id, year, month)
    return {"aporte": aporte if aporte is not None else 0}


@router.get("/cenarios/principal/aporte-periodo")
def get_aporte_principal_periodo(
    year: int = Query(..., description="Ano (ex: 2026)"),
    ytd_month: Optional[int] = Query(None, ge=1, le=12, description="YTD: mês limite (1-12). Se None, ano inteiro"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Soma aportes planejados do cenário principal para ano ou YTD (Jan..ytd_month).
    """
    service = InvestimentoService(db)
    aporte = service.get_aporte_principal_periodo(user_id, year, ytd_month)
    return {"aporte": aporte if aporte is not None else 0}


@router.get("/cenarios/{cenario_id}/simular", response_model=schemas.SimulacaoCompleta)
def simular_cenario(
    cenario_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Executa simulação completa de um cenário"""
    service = InvestimentoService(db)
    simulacao = service.simular_cenario(cenario_id, user_id)

    if not simulacao:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")

    return simulacao


@router.get("/cenarios/{cenario_id}/projecao")
def get_cenario_projecao(
    cenario_id: int,
    recalc: bool = Query(False, description="Forçar recálculo da projeção"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna projeção mês a mês do cenário"""
    service = InvestimentoService(db)
    return service.get_projecao(cenario_id, user_id, force_recalc=recalc)


@router.get("/cenarios/{cenario_id}", response_model=schemas.InvestimentoCenarioResponse)
def get_cenario(
    cenario_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca cenário por ID (para edição)"""
    service = InvestimentoService(db)
    cenario = service.get_cenario(cenario_id, user_id)
    if not cenario:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    return cenario


@router.put("/cenarios/{cenario_id}", response_model=schemas.InvestimentoCenarioResponse)
def update_cenario(
    cenario_id: int,
    data: schemas.InvestimentoCenarioUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza cenário e recalcula projeção mês a mês"""
    service = InvestimentoService(db)
    cenario = service.update_cenario(cenario_id, user_id, data)
    if not cenario:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")
    return cenario


@router.delete("/cenarios/{cenario_id}", status_code=204)
def delete_cenario(
    cenario_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Deleta cenário (soft delete)"""
    service = InvestimentoService(db)
    ok = service.delete_cenario(cenario_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cenário não encontrado")


# ============================================================================
# PORTFOLIO BY ID (rotas genéricas por último)
# ============================================================================

@router.get("/{investimento_id}", response_model=schemas.InvestimentoComHistoricoResponse)
def get_investimento(
    investimento_id: int,
    anomes: Optional[int] = Query(None, description="Mês (YYYYMM) para retornar valores do histórico"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca investimento por ID. Se anomes informado, inclui valor_total_mes, valor_unitario_mes, quantidade_mes."""
    service = InvestimentoService(db)
    investimento = service.get_investimento(investimento_id, user_id, anomes)

    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")

    # Garantir resposta como InvestimentoComHistoricoResponse
    if isinstance(investimento, schemas.InvestimentoPortfolioResponse):
        return schemas.InvestimentoComHistoricoResponse(
            **investimento.model_dump(),
            valor_total_mes=None,
            valor_unitario_mes=None,
            quantidade_mes=None,
        )
    return investimento


@router.patch("/{investimento_id}", response_model=schemas.InvestimentoPortfolioResponse)
def update_investimento(
    investimento_id: int,
    data: schemas.InvestimentoPortfolioUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza investimento"""
    service = InvestimentoService(db)
    investimento = service.update_investimento(investimento_id, user_id, data)

    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")

    return investimento


@router.delete("/{investimento_id}", status_code=204)
def delete_investimento(
    investimento_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Deleta investimento (soft delete)"""
    service = InvestimentoService(db)
    success = service.delete_investimento(investimento_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")


# ============================================================================
# HISTORICO ENDPOINTS
# ============================================================================

@router.get("/historico/ultimo", response_model=schemas.InvestimentoHistoricoResponse)
def get_ultimo_historico(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca o último registro de histórico (patrimônio mais recente)"""
    service = InvestimentoService(db)
    ultimo = service.get_ultimo_historico(user_id)
    
    if not ultimo:
        raise HTTPException(status_code=404, detail="Nenhum histórico encontrado")
    
    return ultimo


@router.post("/historico", response_model=schemas.InvestimentoHistoricoResponse, status_code=201)
def add_historico(
    data: schemas.InvestimentoHistoricoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Adiciona registro de histórico mensal"""
    service = InvestimentoService(db)
    return service.add_historico(data)


@router.get("/{investimento_id}/historico", response_model=List[schemas.InvestimentoHistoricoResponse])
def get_historico_investimento(
    investimento_id: int,
    ano_inicio: Optional[int] = Query(None, ge=2000, le=2100),
    ano_fim: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca histórico de um investimento"""
    service = InvestimentoService(db)
    return service.get_historico_investimento(
        investimento_id, user_id, ano_inicio, ano_fim
    )


@router.patch("/{investimento_id}/historico/{anomes}", response_model=schemas.InvestimentoHistoricoResponse)
def update_historico_mes(
    investimento_id: int,
    anomes: int = Path(..., ge=200001, le=210012, description="Mês no formato YYYYMM"),
    data: schemas.InvestimentoHistoricoUpdate = Body(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza valores do histórico (patrimônio) de um investimento para um mês específico."""
    service = InvestimentoService(db)
    historico = service.update_historico_mes(investimento_id, anomes, user_id, data)

    if not historico:
        raise HTTPException(
            status_code=404,
            detail="Investimento ou histórico do mês não encontrado"
        )

    return historico


@router.delete("/{investimento_id}/historico/{anomes}", status_code=204)
def delete_historico_mes(
    investimento_id: int,
    anomes: int = Path(..., ge=200001, le=210012, description="Mês no formato YYYYMM"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Remove o investimento deste mês (apaga registro do histórico)."""
    service = InvestimentoService(db)
    ok = service.delete_historico_mes(investimento_id, anomes, user_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Investimento ou histórico do mês não encontrado"
        )


# ============================================================================
# PLANEJAMENTO ENDPOINTS
# ============================================================================

@router.post("/planejamento", response_model=schemas.InvestimentoPlanejamentoResponse)
def upsert_planejamento(
    data: schemas.InvestimentoPlanejamentoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria ou atualiza planejamento mensal"""
    data.user_id = user_id
    service = InvestimentoService(db)
    return service.upsert_planejamento(data)


@router.get("/planejamento", response_model=List[schemas.InvestimentoPlanejamentoResponse])
def get_planejamento_periodo(
    ano_inicio: int = Query(..., ge=2000, le=2100),
    ano_fim: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista planejamento por período"""
    service = InvestimentoService(db)
    return service.get_planejamento_periodo(user_id, ano_inicio, ano_fim)
