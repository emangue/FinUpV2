"""
Endpoint para upload e preview de arquivos
Processa arquivo, salva em preview_transacoes e retorna session_id
"""

import sys
import tempfile
import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import PreviewTransacao
from app.dependencies import get_current_user_id

# Importa processadores específicos
# TODO: Reimplementar processadores específicos
# codigos_apoio_path = Path(__file__).parents[4] / 'codigos_apoio'
# sys.path.insert(0, str(codigos_apoio_path))
# from fatura_itau import preprocessar_fatura_itau
# from universal_processor import universal_processor

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/preview")
async def upload_preview(
    file: UploadFile = File(...),
    banco: str = Form(...),
    cartao: str = Form(None),
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
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errorCode": "UPL_001", "error": "Arquivo não fornecido"}
        )
    
    if not banco:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errorCode": "UPL_002", "error": "Banco não especificado"}
        )
    
    if not mesFatura:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errorCode": "UPL_003", "error": "Mês fatura não especificado"}
        )
    
    try:
        # Limpar TODOS os registros de preview deste usuário antes de novo upload
        deleted = db.query(PreviewTransacao).filter(
            PreviewTransacao.user_id == user_id
        ).delete(synchronize_session=False)
        
        if deleted > 0:
            db.commit()
            print(f"🗑️  Limpeza: {deleted} registros de preview removidos antes de novo upload")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Processar arquivo com processador específico
        processador = get_processador(banco, tipoDocumento, formato)
        
        if not processador:
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "errorCode": "UPL_004",
                    "error": f"Processador não encontrado para {banco}-{tipoDocumento}-{formato}"
                }
            )
        
        # Chamar processador específico
        df_raw = pd.read_csv(tmp_path, header=None) if formato == 'csv' else pd.read_excel(tmp_path, header=None)
        df_processado, validacao = processador(df_raw)
        os.unlink(tmp_path)  # Limpar arquivo temporário
        
        print(f"   ✓ Processador específico extraiu {len(df_processado)} transações")
        
        # Converter DataFrame para lista de dicts
        dados_processados = []
        for _, row in df_processado.iterrows():
            dados_processados.append({
                'data': row['data'],
                'lancamento': row['lançamento'],
                'valor': row['valor (R$)']  # Já vem com sinal correto do processador
            })
        
        # Gerar session_id único
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        # Salvar em preview_transacoes
        for row in dados_processados:
            preview = PreviewTransacao(
                session_id=session_id,
                user_id=user_id,
                banco=banco,
                cartao=cartao or 'N/A',
                nome_arquivo=file.filename,
                mes_fatura=mesFatura,
                data=row['data'],
                lancamento=row['lancamento'],
                valor=row['valor'],
                created_at=datetime.now()
            )
            db.add(preview)
        
        db.commit()
        
        print(f"✅ Upload processado: {len(dados_processados)} transações | Session: {session_id}")
        
        return {
            "success": True,
            "sessionId": session_id,
            "totalRegistros": len(dados_processados)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "errorCode": "UPL_006",
                "error": "Erro ao processar arquivo",
                "details": str(e)
            }
        )


@router.get("/preview/{session_id}")
async def get_preview_data(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Lista os dados de preview de uma sessão específica
    """
    try:
        
        # Buscar dados da sessão específica
        preview_data = db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).all()
        
        if not preview_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_007", "error": "Sessão de preview não encontrada"}
            )
        
        # Converter para formato JSON
        dados_formatados = []
        for item in preview_data:
            dados_formatados.append({
                "id": item.id,
                "data": item.data,
                "lancamento": item.lancamento,
                "valor": item.valor,
                "banco": item.banco,
                "cartao": item.cartao,
                "mes_fatura": item.mes_fatura,
                "nome_arquivo": item.nome_arquivo,
                "created_at": item.created_at.isoformat() if item.created_at else None
            })
        
        return {
            "success": True,
            "sessionId": session_id,
            "totalRegistros": len(dados_formatados),
            "dados": dados_formatados
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "errorCode": "UPL_008",
                "error": "Erro ao buscar dados de preview",
                "details": str(e)
            }
        )


@router.post("/confirm/{session_id}")
async def confirm_upload(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Confirma upload e salva dados de preview na tabela principal
    """
    try:
        
        # Buscar dados da sessão
        preview_data = db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).all()
        
        if not preview_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_009", "error": "Sessão de preview não encontrada"}
            )
        
        # Importar modelo JournalEntry
        from ..models import JournalEntry
        from datetime import datetime
        
        transacoes_criadas = 0
        
        for item in preview_data:
            # Criar transação simples - apenas campos básicos
            nova_transacao = JournalEntry(
                user_id=user_id,
                Data=item.data,
                Estabelecimento=item.lancamento,
                Valor=item.valor,
                MesFatura=item.mes_fatura,
                arquivo_origem=item.nome_arquivo,
                banco_origem=item.banco,
                created_at=datetime.now()
                # Todos os outros campos ficam NULL
            )
            
            db.add(nova_transacao)
            transacoes_criadas += 1
        
        # Salvar todas as transações
        db.commit()
        
        # Limpar dados de preview após confirmação
        db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id
        ).delete(synchronize_session=False)
        db.commit()
        
        print(f"✅ Upload confirmado: {transacoes_criadas} criadas, {transacoes_duplicadas} duplicadas")
        
        return {
            "success": True,
            "sessionId": session_id,
            "transacoesCriadas": transacoes_criadas,
            "total": transacoes_criadas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "errorCode": "UPL_010",
                "error": "Erro ao confirmar upload",
                "details": str(e)
            }
        )


@router.delete("/preview/{session_id}")
async def delete_preview(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Remove dados de preview de uma sessão específica
    """
    try:
        
        # Deletar apenas da sessão específica deste usuário
        deleted_count = db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "success": True,
            "deletedCount": deleted_count,
            "sessionId": session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "errorCode": "UPL_011",
                "error": "Erro ao deletar preview",
                "details": str(e)
            }
        )


def get_processador(banco: str, tipo: str, formato: str):
    """
    Retorna função processadora baseada em banco+tipo+formato
    """
    banco_norm = banco.lower().replace('ú', 'u').replace('ã', 'a')
    key = f"{banco_norm}_{tipo}_{formato}"
    
    processadores = {
        'itau_fatura_csv': preprocessar_fatura_itau,
    }
    
    return processadores.get(key)
