"""
Domínio Transactions - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException
from datetime import datetime, timedelta
from .repository import TransactionRepository
from .models import JournalEntry
from .schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionFilters,
    TransactionListResponse,
    TiposGastoComMediaResponse,
    TipoGastoComMedia
)

class TransactionService:
    """
    Service layer para transações
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def get_transaction(self, transaction_id: str, user_id: int) -> TransactionResponse:
        """
        Busca uma transação por ID
        
        Raises:
            HTTPException: Se transação não encontrada
        """
        transaction = self.repository.get_by_id(transaction_id, user_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction {transaction_id} not found"
            )
        return TransactionResponse.from_orm(transaction)
    
    def list_transactions(
        self,
        user_id: int,
        filters: Optional[TransactionFilters] = None,
        page: int = 1,
        limit: int = 10
    ) -> TransactionListResponse:
        """
        Lista transações com filtros e paginação
        """
        skip = (page - 1) * limit
        
        if filters:
            transactions = self.repository.list_with_filters(
                user_id, filters, skip, limit
            )
            total = self.repository.count_with_filters(user_id, filters)
        else:
            transactions = self.repository.list_all(user_id, skip, limit)
            total = self.repository.count_with_filters(
                user_id, TransactionFilters()
            )
        
        return TransactionListResponse(
            transactions=[TransactionResponse.from_orm(t) for t in transactions],
            total=total,
            page=page,
            limit=limit
        )
    
    def create_transaction(
        self,
        transaction_data: TransactionCreate
    ) -> TransactionResponse:
        """
        Cria nova transação
        
        Lógica de negócio:
        - Calcula ValorPositivo
        - Define Ano baseado em Data
        - Etc.
        """
        # Criar modelo
        transaction = JournalEntry(**transaction_data.dict())
        
        # Lógica de negócio: calcular ValorPositivo
        transaction.ValorPositivo = abs(transaction.Valor)
        
        # Extrair ano da data (formato DD/MM/YYYY)
        if transaction.Data and "/" in transaction.Data:
            parts = transaction.Data.split("/")
            if len(parts) == 3:
                transaction.Ano = int(parts[2])
        
        # Salvar
        created = self.repository.create(transaction)
        return TransactionResponse.from_orm(created)
    
    def update_transaction(
        self,
        transaction_id: str,
        user_id: int,
        update_data: TransactionUpdate
    ) -> TransactionResponse:
        """
        Atualiza transação
        
        Raises:
            HTTPException: Se transação não encontrada
        """
        # Buscar transação
        transaction = self.repository.get_by_id(transaction_id, user_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction {transaction_id} not found"
            )
        
        # Aplicar mudanças (apenas campos não-None)
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(transaction, field, value)
        
        # Recalcular ValorPositivo se Valor mudou
        if "Valor" in update_dict:
            transaction.ValorPositivo = abs(transaction.Valor)
        
        # Salvar
        updated = self.repository.update(transaction)
        return TransactionResponse.from_orm(updated)
    
    def delete_transaction(
        self,
        transaction_id: str,
        user_id: int
    ) -> dict:
        """
        Deleta transação
        
        Raises:
            HTTPException: Se transação não encontrada
        """
        transaction = self.repository.get_by_id(transaction_id, user_id)
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction {transaction_id} not found"
            )
        
        self.repository.delete(transaction)
        return {"message": "Transaction deleted successfully"}
    
    def get_filtered_total(
        self,
        user_id: int,
        filters: TransactionFilters
    ) -> dict:
        """
        Retorna soma total de valores filtrados
        """
        total = self.repository.get_total_by_filters(user_id, filters)
        return {
            "total": total,
            "filters": filters.dict(exclude_none=True)
        }
    
    def get_tipos_gasto_com_media(
        self,
        user_id: int,
        mes_referencia: str
    ) -> TiposGastoComMediaResponse:
        """
        Retorna tipos de gasto únicos de Despesa com média dos últimos 3 meses
        
        Args:
            user_id: ID do usuário
            mes_referencia: Mês de referência no formato YYYY-MM
            
        Returns:
            TiposGastoComMediaResponse com lista de tipos e suas médias
        """
        # Converter mes_referencia para datetime
        ano, mes = map(int, mes_referencia.split('-'))
        
        # Calcular os 3 meses anteriores ao mês de referência
        meses_anteriores = []
        for i in range(1, 4):  # 3 meses atrás
            m = mes - i
            a = ano
            if m < 1:
                m += 12
                a -= 1
            meses_anteriores.append(f"{a:04d}-{m:02d}")
        
        print(f"DEBUG: Meses anteriores: {meses_anteriores}")  # Debug
        
        # Buscar transações de Despesa dos últimos 3 meses
        # Data está em formato dd/mm/yyyy, então extraímos ano-mês: substr(7,4) + '-' + substr(4,2)
        from sqlalchemy import or_
        
        # Criar condição para cada mês
        condicoes_meses = []
        for mes_anterior in meses_anteriores:
            ano_mes, mes_num = mes_anterior.split('-')
            # Formato: dd/mm/yyyy → substr(4,2)=mm, substr(7,4)=yyyy
            condicao = func.concat(
                func.substr(JournalEntry.Data, 7, 4),  # ano
                '-',
                func.substr(JournalEntry.Data, 4, 2)   # mês
            ) == mes_anterior
            condicoes_meses.append(condicao)
        
        transacoes = self.repository.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.TipoGasto.isnot(None),
            JournalEntry.Valor < 0,  # Apenas saídas
            or_(*condicoes_meses)
        ).all()
        
        print(f"DEBUG: Total de transações encontradas: {len(transacoes)}")  # Debug
        
        # Se não encontrou transações, buscar todos os tipos de gasto que já existem no sistema
        if not transacoes:
            # Buscar tipos únicos de todas as transações de Despesa do usuário
            tipos_unicos = self.repository.db.query(JournalEntry.TipoGasto).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.CategoriaGeral == 'Despesa',
                JournalEntry.TipoGasto.isnot(None)
            ).distinct().all()
            
            tipos_com_media = []
            for (tipo_gasto,) in sorted(tipos_unicos):
                tipos_com_media.append(TipoGastoComMedia(
                    tipo_gasto=tipo_gasto,
                    media_3_meses=0.0
                ))
            
            return TiposGastoComMediaResponse(
                tipos_gasto=tipos_com_media,
                mes_referencia=mes_referencia
            )
        
        # Agrupar por TipoGasto e contar em quantos meses aparece
        somas_por_tipo = {}
        meses_por_tipo = {}
        for t in transacoes:
            if t.TipoGasto not in somas_por_tipo:
                somas_por_tipo[t.TipoGasto] = 0
                meses_por_tipo[t.TipoGasto] = set()
            somas_por_tipo[t.TipoGasto] += abs(t.Valor)
            # Extrair mês-ano da transação para contar meses únicos
            mes_transacao = t.Data[3:10] if len(t.Data) >= 10 else None
            if mes_transacao:
                meses_por_tipo[t.TipoGasto].add(mes_transacao)
        
        # Calcular média real (soma / quantidade de meses com dados)
        tipos_com_media = []
        for tipo_gasto, soma in sorted(somas_por_tipo.items()):
            qtd_meses = len(meses_por_tipo[tipo_gasto])
            media = soma / qtd_meses if qtd_meses > 0 else 0
            tipos_com_media.append(TipoGastoComMedia(
                tipo_gasto=tipo_gasto,
                media_3_meses=round(media, 2)
            ))
        
        return TiposGastoComMediaResponse(
            tipos_gasto=tipos_com_media,
            mes_referencia=mes_referencia
        )
