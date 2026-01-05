"""
Domínio Categories - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status

from .repository import CategoryRepository
from .models import BaseMarcacao
from .schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryGrouped
)

class CategoryService:
    """
    Service layer para categorias
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)
    
    def get_category(self, category_id: int) -> CategoryResponse:
        """
        Busca uma categoria por ID
        
        Raises:
            HTTPException: Se categoria não encontrada
        """
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria com ID {category_id} não encontrada"
            )
        return CategoryResponse.from_orm(category)
    
    def list_categories(self) -> CategoryListResponse:
        """
        Lista todas as categorias
        """
        categories = self.repository.list_all()
        total = self.repository.count_all()
        
        return CategoryListResponse(
            categories=[CategoryResponse.from_orm(c) for c in categories],
            total=total
        )
    
    def list_grouped_categories(self) -> List[CategoryGrouped]:
        """
        Lista categorias agrupadas por GRUPO
        """
        grupos = self.repository.get_distinct_grupos()
        
        result = []
        for grupo in grupos:
            subgrupos = self.repository.get_subgrupos_by_grupo(grupo)
            tipos_gasto = self.repository.get_tipos_gasto_by_grupo(grupo)
            
            result.append(CategoryGrouped(
                grupo=grupo,
                subgrupos=subgrupos,
                tipos_gasto=tipos_gasto
            ))
        
        return result
    
    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """
        Cria nova categoria
        
        Lógica de negócio:
        - Verifica duplicatas
        
        Raises:
            HTTPException: Se categoria já existe
        """
        # Verificar duplicata
        existing = self.repository.find_duplicate(
            category_data.GRUPO,
            category_data.SUBGRUPO,
            category_data.TipoGasto
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria já existe com esses valores"
            )
        
        # Criar modelo
        category = BaseMarcacao(**category_data.dict())
        
        # Salvar
        created = self.repository.create(category)
        return CategoryResponse.from_orm(created)
    
    def update_category(
        self,
        category_id: int,
        update_data: CategoryUpdate
    ) -> CategoryResponse:
        """
        Atualiza categoria
        
        Raises:
            HTTPException: Se categoria não encontrada
        """
        # Buscar categoria
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria com ID {category_id} não encontrada"
            )
        
        # Aplicar mudanças (apenas campos não-None)
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        # Verificar duplicata após update
        if update_dict:
            existing = self.repository.find_duplicate(
                category.GRUPO,
                category.SUBGRUPO,
                category.TipoGasto,
                category_id
            )
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe outra categoria com esses valores"
                )
        
        # Salvar
        updated = self.repository.update(category)
        return CategoryResponse.from_orm(updated)
    
    def delete_category(self, category_id: int) -> dict:
        """
        Deleta categoria
        
        Raises:
            HTTPException: Se categoria não encontrada
        """
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoria com ID {category_id} não encontrada"
            )
        
        self.repository.delete(category)
        return {"message": "Categoria deletada com sucesso"}
