from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExclusaoBase(BaseModel):
    nome_transacao: str
    banco: Optional[str] = None
    tipo_documento: Optional[str] = "ambos"  # 'cartao', 'extrato', 'ambos'
    descricao: Optional[str] = None
    acao: str = "EXCLUIR"  # 'EXCLUIR' ou 'IGNORAR'


class ExclusaoCreate(ExclusaoBase):
    pass


class ExclusaoUpdate(ExclusaoBase):
    nome_transacao: Optional[str] = None
    acao: Optional[str] = None


class ExclusaoResponse(ExclusaoBase):
    id: int
    user_id: int
    ativo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
