from sqlalchemy.orm import Session
from typing import List, Optional
from .models import TransacaoExclusao
from .schemas import ExclusaoCreate, ExclusaoUpdate


class ExclusaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int) -> List[TransacaoExclusao]:
        return (
            self.db.query(TransacaoExclusao)
            .filter(TransacaoExclusao.user_id == user_id)
            .filter(TransacaoExclusao.ativo == 1)
            .all()
        )

    def get_by_id(self, exclusao_id: int, user_id: int) -> Optional[TransacaoExclusao]:
        return (
            self.db.query(TransacaoExclusao)
            .filter(TransacaoExclusao.id == exclusao_id)
            .filter(TransacaoExclusao.user_id == user_id)
            .first()
        )

    def create(self, exclusao: ExclusaoCreate, user_id: int) -> TransacaoExclusao:
        db_exclusao = TransacaoExclusao(
            nome_transacao=exclusao.nome_transacao,
            banco=exclusao.banco,
            tipo_documento=exclusao.tipo_documento,
            descricao=exclusao.descricao,
            acao=exclusao.acao,
            user_id=user_id,
            ativo=1,
        )
        self.db.add(db_exclusao)
        self.db.commit()
        self.db.refresh(db_exclusao)
        return db_exclusao

    def update(
        self, exclusao_id: int, exclusao: ExclusaoUpdate, user_id: int
    ) -> Optional[TransacaoExclusao]:
        db_exclusao = self.get_by_id(exclusao_id, user_id)
        if not db_exclusao:
            return None

        update_data = exclusao.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_exclusao, field, value)

        self.db.commit()
        self.db.refresh(db_exclusao)
        return db_exclusao

    def delete(self, exclusao_id: int, user_id: int) -> bool:
        db_exclusao = self.get_by_id(exclusao_id, user_id)
        if not db_exclusao:
            return False

        db_exclusao.ativo = 0
        self.db.commit()
        return True
