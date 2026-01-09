from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from .schemas import (
    BankCompatibilityCreate,
    BankCompatibilityUpdate,
    BankCompatibilityResponse,
    BankCompatibilityListResponse,
    FormatValidationResponse
)
from .service import CompatibilityService

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])

@router.get("/", response_model=BankCompatibilityListResponse)
def list_banks(db: Session = Depends(get_db)):
    """
    Listar todos os bancos com seus formatos
    
    Retorna estrutura matricial: 1 linha por banco com colunas para cada formato
    """
    service = CompatibilityService(db)
    banks = service.get_all()
    total = service.get_count()
    return BankCompatibilityListResponse(banks=banks, total=total)

@router.get("/validate", response_model=FormatValidationResponse)
def validate_format(
    bank_name: str = Query(..., description="Nome do banco"),
    file_format: str = Query(..., description="Formato do arquivo (CSV, Excel, PDF, OFX)"),
    db: Session = Depends(get_db)
):
    """
    Validar se banco suporta formato específico
    
    Retorna status e flag is_supported.
    Usado pelo upload para validar antes de processar.
    
    Raises:
        404: Banco não cadastrado
        400: Formato inválido
    """
    service = CompatibilityService(db)
    return service.validate_format(bank_name, file_format)

@router.get("/{id}", response_model=BankCompatibilityResponse)
def get_bank(id: int, db: Session = Depends(get_db)):
    """Buscar banco por ID"""
    service = CompatibilityService(db)
    return service.get_by_id(id)

@router.post("/", response_model=BankCompatibilityResponse, status_code=201)
def create_bank(data: BankCompatibilityCreate, db: Session = Depends(get_db)):
    """
    Criar novo banco com todos os formatos
    
    Todos os formatos (CSV, Excel, PDF, OFX) devem ter status definido.
    """
    service = CompatibilityService(db)
    return service.create(data)

@router.put("/{id}", response_model=BankCompatibilityResponse)
def update_bank(id: int, data: BankCompatibilityUpdate, db: Session = Depends(get_db)):
    """
    Atualizar banco e/ou status de formatos
    
    Qualquer campo é opcional (partial update)
    """
    service = CompatibilityService(db)
    return service.update(id, data)

@router.delete("/{id}")
def delete_bank(id: int, db: Session = Depends(get_db)):
    """Deletar banco"""
    service = CompatibilityService(db)
    return service.delete(id)
