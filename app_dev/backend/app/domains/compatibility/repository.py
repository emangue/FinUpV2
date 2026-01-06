from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .models import BankFormatCompatibility
from .schemas import BankCompatibilityCreate, BankCompatibilityUpdate

class CompatibilityRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[BankFormatCompatibility]:
        """Buscar todos os registros de compatibilidade"""
        return self.db.query(BankFormatCompatibility).order_by(
            BankFormatCompatibility.bank_name,
            BankFormatCompatibility.file_format
        ).all()
    
    def get_by_id(self, id: int) -> Optional[BankFormatCompatibility]:
        """Buscar por ID"""
        return self.db.query(BankFormatCompatibility).filter(
            BankFormatCompatibility.id == id
        ).first()
    
    def get_by_bank_and_format(self, bank_name: str, file_format: str) -> Optional[BankFormatCompatibility]:
        """Buscar por banco e formato específicos"""
        return self.db.query(BankFormatCompatibility).filter(
            BankFormatCompatibility.bank_name == bank_name,
            BankFormatCompatibility.file_format == file_format
        ).first()
    
    def create(self, data: BankCompatibilityCreate) -> BankFormatCompatibility:
        """Criar novo registro"""
        db_obj = BankFormatCompatibility(**data.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, data: BankCompatibilityUpdate) -> Optional[BankFormatCompatibility]:
        """Atualizar registro existente"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Deletar registro"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def count(self) -> int:
        """Contar total de registros"""
        return self.db.query(func.count(BankFormatCompatibility.id)).scalar()
