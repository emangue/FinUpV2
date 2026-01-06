from sqlalchemy.orm import Session
from typing import List
from .repository import ExclusaoRepository
from .schemas import ExclusaoCreate, ExclusaoUpdate, ExclusaoResponse


class ExclusaoService:
    def __init__(self, db: Session):
        self.repository = ExclusaoRepository(db)

    def get_all_exclusoes(self, user_id: int) -> List[ExclusaoResponse]:
        exclusoes = self.repository.get_all(user_id)
        return [ExclusaoResponse.model_validate(exc) for exc in exclusoes]

    def create_exclusao(self, exclusao: ExclusaoCreate, user_id: int) -> ExclusaoResponse:
        db_exclusao = self.repository.create(exclusao, user_id)
        return ExclusaoResponse.model_validate(db_exclusao)

    def update_exclusao(
        self, exclusao_id: int, exclusao: ExclusaoUpdate, user_id: int
    ) -> ExclusaoResponse:
        db_exclusao = self.repository.update(exclusao_id, exclusao, user_id)
        if not db_exclusao:
            raise ValueError("Exclusão não encontrada")
        return ExclusaoResponse.model_validate(db_exclusao)

    def delete_exclusao(self, exclusao_id: int, user_id: int) -> bool:
        return self.repository.delete(exclusao_id, user_id)
