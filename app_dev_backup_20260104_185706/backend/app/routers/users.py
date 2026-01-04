"""
Router para gerenciamento de usuários (Admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
import hashlib

from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/v1/users", tags=["Usuários"])

# Hash de senha
def hash_password(password: str) -> str:
    """Hash de senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Schemas Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    nome: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    ativo: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: str
    nome: str
    role: str
    ativo: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
def listar_usuarios(
    apenas_ativos: bool = True,
    db: Session = Depends(get_db)
):
    """Lista todos os usuários"""
    query = db.query(User)
    
    if apenas_ativos:
        query = query.filter(User.ativo == 1)
    
    usuarios = query.order_by(User.nome).all()
    return usuarios

@router.get("/{user_id}", response_model=UserResponse)
def obter_usuario(user_id: int, db: Session = Depends(get_db)):
    """Obtém um usuário específico"""
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return usuario

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário"""
    
    # Verificar se email já existe
    existing = db.query(User).filter(User.email == usuario.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{usuario.email}' já está cadastrado"
        )
    
    novo_usuario = User(
        email=usuario.email,
        nome=usuario.nome,
        password_hash=hash_password(usuario.password),
        role=usuario.role,
        ativo=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@router.put("/{user_id}", response_model=UserResponse)
def atualizar_usuario(
    user_id: int,
    usuario_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um usuário existente"""
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar campos fornecidos
    if usuario_data.email is not None:
        # Verificar se email já existe em outro usuário
        existing = db.query(User).filter(
            User.email == usuario_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{usuario_data.email}' já está cadastrado"
            )
        usuario.email = usuario_data.email
    
    if usuario_data.nome is not None:
        usuario.nome = usuario_data.nome
    
    if usuario_data.password is not None:
        usuario.password_hash = hash_password(usuario_data.password)
    
    if usuario_data.role is not None:
        usuario.role = usuario_data.role
    
    if usuario_data.ativo is not None:
        usuario.ativo = usuario_data.ativo
    
    usuario.updated_at = datetime.now()
    
    db.commit()
    db.refresh(usuario)
    
    return usuario

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_usuario(user_id: int, db: Session = Depends(get_db)):
    """Desativa um usuário (soft delete)"""
    if user_id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é possível desativar o usuário administrador principal"
        )
    
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Soft delete
    usuario.ativo = 0
    usuario.updated_at = datetime.now()
    
    db.commit()
    
    return None

@router.post("/{user_id}/reset-password")
def resetar_senha(
    user_id: int,
    nova_senha: str,
    db: Session = Depends(get_db)
):
    """Reseta a senha de um usuário"""
    usuario = db.query(User).filter(User.id == user_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    usuario.password_hash = hash_password(nova_senha)
    usuario.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}
