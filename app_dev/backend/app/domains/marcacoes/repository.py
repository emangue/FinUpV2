"""
Domínio Marcações - Repository
Acesso a dados para marcações (grupos e subgrupos)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import BaseMarcacao
from .schemas import MarcacaoCreate
from app.domains.grupos.models import BaseGruposConfig


class MarcacaoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[BaseMarcacao]:
        """Busca todas as marcações (grupo + subgrupo)"""
        return self.db.query(BaseMarcacao).order_by(BaseMarcacao.GRUPO, BaseMarcacao.SUBGRUPO).all()
    
    def get_by_grupo(self, grupo: str) -> List[BaseMarcacao]:
        """Busca todas as marcações de um grupo específico"""
        return self.db.query(BaseMarcacao).filter(BaseMarcacao.GRUPO == grupo).order_by(BaseMarcacao.SUBGRUPO).all()
    
    def get_by_grupo_subgrupo(self, grupo: str, subgrupo: str) -> Optional[BaseMarcacao]:
        """Busca marcação específica por grupo + subgrupo"""
        return self.db.query(BaseMarcacao).filter(
            BaseMarcacao.GRUPO == grupo,
            BaseMarcacao.SUBGRUPO == subgrupo
        ).first()
    
    def get_grupos_unicos(self) -> List[str]:
        """Retorna lista de grupos únicos"""
        result = self.db.query(BaseMarcacao.GRUPO).distinct().order_by(BaseMarcacao.GRUPO).all()
        return [r[0] for r in result]
    
    def get_subgrupos_by_grupo(self, grupo: str) -> List[str]:
        """Retorna lista de subgrupos de um grupo"""
        result = self.db.query(BaseMarcacao.SUBGRUPO).filter(
            BaseMarcacao.GRUPO == grupo
        ).distinct().order_by(BaseMarcacao.SUBGRUPO).all()
        return [r[0] for r in result]
    
    def get_grupo_config(self, nome_grupo: str) -> Optional[BaseGruposConfig]:
        """Busca configuração do grupo em base_grupos_config"""
        return self.db.query(BaseGruposConfig).filter(
            BaseGruposConfig.nome_grupo == nome_grupo
        ).first()
    
    def create_marcacao(self, grupo: str, subgrupo: str, tipo_gasto: str, categoria_geral: str) -> BaseMarcacao:
        """Cria nova marcação (grupo + subgrupo)"""
        marcacao = BaseMarcacao(
            GRUPO=grupo,
            SUBGRUPO=subgrupo,
            TipoGasto=tipo_gasto,
            CategoriaGeral=categoria_geral
        )
        self.db.add(marcacao)
        self.db.commit()
        self.db.refresh(marcacao)
        return marcacao
    
    def delete_marcacao(self, grupo: str, subgrupo: str) -> bool:
        """Exclui marcação específica"""
        marcacao = self.get_by_grupo_subgrupo(grupo, subgrupo)
        if not marcacao:
            return False
        
        self.db.delete(marcacao)
        self.db.commit()
        return True
    
    def count_transacoes_by_marcacao(self, grupo: str, subgrupo: str) -> int:
        """Conta quantas transações usam esta marcação"""
        from app.domains.transactions.models import JournalEntry
        return self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.Grupo == grupo,
            JournalEntry.Subgrupo == subgrupo
        ).scalar() or 0
