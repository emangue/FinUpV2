from sqlalchemy.orm import Session
from typing import List
from .repository import CompatibilityRepository
from .schemas import (
    BankCompatibilityCreate, 
    BankCompatibilityUpdate, 
    BankCompatibilityResponse,
    FormatValidationResponse
)
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class CompatibilityService:
    """
    Service para gerenciamento de compatibilidade de formatos
    
    Estrutura Matricial: 1 banco com 4 formatos (CSV, Excel, PDF, OFX)
    """
    
    def __init__(self, db: Session):
        self.repository = CompatibilityRepository(db)
    
    def get_all(self) -> List[BankCompatibilityResponse]:
        """Listar todos os bancos com seus formatos"""
        banks = self.repository.get_all()
        return [BankCompatibilityResponse.model_validate(bank) for bank in banks]
    
    def get_by_id(self, id: int) -> BankCompatibilityResponse:
        """Buscar banco por ID"""
        bank = self.repository.get_by_id(id)
        if not bank:
            raise HTTPException(status_code=404, detail="Banco não encontrado")
        return BankCompatibilityResponse.model_validate(bank)
    
    def validate_format(self, bank_name: str, file_format: str) -> FormatValidationResponse:
        """
        Validar se banco suporta formato específico
        
        Args:
            bank_name: Nome do banco (ex: 'Itaú', 'BTG Pactual')
            file_format: 'CSV', 'Excel', 'PDF', 'OFX'
        
        Returns:
            FormatValidationResponse com status e flag is_supported
            
        Raises:
            HTTPException 404: Se banco não cadastrado
            HTTPException 400: Se formato inválido
        """
        # Validar formato
        valid_formats = ['CSV', 'Excel', 'PDF', 'OFX']
        if file_format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Formato inválido: {file_format}. Formatos válidos: {', '.join(valid_formats)}"
            )
        
        # Buscar status
        status = self.repository.get_format_status(bank_name, file_format)
        
        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Banco '{bank_name}' não cadastrado. Acesse Settings → Bancos para cadastrar."
            )
        
        is_supported = (status == "OK")
        
        message = None
        if status == "WIP":
            message = f"Formato {file_format} está em desenvolvimento para {bank_name}"
        elif status == "TBD":
            message = f"Formato {file_format} ainda não suportado para {bank_name}"
        
        logger.info(f"✅ Validação: {bank_name} + {file_format} = {status} (suportado={is_supported})")
        
        return FormatValidationResponse(
            bank_name=bank_name,
            file_format=file_format,
            status=status,
            is_supported=is_supported,
            message=message
        )
    
    def create(self, data: BankCompatibilityCreate) -> BankCompatibilityResponse:
        """Criar novo banco com todos os formatos"""
        # Verificar se banco já existe
        existing = self.repository.get_by_bank_name(data.bank_name)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Banco '{data.bank_name}' já cadastrado"
            )
        
        bank = self.repository.create(data)
        logger.info(f"✅ Banco criado: {bank.bank_name}")
        return BankCompatibilityResponse.model_validate(bank)
    
    def update(self, id: int, data: BankCompatibilityUpdate) -> BankCompatibilityResponse:
        """Atualizar banco e/ou status de formatos"""
        bank = self.repository.update(id, data)
        if not bank:
            raise HTTPException(status_code=404, detail="Banco não encontrado")
        
        logger.info(f"✅ Banco atualizado: {bank.bank_name}")
        return BankCompatibilityResponse.model_validate(bank)
    
    def delete(self, id: int) -> dict:
        """Deletar banco"""
        bank = self.repository.get_by_id(id)
        if not bank:
            raise HTTPException(status_code=404, detail="Banco não encontrado")
        
        bank_name = bank.bank_name
        success = self.repository.delete(id)
        
        logger.warning(f"🗑️  Banco deletado: {bank_name}")
        return {"message": f"Banco '{bank_name}' deletado com sucesso"}
    
    def get_count(self) -> int:
        """Contar total de bancos"""
        return self.repository.count()
