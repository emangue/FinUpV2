from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .models import BankFormatCompatibility
from .schemas import BankCompatibilityCreate, BankCompatibilityUpdate

class CompatibilityRepository:
    """
    Repository para Compatibilidade de Formatos
    
    Estrutura Matricial: 1 banco = 1 linha com colunas para cada formato
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[BankFormatCompatibility]:
        """Buscar todos os bancos (1 linha por banco)"""
        return self.db.query(BankFormatCompatibility).order_by(
            BankFormatCompatibility.bank_name
        ).all()
    
    def get_by_id(self, id: int) -> Optional[BankFormatCompatibility]:
        """Buscar banco por ID"""
        return self.db.query(BankFormatCompatibility).filter(
            BankFormatCompatibility.id == id
        ).first()
    
    def get_by_bank_name(self, bank_name: str) -> Optional[BankFormatCompatibility]:
        """Buscar por nome do banco (case-insensitive)"""
        return self.db.query(BankFormatCompatibility).filter(
            func.lower(BankFormatCompatibility.bank_name) == bank_name.lower()
        ).first()
    
    def get_format_status(self, bank_name: str, file_format: str) -> Optional[str]:
        """
        Buscar status de formato específico
        
        Args:
            bank_name: Nome do banco
            file_format: 'CSV', 'Excel', 'PDF', 'OFX'
        
        Returns:
            'OK', 'WIP', 'TBD' ou None se banco não existe
        """
        bank = self.get_by_bank_name(bank_name)
        if not bank:
            return None
        
        # Mapear formato para coluna
        format_map = {
            'CSV': bank.csv_status,
            'Excel': bank.excel_status,
            'PDF': bank.pdf_status,
            'OFX': bank.ofx_status
        }
        
        return format_map.get(file_format)
    
    def create(self, data: BankCompatibilityCreate) -> BankFormatCompatibility:
        """Criar novo banco com todos os formatos"""
        db_obj = BankFormatCompatibility(**data.model_dump())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, data: BankCompatibilityUpdate) -> Optional[BankFormatCompatibility]:
        """Atualizar banco e/ou status de formatos"""
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
        """Deletar banco"""
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        return True
    
    def count(self) -> int:
        """Contar total de bancos"""
        return self.db.query(func.count(BankFormatCompatibility.id)).scalar()
