"""
Domínio Upload - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import UploadService
from .schemas import (
    UploadPreviewResponse,
    GetPreviewResponse,
    ConfirmUploadResponse,
    DeletePreviewResponse
)
from .history_schemas import UploadHistoryListResponse

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/preview", response_model=UploadPreviewResponse)
async def upload_preview(
    file: UploadFile = File(...),
    banco: str = Form(...),
    cartao: str = Form(None),
    final_cartao: str = Form(None),
    mesFatura: str = Form(...),
    tipoDocumento: str = Form("fatura"),
    formato: str = Form("csv"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recebe arquivo, processa e salva em preview_transacoes
    
    **Parâmetros:**
    - file: Arquivo CSV/XLS
    - banco: Nome do banco (ex: 'itau', 'btg')
    - cartao: Nome do cartão (opcional)
    - mesFatura: Mês da fatura no formato YYYY-MM
    - tipoDocumento: 'fatura' ou 'extrato'
    - formato: 'csv', 'xls', 'xlsx'
    
    **Retorna:**
    - sessionId: ID único da sessão de preview
    - totalRegistros: Número de transações processadas
    """
    service = UploadService(db)
    return service.process_and_preview(
        file=file,
        banco=banco,
        mes_fatura=mesFatura,
        user_id=user_id,
        cartao=cartao,
        tipo_documento=tipoDocumento,
        formato=formato,
        final_cartao=final_cartao
    )

@router.get("/preview/{session_id}", response_model=GetPreviewResponse)
async def get_preview_data(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista os dados de preview de uma sessão específica
    """
    service = UploadService(db)
    return service.get_preview_data(session_id, user_id)

@router.post("/confirm/{session_id}", response_model=ConfirmUploadResponse)
async def confirm_upload(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Confirma upload e salva dados de preview na tabela principal
    """
    service = UploadService(db)
    return service.confirm_upload(session_id, user_id)

@router.delete("/preview/{session_id}", response_model=DeletePreviewResponse)
async def delete_preview(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Remove dados de preview de uma sessão específica
    """
    service = UploadService(db)
    return service.delete_preview(session_id, user_id)

@router.patch("/preview/{session_id}/{preview_id}")
async def update_preview_classification(
    session_id: str,
    preview_id: int,
    grupo: str = None,
    subgrupo: str = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza classificação (grupo/subgrupo) de um registro de preview
    """
    service = UploadService(db)
    return service.update_preview_classification(
        session_id=session_id,
        preview_id=preview_id,
        grupo=grupo,
        subgrupo=subgrupo,
        user_id=user_id
    )

@router.get("/history", response_model=UploadHistoryListResponse)
async def get_upload_history(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista histórico de uploads do usuário
    
    **Parâmetros:**
    - limit: Número máximo de registros (padrão: 50)
    - offset: Deslocamento para paginação (padrão: 0)
    
    **Retorna:**
    - total: Total de uploads no histórico
    - uploads: Lista de registros de upload
    """
    service = UploadService(db)
    return service.get_upload_history(user_id, limit, offset)
