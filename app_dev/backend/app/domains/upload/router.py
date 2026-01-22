"""
Domínio Upload - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from typing import List
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

@router.post("/batch", response_model=dict)
async def upload_batch(
    files: List[UploadFile] = File(...),
    banco: str = Form(...),
    tipoDocumento: str = Form("extrato"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recebe múltiplos arquivos e processa em lote (CONSOLIDADO em uma única sessão)
    
    **Parâmetros:**
    - files: Lista de arquivos
    - banco: Nome do banco (deve ser o mesmo para todos)
    - tipoDocumento: 'fatura' ou 'extrato'
    
    **Retorna:**
    - sessionId: ID único da sessão consolidada
    - totalArquivos: Número de arquivos processados
    - totalTransacoes: Número total de transações (de todos os arquivos)
    - erros: Lista de erros (se houver)
    """
    import logging
    from datetime import datetime
    logger = logging.getLogger(__name__)
    
    logger.info(f"📦 Upload em lote iniciado: {len(files)} arquivos")
    
    service = UploadService(db)
    resultados = []
    erros = []
    total_transacoes = 0
    
    # Gerar UMA ÚNICA session_id para todos os arquivos
    session_id_consolidado = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
    logger.info(f"🎯 Sessão consolidada: {session_id_consolidado}")
    
    for i, file in enumerate(files, 1):
        try:
            logger.info(f"  {i}/{len(files)} - Processando: {file.filename}")
            
            # Extrair mês da fatura do nome do arquivo se for fatura
            # Ex: MP202501.xlsx → mesFatura = "2025-01"
            mes_fatura = "2025-01"  # Default
            if tipoDocumento == "fatura" and file.filename:
                # Tentar extrair do nome do arquivo
                import re
                match = re.search(r'(\d{4})(\d{2})', file.filename)
                if match:
                    ano, mes = match.groups()
                    mes_fatura = f"{ano}-{mes}"
            
            result = service.process_and_preview(
                file=file,
                banco=banco,
                mes_fatura=mes_fatura,
                user_id=user_id,
                cartao=None,
                tipo_documento=tipoDocumento,
                formato="Excel",
                final_cartao=None,
                skip_cleanup=(i > 1),  # Limpar apenas no primeiro arquivo
                shared_session_id=session_id_consolidado  # Usar sessão compartilhada
            )
            
            resultados.append({
                "arquivo": file.filename,
                "totalRegistros": result.totalRegistros,
                "success": True
            })
            
            total_transacoes += result.totalRegistros
            logger.info(f"    ✅ {result.totalRegistros} transações processadas")
            
        except Exception as e:
            logger.error(f"    ❌ Erro: {str(e)}")
            erros.append({
                "arquivo": file.filename,
                "erro": str(e)
            })
            resultados.append({
                "arquivo": file.filename,
                "success": False,
                "erro": str(e)
            })
    
    logger.info(f"✅ Lote concluído: {len(resultados)} arquivos, {total_transacoes} transações")
    
    return {
        "success": len(erros) == 0,
        "sessionId": session_id_consolidado,  # Sessão única consolidada
        "totalArquivos": len(files),
        "arquivosProcessados": len([r for r in resultados if r.get("success")]),
        "totalTransacoes": total_transacoes,
        "arquivos": resultados,  # Lista de arquivos processados
        "erros": erros
    }

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
    excluir: int = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza classificação (grupo/subgrupo) ou marca exclusão de um registro de preview
    """
    service = UploadService(db)
    return service.update_preview_classification(
        session_id=session_id,
        preview_id=preview_id,
        grupo=grupo,
        subgrupo=subgrupo,
        excluir=excluir,
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
