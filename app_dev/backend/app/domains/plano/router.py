"""Router do domínio Plano"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id

from .service import PlanoService
from .schemas import RendaUpdate, MetaCreate

router = APIRouter(prefix="/plano", tags=["plano"])


@router.post("/renda")
def atualizar_renda(
    data: RendaUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Upsert renda mensal líquida no perfil financeiro"""
    service = PlanoService(db)
    return service.upsert_renda(user_id, data.renda_mensal_liquida)


@router.get("/renda")
def obter_renda(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna renda declarada ou null"""
    service = PlanoService(db)
    renda = service.get_renda(user_id)
    return {"renda": renda}


@router.get("/resumo")
def resumo_plano(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """A.07: Retorna renda, total_budget, disponivel_real (renda - total budget)"""
    service = PlanoService(db)
    return service.get_resumo(user_id, ano, mes)


@router.get("/impacto-longo-prazo")
def impacto_longo_prazo(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Anos perdidos quando gasto/plano > renda. Retorna null quando sem déficit."""
    service = PlanoService(db)
    result = service.get_impacto_longo_prazo(user_id, ano, mes)
    return result if result else {}


@router.get("/orcamento")
def orcamento_por_categoria(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna gasto real vs meta por grupo para o mês"""
    service = PlanoService(db)
    return service.get_orcamento(user_id, ano, mes)


@router.post("/metas/{grupo}")
def salvar_meta(
    grupo: str,
    data: MetaCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Salva meta de gasto para um grupo no mês"""
    service = PlanoService(db)
    return service.salvar_meta(user_id, grupo, data.valor_meta, data.ano, data.mes)
