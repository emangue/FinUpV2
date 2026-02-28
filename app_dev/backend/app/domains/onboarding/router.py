"""Router do domínio Onboarding"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from app.domains.transactions.models import JournalEntry
from .service import OnboardingService
from .schemas import OnboardingProgressResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/progress", response_model=OnboardingProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Retorna 4 flags de completude do onboarding"""
    return OnboardingService(db).get_progress(user_id)


@router.post("/modo-demo")
def ativar_modo_demo(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Insere seed de transações demo. Idempotente: se já tem demo, retorna sem duplicar."""
    if db.query(JournalEntry).filter(JournalEntry.user_id == user_id, JournalEntry.fonte == "demo").first():
        return {"message": "Modo demo já ativo", "criadas": 0}
    criadas = OnboardingService(db).criar_dados_demo(user_id)
    return {"message": "Dados de demonstração criados", "criadas": criadas}


@router.delete("/modo-demo")
def desativar_modo_demo(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Remove todas as transações demo do usuário."""
    deletadas = OnboardingService(db).limpar_dados_demo(user_id)
    return {"message": f"{deletadas} registros demo removidos", "deletadas": deletadas}
