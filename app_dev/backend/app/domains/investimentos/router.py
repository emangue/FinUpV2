"""
Router do domínio Investimentos.
Endpoints FastAPI isolados aqui.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
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


@router.get("/", response_model=List[schemas.InvestimentoPortfolioResponse])
def list_investimentos(
    tipo_investimento: Optional[str] = Query(None, description="Filtrar por tipo"),
    ativo: Optional[bool] = Query(True, description="Apenas ativos"),
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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna distribuição do portfólio por tipo de investimento"""
    service = InvestimentoService(db)
    return service.get_distribuicao_por_tipo(user_id)


@router.get("/{investimento_id}", response_model=schemas.InvestimentoPortfolioResponse)
def get_investimento(
    investimento_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca investimento por ID"""
    service = InvestimentoService(db)
    investimento = service.get_investimento(investimento_id, user_id)

    if not investimento:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")

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


# ============================================================================
# CENARIOS & SIMULACAO ENDPOINTS
# ============================================================================

@router.post("/cenarios", response_model=schemas.InvestimentoCenarioResponse, status_code=201)
def create_cenario(
    data: schemas.InvestimentoCenarioCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria novo cenário de simulação"""
    data.user_id = user_id
    service = InvestimentoService(db)
    return service.create_cenario(data)


@router.get("/cenarios", response_model=List[schemas.InvestimentoCenarioResponse])
def list_cenarios(
    ativo: Optional[bool] = Query(True, description="Apenas cenários ativos"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista cenários do usuário"""
    service = InvestimentoService(db)
    return service.list_cenarios(user_id, ativo)


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
