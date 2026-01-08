"""
Domínio Upload - Service
Lógica de negócio com pipeline em 3 fases
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status, UploadFile
from datetime import datetime
import tempfile
import os
import logging
from pathlib import Path

from .repository import UploadRepository
from .models import PreviewTransacao
from .history_models import UploadHistory
from .schemas import (
    PreviewTransacaoResponse,
    UploadPreviewResponse,
    GetPreviewResponse,
    ConfirmUploadResponse,
    DeletePreviewResponse,
    ClassificationStats,
)
from .history_schemas import UploadHistoryResponse, UploadHistoryListResponse
from .processors import get_processor
from .processors.marker import TransactionMarker
from .processors.classifier import CascadeClassifier
from app.domains.exclusoes.models import TransacaoExclusao
from app.shared.utils import normalizar

logger = logging.getLogger(__name__)


class UploadService:
    """
    Service layer para upload
    Pipeline em 3 fases: Raw → Marking → Classification
    """
    
    def __init__(self, db: Session):
        self.repository = UploadRepository(db)
        self.db = db
    
    def process_and_preview(
        self,
        file: UploadFile,
        banco: str,
        mes_fatura: str,
        user_id: int,
        cartao: str = None,
        final_cartao: str = None,
        tipo_documento: str = "fatura",
        formato: str = "csv"
    ) -> UploadPreviewResponse:
        """
        Processa arquivo em 3 fases com salvamento incremental
        
        Fase 1: Raw Processing → Salvar dados básicos
        Fase 2: ID Marking → Atualizar com IDs
        Fase 3: Classification → Atualizar com classificação
        
        Raises:
            HTTPException: Se dados inválidos ou erro no processamento
        """
        logger.info(f"🚀 Iniciando upload: {file.filename} | Banco: {banco} | Tipo: {tipo_documento}")
        
        # Validações
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errorCode": "UPL_001", "error": "Arquivo não fornecido"}
            )
        
        session_id = None
        history_record = None
        
        try:
            # SEMPRE limpar preview do usuário ANTES de processar
            deleted = self.repository.delete_all_by_user(user_id)
            if deleted > 0:
                logger.info(f"🗑️  Limpeza: {deleted} registros de preview removidos")
            
            # Gerar session_id único
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            # Criar registro de histórico com status='processing'
            history_record = UploadHistory(
                user_id=user_id,
                session_id=session_id,
                banco=banco,
                tipo_documento=tipo_documento,
                nome_arquivo=file.filename,
                nome_cartao=cartao,
                final_cartao=final_cartao,
                mes_fatura=mes_fatura,
                status='processing',
                data_upload=datetime.now()
            )
            history_record = self.repository.create_upload_history(history_record)
            logger.info(f"📝 Histórico criado: ID {history_record.id}")
            
            # Salvar arquivo temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
                content = file.file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                # ========== FASE 1: RAW PROCESSING ==========
                logger.info("📝 Fase 1: Processamento Raw")
                raw_transactions = self._fase1_raw_processing(
                    tmp_path,
                    banco,
                    tipo_documento,
                    file.filename,
                    cartao,
                    final_cartao
                )
                logger.info(f"  ✅ {len(raw_transactions)} transações brutas processadas")
                
                # Aplicar regras de exclusão
                raw_transactions = self._apply_exclusion_rules(
                    raw_transactions,
                    banco,
                    tipo_documento,
                    user_id
                )
                logger.info(f"  🚫 Após exclusões: {len(raw_transactions)} transações restantes")
                
                # Atualizar histórico com total_registros
                self.repository.update_upload_history(
                    history_record.id,
                    total_registros=len(raw_transactions)
                )
                
                # Salvar dados brutos no preview
                self._save_raw_to_preview(raw_transactions, session_id, user_id)
                logger.info(f"  💾 Dados brutos salvos no preview")
                
                # ========== FASE 2: ID MARKING ==========
                logger.info("🔖 Fase 2: Marcação de IDs")
                marked_count = self._fase2_marking(session_id, user_id)
                logger.info(f"  ✅ {marked_count} transações marcadas com IDs")
                
                # ========== FASE 3: CLASSIFICATION ==========
                logger.info("🎯 Fase 3: Classificação")
                stats = self._fase3_classification(session_id, user_id)
                logger.info(f"  ✅ {stats.total} transações classificadas")
                logger.info(f"  📊 Base Parcelas: {stats.base_parcelas} | Base Padrões: {stats.base_padroes} | Journal: {stats.journal_entries} | Marcas: {stats.marcas_gerais} | Não Classificado: {stats.nao_classificado}")
                
                # Atualizar histórico com classification_stats
                self.repository.update_upload_history(
                    history_record.id,
                    classification_stats={
                        'base_parcelas': stats.base_parcelas,
                        'base_padroes': stats.base_padroes,
                        'journal_entries': stats.journal_entries,
                        'marcas_gerais': stats.marcas_gerais,
                        'nao_classificado': stats.nao_classificado,
                    }
                )
                
            finally:
                # Limpar arquivo temporário
                os.unlink(tmp_path)
            
            logger.info(f"✅ Upload processado com sucesso! Session: {session_id}")
            
            return UploadPreviewResponse(
                success=True,
                sessionId=session_id,
                totalRegistros=len(raw_transactions),
                stats=stats
            )
            
        except HTTPException as http_exc:
            # Rollback: deletar session_id se falhou
            if session_id:
                logger.error(f"❌ Erro no processamento, fazendo rollback da sessão {session_id}")
                self.repository.delete_by_session_id(session_id, user_id)
            
            # Atualizar histórico com erro
            if history_record:
                self.repository.update_upload_history(
                    history_record.id,
                    status='error',
                    error_message=str(http_exc.detail)
                )
            raise
        except Exception as e:
            # Rollback: deletar session_id se falhou
            if session_id:
                logger.error(f"❌ Erro no processamento, fazendo rollback da sessão {session_id}")
                self.repository.delete_by_session_id(session_id, user_id)
            
            # Atualizar histórico com erro
            if history_record:
                self.repository.update_upload_history(
                    history_record.id,
                    status='error',
                    error_message=str(e)
                )
                self.repository.delete_by_session_id(session_id, user_id)
            
            logger.error(f"❌ Erro fatal: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "errorCode": "UPL_006",
                    "error": "Erro ao processar arquivo",
                    "details": str(e)
                }
            )
    
    def _apply_exclusion_rules(
        self,
        raw_transactions,
        banco: str,
        tipo_documento: str,
        user_id: int
    ):
        """
        Aplica regras de exclusão da tabela transacoes_exclusao
        Remove transações que têm regras com acao='EXCLUIR'
        
        Matching: nome_transacao normalizado contains regra normalizada
        """
        # Buscar regras ativas de exclusão
        exclusoes = self.db.query(TransacaoExclusao).filter(
            TransacaoExclusao.user_id == user_id,
            TransacaoExclusao.ativo == 1,
            TransacaoExclusao.acao.ilike('EXCLUIR')
        ).all()
        
        if not exclusoes:
            return raw_transactions
        
        logger.info(f"🔍 Aplicando {len(exclusoes)} regras de exclusão")
        
        # Filtrar transações
        transactions_filtered = []
        excluded_count = 0
        
        for transaction in raw_transactions:
            should_exclude = False
            lancamento_norm = normalizar(transaction.lancamento)
            
            for regra in exclusoes:
                # Verificar se banco corresponde (se especificado na regra)
                if regra.banco and normalizar(regra.banco) != normalizar(banco):
                    continue
                
                # Verificar tipo_documento (se especificado)
                # Regra pode ser: 'cartao', 'extrato', 'ambos', ou None
                if regra.tipo_documento:
                    tipo_regra_norm = normalizar(regra.tipo_documento)
                    if tipo_regra_norm not in ['ambos', 'todos']:
                        # Mapear 'fatura' -> 'cartao'
                        tipo_doc_norm = 'cartao' if tipo_documento == 'fatura' else normalizar(tipo_documento)
                        if tipo_regra_norm != tipo_doc_norm:
                            continue
                
                # Verificar se nome da transação contém o padrão da regra
                regra_norm = normalizar(regra.nome_transacao)
                if regra_norm in lancamento_norm:
                    should_exclude = True
                    excluded_count += 1
                    logger.debug(f"  ❌ Excluindo: {transaction.lancamento} (regra: {regra.nome_transacao})")
                    break
            
            if not should_exclude:
                transactions_filtered.append(transaction)
        
        logger.info(f"📊 Exclusões aplicadas: {excluded_count} de {len(raw_transactions)} transações")
        return transactions_filtered

    def _fase1_raw_processing(
        self,
        file_path: str,
        banco: str,
        tipo_documento: str,
        nome_arquivo: str,
        nome_cartao: str = None,
        final_cartao: str = None
    ):
        """
        Fase 1: Processa arquivo bruto usando processadores específicos
        """
        # Buscar processador adequado (normalização feita dentro de get_processor)
        processor = get_processor(banco, tipo_documento)
        
        if not processor:
            logger.warning(f"⚠️ Processador não encontrado para {banco}/{tipo_documento}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "errorCode": "UPL_004",
                    "error": f"Processador não disponível para {banco} / {tipo_documento}"
                }
            )
        
        # Processar arquivo
        try:
            file_path_obj = Path(file_path)
            raw_transactions = processor(
                file_path_obj,
                nome_arquivo,
                nome_cartao,
                final_cartao
            )
        except ValueError as e:
            # Erro de formato de arquivo (header não encontrado, estrutura incorreta)
            logger.warning(f"⚠️ Formato de arquivo inválido: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "errorCode": "UPL_005",
                    "error": "Formato de arquivo inválido",
                    "details": str(e)
                }
            )
        
        return raw_transactions
    
    def _save_raw_to_preview(self, raw_transactions, session_id: str, user_id: int):
        """
        Salva transações brutas no preview (Fase 1)
        """
        previews = []
        now = datetime.now()
        
        for raw in raw_transactions:
            preview = PreviewTransacao(
                session_id=session_id,
                user_id=user_id,
                # Campos da Fase 1
                banco=raw.banco,
                tipo_documento=raw.tipo_documento,
                nome_arquivo=raw.nome_arquivo,
                data_criacao=raw.data_criacao,
                data=raw.data,
                lancamento=raw.lancamento,
                valor=raw.valor,
                nome_cartao=raw.nome_cartao,
                cartao=raw.final_cartao,
                mes_fatura=raw.mes_fatura,
                created_at=now,
                # Campos das fases seguintes (NULL por enquanto)
                id_transacao=None,
                id_parcela=None,
                estabelecimento_base=None,
                parcela_atual=None,
                total_parcelas=None,
                valor_positivo=None,
                grupo=None,
                subgrupo=None,
                tipo_gasto=None,
                categoria_geral=None,
                origem_classificacao=None,
            )
            previews.append(preview)
        
        self.repository.create_batch(previews)
    
    def _fase2_marking(self, session_id: str, user_id: int) -> int:
        """
        Fase 2: Marca transações com IDs (IdTransacao, IdParcela)
        Atualiza registros existentes no preview
        """
        # Buscar registros do preview
        previews = self.repository.get_by_session_id(session_id, user_id)
        
        if not previews:
            return 0
        
        # Converter para RawTransaction
        from .processors.raw.base import RawTransaction
        raw_transactions = []
        for p in previews:
            raw = RawTransaction(
                banco=p.banco,
                tipo_documento=p.tipo_documento,
                nome_arquivo=p.nome_arquivo,
                data_criacao=p.data_criacao,
                data=p.data,
                lancamento=p.lancamento,
                valor=p.valor,
                nome_cartao=p.nome_cartao,
                final_cartao=p.cartao,
                mes_fatura=p.mes_fatura,
            )
            raw_transactions.append((p.id, raw))
        
        # Marcar com IDs
        marker = TransactionMarker()
        
        for preview_id, raw in raw_transactions:
            marked = marker.mark_transaction(raw)
            
            # Atualizar preview com dados marcados
            preview = self.db.query(PreviewTransacao).filter(
                PreviewTransacao.id == preview_id
            ).first()
            
            if preview:
                preview.id_transacao = marked.id_transacao
                preview.id_parcela = marked.id_parcela
                preview.estabelecimento_base = marked.estabelecimento_base
                preview.parcela_atual = marked.parcela_atual
                preview.total_parcelas = marked.total_parcelas
                preview.valor_positivo = marked.valor_positivo
                preview.updated_at = datetime.now()
        
        self.db.commit()
        return len(raw_transactions)
    
    def _fase3_classification(self, session_id: str, user_id: int) -> ClassificationStats:
        """
        Fase 3: Classifica transações em 5 níveis
        Atualiza registros existentes no preview
        """
        # Buscar registros marcados
        previews = self.repository.get_by_session_id(session_id, user_id)
        
        if not previews:
            return ClassificationStats(total=0)
        
        # Converter para MarkedTransaction
        from .processors.marker import MarkedTransaction
        marked_transactions = []
        for p in previews:
            marked = MarkedTransaction(
                # Raw fields
                banco=p.banco,
                tipo_documento=p.tipo_documento,
                nome_arquivo=p.nome_arquivo,
                data_criacao=p.data_criacao,
                data=p.data,
                lancamento=p.lancamento,
                valor=p.valor,
                nome_cartao=p.nome_cartao,
                final_cartao=p.cartao,
                mes_fatura=p.mes_fatura,
                # Marked fields
                id_transacao=p.id_transacao,
                estabelecimento_base=p.estabelecimento_base,
                valor_positivo=p.valor_positivo,
                id_parcela=p.id_parcela,
                parcela_atual=p.parcela_atual,
                total_parcelas=p.total_parcelas,
            )
            marked_transactions.append((p.id, marked))
        
        # Classificar
        classifier = CascadeClassifier(self.db, user_id)
        
        for preview_id, marked in marked_transactions:
            classified = classifier.classify(marked)
            
            # Atualizar preview com classificação
            preview = self.db.query(PreviewTransacao).filter(
                PreviewTransacao.id == preview_id
            ).first()
            
            if preview:
                preview.grupo = classified.grupo
                preview.subgrupo = classified.subgrupo
                preview.tipo_gasto = classified.tipo_gasto
                preview.categoria_geral = classified.categoria_geral
                preview.origem_classificacao = classified.origem_classificacao
                preview.updated_at = datetime.now()
        
        self.db.commit()
        
        # Retornar estatísticas
        stats_dict = classifier.get_stats()
        return ClassificationStats(
            total=stats_dict['total'],
            base_parcelas=stats_dict.get('Base Parcelas', 0),
            base_padroes=stats_dict.get('Base Padrões', 0),
            journal_entries=stats_dict.get('Journal Entries', 0),
            marcas_gerais=stats_dict.get('Marcas Gerais', 0),
            nao_classificado=stats_dict.get('Não Classificado', 0),
        )
    
    def get_preview_data(
        self,
        session_id: str,
        user_id: int
    ) -> GetPreviewResponse:
        """
        Retorna dados de preview de uma sessão
        
        Raises:
            HTTPException: Se sessão não encontrada
        """
        previews = self.repository.get_by_session_id(session_id, user_id)
        
        if not previews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_007", "error": "Sessão de preview não encontrada"}
            )
        
        dados = [PreviewTransacaoResponse.from_orm(p) for p in previews]
        
        return GetPreviewResponse(
            success=True,
            sessionId=session_id,
            totalRegistros=len(dados),
            dados=dados
        )
    
    def confirm_upload(
        self,
        session_id: str,
        user_id: int
    ) -> ConfirmUploadResponse:
        """
        Confirma upload e move dados para journal_entries
        FILTRA duplicatas (is_duplicate=False)
        
        Raises:
            HTTPException: Se sessão não encontrada
        """
        logger.info(f"📤 Confirmando upload: {session_id}")
        
        # Buscar histórico
        history = self.repository.get_upload_history_by_session(session_id, user_id)
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_008", "error": "Histórico de upload não encontrado"}
            )
        
        # Buscar dados de preview (filtrar não-duplicatas)
        previews = self.db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id,
            PreviewTransacao.is_duplicate == False
        ).all()
        
        if not previews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_009", "error": "Sessão de preview não encontrada ou todas duplicatas"}
            )
        
        try:
            # Importar JournalEntry
            from app.domains.transactions.models import JournalEntry
            
            transacoes_criadas = 0
            now = datetime.now()
            
            for item in previews:
                # Criar transação usando os dados já processados
                nova_transacao = JournalEntry(
                    user_id=user_id,
                    Data=item.data,
                    Estabelecimento=item.lancamento,
                    EstabelecimentoBase=item.estabelecimento_base,
                    Valor=item.valor,
                    ValorPositivo=item.valor_positivo,
                    MesFatura=item.mes_fatura.replace('-', '') if item.mes_fatura else None,
                    arquivo_origem=item.nome_arquivo,
                    banco_origem=item.banco,
                    NomeCartao=item.nome_cartao,
                    IdTransacao=item.id_transacao,
                    IdParcela=item.id_parcela,
                    parcela_atual=item.parcela_atual,
                    TotalParcelas=item.total_parcelas,
                    GRUPO=item.grupo,
                    SUBGRUPO=item.subgrupo,
                    TipoGasto=item.tipo_gasto,
                    CategoriaGeral=item.categoria_geral,
                    origem_classificacao=item.origem_classificacao,
                    tipodocumento=item.tipo_documento,
                    upload_history_id=history.id,  # ✅ Vincular ao histórico
                    created_at=now,
                    DataPostagem=now,
                )
                
                self.db.add(nova_transacao)
                transacoes_criadas += 1
            
            # Salvar todas as transações
            self.db.commit()
            logger.info(f"✅ {transacoes_criadas} transações salvas no journal_entries")
            
            # Contar duplicatas (total_registros - transacoes_criadas)
            total_duplicatas = history.total_registros - transacoes_criadas
            
            # Atualizar histórico: status='success', contadores, data_confirmacao
            self.repository.update_upload_history(
                history.id,
                status='success',
                transacoes_importadas=transacoes_criadas,
                transacoes_duplicadas=total_duplicatas,
                data_confirmacao=now
            )
            logger.info(f"📝 Histórico atualizado: {transacoes_criadas} importadas, {total_duplicatas} duplicadas")
            
            # Limpar dados de preview
            deleted = self.repository.delete_by_session_id(session_id, user_id)
            logger.info(f"🗑️  {deleted} registros de preview removidos")
            
            return ConfirmUploadResponse(
                success=True,
                sessionId=session_id,
                transacoesCriadas=transacoes_criadas,
                total=transacoes_criadas
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Erro ao confirmar upload: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "errorCode": "UPL_010",
                    "error": "Erro ao confirmar upload",
                    "details": str(e)
                }
            )
    
    def delete_preview(
        self,
        session_id: str,
        user_id: int
    ) -> DeletePreviewResponse:
        """
        Remove dados de preview de uma sessão
        Marca histórico como 'cancelled'
        """
        logger.info(f"🗑️  Deletando preview: {session_id}")
        
        # Atualizar histórico para 'cancelled'
        history = self.repository.get_upload_history_by_session(session_id, user_id)
        if history and history.status == 'processing':
            self.repository.update_upload_history(
                history.id,
                status='cancelled'
            )
            logger.info(f"  📝 Histórico marcado como cancelado")
        
        deleted_count = self.repository.delete_by_session_id(session_id, user_id)
        logger.info(f"  ✅ {deleted_count} registros removidos")
        
        return DeletePreviewResponse(
            success=True,
            sessionId=session_id,
            deletedCount=deleted_count
        )
    
    def get_upload_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> UploadHistoryListResponse:
        """
        Lista histórico de uploads do usuário
        """
        uploads = self.repository.list_upload_history(user_id, limit, offset)
        total = self.repository.count_upload_history(user_id)
        
        return UploadHistoryListResponse(
            success=True,
            total=total,
            uploads=[UploadHistoryResponse.from_orm(u) for u in uploads]
        )
