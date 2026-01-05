"""
Domínio Categories - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional, List
from .models import BaseMarcacao

class CategoryRepository:
    """
    Repository pattern para categorias
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: int) -> Optional[BaseMarcacao]:
        """Busca categoria por ID"""
        return self.db.query(BaseMarcacao).filter(
            BaseMarcacao.id == category_id
        ).first()
    
    def list_all(self) -> List[BaseMarcacao]:
        """Lista todas as categorias"""
        return self.db.query(BaseMarcacao).order_by(
            BaseMarcacao.GRUPO,
            BaseMarcacao.SUBGRUPO
        ).all()
    
    def count_all(self) -> int:
        """Conta total de categorias"""
        return self.db.query(func.count(BaseMarcacao.id)).scalar()
    
    def find_duplicate(
        self,
        grupo: str,
        subgrupo: str,
        tipo_gasto: str,
        exclude_id: Optional[int] = None
    ) -> Optional[BaseMarcacao]:
        """Busca categoria duplicada"""
        query = self.db.query(BaseMarcacao).filter(
            BaseMarcacao.GRUPO == grupo,
            BaseMarcacao.SUBGRUPO == subgrupo,
            BaseMarcacao.TipoGasto == tipo_gasto
        )
        
        if exclude_id:
            query = query.filter(BaseMarcacao.id != exclude_id)
        
        return query.first()
    
    def get_distinct_grupos(self) -> List[str]:
        """Retorna lista de GRUPOs únicos"""
        result = self.db.query(distinct(BaseMarcacao.GRUPO)).all()
        return [r[0] for r in result]
    
    def get_subgrupos_by_grupo(self, grupo: str) -> List[str]:
        """Retorna SUBGRUPOs de um GRUPO específico"""
        result = self.db.query(distinct(BaseMarcacao.SUBGRUPO)).filter(
            BaseMarcacao.GRUPO == grupo
        ).all()
        return [r[0] for r in result]
    
    def get_tipos_gasto_by_grupo(self, grupo: str) -> List[str]:
        """Retorna TipoGasto de um GRUPO específico"""
        result = self.db.query(distinct(BaseMarcacao.TipoGasto)).filter(
            BaseMarcacao.GRUPO == grupo
        ).all()
        return [r[0] for r in result]
    
    def create(self, category: BaseMarcacao) -> BaseMarcacao:
        """Cria nova categoria"""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def update(self, category: BaseMarcacao) -> BaseMarcacao:
        """Atualiza categoria existente"""
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete(self, category: BaseMarcacao) -> None:
        """Deleta categoria"""
        self.db.delete(category)
        self.db.commit()
