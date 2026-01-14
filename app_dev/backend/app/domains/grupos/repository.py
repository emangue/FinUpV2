"""
Domínio Grupos - Repository
Acesso a dados para configuração de grupos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import BaseGruposConfig
from .schemas import GrupoCreate, GrupoUpdate


class GrupoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[BaseGruposConfig]:
        """Busca todos os grupos configurados"""
        return self.db.query(BaseGruposConfig).order_by(BaseGruposConfig.nome_grupo).all()
    
    def get_by_id(self, grupo_id: int) -> Optional[BaseGruposConfig]:
        """Busca grupo por ID"""
        return self.db.query(BaseGruposConfig).filter(BaseGruposConfig.id == grupo_id).first()
    
    def get_by_nome(self, nome_grupo: str) -> Optional[BaseGruposConfig]:
        """Busca grupo por nome"""
        return self.db.query(BaseGruposConfig).filter(BaseGruposConfig.nome_grupo == nome_grupo).first()
    
    def create(self, grupo_data: GrupoCreate) -> BaseGruposConfig:
        """Cria novo grupo"""
        grupo = BaseGruposConfig(**grupo_data.model_dump())
        self.db.add(grupo)
        self.db.commit()
        self.db.refresh(grupo)
        return grupo
    
    def update(self, grupo_id: int, grupo_data: GrupoUpdate) -> Optional[BaseGruposConfig]:
        """Atualiza grupo existente"""
        grupo = self.get_by_id(grupo_id)
        if not grupo:
            return None
        
        update_data = grupo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grupo, field, value)
        
        self.db.commit()
        self.db.refresh(grupo)
        return grupo
    
    def delete(self, grupo_id: int) -> bool:
        """Exclui grupo"""
        grupo = self.get_by_id(grupo_id)
        if not grupo:
            return False
        
        self.db.delete(grupo)
        self.db.commit()
        return True
    
    def count_transacoes_by_grupo(self, nome_grupo: str) -> int:
        """Conta quantas transações usam este grupo"""
        from app.domains.transactions.models import JournalEntry
        return self.db.query(func.count(JournalEntry.id)).filter(JournalEntry.Grupo == nome_grupo).scalar() or 0
    
    def get_tipos_gasto_disponiveis(self) -> List[str]:
        """Retorna tipos de gasto únicos disponíveis"""
        return ["Fixo", "Ajustável"]
    
    def get_categorias_disponiveis(self) -> List[str]:
        """Retorna categorias gerais disponíveis"""
        return ["Despesa", "Receita", "Investimentos", "Transferência Entre Contas"]