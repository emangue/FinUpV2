"""
Domínio Upload - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from typing import List, Optional
from dataclasses import asdict
import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.orm import Session

# Validação de upload — segurança contra DoS e arquivos maliciosos
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50MB
EXTENSOES_PERMITIDAS = {"csv", "xls", "xlsx", "pdf", "ofx", "txt"}

# Bancos que não geram IdTransacao v5 confiável (não identificados)
_BANCOS_INVALIDOS = {'', 'generico', 'outros', 'outro', 'desconhecido'}
MIME_TYPES_PERMITIDOS = {
    "text/csv", "text/plain",
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/octet-stream",  # .ofx em alguns browsers
    "application/x-ofx",
}

def _validar_arquivo(file: UploadFile) -> None:
    """Valida extensão, MIME type. Tamanho é validado após leitura."""
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise HTTPException(400, f"Extensão .{ext} não permitida. Use: {', '.join(sorted(EXTENSOES_PERMITIDAS))}")
    if file.content_type and file.content_type.split(";")[0].strip() not in MIME_TYPES_PERMITIDOS:
        raise HTTPException(400, f"Tipo de arquivo não permitido: {file.content_type}")

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import UploadService
from .fingerprints import DetectionEngine, DetectionResult
from .content_extractor import extract_content_sample
from .history_models import UploadHistory
from .schemas import (
    UploadPreviewResponse,
    GetPreviewResponse,
    ConfirmUploadResponse,
    DeletePreviewResponse
)
from .history_schemas import UploadHistoryListResponse, RollbackPreviewResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/detect")
async def detect_arquivo(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Sprint 3: Detecta banco/tipo/período + verifica duplicata (S30).
    Retorna sugestão de processamento e alerta se já existe upload similar.
    """
    file_bytes = await file.read()
    content_sample = extract_content_sample(file_bytes, file.filename or "arquivo")

    engine = DetectionEngine()
    result = engine.detect(file.filename or "arquivo", content_sample, file_bytes)

    # S30: verificar duplicata
    duplicata = None
    if result.banco != "generico" and (result.mes_fatura or result.periodo_inicio):
        mes = result.mes_fatura
        if not mes and result.periodo_inicio:
            parts = result.periodo_inicio.split("-")
            if len(parts) >= 2:
                mes = f"{parts[0]}{parts[1]}"
        if mes:
            existing = (
                db.query(UploadHistory)
                .filter(
                    UploadHistory.user_id == user_id,
                    UploadHistory.banco == result.banco,
                    UploadHistory.tipo_documento == result.tipo,
                    UploadHistory.mes_fatura == mes,
                    UploadHistory.status == "success",
                )
                .first()
            )
            if existing:
                duplicata = {
                    "upload_id": existing.id,
                    "data_importacao": (
                        existing.data_confirmacao.isoformat()
                        if existing.data_confirmacao
                        else (existing.data_upload.isoformat() if existing.data_upload else None)
                    ),
                    "total_transacoes": existing.transacoes_importadas or existing.total_registros,
                }

    return {
        **asdict(result),
        "filename": file.filename,
        "duplicata_detectada": duplicata,
    }


@router.post("/preview", response_model=UploadPreviewResponse)
async def upload_preview(
    file: UploadFile = File(...),
    banco: str = Form(...),
    cartao: str = Form(None),
    final_cartao: str = Form(None),
    mesFatura: str = Form(...),
    tipoDocumento: str = Form("fatura"),
    formato: str = Form("csv"),
    senha: Optional[str] = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recebe arquivo, processa e salva em preview_transacoes
    
    **Parâmetros:**
    - file: Arquivo CSV/XLS/PDF
    - banco: Nome do banco (ex: 'itau', 'btg')
    - cartao: Nome do cartão (opcional)
    - mesFatura: Mês da fatura no formato YYYY-MM
    - tipoDocumento: 'fatura' ou 'extrato'
    - formato: 'csv', 'excel', 'pdf', 'ofx'
    - senha: Senha do PDF (opcional, apenas para PDFs protegidos)
    
    **Retorna:**
    - sessionId: ID único da sessão de preview
    - totalRegistros: Número de transações processadas
    """
    # Validação: banco identificável é obrigatório para IdTransacao v5 correto
    if banco.strip().lower() in _BANCOS_INVALIDOS:
        raise HTTPException(
            status_code=422,
            detail={
                "errorCode": "UPL_010",
                "error": "Instituição financeira obrigatória",
                "detail": (
                    "Selecione a instituição financeira correta. "
                    "Uploads sem banco identificado não permitem deduplicação."
                )
            }
        )

    service = UploadService(db)
    return service.process_and_preview(
        file=file,
        banco=banco,
        mes_fatura=mesFatura,
        user_id=user_id,
        cartao=cartao,
        tipo_documento=tipoDocumento,
        formato=formato,
        final_cartao=final_cartao,
        senha=senha
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
    
    def _formato_from_filename(filename: str) -> str:
        ext = (filename or "").lower().split(".")[-1]
        if ext in ("xls", "xlsx", "xlsm"):
            return "Excel"
        if ext == "pdf":
            return "PDF"
        if ext == "ofx":
            return "OFX"
        return "CSV"

    for i, file in enumerate(files, 1):
        try:
            logger.info(f"  {i}/{len(files)} - Processando: {file.filename}")
            
            formato = _formato_from_filename(file.filename or "")
            mes_fatura = "2025-01"
            if tipoDocumento == "fatura" and file.filename:
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
                formato=formato,
                final_cartao=None,
                skip_cleanup=(i > 1),
                shared_session_id=session_id_consolidado
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


@router.post("/import-planilha")
async def import_planilha(
    file: UploadFile = File(...),
    mapeamento: Optional[str] = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Sprint 5: Importa planilha genérica CSV/XLSX.
    Valida colunas obrigatórias (Data, Descrição, Valor) e retorna preview.
    Usa detecção automática de colunas ou mapeamento explícito.
    Confirmação via POST /upload/confirm/{sessionId}.
    """
    mapeamento_dict = None
    if mapeamento:
        try:
            mapeamento_dict = json.loads(mapeamento)
        except json.JSONDecodeError:
            pass
    service = UploadService(db)
    return service.import_planilha(file=file, user_id=user_id, mapeamento=mapeamento_dict)


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
    criar_regra: bool = Query(False, description="Sprint D: criar regra em transacoes_exclusao para sempre excluir"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza classificação (grupo/subgrupo) ou marca exclusão de um registro de preview.
    Sprint D: se criar_regra=True e excluir=1, cria TransacaoExclusao (banco+tipo_documento).
    """
    service = UploadService(db)
    return service.update_preview_classification(
        session_id=session_id,
        preview_id=preview_id,
        grupo=grupo,
        subgrupo=subgrupo,
        excluir=excluir,
        criar_regra=criar_regra,
        user_id=user_id
    )

@router.get("/estabelecimentos/sugestoes")
async def get_estabelecimentos_sugestoes(
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna grupos históricos por estabelecimento (para classificação em lote).
    Útil no BatchClassifyModal para sugerir grupo ao usuário.
    """
    from app.domains.transactions.models import JournalEntry
    from sqlalchemy import func

    rows = (
        db.query(JournalEntry.EstabelecimentoBase, JournalEntry.GRUPO)
        .filter(
            JournalEntry.user_id == user_id,
            JournalEntry.EstabelecimentoBase.isnot(None),
            JournalEntry.EstabelecimentoBase != "",
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.GRUPO != "",
        )
        .distinct()
        .limit(limit)
        .all()
    )

    return {
        "sugestoes": [
            {"estabelecimento": r[0], "grupo": r[1]}
            for r in rows
        ]
    }


@router.get("/history/{history_id}/rollback-preview", response_model=RollbackPreviewResponse)
async def get_rollback_preview(
    history_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Preview do que será removido ao desfazer o upload.
    Usado pelo modal de confirmação antes do delete.
    """
    service = UploadService(db)
    return service.get_rollback_preview(history_id, user_id)


@router.get("/history", response_model=UploadHistoryListResponse)
async def get_upload_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista histórico de uploads do usuário.
    status='success' retorna apenas uploads confirmados (realizados).
    """
    service = UploadService(db)
    return service.get_upload_history(user_id, limit, offset, status=status)


@router.delete("/history/{history_id}")
async def delete_upload_history(
    history_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deleta todas as transações de um upload e o registro de histórico.
    
    **Retorna:**
    - transacoes_deletadas: quantidade de transações removidas
    """
    service = UploadService(db)
    return service.delete_upload_history(history_id, user_id)


@router.post("/recreate-preview/{history_id}")
async def recreate_preview_from_history(
    history_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Recria preview a partir de um upload já confirmado.
    Permite revisar e re-salvar alterações.
    
    **Retorna:**
    - session_id: ID da sessão de preview para redirecionar
    - revision_of: ID do upload original
    """
    service = UploadService(db)
    return service.recreate_preview_from_history(history_id, user_id)


@router.patch("/history/{history_id}/periodo")
async def update_upload_periodo(
    history_id: int,
    ano: int = Query(..., ge=2020, le=2030, description="Ano (ex: 2025)"),
    mes: int = Query(..., ge=1, le=12, description="Mês (1 a 12)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Ajusta período (ano/mês) de todas as transações de um upload.
    Usado para corrigir erros sem refazer o upload.
    
    **Parâmetros:**
    - ano: 2024, 2025, 2026, etc
    - mes: 1 a 12
    """
    service = UploadService(db)
    return service.update_upload_periodo(history_id, user_id, ano, mes)
