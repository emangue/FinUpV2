from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from .schemas import ExclusaoCreate, ExclusaoUpdate, ExclusaoResponse
from .service import ExclusaoService

router = APIRouter(prefix="/exclusoes", tags=["exclusoes"])


def get_current_user_id():
    """Mock - retorna user_id fixo para desenvolvimento"""
    return 1


@router.get("/", response_model=dict)
def list_exclusoes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExclusaoService(db)
    exclusoes = service.get_all_exclusoes(user_id)
    return {"exclusoes": exclusoes}


@router.post("/", response_model=ExclusaoResponse, status_code=201)
def create_exclusao(
    exclusao: ExclusaoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExclusaoService(db)
    return service.create_exclusao(exclusao, user_id)


@router.put("/{exclusao_id}", response_model=ExclusaoResponse)
def update_exclusao(
    exclusao_id: int,
    exclusao: ExclusaoUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExclusaoService(db)
    try:
        return service.update_exclusao(exclusao_id, exclusao, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{exclusao_id}", status_code=204)
def delete_exclusao(
    exclusao_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExclusaoService(db)
    if not service.delete_exclusao(exclusao_id, user_id):
        raise HTTPException(status_code=404, detail="Exclusão não encontrada")
    return None
