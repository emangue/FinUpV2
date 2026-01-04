"""
Router para gerenciamento de transações a excluir na importação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models import TransacaoExclusao
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/exclusoes", tags=["Exclusões"])

# Schemas Pydantic
class ExclusaoCreate(BaseModel):
    nome_transacao: str
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None  # 'cartao', 'extrato', 'ambos'
    descricao: Optional[str] = None
    acao: Optional[str] = 'EXCLUIR'  # 'EXCLUIR' ou 'IGNORAR'

class ExclusaoUpdate(BaseModel):
    nome_transacao: Optional[str] = None
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[int] = None
    acao: Optional[str] = None  # 'EXCLUIR' ou 'IGNORAR'

class ExclusaoResponse(BaseModel):
    id: int
    nome_transacao: str
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None
    descricao: Optional[str] = None
    ativo: int
    acao: str = 'EXCLUIR'  # 'EXCLUIR' ou 'IGNORAR'
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ExclusaoResponse])
def listar_exclusoes(
    apenas_ativos: bool = True,
    banco: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Lista todas as transações configuradas para exclusão do usuário"""
    query = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.user_id == user_id
    )
    
    if apenas_ativos:
        query = query.filter(TransacaoExclusao.ativo == 1)
    
    if banco:
        # Buscar regras específicas do banco OU regras gerais (banco=NULL)
        query = query.filter(
            (TransacaoExclusao.banco == banco) | 
            (TransacaoExclusao.banco == None)
        )
    
    exclusoes = query.order_by(TransacaoExclusao.nome_transacao).all()
    return exclusoes

@router.get("/{exclusao_id}", response_model=ExclusaoResponse)
def obter_exclusao(
    exclusao_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtém uma exclusão específica do usuário"""
    exclusao = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.id == exclusao_id,
        TransacaoExclusao.user_id == user_id
    ).first()
    
    if not exclusao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusão não encontrada"
        )
    
    return exclusao

@router.post("/", response_model=ExclusaoResponse, status_code=status.HTTP_201_CREATED)
def criar_exclusao(
    exclusao: ExclusaoCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cria uma nova regra de exclusão para o usuário"""
    
    # Verificar se já existe regra com mesmo nome para este usuário
    existing = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.nome_transacao == exclusao.nome_transacao.strip().upper(),
        TransacaoExclusao.ativo == 1,
        TransacaoExclusao.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma regra de exclusão para '{exclusao.nome_transacao}'"
        )
    
    nova_exclusao = TransacaoExclusao(
        nome_transacao=exclusao.nome_transacao.strip().upper(),
        banco=exclusao.banco.strip() if exclusao.banco else None,
        tipo_documento=exclusao.tipo_documento if exclusao.tipo_documento else 'ambos',
        descricao=exclusao.descricao.strip() if exclusao.descricao else None,
        acao=exclusao.acao if exclusao.acao else 'EXCLUIR',
        ativo=1,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(nova_exclusao)
    db.commit()
    db.refresh(nova_exclusao)
    
    return nova_exclusao

@router.put("/{exclusao_id}", response_model=ExclusaoResponse)
def atualizar_exclusao(
    exclusao_id: int,
    exclusao_data: ExclusaoUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Atualiza uma exclusão existente do usuário"""
    exclusao = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.id == exclusao_id,
        TransacaoExclusao.user_id == user_id
    ).first()
    
    if not exclusao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusão não encontrada"
        )
    
    # Atualizar campos fornecidos
    if exclusao_data.nome_transacao is not None:
        exclusao.nome_transacao = exclusao_data.nome_transacao.strip().upper()
    
    if exclusao_data.banco is not None:
        exclusao.banco = exclusao_data.banco.strip() if exclusao_data.banco else None
    
    if exclusao_data.tipo_documento is not None:
        exclusao.tipo_documento = exclusao_data.tipo_documento
    
    if exclusao_data.descricao is not None:
        exclusao.descricao = exclusao_data.descricao.strip() if exclusao_data.descricao else None
    
    if exclusao_data.ativo is not None:
        exclusao.ativo = exclusao_data.ativo
    
    if exclusao_data.acao is not None:
        exclusao.acao = exclusao_data.acao
    
    exclusao.updated_at = datetime.now()
    
    db.commit()
    db.refresh(exclusao)
    
    return exclusao

@router.delete("/{exclusao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_exclusao(
    exclusao_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Desativa uma exclusão (soft delete) do usuário"""
    exclusao = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.id == exclusao_id,
        TransacaoExclusao.user_id == user_id
    ).first()
    
    if not exclusao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exclusão não encontrada"
        )
    
    # Soft delete
    exclusao.ativo = 0
    exclusao.updated_at = datetime.now()
    
    db.commit()
    
    return None

@router.post("/verificar")
def verificar_exclusoes(
    transacoes: List[str],
    banco: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Verifica quais transações devem ser excluídas para este usuário
    Retorna lista de transações que NÃO devem ser excluídas
    """
    query = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.ativo == 1,
        TransacaoExclusao.user_id == user_id
    )
    
    if banco:
        query = query.filter(
            (TransacaoExclusao.banco == banco) | 
            (TransacaoExclusao.banco == None)
        )
    
    exclusoes = query.all()
    nomes_excluir = {exc.nome_transacao.upper() for exc in exclusoes}
    
    # Filtrar transações
    transacoes_validas = [
        t for t in transacoes 
        if t.upper() not in nomes_excluir
    ]
    
    return {
        "total_recebidas": len(transacoes),
        "total_excluidas": len(transacoes) - len(transacoes_validas),
        "total_validas": len(transacoes_validas),
        "transacoes_validas": transacoes_validas
    }
