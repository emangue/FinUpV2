"""
Router de Compatibilidade de Bancos
Gestão de formatos de arquivo por banco
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import BankFormatCompatibility, User
from ..schemas import BankCompatibilityResponse
from .auth import get_current_user

router = APIRouter(prefix="/api/v1/compatibility", tags=["compatibility"])

@router.get("/", response_model=List[BankCompatibilityResponse])
def list_compatibility(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista compatibilidade de bancos e formatos"""
    compat = db.query(BankFormatCompatibility).order_by(
        BankFormatCompatibility.bank_name,
        BankFormatCompatibility.file_format
    ).all()
    return compat

@router.get("/{bank_name}")
def get_bank_compatibility(
    bank_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna compatibilidade de um banco específico"""
    compat = db.query(BankFormatCompatibility).filter(
        BankFormatCompatibility.bank_name == bank_name
    ).all()
    
    if not compat:
        raise HTTPException(status_code=404, detail="Banco não encontrado")
    
    return compat
