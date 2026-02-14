"""
Domínio Marcações - Router
Endpoints HTTP para marcações (grupos e subgrupos)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import MarcacaoService
from .schemas import (
    MarcacaoCreate,
    MarcacaoResponse,
    MarcacaoListResponse,
    SubgrupoCreate,
    SubgrupoResponse,
    GrupoComSubgrupos,
    GrupoComSubgrupoCreate
)

router = APIRouter(prefix="/marcacoes", tags=["marcacoes"])


@router.get("/", response_model=MarcacaoListResponse)
def list_marcacoes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista todas as marcações (grupo + subgrupo)"""
    service = MarcacaoService(db)
    return service.list_marcacoes()


@router.get("/grupos-com-subgrupos", response_model=List[GrupoComSubgrupos])
def get_grupos_com_subgrupos(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna todos os grupos com seus subgrupos"""
    service = MarcacaoService(db)
    return service.get_grupos_com_subgrupos()


@router.get("/grupos/{grupo}", response_model=List[MarcacaoResponse])
def get_marcacoes_by_grupo(
    grupo: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista marcações de um grupo específico"""
    service = MarcacaoService(db)
    return service.get_marcacoes_by_grupo(grupo)


@router.post("/grupos", status_code=201)
def create_grupo_com_subgrupo(
    data: GrupoComSubgrupoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Cria GRUPO em base_grupos_config E primeiro subgrupo em base_marcacoes.
    Operação atômica: se falhar, nada é criado.
    """
    service = MarcacaoService(db)
    return service.create_grupo_com_subgrupo(
        grupo=data.grupo,
        subgrupo=data.subgrupo,
        tipo_gasto=data.tipo_gasto,
        categoria_geral=data.categoria_geral
    )


@router.post("/grupos/{grupo}/subgrupos", response_model=SubgrupoResponse)
def create_subgrupo(
    grupo: str,
    subgrupo_data: SubgrupoCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Cria novo subgrupo para um grupo existente.
    Busca tipo_gasto e categoria de base_grupos_config automaticamente.
    """
    service = MarcacaoService(db)
    return service.create_subgrupo(grupo, subgrupo_data)


@router.delete("/grupos/{grupo}/subgrupos/{subgrupo}")
def delete_subgrupo(
    grupo: str,
    subgrupo: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Exclui subgrupo específico"""
    service = MarcacaoService(db)
    return service.delete_subgrupo(grupo, subgrupo)
