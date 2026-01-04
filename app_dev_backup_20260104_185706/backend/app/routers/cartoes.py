"""
Router para gerenciamento de cartões de crédito
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models import Cartao
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/cartoes", tags=["Cartões"])

# Schemas Pydantic
class CartaoCreate(BaseModel):
    nome_cartao: str
    final_cartao: str
    banco: str

class CartaoUpdate(BaseModel):
    nome_cartao: Optional[str] = None
    final_cartao: Optional[str] = None
    banco: Optional[str] = None
    ativo: Optional[int] = None

class CartaoResponse(BaseModel):
    id: int
    nome_cartao: str
    final_cartao: str
    banco: str
    ativo: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CartaoResponse])
def listar_cartoes(
    apenas_ativos: bool = True,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Lista todos os cartões cadastrados do usuário"""
    query = db.query(Cartao).filter(Cartao.user_id == user_id)
    
    if apenas_ativos:
        query = query.filter(Cartao.ativo == 1)
    
    cartoes = query.order_by(Cartao.banco, Cartao.nome_cartao).all()
    return cartoes

@router.get("/{cartao_id}", response_model=CartaoResponse)
def obter_cartao(
    cartao_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtém um cartão específico do usuário"""
    cartao = db.query(Cartao).filter(
        Cartao.id == cartao_id,
        Cartao.user_id == user_id
    ).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    return cartao

@router.post("/", response_model=CartaoResponse, status_code=status.HTTP_201_CREATED)
def criar_cartao(
    cartao: CartaoCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cria um novo cartão para o usuário"""
    
    # Validar final do cartão (4 dígitos)
    if len(cartao.final_cartao) != 4 or not cartao.final_cartao.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Final do cartão deve ter exatamente 4 dígitos"
        )
    
    # Verificar se já existe cartão com mesmo banco e final para este usuário
    existing = db.query(Cartao).filter(
        Cartao.user_id == user_id,
        Cartao.banco == cartao.banco,
        Cartao.final_cartao == cartao.final_cartao,
        Cartao.ativo == 1
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um cartão ativo do {cartao.banco} com final {cartao.final_cartao}"
        )
    
    novo_cartao = Cartao(
        nome_cartao=cartao.nome_cartao.strip(),
        final_cartao=cartao.final_cartao,
        banco=cartao.banco.strip(),
        user_id=user_id,
        ativo=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(novo_cartao)
    db.commit()
    db.refresh(novo_cartao)
    
    return novo_cartao

@router.put("/{cartao_id}", response_model=CartaoResponse)
def atualizar_cartao(
    cartao_id: int,
    cartao_data: CartaoUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Atualiza um cartão existente do usuário"""
    cartao = db.query(Cartao).filter(
        Cartao.id == cartao_id,
        Cartao.user_id == user_id
    ).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    # Atualizar campos fornecidos
    if cartao_data.nome_cartao is not None:
        cartao.nome_cartao = cartao_data.nome_cartao.strip()
    
    if cartao_data.final_cartao is not None:
        if len(cartao_data.final_cartao) != 4 or not cartao_data.final_cartao.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Final do cartão deve ter exatamente 4 dígitos"
            )
        cartao.final_cartao = cartao_data.final_cartao
    
    if cartao_data.banco is not None:
        cartao.banco = cartao_data.banco.strip()
    
    if cartao_data.ativo is not None:
        cartao.ativo = cartao_data.ativo
    
    cartao.updated_at = datetime.now()
    
    db.commit()
    db.refresh(cartao)
    
    return cartao

@router.delete("/{cartao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cartao(
    cartao_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Desativa um cartão (soft delete) do usuário"""
    cartao = db.query(Cartao).filter(
        Cartao.id == cartao_id,
        Cartao.user_id == user_id
    ).first()
    
    if not cartao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cartão não encontrado"
        )
    
    # Soft delete
    cartao.ativo = 0
    cartao.updated_at = datetime.now()
    
    db.commit()
    
    return None

@router.get("/banco/{banco_nome}", response_model=List[CartaoResponse])
def listar_cartoes_por_banco(
    banco_nome: str,
    apenas_ativos: bool = True,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Lista cartões de um banco específico do usuário"""
    query = db.query(Cartao).filter(
        Cartao.banco == banco_nome,
        Cartao.user_id == user_id
    )
    
    if apenas_ativos:
        query = query.filter(Cartao.ativo == 1)
    
    cartoes = query.order_by(Cartao.nome_cartao).all()
    return cartoes
