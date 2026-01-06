from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from .schemas import (
    BankCompatibilityCreate,
    BankCompatibilityUpdate,
    BankCompatibilityResponse,
    BankCompatibilityListResponse
)
from .service import CompatibilityService

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])

@router.get("/", response_model=BankCompatibilityListResponse)
def list_banks(db: Session = Depends(get_db)):
    """Listar todos os bancos e formatos compatíveis"""
    service = CompatibilityService(db)
    banks = service.get_all()
    total = service.get_count()
    return BankCompatibilityListResponse(banks=banks, total=total)

@router.get("/{id}", response_model=BankCompatibilityResponse)
def get_bank(id: int, db: Session = Depends(get_db)):
    """Buscar banco por ID"""
    service = CompatibilityService(db)
    return service.get_by_id(id)

@router.post("/", response_model=BankCompatibilityResponse, status_code=201)
def create_bank(data: BankCompatibilityCreate, db: Session = Depends(get_db)):
    """Criar novo registro de compatibilidade"""
    service = CompatibilityService(db)
    return service.create(data)

@router.put("/{id}", response_model=BankCompatibilityResponse)
def update_bank(id: int, data: BankCompatibilityUpdate, db: Session = Depends(get_db)):
    """Atualizar registro de compatibilidade"""
    service = CompatibilityService(db)
    return service.update(id, data)

@router.delete("/{id}")
def delete_bank(id: int, db: Session = Depends(get_db)):
    """Deletar registro de compatibilidade"""
    service = CompatibilityService(db)
    return service.delete(id)
