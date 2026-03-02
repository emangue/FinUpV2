"""
Schemas para classificação configurável
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class GenericRuleCreate(BaseModel):
    """Schema para criação de regra genérica"""
    nome_regra: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = None
    keywords: str = Field(..., description="Palavras-chave separadas por vírgula")
    grupo: str = Field(..., min_length=1, max_length=100)
    subgrupo: str = Field(..., min_length=1, max_length=100)
    tipo_gasto: str = Field(..., min_length=1, max_length=50)  # Permite qualquer tipo da base de grupos
    prioridade: int = Field(default=50, ge=1, le=100)  # Prioridade de 1-100
    ativo: bool = True
    case_sensitive: bool = False
    match_completo: bool = False


class GenericRuleUpdate(BaseModel):
    """Schema para atualização de regra genérica"""
    nome_regra: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None
    keywords: Optional[str] = None
    grupo: Optional[str] = Field(None, min_length=1, max_length=100)
    subgrupo: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo_gasto: Optional[str] = Field(None, min_length=1, max_length=50)  # Permite qualquer tipo da base
    prioridade: Optional[int] = Field(None, ge=1, le=100)  # Prioridade de 1-100
    ativo: Optional[bool] = None
    case_sensitive: Optional[bool] = None
    match_completo: Optional[bool] = None


class GenericRuleResponse(BaseModel):
    """Schema para resposta de regra genérica"""
    id: int
    nome_regra: str
    descricao: Optional[str]
    keywords: str
    keywords_list: List[str]
    grupo: str
    subgrupo: str
    tipo_gasto: str
    prioridade: int
    ativo: bool
    case_sensitive: bool
    match_completo: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    total_matches: int
    last_match_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, rule):
        """Converte modelo para schema"""
        return cls(
            id=rule.id,
            nome_regra=rule.nome_regra,
            descricao=rule.descricao,
            keywords=rule.keywords,
            keywords_list=rule.get_keywords_list(),
            grupo=rule.grupo,
            subgrupo=rule.subgrupo,
            tipo_gasto=rule.tipo_gasto,
            prioridade=rule.prioridade or 50,
            ativo=rule.ativo if rule.ativo is not None else True,
            case_sensitive=rule.case_sensitive if rule.case_sensitive is not None else False,
            match_completo=rule.match_completo if rule.match_completo is not None else False,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            created_by=rule.created_by,
            total_matches=rule.total_matches or 0,
            last_match_at=rule.last_match_at,
        )


class GenericRuleTestRequest(BaseModel):
    """Schema para testar regra contra texto"""
    texto: str = Field(..., min_length=1)


class GenericRuleTestResponse(BaseModel):
    """Schema para resultado do teste"""
    texto: str
    regras_matched: List[GenericRuleResponse]
    melhor_regra: Optional[GenericRuleResponse]
    
    
class GenericRuleImportRequest(BaseModel):
    """Schema para importar regras hardcoded existentes"""
    sobrescrever_existentes: bool = False