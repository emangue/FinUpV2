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
from app.shared.utils import determine_categoria_geral

class TransactionService:
    """
    Service layer para transações
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def get_grupo_breakdown(self, user_id: int, grupo: str, year: int, month: int) -> dict:
        """
        Retorna breakdown de subgrupos de um grupo específico com valores agregados
        
        Args:
            user_id: ID do usuário
            grupo: Nome do grupo (ex: "Cartão de Crédito")
            year: Ano
            month: Mês
            
        Returns:
            dict com grupo, total, e lista de subgrupos com valores e percentuais
        """
        from sqlalchemy import func
        
        # Formatar MesFatura (YYYYMM)
        mes_fatura = f"{year}{str(month).zfill(2)}"
        
        # Query: agregar por subgrupo
        results = self.repository.db.query(
            JournalEntry.SUBGRUPO,
            func.sum(JournalEntry.Valor).label('total'),
            func.count(JournalEntry.IdTransacao).label('quantidade')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo,
            JournalEntry.MesFatura == mes_fatura,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0
        ).group_by(
            JournalEntry.SUBGRUPO
        ).order_by(
            func.sum(JournalEntry.Valor).desc()
        ).all()
        
        # Calcular total geral
        total_geral = sum(r.total for r in results)
        
        # Formatar resposta
        subgrupos = [
            {
                "subgrupo": r.SUBGRUPO or "Sem subgrupo",
                "valor": float(r.total),
                "percentual": round((float(r.total) / total_geral * 100), 2) if total_geral > 0 else 0,
                "quantidade_transacoes": r.quantidade
            }
            for r in results
        ]
        
        return {
            "grupo": grupo,
            "total": float(total_geral),
            "subgrupos": subgrupos
        }
    
    def get_all_grupos_breakdown(self, user_id: int, data_inicio: str, data_fim: str) -> dict:
        """
        Retorna breakdown de gastos por grupo em um período
        
        Args:
            user_id: ID do usuário
            data_inicio: Data início (YYYY-MM-DD)
            data_fim: Data fim (YYYY-MM-DD)
            
        Returns:
            dict com grupos: {grupo: {total, transacoes}}
        """
        from sqlalchemy import func
        from datetime import datetime
        
        # Converter strings de data para datetime
        try:
            dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Converter para MesFatura (YYYYMM)
        mes_fatura_inicio = dt_inicio.strftime('%Y%m')
        mes_fatura_fim = dt_fim.strftime('%Y%m')
        
        # Query: agregar por grupo
        results = self.repository.db.query(
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total'),
            func.count(JournalEntry.IdTransacao).label('quantidade')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.MesFatura >= mes_fatura_inicio,
            JournalEntry.MesFatura <= mes_fatura_fim,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.GRUPO.isnot(None)
        ).group_by(JournalEntry.GRUPO).all()
        
        # Montar dict de grupos
        grupos = {}
        for row in results:
            if row.GRUPO:
                grupos[row.GRUPO] = {
                    "total": abs(float(row.total)),
                    "transacoes": row.quantidade
                }
        
        return {
            "grupos": grupos,
            "periodo": {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }
        }
    
    def get_receitas_despesas(self, user_id: int, data_inicio: str, data_fim: str) -> dict:
        """
        Retorna total de receitas, despesas e investimentos em um período
        
        Args:
            user_id: ID do usuário
            data_inicio: Data início (YYYY-MM-DD)
            data_fim: Data fim (YYYY-MM-DD)
            
        Returns:
            dict com receitas, despesas, investimentos e saldo
        """
        from sqlalchemy import func
        from datetime import datetime
        
        # Converter strings de data para datetime
        try:
            dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Converter para MesFatura (YYYYMM)
        mes_fatura_inicio = dt_inicio.strftime('%Y%m')
        mes_fatura_fim = dt_fim.strftime('%Y%m')
        
        # Buscar receitas
        receitas_result = self.repository.db.query(
            func.sum(JournalEntry.ValorPositivo).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.MesFatura >= mes_fatura_inicio,
            JournalEntry.MesFatura <= mes_fatura_fim,
            JournalEntry.CategoriaGeral == 'Receita',
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        # Buscar despesas
        despesas_result = self.repository.db.query(
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.MesFatura >= mes_fatura_inicio,
            JournalEntry.MesFatura <= mes_fatura_fim,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        # Buscar investimentos
        # Valores negativos = aplicações (saídas)
        # Valores positivos = resgates (entradas)
        # Multiplicar por -1 para mostrar total investido como positivo
        investimentos_result = self.repository.db.query(
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.MesFatura >= mes_fatura_inicio,
            JournalEntry.MesFatura <= mes_fatura_fim,
            JournalEntry.CategoriaGeral == 'Investimentos',
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        receitas = float(receitas_result or 0)
        despesas = abs(float(despesas_result or 0))
        investimentos = abs(float(investimentos_result or 0))  # * -1 já está nos valores, só precisamos do abs()
        saldo = receitas - despesas  # Investimentos NÃO entram no saldo (mostrados separadamente)
        
        return {
            "receitas": receitas,
            "despesas": despesas,
            "investimentos": investimentos,
            "saldo": saldo,
            "periodo": {
                "data_inicio": data_inicio,
                "data_fim": data_fim
            }
        }
    
    
    
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
        
        # Se mudou GRUPO ou SUBGRUPO manualmente, marcar como Manual
        if "GRUPO" in update_dict or "SUBGRUPO" in update_dict:
            transaction.origem_classificacao = "Manual"
        
        # Recalcular ValorPositivo se Valor mudou
        if "Valor" in update_dict:
            transaction.ValorPositivo = abs(transaction.Valor)
        
        # Se GRUPO ou SUBGRUPO mudaram, buscar TipoGasto na base_marcacoes
        if "GRUPO" in update_dict or "SUBGRUPO" in update_dict:
            # Buscar TipoGasto e CategoriaGeral da base_grupos_config
            if transaction.GRUPO:
                from app.domains.grupos.models import BaseGruposConfig
                grupo_config = self.repository.db.query(BaseGruposConfig).filter(
                    BaseGruposConfig.nome_grupo == transaction.GRUPO
                ).first()
                
                if grupo_config:
                    transaction.TipoGasto = grupo_config.tipo_gasto_padrao
                    transaction.CategoriaGeral = grupo_config.categoria_geral
            
            # Inserir automaticamente em base_marcacoes se não existir
            if transaction.GRUPO and transaction.SUBGRUPO and transaction.TipoGasto:
                self._ensure_marcacao_exists(
                    grupo=transaction.GRUPO,
                    subgrupo=transaction.SUBGRUPO,
                    tipo_gasto=transaction.TipoGasto,
                    user_id=user_id
                )
        
        # Salvar
        updated = self.repository.update(transaction)
        return TransactionResponse.from_orm(updated)
    
    def _buscar_tipo_gasto_base_marcacoes(
        self, 
        grupo: Optional[str], 
        subgrupo: Optional[str],
        valor: float
    ) -> Optional[str]:
        """
        Busca TipoGasto na base_marcacoes baseado em GRUPO e SUBGRUPO
        
        Para combinações com múltiplos TipoGasto (ex: Outros | Outros),
        usa o valor da transação para decidir:
        - Valor >= 0 → Receita - Outras
        - Valor < 0 → Ajustável (despesa)
        """
        if not grupo or not subgrupo:
            return None
        
        from app.domains.categories.models import BaseMarcacao
        
        # Buscar TipoGasto na base_marcacoes
        marcacoes = self.repository.db.query(BaseMarcacao).filter(
            BaseMarcacao.GRUPO == grupo,
            BaseMarcacao.SUBGRUPO == subgrupo
        ).all()
        
        if not marcacoes:
            return None
        
        # Se há apenas um TipoGasto, usar esse
        if len(marcacoes) == 1:
            return marcacoes[0].TipoGasto
        
        # Se há múltiplos (ex: Outros | Outros), decidir pelo valor
        # Valor >= 0 → buscar TipoGasto que contenha "Receita"
        # Valor < 0 → buscar TipoGasto que não contenha "Receita"
        if valor >= 0:
            for m in marcacoes:
                if m.TipoGasto and 'Receita' in m.TipoGasto:
                    return m.TipoGasto
        else:
            for m in marcacoes:
                if m.TipoGasto and 'Receita' not in m.TipoGasto:
                    return m.TipoGasto
        
        # Fallback: retornar o primeiro
        return marcacoes[0].TipoGasto
    
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
    
    def get_grupos_com_media(
        self,
        user_id: int,
        mes_referencia: str
    ) -> TiposGastoComMediaResponse:
        """
        Retorna grupos únicos de Despesa com média PRÉ-CALCULADA da tabela budget_planning
        
        ⚡ OTIMIZAÇÃO: Usa valores pré-calculados em vez de calcular em tempo real
        
        Args:
            user_id: ID do usuário
            mes_referencia: Mês de referência no formato YYYY-MM
            
        Returns:
            TiposGastoComMediaResponse com lista de grupos e suas médias PRÉ-CALCULADAS
        """
        from app.domains.budget.models import BudgetPlanning
        
        # Buscar médias PRÉ-CALCULADAS da tabela budget_planning
        planning_records = self.repository.db.query(BudgetPlanning).filter(
            BudgetPlanning.user_id == user_id,
            BudgetPlanning.mes_referencia == mes_referencia,
            BudgetPlanning.valor_medio_3_meses > 0  # Apenas com média válida
        ).all()
        
        print(f"⚡ OTIMIZADO: Encontrados {len(planning_records)} registros pré-calculados")  # Debug
        
        # Se não encontrou médias pré-calculadas, buscar todos os grupos disponíveis
        if not planning_records:
            print(f"⚠️ AVISO: Nenhum valor pré-calculado para {mes_referencia}. Buscar grupos únicos...")
            
            # Buscar grupos únicos de todas as transações de Despesa do usuário
            grupos_unicos = self.repository.db.query(JournalEntry.GRUPO).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.CategoriaGeral == 'Despesa',
                JournalEntry.GRUPO.isnot(None)
            ).distinct().all()
            
            grupos_com_media = []
            for (grupo,) in sorted(grupos_unicos):
                grupos_com_media.append(TipoGastoComMedia(
                    tipo_gasto=grupo,  # Usando mesmo schema, mas agora é grupo
                    media_3_meses=0.0
                ))
            
            return TiposGastoComMediaResponse(
                tipos_gasto=grupos_com_media,  # Mantém nome do schema por compatibilidade
                mes_referencia=mes_referencia
            )
        
        # Construir resposta a partir dos valores PRÉ-CALCULADOS
        grupos_com_media = []
        for record in sorted(planning_records, key=lambda x: x.grupo):
            grupos_com_media.append(TipoGastoComMedia(
                tipo_gasto=record.grupo,  # Usando grupo no lugar de tipo_gasto
                media_3_meses=round(record.valor_medio_3_meses, 2)
            ))
        
        print(f"✅ Retornando {len(grupos_com_media)} grupos com médias pré-calculadas")
        
        return TiposGastoComMediaResponse(
            tipos_gasto=grupos_com_media,  # Mantém nome do schema por compatibilidade
            mes_referencia=mes_referencia
        )
    
    def get_grupos_subgrupos_disponiveis(self, user_id: int):
        """
        Lista todos os grupos/subgrupos únicos disponíveis no sistema
        """
        from .schemas_migration import GrupoSubgrupoOption, GrupoSubgrupoListResponse
        
        results = self.repository.db.query(
            JournalEntry.GRUPO,
            JournalEntry.SUBGRUPO,
            func.count(JournalEntry.id).label('total')
        ).filter(
            JournalEntry.user_id == user_id
        ).group_by(
            JournalEntry.GRUPO,
            JournalEntry.SUBGRUPO
        ).order_by(
            JournalEntry.GRUPO,
            JournalEntry.SUBGRUPO
        ).all()
        
        opcoes = [
            GrupoSubgrupoOption(
                grupo=r.GRUPO or "",
                subgrupo=r.SUBGRUPO,
                total_transacoes=r.total
            )
            for r in results if r.GRUPO
        ]
        
        return GrupoSubgrupoListResponse(opcoes=opcoes)
    
    def preview_migration(self, user_id: int, grupo_origem: str, subgrupo_origem: Optional[str],
                         grupo_destino: str, subgrupo_destino: Optional[str]):
        """
        Preview de quantas transações serão impactadas pela migração
        """
        from .schemas_migration import MigrationPreviewResponse
        from app.domains.grupos.repository import GrupoRepository
        
        # Contar transações que serão migradas
        query = self.repository.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo_origem
        )
        
        if subgrupo_origem:
            query = query.filter(JournalEntry.SUBGRUPO == subgrupo_origem)
        else:
            query = query.filter(JournalEntry.SUBGRUPO.is_(None))
        
        total = query.scalar()
        
        # Buscar tipo_gasto e categoria_geral do grupo destino
        grupo_repo = GrupoRepository(self.repository.db)
        grupo_config = grupo_repo.get_by_nome(grupo_destino)
        
        if not grupo_config:
            raise HTTPException(
                status_code=400,
                detail=f"Grupo destino '{grupo_destino}' não encontrado em base_grupos_config"
            )
        
        return MigrationPreviewResponse(
            total_transacoes=total,
            grupo_origem=grupo_origem,
            subgrupo_origem=subgrupo_origem,
            grupo_destino=grupo_destino,
            subgrupo_destino=subgrupo_destino,
            tipo_gasto_destino=grupo_config.tipo_gasto_padrao,
            categoria_geral_destino=grupo_config.categoria_geral
        )
    
    def execute_migration(self, user_id: int, grupo_origem: str, subgrupo_origem: Optional[str],
                         grupo_destino: str, subgrupo_destino: Optional[str]):
        """
        Executa migração em massa de transações
        Atualiza GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
        Recalcula médias no budget_planning
        """
        from .schemas_migration import MigrationExecuteResponse
        from app.domains.grupos.repository import GrupoRepository
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        # Buscar configuração do grupo destino
        grupo_repo = GrupoRepository(self.repository.db)
        grupo_config = grupo_repo.get_by_nome(grupo_destino)
        
        if not grupo_config:
            raise HTTPException(
                status_code=400,
                detail=f"Grupo destino '{grupo_destino}' não encontrado em base_grupos_config"
            )
        
        # Buscar transações a migrar
        query = self.repository.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo_origem
        )
        
        if subgrupo_origem:
            query = query.filter(JournalEntry.SUBGRUPO == subgrupo_origem)
        else:
            query = query.filter(JournalEntry.SUBGRUPO.is_(None))
        
        transacoes = query.all()
        total_atualizadas = len(transacoes)
        
        # Atualizar todas as transações
        for t in transacoes:
            t.GRUPO = grupo_destino
            t.SUBGRUPO = subgrupo_destino
            t.TipoGasto = grupo_config.tipo_gasto_padrao
            t.CategoriaGeral = grupo_config.categoria_geral
        
        self.repository.db.commit()
        
        # Recalcular médias no budget_planning para ambos os grupos
        grupos_recalculados = []
        
        for grupo in [grupo_origem, grupo_destino]:
            # Gerar lista de meses (últimos 36 meses + próximos 12)
            data_atual = datetime.now()
            meses = []
            for i in range(-36, 13):
                mes = data_atual + relativedelta(months=i)
                meses.append(mes.strftime('%Y-%m'))
            
            for mes_ref in meses:
                ano, mes = map(int, mes_ref.split('-'))
                data_ref = datetime(ano, mes, 1)
                
                # Calcular 3 meses anteriores
                mes_1 = (data_ref - relativedelta(months=1)).strftime('%Y%m')
                mes_2 = (data_ref - relativedelta(months=2)).strftime('%Y%m')
                mes_3 = (data_ref - relativedelta(months=3)).strftime('%Y%m')
                
                # Calcular média
                result = self.repository.db.query(
                    func.avg(
                        func.coalesce(
                            self.repository.db.query(func.sum(func.abs(JournalEntry.Valor)))
                            .filter(
                                JournalEntry.user_id == user_id,
                                JournalEntry.GRUPO == grupo,
                                JournalEntry.CategoriaGeral == 'Despesa',
                                JournalEntry.MesFatura.in_([mes_1, mes_2, mes_3])
                            )
                            .group_by(JournalEntry.MesFatura)
                            .subquery()
                            .c[0],
                            0
                        )
                    )
                ).scalar()
                
                media = round(result or 0, 2)
                
                # Atualizar ou inserir no budget_planning
                from app.domains.budget.models import BudgetPlanning
                
                planning = self.repository.db.query(BudgetPlanning).filter(
                    BudgetPlanning.user_id == user_id,
                    BudgetPlanning.grupo == grupo,
                    BudgetPlanning.mes_referencia == mes_ref
                ).first()
                
                if planning:
                    planning.valor_medio_3_meses = media
                    planning.valor_planejado = media
                    planning.updated_at = datetime.now()
                else:
                    planning = BudgetPlanning(
                        user_id=user_id,
                        grupo=grupo,
                        mes_referencia=mes_ref,
                        valor_planejado=media,
                        valor_medio_3_meses=media
                    )
                    self.repository.db.add(planning)
            
            grupos_recalculados.append(grupo)
        
        self.repository.db.commit()
        
        return MigrationExecuteResponse(
            success=True,
            total_transacoes_atualizadas=total_atualizadas,
            grupo_origem=grupo_origem,
            subgrupo_origem=subgrupo_origem,
            grupo_destino=grupo_destino,
            subgrupo_destino=subgrupo_destino,
            tipo_gasto_destino=grupo_config.tipo_gasto_padrao,
            categoria_geral_destino=grupo_config.categoria_geral,
            grupos_recalculados=grupos_recalculados
        )
    
    def _ensure_marcacao_exists(self, grupo: str, subgrupo: str, tipo_gasto: str, user_id: int = None):
        """
        Garante que a combinação grupo+subgrupo+tipo_gasto existe em base_marcacoes
        Se não existir, cria automaticamente
        """
        from app.domains.categories.models import BaseMarcacao
        
        # Verificar se já existe
        existing = self.repository.db.query(BaseMarcacao).filter(
            BaseMarcacao.GRUPO == grupo,
            BaseMarcacao.SUBGRUPO == subgrupo,
            BaseMarcacao.TipoGasto == tipo_gasto
        ).first()
        
        if not existing:
            # Criar nova marcação
            nova_marcacao = BaseMarcacao(
                GRUPO=grupo,
                SUBGRUPO=subgrupo,
                TipoGasto=tipo_gasto
            )
            self.repository.db.add(nova_marcacao)
            self.repository.db.flush()  # Flush para garantir inserção sem commit ainda
            print(f"➕ Nova marcação criada: {grupo} > {subgrupo} ({tipo_gasto})")
