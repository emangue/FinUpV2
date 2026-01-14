"""
Domínio Grupos - Router
Endpoints HTTP para configuração de grupos
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import GrupoService
from .schemas import GrupoCreate, GrupoUpdate, GrupoResponse, GrupoListResponse

router = APIRouter(prefix="/grupos", tags=["grupos"])


@router.get("/", response_model=GrupoListResponse)
def list_grupos(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista todos os grupos configurados"""
    service = GrupoService(db)
    return service.list_grupos()


@router.get("/opcoes")
def get_opcoes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna opções disponíveis para formulários"""
    service = GrupoService(db)
    return service.get_opcoes()


@router.get("/{grupo_id}", response_model=GrupoResponse)
def get_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca grupo por ID"""
    service = GrupoService(db)
    return service.get_grupo(grupo_id)


@router.post("/", response_model=GrupoResponse)
def create_grupo(
    grupo_data: GrupoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria novo grupo"""
    service = GrupoService(db)
    return service.create_grupo(grupo_data)


@router.put("/{grupo_id}", response_model=GrupoResponse)
def update_grupo(
    grupo_id: int,
    grupo_data: GrupoUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza grupo existente"""
    service = GrupoService(db)
    return service.update_grupo(grupo_id, grupo_data)


@router.delete("/{grupo_id}")
def delete_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Exclui grupo"""
    service = GrupoService(db)
    return service.delete_grupo(grupo_id)