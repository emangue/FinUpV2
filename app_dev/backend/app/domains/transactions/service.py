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
        
        # Recalcular CategoriaGeral se GRUPO mudou
        if "GRUPO" in update_dict:
            transaction.CategoriaGeral = self._determine_categoria_geral(
                transaction.GRUPO, 
                transaction.Valor
            )
        
        # Salvar
        updated = self.repository.update(transaction)
        return TransactionResponse.from_orm(updated)
    
    def _determine_categoria_geral(self, grupo: Optional[str], valor: float) -> Optional[str]:
        """
        Determina CategoriaGeral baseado no GRUPO e valor da transação
        
        Regras:
        - Transferência Entre Contas → Transferência
        - Investimentos → Investimentos
        - Valor positivo → Receita
        - Valor negativo → Despesa
        """
        if not grupo:
            return None
        
        # Normalizar grupo para comparação
        grupo_lower = grupo.lower().strip()
        
        # Regra 1: Transferência
        if 'transferencia' in grupo_lower or 'transferência' in grupo_lower:
            return 'Transferência'
        
        # Regra 2: Investimentos
        if 'investimento' in grupo_lower:
            return 'Investimentos'
        
        # Regra 3: Baseado no sinal do valor
        if valor >= 0:
            return 'Receita'
        else:
            return 'Despesa'
    
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
        Retorna tipos de gasto únicos de Despesa com média PRÉ-CALCULADA da tabela budget_planning
        
        ⚡ OTIMIZAÇÃO: Usa valores pré-calculados em vez de calcular em tempo real
        
        Args:
            user_id: ID do usuário
            mes_referencia: Mês de referência no formato YYYY-MM
            
        Returns:
            TiposGastoComMediaResponse com lista de tipos e suas médias PRÉ-CALCULADAS
        """
        from app.domains.budget.models import BudgetPlanning
        
        # Buscar médias PRÉ-CALCULADAS da tabela budget_planning
        planning_records = self.repository.db.query(BudgetPlanning).filter(
            BudgetPlanning.user_id == user_id,
            BudgetPlanning.mes_referencia == mes_referencia,
            BudgetPlanning.valor_medio_3_meses > 0  # Apenas com média válida
        ).all()
        
        print(f"⚡ OTIMIZADO: Encontrados {len(planning_records)} registros pré-calculados")  # Debug
        
        # Se não encontrou médias pré-calculadas, buscar todos os tipos de gasto disponíveis
        if not planning_records:
            print(f"⚠️ AVISO: Nenhum valor pré-calculado para {mes_referencia}. Buscar tipos únicos...")
            
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
        
        # Construir resposta a partir dos valores PRÉ-CALCULADOS
        tipos_com_media = []
        for record in sorted(planning_records, key=lambda x: x.tipo_gasto):
            tipos_com_media.append(TipoGastoComMedia(
                tipo_gasto=record.tipo_gasto,
                media_3_meses=round(record.valor_medio_3_meses, 2)
            ))
        
        print(f"✅ Retornando {len(tipos_com_media)} tipos de gasto com médias pré-calculadas")
        
        return TiposGastoComMediaResponse(
            tipos_gasto=tipos_com_media,
            mes_referencia=mes_referencia
        )
