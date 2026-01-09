from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

StatusType = Literal["OK", "WIP", "TBD"]

class BankCompatibilityBase(BaseModel):
    """Esquema base com todos os formatos como colunas"""
    bank_name: str
    csv_status: StatusType = "TBD"
    excel_status: StatusType = "TBD"
    pdf_status: StatusType = "TBD"
    ofx_status: StatusType = "TBD"

class BankCompatibilityCreate(BankCompatibilityBase):
    """Schema para criar novo banco (todos os formatos obrigatórios)"""
    pass

class BankCompatibilityUpdate(BaseModel):
    """Schema para atualizar (qualquer campo opcional)"""
    bank_name: Optional[str] = None
    csv_status: Optional[StatusType] = None
    excel_status: Optional[StatusType] = None
    pdf_status: Optional[StatusType] = None
    ofx_status: Optional[StatusType] = None

class BankCompatibilityResponse(BankCompatibilityBase):
    """Schema de resposta com ID e timestamps"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BankCompatibilityListResponse(BaseModel):
    """Schema para lista de bancos"""
    banks: list[BankCompatibilityResponse]
    total: int

class FormatValidationResponse(BaseModel):
    """Schema para validação de formato específico"""
    bank_name: str
    file_format: str
    status: StatusType
    is_supported: bool
    message: Optional[str] = None
