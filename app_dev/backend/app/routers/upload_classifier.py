"""
Endpoint para processar e classificar transações do upload
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Adiciona codigos_apoio ao path (parents[4] = ProjetoFinancasV3)
codigos_apoio_path = Path(__file__).resolve().parents[4] / 'codigos_apoio'
sys.path.insert(0, str(codigos_apoio_path))

from universal_processor import process_batch as universal_process_batch
from cascade_classifier import CascadeClassifier

from app.database import get_db
from app.models import User, PreviewTransacao
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


def get_badge_color(origem_classificacao: str) -> str:
    """
    Retorna cor do badge baseado na origem da classificação
    """
    cores = {
        'IdParcela': 'blue',
        'Fatura Cartão': 'purple',
        'Ignorar': 'gray',
        'Base_Padroes': 'green',
        'Journal Entries': 'emerald',
        'Palavras-chave': 'yellow',
        'Não Encontrado': 'red'
    }
    return cores.get(origem_classificacao, 'gray')


def get_error_code_info(code: str, db: Session) -> dict:
    """Busca informações de um código de erro"""
    try:
        result = db.execute("""
            SELECT code, message_pt, technical_details, suggested_action, severity
            FROM error_codes WHERE code = :code
        """, {"code": code}).fetchone()
        
        if result:
            return {
                "errorCode": result[0],
                "error": result[1],
                "technicalDetails": result[2],
                "suggestedAction": result[3],
                "severity": result[4]
            }
    except:
        pass
    
    return {
        "errorCode": code,
        "error": "Erro no processamento",
        "suggestedAction": "Tente novamente ou contate o suporte"
    }


@router.get("/process-classify/{session_id}")
async def process_and_classify_preview(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Busca preview da sessão, processa através do universal_processor
    e classifica com o cascade_classifier
    
    Retorna transações classificadas com origem_classificacao
    
    **Códigos de Erro:**
    - PREV_001: Sessão não encontrada
    - PREV_004: Erro ao processar transações  
    - PREV_005: Erro ao classificar transações
    """
    
    # Buscar transações do preview
    preview_records = db.query(PreviewTransacao).filter(
        PreviewTransacao.session_id == session_id,
        PreviewTransacao.user_id == user_id
    ).all()
    
    if not preview_records:
        error_info = get_error_code_info("PREV_001", db)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                **error_info,
                "details": {"session_id": session_id, "user_id": user_id}
            }
        )
        # Se já tem classificações salvas, retornar direto (não reprocessar)
    if preview_records[0].origem_classificacao:
        print(f"ℹ️  Sessão {session_id} já classificada - retornando cache")
        
        # Montar resposta a partir dos dados salvos
        transacoes_classificadas = []
        for record in preview_records:
            t = {
                'Data': record.data,
                'Estabelecimento': record.lancamento,
                'Valor': record.valor,
                'ValorPositivo': record.ValorPositivo,
                'TipoTransacao': record.TipoTransacao,
                'IdTransacao': record.IdTransacao,
                'IdParcela': record.IdParcela,
                'EstabelecimentoBase': record.EstabelecimentoBase,
                'ParcelaAtual': record.ParcelaAtual,
                'TotalParcelas': record.TotalParcelas,
                'TemParcela': bool(record.TemParcela),
                'GRUPO': record.GRUPO or '',
                'SUBGRUPO': record.SUBGRUPO or '',
                'TipoGasto': record.TipoGasto or '',
                'CategoriaGeral': record.CategoriaGeral or '',
                'origem_classificacao': record.origem_classificacao,
                'ValidarIA': record.ValidarIA,
                'MarcacaoIA': record.MarcacaoIA,
                'IgnorarDashboard': bool(record.IgnorarDashboard),
                'classificationBadge': {
                    'level': record.origem_classificacao,
                    'color': get_badge_color(record.origem_classificacao),
                    'label': record.origem_classificacao
                }
            }
            transacoes_classificadas.append(t)
        
        # Calcular estatísticas do cache
        stats = {
            'total': len(transacoes_classificadas),
            'nivel_0_id_parcela': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'IdParcela'),
            'nivel_1_fatura_cartao': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Fatura Cartão'),
            'nivel_2_ignorar': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Ignorar'),
            'nivel_3_base_padroes': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Base_Padroes'),
            'nivel_4_journal_entries': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Journal Entries'),
            'nivel_5_palavras_chave': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Palavras-chave'),
            'nivel_6_nao_encontrado': sum(1 for t in transacoes_classificadas if t['origem_classificacao'] == 'Não Encontrado'),
        }
        
        first_record = preview_records[0]
        soma_total = sum(t['Valor'] for t in transacoes_classificadas)
        
        metadata = {
            'banco': first_record.banco or 'Não informado',
            'cartao': first_record.cartao or 'Não informado',
            'nomeArquivo': first_record.nome_arquivo or 'upload.csv',
            'mesFatura': first_record.mes_fatura or '2025-01',
            'totalRegistros': len(transacoes_classificadas),
            'somaTotal': soma_total,
            'estatisticas': stats
        }
        
        return {
            'metadata': metadata,
            'transacoes': transacoes_classificadas
        }
        # Converter para formato esperado pelo processor
    transacoes_raw = []
    for record in preview_records:
        transacoes_raw.append({
            'Data': record.data,
            'Estabelecimento': record.lancamento,  # Assumindo que lancamento = estabelecimento
            'Valor': record.valor
        })
    
    # Processar através do universal_processor
    try:
        transacoes_processadas = universal_process_batch(transacoes_raw)
    except Exception as e:
        error_info = get_error_code_info("PREV_004", db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                **error_info,
                "details": {"exception": str(e)}
            }
        )
    
    # Classificar através do cascade_classifier
    try:
        classifier = CascadeClassifier(db_session=db, user_id=user_id)
        transacoes_classificadas = classifier.classify_batch(transacoes_processadas)
        
        # Salvar classificações de volta em preview_transacoes
        for idx, t_classificada in enumerate(transacoes_classificadas):
            preview_record = preview_records[idx]
            
            # Atualizar com dados processados e classificados
            preview_record.IdTransacao = t_classificada.get('IdTransacao')
            preview_record.IdParcela = t_classificada.get('IdParcela')
            preview_record.EstabelecimentoBase = t_classificada.get('EstabelecimentoBase')
            preview_record.ValorPositivo = t_classificada.get('ValorPositivo')
            preview_record.TipoTransacao = t_classificada.get('TipoTransacao')
            
            preview_record.GRUPO = t_classificada.get('GRUPO', '')
            preview_record.SUBGRUPO = t_classificada.get('SUBGRUPO', '')
            preview_record.TipoGasto = t_classificada.get('TipoGasto', '')
            preview_record.CategoriaGeral = t_classificada.get('CategoriaGeral', '')
            
            preview_record.origem_classificacao = t_classificada.get('origem_classificacao', 'Não Encontrado')
            preview_record.ValidarIA = t_classificada.get('ValidarIA', 'Revisar')
            preview_record.MarcacaoIA = t_classificada.get('MarcacaoIA', 'Automático')
            
            preview_record.ParcelaAtual = t_classificada.get('ParcelaAtual')
            preview_record.TotalParcelas = t_classificada.get('TotalParcelas')
            preview_record.TemParcela = 1 if t_classificada.get('TemParcela') else 0
            preview_record.IgnorarDashboard = 1 if t_classificada.get('IgnorarDashboard') else 0
            
            # Adicionar badge de classificação para o frontend
            t_classificada['classificationBadge'] = {
                'level': preview_record.origem_classificacao,
                'color': get_badge_color(preview_record.origem_classificacao),
                'label': preview_record.origem_classificacao
            }
        
        db.commit()
        print(f"✅ {len(transacoes_classificadas)} transações classificadas e salvas em preview_transacoes")
        
        # Obter estatísticas
        stats = classifier.get_stats()
    except Exception as e:
        db.rollback()
        error_info = get_error_code_info("PREV_005", db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                **error_info,
                "details": {"exception": str(e)}
            }
        )
    
    # Montar metadata
    first_record = preview_records[0]
    soma_total = sum(t['Valor'] for t in transacoes_classificadas)
    
    metadata = {
        'banco': first_record.banco or 'Não informado',
        'cartao': first_record.cartao or 'Não informado',
        'nomeArquivo': first_record.nome_arquivo or 'upload.csv',
        'mesFatura': first_record.mes_fatura or '2025-01',
        'totalRegistros': len(transacoes_classificadas),
        'somaTotal': soma_total,
        'estatisticas': stats
    }
    
    return {
        'metadata': metadata,
        'transacoes': transacoes_classificadas
    }


@router.post("/confirm/{session_id}")
async def confirm_import(
    session_id: str,
    payload: Dict[str, Any],
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Confirma importação e salva transações classificadas no journal_entries
    
    Body: { "transacoes": [...] }
    """
    from app.models import JournalEntry
    from datetime import datetime
    
    transacoes = payload.get('transacoes', [])
    
    if not transacoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma transação fornecida"
        )
    
    try:
        # Inserir no journal_entries
        for transacao in transacoes:
            # Converter data DD/MM/YYYY para YYYY-MM-DD
            data_parts = transacao['Data'].split('/')
            data_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
            
            journal_entry = JournalEntry(
                user_id=user_id,
                Data=datetime.strptime(data_iso, '%Y-%m-%d').date(),
                Estabelecimento=transacao['Estabelecimento'],
                EstabelecimentoBase=transacao.get('EstabelecimentoBase', ''),
                Valor=transacao['Valor'],
                ValorPositivo=transacao['ValorPositivo'],
                TipoTransacao=transacao['TipoTransacao'],
                GRUPO=transacao.get('GRUPO', ''),
                SUBGRUPO=transacao.get('SUBGRUPO', ''),
                TipoGasto=transacao.get('TipoGasto', ''),
                CategoriaGeral=transacao.get('CategoriaGeral', ''),
                IdTransacao=transacao['IdTransacao'],
                IdParcela=transacao.get('IdParcela'),
                origem_classificacao=transacao.get('origem_classificacao', 'Não Encontrado'),
                IgnorarDashboard=transacao.get('IgnorarDashboard', False),
                ValidarIA=transacao.get('ValidarIA', 'NAO'),
                MarcacaoIA=transacao.get('MarcacaoIA', 'Manual (Lote)'),
                arquivo_origem=transacao.get('origem', 'upload_manual'),
                data_processamento=datetime.utcnow()
            )
            db.add(journal_entry)
        
        db.commit()
        
        # Limpar preview
        db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).delete()
        db.commit()
        
        return {
            'success': True,
            'message': f'{len(transacoes)} transações importadas com sucesso'
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar transações: {str(e)}"
        )
