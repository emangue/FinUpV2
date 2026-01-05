"""
Domínio Upload - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from typing import List, Tuple
from fastapi import HTTPException, status, UploadFile
from datetime import datetime
import tempfile
import os
import pandas as pd
import uuid

from .repository import UploadRepository
from .models import PreviewTransacao
from .schemas import (
    PreviewTransacaoResponse,
    UploadPreviewResponse,
    GetPreviewResponse,
    ConfirmUploadResponse,
    DeletePreviewResponse,
    ProcessorResult
)

class UploadService:
    """
    Service layer para upload
    Contém TODA a lógica de negócio
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
        tipo_documento: str = "fatura",
        formato: str = "csv"
    ) -> UploadPreviewResponse:
        """
        Processa arquivo e cria preview
        
        Lógica de negócio:
        - Limpa previews antigos do usuário
        - Salva arquivo temporariamente
        - Processa com processador específico
        - Salva em preview_transacoes
        - Retorna session_id
        
        Raises:
            HTTPException: Se dados inválidos ou erro no processamento
        """
        # Validações
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
        
        if not mes_fatura:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errorCode": "UPL_003", "error": "Mês fatura não especificado"}
            )
        
        try:
            # Limpar previews antigos
            deleted = self.repository.delete_all_by_user(user_id)
            if deleted > 0:
                print(f"🗑️  Limpeza: {deleted} registros de preview removidos")
            
            # Salvar arquivo temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
                content = file.file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Processar arquivo
            dados_processados = self._process_file(
                tmp_path,
                banco,
                tipo_documento,
                formato
            )
            
            os.unlink(tmp_path)  # Limpar arquivo temporário
            
            # Gerar session_id único
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            
            # Criar previews
            previews = []
            now = datetime.now()
            for row in dados_processados:
                preview = PreviewTransacao(
                    session_id=session_id,
                    user_id=user_id,
                    banco=banco,
                    cartao=cartao or 'N/A',
                    nome_arquivo=file.filename,
                    mes_fatura=mes_fatura,
                    data=row.data,
                    lancamento=row.lancamento,
                    valor=row.valor,
                    created_at=now
                )
                previews.append(preview)
            
            self.repository.create_batch(previews)
            
            print(f"✅ Upload processado: {len(dados_processados)} transações | Session: {session_id}")
            
            return UploadPreviewResponse(
                success=True,
                sessionId=session_id,
                totalRegistros=len(dados_processados)
            )
            
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
        
        Lógica de negócio:
        - Busca dados de preview
        - Cria transações no journal_entries
        - Limpa dados de preview
        
        Raises:
            HTTPException: Se sessão não encontrada
        """
        # Buscar dados de preview
        previews = self.repository.get_by_session_id(session_id, user_id)
        
        if not previews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errorCode": "UPL_009", "error": "Sessão de preview não encontrada"}
            )
        
        try:
            # Importar JournalEntry do domínio transactions
            from app.domains.transactions.models import JournalEntry
            
            transacoes_criadas = 0
            now = datetime.now()
            
            for item in previews:
                # Gerar IdTransacao único
                id_transacao = f"{item.banco}_{item.mes_fatura}_{item.data}_{uuid.uuid4().hex[:8]}"
                
                # Criar transação
                nova_transacao = JournalEntry(
                    user_id=user_id,
                    Data=item.data,
                    Estabelecimento=item.lancamento,
                    Valor=item.valor,
                    ValorPositivo=abs(item.valor),
                    MesFatura=item.mes_fatura.replace('-', ''),  # YYYY-MM -> YYYYMM
                    arquivo_origem=item.nome_arquivo,
                    banco_origem=item.banco,
                    NomeCartao=item.cartao if item.cartao != 'N/A' else None,
                    IdTransacao=id_transacao,
                    created_at=now
                )
                
                self.db.add(nova_transacao)
                transacoes_criadas += 1
            
            # Salvar todas as transações
            self.db.commit()
            
            # Limpar dados de preview
            self.repository.delete_by_session_id(session_id, user_id)
            
            print(f"✅ Upload confirmado: {transacoes_criadas} transações criadas")
            
            return ConfirmUploadResponse(
                success=True,
                sessionId=session_id,
                transacoesCriadas=transacoes_criadas,
                total=transacoes_criadas
            )
            
        except Exception as e:
            self.db.rollback()
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
        """
        deleted_count = self.repository.delete_by_session_id(session_id, user_id)
        
        return DeletePreviewResponse(
            success=True,
            sessionId=session_id,
            deletedCount=deleted_count
        )
    
    def _process_file(
        self,
        file_path: str,
        banco: str,
        tipo: str,
        formato: str
    ) -> List[ProcessorResult]:
        """
        Processa arquivo com processador específico
        
        TODO: Implementar processadores específicos por banco
        Por enquanto, apenas lê CSV simples
        """
        try:
            # Lógica simplificada - assumir CSV com colunas: data, descricao, valor
            if formato == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Assumir formato padrão por enquanto
            # TODO: Implementar processadores específicos
            results = []
            for _, row in df.iterrows():
                results.append(ProcessorResult(
                    data=str(row.get('data', row.get('Data', ''))),
                    lancamento=str(row.get('descricao', row.get('lancamento', row.get('Estabelecimento', '')))),
                    valor=float(row.get('valor', row.get('Valor', 0)))
                ))
            
            return results
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "errorCode": "UPL_005",
                    "error": f"Erro ao processar arquivo: {str(e)}"
                }
            )
