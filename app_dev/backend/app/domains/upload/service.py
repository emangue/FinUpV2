"""
Domínio Upload - Service
Lógica de negócio com pipeline em 3 fases
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
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
    BalanceValidationResponse,
)
from .history_schemas import UploadHistoryResponse, UploadHistoryListResponse
from .processors import get_processor
from .processors.marker import TransactionMarker
from .processors.classifier import CascadeClassifier
from app.domains.exclusoes.models import TransacaoExclusao
from app.domains.compatibility.service import CompatibilityService
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
        
        # Validações iniciais
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errorCode": "UPL_001", "error": "Arquivo não fornecido"}
            )
        
        # ========== VALIDAÇÃO DE COMPATIBILIDADE ==========
        logger.info(f"🔍 Validando compatibilidade: {banco} + {formato}")
        
        try:
            compatibility_service = CompatibilityService(self.db)
            validation = compatibility_service.validate_format(banco, formato)
            
            if not validation.is_supported:
                logger.warning(f"❌ Formato não suportado: {banco} + {formato} (status: {validation.status})")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "errorCode": "UPL_002",
                        "error": f"Formato {formato} não suportado para {banco}",
                        "status": validation.status,
                        "message": validation.message,
                        "suggestion": "Acesse Settings → Bancos para verificar formatos disponíveis"
                    }
                )
            
            logger.info(f"✅ Compatibilidade OK: {banco} + {formato}")
            
        except HTTPException as e:
            # Se erro 404 (banco não cadastrado) ou 400 (formato inválido), propagar
            if e.status_code in [404, 400]:
                raise
            # Outros erros de validação também propagam
            raise
        
        session_id = None
        history_record = None
        
        try:
            # SEMPRE limpar preview do usuário ANTES de processar
            deleted = self.repository.delete_all_by_user(user_id)
            if deleted > 0:
                logger.info(f"🗑️  Limpeza: {deleted} registros de preview removidos")
            
            # ========== NOVA FASE 0: REGENERAR PADRÕES ==========
            logger.info("🔄 Fase 0: Regeneração de Base Padrões")
            try:
                from app.domains.upload.processors.pattern_generator import regenerar_base_padroes_completa
                resultado = regenerar_base_padroes_completa(self.db, user_id)
                logger.info(f"  ✅ Padrões regenerados: {resultado['total_padroes_gerados']} gerados, {resultado['criados']} criados, {resultado['atualizados']} atualizados")
                logger.info("  🎯 Classificação usará padrões atualizados neste upload")
            except Exception as e:
                # NÃO bloquear upload se regeneração falhar
                logger.warning(f"  ⚠️ Erro na regeneração: {str(e)}")
                logger.warning("  📂 Continuando com padrões existentes...")
            
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
                raw_transactions, balance_validation = self._fase1_raw_processing(
                    tmp_path,
                    banco,
                    tipo_documento,
                    file.filename,
                    cartao,
                    final_cartao,
                    mes_fatura
                )
                logger.info(f"  ✅ {len(raw_transactions)} transações brutas processadas")
                
                # Log de validação de saldo (se houver)
                if balance_validation and balance_validation.saldo_inicial is not None:
                    logger.info(f"  💰 Saldo inicial: R$ {balance_validation.saldo_inicial:.2f}")
                    logger.info(f"  💰 Saldo final: R$ {balance_validation.saldo_final:.2f}")
                    logger.info(f"  💰 Soma transações: R$ {balance_validation.soma_transacoes:.2f}")
                    logger.info(f"  {'✅' if balance_validation.is_valid else '⚠️'} Validação: {balance_validation.is_valid} (diferença: R$ {balance_validation.diferenca:.2f})")
                
                # Aplicar regras de exclusão
                raw_transactions = self._apply_exclusion_rules(
                    raw_transactions,
                    banco,
                    tipo_documento,
                    user_id
                )
                logger.info(f"  🚫 Após exclusões: {len(raw_transactions)} transações restantes")
                
                # Preparar balance_validation_dict para salvar no histórico
                balance_validation_dict = None
                if balance_validation and balance_validation.saldo_inicial is not None:
                    balance_validation_dict = balance_validation.to_dict()
                
                # Atualizar histórico com total_registros e balance_validation
                self.repository.update_upload_history(
                    history_record.id,
                    total_registros=len(raw_transactions),
                    balance_validation=balance_validation_dict
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
                logger.info(f"  📊 Base Parcelas: {stats.base_parcelas} | Base Padrões: {stats.base_padroes} | Journal: {stats.journal_entries} | Regras Genéricas: {stats.regras_genericas} | Não Classificado: {stats.nao_classificado}")
                
                # ========== FASE 4: DEDUPLICATION ==========
                logger.info("🔍 Fase 4: Deduplicação")
                duplicates_count = self._fase4_deduplication(session_id, user_id)
                logger.info(f"  ✅ {duplicates_count} transações duplicadas identificadas")
                
                # Atualizar histórico com classification_stats
                self.repository.update_upload_history(
                    history_record.id,
                    classification_stats={
                        'base_parcelas': stats.base_parcelas,
                        'base_padroes': stats.base_padroes,
                        'journal_entries': stats.journal_entries,
                        'regras_genericas': stats.regras_genericas,
                        'nao_classificado': stats.nao_classificado,
                        'duplicadas': duplicates_count,
                    }
                )
                
            finally:
                # Limpar arquivo temporário
                os.unlink(tmp_path)
            
            logger.info(f"✅ Upload processado com sucesso! Session: {session_id}")
            
            # Preparar resposta com balance_validation (se disponível)
            response = UploadPreviewResponse(
                success=True,
                sessionId=session_id,
                totalRegistros=len(raw_transactions),
                stats=stats
            )
            
            # Adicionar validação de saldo se for extrato
            if balance_validation and balance_validation.saldo_inicial is not None:
                from .schemas import BalanceValidationResponse
                response.balance_validation = BalanceValidationResponse(**balance_validation.to_dict())
            
            return response
            
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
        
        Matching SIMPLIFICADO:
        1. Normaliza nome da transação e regra (sem acentos, uppercase)
        2. Se regra está contida no nome da transação → EXCLUIR
        3. Ignora verificações de banco e tipo (aplicar em TODOS)
        """
        # Buscar regras ativas de exclusão
        exclusoes = self.db.query(TransacaoExclusao).filter(
            TransacaoExclusao.user_id == user_id,
            TransacaoExclusao.ativo == 1,
            TransacaoExclusao.acao.ilike('EXCLUIR')
        ).all()
        
        if not exclusoes:
            logger.info("✅ Nenhuma regra de exclusão ativa")
            return raw_transactions
        
        logger.info(f"🔍 Aplicando {len(exclusoes)} regras de exclusão para user_id={user_id}")
        
        # Normalizar regras uma vez
        regras_normalizadas = [(regra, normalizar(regra.nome_transacao)) for regra in exclusoes]
        logger.info(f"  📋 Regras: {[r[1] for r in regras_normalizadas]}")
        
        # Filtrar transações
        transactions_filtered = []
        excluded_count = 0
        
        for transaction in raw_transactions:
            lancamento_norm = normalizar(transaction.lancamento)
            should_exclude = False
            
            # Verificar cada regra
            for regra, regra_norm in regras_normalizadas:
                if regra_norm in lancamento_norm:
                    should_exclude = True
                    excluded_count += 1
                    logger.info(f"  ❌ EXCLUÍDO: '{transaction.lancamento}' (matched regra: '{regra.nome_transacao}')")
                    break
            
            if not should_exclude:
                transactions_filtered.append(transaction)
        
        logger.info(f"📊 RESULTADO: {excluded_count} excluídas | {len(transactions_filtered)} mantidas (de {len(raw_transactions)} total)")
        return transactions_filtered

    def _fase1_raw_processing(
        self,
        file_path: str,
        banco: str,
        tipo_documento: str,
        nome_arquivo: str,
        nome_cartao: str = None,
        final_cartao: str = None,
        mes_fatura_input: str = None
    ):
        """
        Fase 1: Processa arquivo bruto usando processadores específicos
        
        Args:
            mes_fatura_input: Mês da fatura do Form (YYYY-MM) - usado apenas para faturas
        
        Returns:
            Tupla (raw_transactions, balance_validation)
            Para faturas: balance_validation será None
            Para extratos: balance_validation com dados de validação
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
            result = processor(
                file_path_obj,
                nome_arquivo,
                nome_cartao,
                final_cartao
            )
            
            # Verificar se retornou tupla (extrato com validação) ou lista (fatura)
            if isinstance(result, tuple):
                raw_transactions, balance_validation = result
            else:
                raw_transactions = result
                balance_validation = None
            
            # ========== GERAR MesFatura CORRETAMENTE ==========
            # EXTRATO: MesFatura = YYYYMM da Data da transação
            # FATURA: MesFatura = input do Form (YYYY-MM) convertido para YYYYMM
            for raw in raw_transactions:
                if tipo_documento == 'extrato':
                    # Extrair YYYYMM da Data (formato DD/MM/YYYY)
                    if raw.data and '/' in raw.data:
                        partes = raw.data.split('/')
                        if len(partes) == 3:
                            dia, mes, ano = partes
                            raw.mes_fatura = f"{ano}{mes.zfill(2)}"
                    else:
                        raw.mes_fatura = None
                else:
                    # Fatura: usar input do Form (YYYY-MM → YYYYMM)
                    if mes_fatura_input:
                        raw.mes_fatura = mes_fatura_input.replace('-', '')
                    else:
                        raw.mes_fatura = raw.mes_fatura  # Mantém o que veio do processador
                
            return raw_transactions, balance_validation
            
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
        
        return raw_transactions, None
    
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
                # Campos das fases seguintes (NULL por enquanto) - CamelCase
                IdTransacao=None,
                IdParcela=None,
                EstabelecimentoBase=None,
                ParcelaAtual=None,
                TotalParcelas=None,
                ValorPositivo=None,
                TipoTransacao=None,  # ✅ NOVO - Fase 2
                Ano=None,            # ✅ NOVO - Fase 2
                Mes=None,            # ✅ NOVO - Fase 2
                GRUPO=None,
                SUBGRUPO=None,
                TipoGasto=None,
                CategoriaGeral=None,
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
        
        # Marcar com IDs (v4.2.1 - passa user_id)
        marker = TransactionMarker(user_id=user_id)
        
        for preview_id, raw in raw_transactions:
            marked = marker.mark_transaction(raw)
            
            # Atualizar preview com dados marcados
            preview = self.db.query(PreviewTransacao).filter(
                PreviewTransacao.id == preview_id
            ).first()
            
            if preview:
                preview.IdTransacao = marked.id_transacao
                preview.IdParcela = marked.id_parcela
                preview.EstabelecimentoBase = marked.estabelecimento_base
                preview.ParcelaAtual = marked.parcela_atual
                preview.TotalParcelas = marked.total_parcelas
                preview.ValorPositivo = marked.valor_positivo
                preview.TipoTransacao = marked.tipo_transacao  # ✅ NOVO
                preview.Ano = marked.ano                        # ✅ NOVO
                preview.Mes = marked.mes                        # ✅ NOVO
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
                # Marked fields - ler do banco (CamelCase)
                id_transacao=p.IdTransacao,
                estabelecimento_base=p.EstabelecimentoBase,
                valor_positivo=p.ValorPositivo,
                id_parcela=p.IdParcela,
                parcela_atual=p.ParcelaAtual,
                total_parcelas=p.TotalParcelas,
                tipo_transacao=p.TipoTransacao,  # ✅ NOVO
                ano=p.Ano,                        # ✅ NOVO
                mes=p.Mes,                        # ✅ NOVO
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
                preview.GRUPO = classified.grupo
                preview.SUBGRUPO = classified.subgrupo
                preview.TipoGasto = classified.tipo_gasto
                preview.CategoriaGeral = classified.categoria_geral
                preview.origem_classificacao = classified.origem_classificacao
                preview.padrao_buscado = classified.padrao_buscado  # DEBUG
                preview.MarcacaoIA = classified.marcacao_ia  # Sugestão da base_marcacoes
                preview.updated_at = datetime.now()
        
        self.db.commit()
        
        # Retornar estatísticas
        stats_dict = classifier.get_stats()
        return ClassificationStats(
            total=stats_dict['total'],
            base_parcelas=stats_dict.get('base_parcelas', 0),
            base_padroes=stats_dict.get('base_padroes', 0),
            journal_entries=stats_dict.get('journal_entries', 0),
            regras_genericas=stats_dict.get('regras_genericas', 0),
            nao_classificado=stats_dict.get('nao_classificado', 0),
        )
    
    def _fase4_deduplication(self, session_id: str, user_id: int) -> int:
        """
        Fase 4: Identifica transações duplicadas
        Verifica se IdTransacao já existe em journal_entries
        Marca como duplicada e NÃO será importada
        
        Returns:
            Número de duplicatas encontradas
        """
        from app.domains.transactions.models import JournalEntry
        
        # Buscar registros do preview
        previews = self.repository.get_by_session_id(session_id, user_id)
        
        if not previews:
            return 0
        
        duplicates_count = 0
        
        for preview in previews:
            # Só verificar se tem IdTransacao
            if not preview.IdTransacao:
                continue
            
            # Verificar se já existe em journal_entries
            existing = self.db.query(JournalEntry).filter(
                JournalEntry.IdTransacao == preview.IdTransacao,
                JournalEntry.user_id == user_id
            ).first()
            
            if existing:
                # Marcar como duplicada
                preview.is_duplicate = True
                preview.duplicate_reason = f"IdTransacao já existe em journal_entries (ID: {existing.id}, Data: {existing.Data})"
                # IMPORTANTE: Limpar origem_classificacao para evitar aparecer em múltiplas abas
                # Duplicatas devem aparecer APENAS na aba "Duplicadas"
                preview.origem_classificacao = None
                duplicates_count += 1
                logger.debug(f"  🔍 Duplicata: {preview.data} - {preview.lancamento} (IdTransacao: {preview.IdTransacao})")
        
        self.db.commit()
        return duplicates_count
    
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
        
        # Buscar metadados do upload history
        history = self.repository.get_upload_history_by_session(session_id, user_id)
        
        # Preparar balance_validation se existir
        balance_validation_response = None
        if history and history.balance_validation:
            balance_validation_response = BalanceValidationResponse(**history.balance_validation)
        
        return GetPreviewResponse(
            success=True,
            sessionId=session_id,
            totalRegistros=len(dados),
            dados=dados,
            # Metadados do upload
            banco=history.banco if history else None,
            tipo_documento=history.tipo_documento if history else None,
            nome_arquivo=history.nome_arquivo if history else None,
            nome_cartao=history.nome_cartao if history else None,
            mes_fatura=history.mes_fatura if history else None,
            balance_validation=balance_validation_response
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
                    EstabelecimentoBase=item.EstabelecimentoBase,  # ✅ CamelCase
                    Valor=item.valor,
                    ValorPositivo=item.ValorPositivo,  # ✅ CamelCase
                    MesFatura=item.mes_fatura.replace('-', '') if item.mes_fatura else None,
                    arquivo_origem=item.nome_arquivo,
                    banco_origem=item.banco,
                    NomeCartao=item.nome_cartao,
                    IdTransacao=item.IdTransacao,  # ✅ CamelCase
                    IdParcela=item.IdParcela,  # ✅ CamelCase
                    parcela_atual=item.ParcelaAtual,  # ✅ CamelCase
                    TotalParcelas=item.TotalParcelas,  # ✅ CamelCase
                    GRUPO=item.GRUPO,  # ✅ CamelCase
                    SUBGRUPO=item.SUBGRUPO,  # ✅ CamelCase
                    TipoGasto=item.TipoGasto,  # ✅ CamelCase
                    CategoriaGeral=item.CategoriaGeral,  # ✅ CamelCase
                    origem_classificacao=item.origem_classificacao,
                    tipodocumento=item.tipo_documento,
                    TipoTransacao=item.TipoTransacao,    # ✅ CamelCase
                    Ano=item.Ano,                        # ✅ CamelCase
                    Mes=item.Mes,                        # ✅ CamelCase
                    session_id=session_id,               # ✅ RASTREAMENTO
                    upload_history_id=history.id,        # ✅ RASTREAMENTO
                    created_at=now,
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
            
            # ========== NOVA FASE 5: ATUALIZAR BASE_PARCELAS ==========
            logger.info("🔄 Fase 5: Atualização de Base Parcelas")
            try:
                resultado_parcelas = self._fase5_update_base_parcelas(user_id, history.id)
                logger.info(f"  ✅ Parcelas processadas: {resultado_parcelas['total_processadas']} | Atualizadas: {resultado_parcelas['atualizadas']} | Novas: {resultado_parcelas['novas']} | Finalizadas: {resultado_parcelas['finalizadas']}")
            except Exception as e:
                # NÃO bloquear confirmação se atualização falhar
                logger.warning(f"  ⚠️ Erro na atualização de parcelas: {str(e)}")
            
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
    
    def update_preview_classification(
        self,
        session_id: str,
        preview_id: int,
        grupo: Optional[str],
        subgrupo: Optional[str],
        user_id: int
    ):
        """
        Atualiza classificação manual (grupo/subgrupo) de um registro de preview
        """
        logger.info(f"📝 Atualizando classificação manual: preview_id={preview_id}, grupo={grupo}, subgrupo={subgrupo}")
        
        # Buscar preview
        preview = self.db.query(PreviewTransacao).filter(
            PreviewTransacao.id == preview_id,
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).first()
        
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_010", "error": "Registro de preview não encontrado"}
            )
        
        # Atualizar campos
        if grupo is not None:
            preview.GRUPO = grupo
        if subgrupo is not None:
            preview.SUBGRUPO = subgrupo
        
        # Atualizar origem se foi modificado manualmente
        if grupo or subgrupo:
            preview.origem_classificacao = 'Manual'
        
        self.db.commit()
        self.db.refresh(preview)
        
        return {
            "success": True,
            "preview_id": preview_id,
            "grupo": preview.GRUPO,
            "subgrupo": preview.SUBGRUPO,
            "origem_classificacao": preview.origem_classificacao
        }
    
    def _fase5_update_base_parcelas(self, user_id: int, upload_history_id: int) -> dict:
        """
        Fase 5: Atualiza base_parcelas após confirmar upload
        
        Lógica:
        1. Busca transações parceladas do upload atual
        2. Para cada IdParcela:
           - Se existe: atualiza qtd_pagas
           - Se não existe: cria nova entrada
        
        Args:
            user_id: ID do usuário
            upload_history_id: ID do histórico de upload
        
        Returns:
            dict com contadores
        """
        from app.domains.transactions.models import JournalEntry, BaseParcelas
        
        # Buscar transações parceladas do upload atual
        transacoes_parceladas = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.upload_history_id == upload_history_id,
            JournalEntry.IdParcela.isnot(None),
            JournalEntry.TotalParcelas > 1
        ).all()
        
        if not transacoes_parceladas:
            return {'atualizadas': 0, 'novas': 0}
        
        atualizadas = 0
        novas = 0
        finalizadas = 0
        
        for transacao in transacoes_parceladas:
            # Verificar se IdParcela já existe
            parcela_existente = self.db.query(BaseParcelas).filter(
                BaseParcelas.user_id == user_id,
                BaseParcelas.id_parcela == transacao.IdParcela
            ).first()
            
            if parcela_existente:
                # ATUALIZAR qtd_pagas e status se necessário
                if transacao.parcela_atual > parcela_existente.qtd_pagas:
                    # Atualizar quantidade de parcelas pagas
                    parcela_existente.qtd_pagas = transacao.parcela_atual
                    
                    # Atualizar status baseado no progresso
                    if transacao.parcela_atual >= transacao.TotalParcelas:
                        parcela_existente.status = 'finalizada'
                        status_desc = "finalizada"
                        finalizadas += 1
                    else:
                        parcela_existente.status = 'ativa'
                        status_desc = "ativa"
                    
                    # Atualizar data da última atualização
                    parcela_existente.updated_at = datetime.now()
                    
                    atualizadas += 1
                    logger.debug(f"  📝 Atualizada: {transacao.IdParcela} (parcela {transacao.parcela_atual}/{transacao.TotalParcelas}) → {status_desc}")
            
            else:
                # INSERIR nova compra parcelada
                # Buscar categoria_geral via grupo
                categoria_geral = self._get_categoria_geral_from_grupo(transacao.GRUPO)
                
                # Determinar status inicial baseado no progresso
                if transacao.parcela_atual >= transacao.TotalParcelas:
                    status_inicial = 'finalizada'
                    status_desc = "finalizada"
                    finalizadas += 1
                else:
                    status_inicial = 'ativa'
                    status_desc = "ativa"
                
                nova_parcela = BaseParcelas(
                    user_id=user_id,
                    id_parcela=transacao.IdParcela,
                    estabelecimento_base=transacao.EstabelecimentoBase,
                    valor_parcela=transacao.ValorPositivo,
                    qtd_parcelas=transacao.TotalParcelas,
                    qtd_pagas=transacao.parcela_atual,
                    valor_total_plano=transacao.ValorPositivo * transacao.TotalParcelas,
                    grupo_sugerido=transacao.GRUPO,
                    subgrupo_sugerido=transacao.SUBGRUPO,
                    tipo_gasto_sugerido=transacao.TipoGasto,
                    categoria_geral_sugerida=categoria_geral,
                    data_inicio=transacao.Data,
                    status=status_inicial,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.db.add(nova_parcela)
                novas += 1
                logger.debug(f"  ➕ Nova parcela: {transacao.IdParcela} ({transacao.TotalParcelas}x R${transacao.ValorPositivo:.2f}) → {status_desc}")
        
        self.db.commit()
        
        return {
            'atualizadas': atualizadas, 
            'novas': novas,
            'finalizadas': finalizadas,
            'total_processadas': atualizadas + novas
        }
    
    def _get_categoria_geral_from_grupo(self, grupo: str) -> str:
        """
        Busca CategoriaGeral correspondente ao Grupo via base_grupos_config
        """
        from sqlalchemy import text
        
        if not grupo:
            return 'Despesa'  # Fallback padrão
        
        result = self.db.execute(
            text("SELECT categoria_geral FROM base_grupos_config WHERE nome_grupo = :grupo"),
            {"grupo": grupo}
        ).fetchone()
        
        return result[0] if result else 'Despesa'
