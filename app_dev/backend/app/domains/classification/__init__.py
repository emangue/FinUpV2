"""
Domínio de Classification - Regras de Classificação Configuráveis
"""

from .models import GenericClassificationRules
from .schemas import (
    GenericRuleCreate, GenericRuleUpdate, GenericRuleResponse,
    GenericRuleTestRequest, GenericRuleTestResponse
)
from .service import GenericClassificationService
from .router import router

__all__ = [
    # Models
    "GenericClassificationRules",
    
    # Schemas
    "GenericRuleCreate",
    "GenericRuleUpdate", 
    "GenericRuleResponse",
    "GenericRuleTestRequest",
    "GenericRuleTestResponse",
    
    # Service
    "GenericClassificationService",
    
    # Router
    "router",
]