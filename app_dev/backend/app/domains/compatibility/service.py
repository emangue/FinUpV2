from sqlalchemy.orm import Session
from typing import List
from .repository import CompatibilityRepository
from .schemas import BankCompatibilityCreate, BankCompatibilityUpdate, BankCompatibilityResponse
from fastapi import HTTPException

class CompatibilityService:
    def __init__(self, db: Session):
        self.repository = CompatibilityRepository(db)
    
    def get_all(self) -> List[BankCompatibilityResponse]:
        """Listar todos os registros"""
        banks = self.repository.get_all()
        return [BankCompatibilityResponse.model_validate(bank) for bank in banks]
    
    def get_by_id(self, id: int) -> BankCompatibilityResponse:
        """Buscar por ID"""
        bank = self.repository.get_by_id(id)
        if not bank:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return BankCompatibilityResponse.model_validate(bank)
    
    def create(self, data: BankCompatibilityCreate) -> BankCompatibilityResponse:
        """Criar novo registro"""
        # Verificar se já existe
        existing = self.repository.get_by_bank_and_format(data.bank_name, data.file_format)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe registro para {data.bank_name} - {data.file_format}"
            )
        
        bank = self.repository.create(data)
        return BankCompatibilityResponse.model_validate(bank)
    
    def update(self, id: int, data: BankCompatibilityUpdate) -> BankCompatibilityResponse:
        """Atualizar registro"""
        bank = self.repository.update(id, data)
        if not bank:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return BankCompatibilityResponse.model_validate(bank)
    
    def delete(self, id: int) -> dict:
        """Deletar registro"""
        success = self.repository.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return {"message": "Registro deletado com sucesso"}
    
    def get_count(self) -> int:
        """Contar registros"""
        return self.repository.count()
