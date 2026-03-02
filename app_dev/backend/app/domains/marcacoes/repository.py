"""
Domínio Marcações - Repository
Acesso a dados para marcações (grupos e subgrupos)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domains.categories.models import BaseMarcacao  # Importar modelo existente
from .schemas import MarcacaoCreate
from app.domains.grupos.models import BaseGruposConfig


class MarcacaoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, user_id: int) -> List[dict]:
        """Busca todas as marcações do usuário com config do grupo (JOIN)"""
        results = (
            self.db.query(
                BaseMarcacao.id,
                BaseMarcacao.GRUPO,
                BaseMarcacao.SUBGRUPO,
                BaseGruposConfig.tipo_gasto_padrao.label('tipo_gasto'),
                BaseGruposConfig.categoria_geral
            )
            .join(
                BaseGruposConfig,
                (BaseMarcacao.GRUPO == BaseGruposConfig.nome_grupo)
                & (BaseMarcacao.user_id == BaseGruposConfig.user_id),
            )
            .filter(BaseMarcacao.user_id == user_id)
            .order_by(BaseMarcacao.GRUPO, BaseMarcacao.SUBGRUPO)
            .all()
        )
        return [{
            'id': r.id,
            'grupo': r.GRUPO,
            'subgrupo': r.SUBGRUPO,
            'tipo_gasto': r.tipo_gasto,
            'categoria_geral': r.categoria_geral
        } for r in results]

    def get_by_grupo(self, user_id: int, grupo: str) -> List[dict]:
        """Busca todas as marcações de um grupo específico do usuário (com config do grupo)"""
        results = (
            self.db.query(
                BaseMarcacao.id,
                BaseMarcacao.GRUPO,
                BaseMarcacao.SUBGRUPO,
                BaseGruposConfig.tipo_gasto_padrao.label('tipo_gasto'),
                BaseGruposConfig.categoria_geral
            )
            .join(
                BaseGruposConfig,
                (BaseMarcacao.GRUPO == BaseGruposConfig.nome_grupo)
                & (BaseMarcacao.user_id == BaseGruposConfig.user_id),
            )
            .filter(BaseMarcacao.user_id == user_id, BaseMarcacao.GRUPO == grupo)
            .order_by(BaseMarcacao.SUBGRUPO)
            .all()
        )
        return [{'id': r.id, 'grupo': r.GRUPO, 'subgrupo': r.SUBGRUPO, 'tipo_gasto': r.tipo_gasto, 'categoria_geral': r.categoria_geral} for r in results]

    def get_by_grupo_subgrupo(self, user_id: int, grupo: str, subgrupo: str) -> Optional[BaseMarcacao]:
        """Busca marcação específica por grupo + subgrupo do usuário"""
        return (
            self.db.query(BaseMarcacao)
            .filter(
                BaseMarcacao.user_id == user_id,
                BaseMarcacao.GRUPO == grupo,
                BaseMarcacao.SUBGRUPO == subgrupo,
            )
            .first()
        )

    def get_grupos_unicos(self, user_id: int) -> List[str]:
        """Retorna lista de grupos únicos do usuário"""
        result = (
            self.db.query(BaseMarcacao.GRUPO)
            .filter(BaseMarcacao.user_id == user_id)
            .distinct()
            .order_by(BaseMarcacao.GRUPO)
            .all()
        )
        return [r[0] for r in result]

    def get_subgrupos_by_grupo(self, user_id: int, grupo: str) -> List[str]:
        """Retorna lista de subgrupos de um grupo do usuário"""
        result = (
            self.db.query(BaseMarcacao.SUBGRUPO)
            .filter(BaseMarcacao.user_id == user_id, BaseMarcacao.GRUPO == grupo)
            .distinct()
            .order_by(BaseMarcacao.SUBGRUPO)
            .all()
        )
        return [r[0] for r in result]

    def get_grupo_config(self, user_id: int, nome_grupo: str) -> Optional[BaseGruposConfig]:
        """Busca configuração do grupo em base_grupos_config do usuário"""
        return (
            self.db.query(BaseGruposConfig)
            .filter(
                BaseGruposConfig.user_id == user_id,
                BaseGruposConfig.nome_grupo == nome_grupo,
            )
            .first()
        )

    def create_marcacao(self, user_id: int, grupo: str, subgrupo: str) -> BaseMarcacao:
        """Cria nova marcação para o usuário"""
        marcacao = BaseMarcacao(user_id=user_id, GRUPO=grupo, SUBGRUPO=subgrupo)
        self.db.add(marcacao)
        self.db.commit()
        self.db.refresh(marcacao)
        return marcacao
    
    def delete_marcacao(self, user_id: int, grupo: str, subgrupo: str) -> bool:
        """Exclui marcação específica do usuário"""
        marcacao = self.get_by_grupo_subgrupo(user_id, grupo, subgrupo)
        if not marcacao:
            return False
        
        self.db.delete(marcacao)
        self.db.commit()
        return True
    
    def count_transacoes_by_marcacao(self, user_id: int, grupo: str, subgrupo: str) -> int:
        """Conta quantas transações do usuário usam esta marcação"""
        from app.domains.transactions.models import JournalEntry
        return self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Grupo == grupo,
            JournalEntry.Subgrupo == subgrupo
        ).scalar() or 0
