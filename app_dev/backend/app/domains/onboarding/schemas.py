"""Schemas do domínio Onboarding"""
from typing import Optional
from pydantic import BaseModel


class OnboardingProgressResponse(BaseModel):
    """4 flags de completude do onboarding"""
    conta_criada: bool
    primeiro_upload: bool
    plano_criado: bool
    investimento_adicionado: bool
    onboarding_completo: bool
    tem_demo: bool = False  # True se tem transações com fonte='demo'
    ultimo_upload_em: Optional[str] = None  # ISO date ou null — para nudge "30 dias"
