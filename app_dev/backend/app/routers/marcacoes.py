"""
Router de Marcações (Configurações)
Gestão de Categorias (GRUPO, SUBGRUPO, TipoGasto)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import BaseMarcacao, User
from ..schemas import MarcacaoResponse, MarcacaoCreate, MarcacaoUpdate
from .auth import get_current_user

router = APIRouter(prefix="/api/v1/marcacoes", tags=["marcacoes"])

@router.get("/", response_model=List[MarcacaoResponse])
def list_marcacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista todas as marcações (categorias)"""
    marcacoes = db.query(BaseMarcacao).order_by(
        BaseMarcacao.GRUPO, BaseMarcacao.SUBGRUPO
    ).all()
    return marcacoes

@router.get("/{marcacao_id}", response_model=MarcacaoResponse)
def get_marcacao(
    marcacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca uma marcação por ID"""
    marcacao = db.query(BaseMarcacao).filter(BaseMarcacao.id == marcacao_id).first()
    if not marcacao:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")
    return marcacao

@router.post("/", response_model=MarcacaoResponse, status_code=status.HTTP_201_CREATED)
def create_marcacao(
    marcacao: MarcacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria nova marcação"""
    # Verifica duplicata
    existing = db.query(BaseMarcacao).filter(
        BaseMarcacao.GRUPO == marcacao.GRUPO,
        BaseMarcacao.SUBGRUPO == marcacao.SUBGRUPO,
        BaseMarcacao.TipoGasto == marcacao.TipoGasto
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Marcação já existe com esses valores"
        )
    
    # Cria nova marcação
    db_marcacao = BaseMarcacao(**marcacao.model_dump())
    db.add(db_marcacao)
    db.commit()
    db.refresh(db_marcacao)
    
    return db_marcacao

@router.put("/{marcacao_id}", response_model=MarcacaoResponse)
def update_marcacao(
    marcacao_id: int,
    marcacao: MarcacaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza marcação existente"""
    db_marcacao = db.query(BaseMarcacao).filter(BaseMarcacao.id == marcacao_id).first()
    
    if not db_marcacao:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")
    
    # Atualiza campos
    for key, value in marcacao.model_dump().items():
        setattr(db_marcacao, key, value)
    
    db.commit()
    db.refresh(db_marcacao)
    
    return db_marcacao

@router.delete("/{marcacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_marcacao(
    marcacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta marcação"""
    db_marcacao = db.query(BaseMarcacao).filter(BaseMarcacao.id == marcacao_id).first()
    
    if not db_marcacao:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")
    
    db.delete(db_marcacao)
    db.commit()
    
    return None
