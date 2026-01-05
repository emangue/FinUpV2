"""
Domínio Categories - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import CategoryService
from .schemas import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryListResponse,
    CategoryGrouped
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=CategoryListResponse)
def list_categories(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todas as categorias
    """
    service = CategoryService(db)
    return service.list_categories()

@router.get("/grouped", response_model=List[CategoryGrouped])
def list_grouped_categories(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista categorias agrupadas por GRUPO
    """
    service = CategoryService(db)
    return service.list_grouped_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Busca categoria por ID
    """
    service = CategoryService(db)
    return service.get_category(category_id)

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria nova categoria
    """
    service = CategoryService(db)
    return service.create_category(category)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    update_data: CategoryUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza categoria
    """
    service = CategoryService(db)
    return service.update_category(category_id, update_data)

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deleta categoria
    """
    service = CategoryService(db)
    return service.delete_category(category_id)
