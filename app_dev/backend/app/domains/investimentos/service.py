"""
Service do domínio Investimentos.
Toda lógica de negócio isolada aqui.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from .repository import InvestimentoRepository
from .models import (
    InvestimentoPortfolio,
    InvestimentoHistorico,
    InvestimentoCenario,
    AporteExtraordinario,
    InvestimentoPlanejamento
)
from . import schemas


class InvestimentoService:
    """Service para lógica de negócio de investimentos"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = InvestimentoRepository(db)

    # ============================================================================
    # PORTFOLIO BUSINESS LOGIC
    # ============================================================================

    def create_investimento(
        self,
        data: schemas.InvestimentoPortfolioCreate
    ) -> schemas.InvestimentoPortfolioResponse:
        """Cria novo investimento com validações"""
        # Verificar se balance_id já existe
        existing = self.repository.get_by_balance_id(data.balance_id, data.user_id)
        if existing:
            raise ValueError(f"Investimento com balance_id '{data.balance_id}' já existe")

        # Criar investimento
        investimento = InvestimentoPortfolio(**data.model_dump())
        investimento = self.repository.create(investimento)

        return schemas.InvestimentoPortfolioResponse.model_validate(investimento)

    def get_investimento(
        self,
        investimento_id: int,
        user_id: int
    ) -> Optional[schemas.InvestimentoPortfolioResponse]:
        """Busca investimento por ID"""
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return None

        return schemas.InvestimentoPortfolioResponse.model_validate(investimento)

    def list_investimentos(
        self,
        user_id: int,
        tipo_investimento: Optional[str] = None,
        ativo: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.InvestimentoPortfolioResponse]:
        """Lista investimentos com filtros"""
        investimentos = self.repository.list_all(
            user_id=user_id,
            tipo_investimento=tipo_investimento,
            ativo=ativo,
            skip=skip,
            limit=limit
        )

        return [
            schemas.InvestimentoPortfolioResponse.model_validate(inv)
            for inv in investimentos
        ]

    def update_investimento(
        self,
        investimento_id: int,
        user_id: int,
        data: schemas.InvestimentoPortfolioUpdate
    ) -> Optional[schemas.InvestimentoPortfolioResponse]:
        """Atualiza investimento"""
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return None

        # Atualizar campos
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(investimento, field, value)

        investimento = self.repository.update(investimento)
        return schemas.InvestimentoPortfolioResponse.model_validate(investimento)

    def delete_investimento(self, investimento_id: int, user_id: int) -> bool:
        """Deleta investimento (soft delete)"""
        return self.repository.delete(investimento_id, user_id)

    # ============================================================================
    # PORTFOLIO ANALYTICS
    # ============================================================================

    def get_portfolio_resumo(self, user_id: int) -> schemas.PortfolioResumo:
        """Retorna resumo consolidado do portfólio"""
        resumo = self.repository.get_portfolio_resumo(user_id)
        return schemas.PortfolioResumo(**resumo)

    def get_distribuicao_por_tipo(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna distribuição do portfólio por tipo"""
        return self.repository.get_rendimento_por_tipo(user_id)

    def get_rendimentos_timeline(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[schemas.RendimentoMensal]:
        """Retorna série temporal de rendimentos"""
        rendimentos = self.repository.get_rendimentos_mensais(
            user_id, ano_inicio, ano_fim
        )

        return [
            schemas.RendimentoMensal(**r)
            for r in rendimentos
        ]

    # ============================================================================
    # HISTORICO BUSINESS LOGIC
    # ============================================================================

    def get_ultimo_historico(
        self,
        user_id: int
    ) -> Optional[schemas.InvestimentoHistoricoResponse]:
        """Busca o último registro de histórico (patrimônio mais recente)"""
        ultimo = self.repository.get_ultimo_historico(user_id)
        
        if not ultimo:
            return None
        
        # Agora recebe um dict, não um objeto ORM
        return schemas.InvestimentoHistoricoResponse(**ultimo)

    def add_historico(
        self,
        data: schemas.InvestimentoHistoricoCreate
    ) -> schemas.InvestimentoHistoricoResponse:
        """Adiciona registro de histórico"""
        historico = InvestimentoHistorico(**data.model_dump())
        historico = self.repository.create_historico(historico)

        return schemas.InvestimentoHistoricoResponse.model_validate(historico)

    def get_historico_investimento(
        self,
        investimento_id: int,
        user_id: int,
        ano_inicio: Optional[int] = None,
        ano_fim: Optional[int] = None
    ) -> List[schemas.InvestimentoHistoricoResponse]:
        """Busca histórico de um investimento"""
        # Validar ownership
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return []

        historicos = self.repository.get_historico_by_investimento(
            investimento_id, ano_inicio, ano_fim
        )

        return [
            schemas.InvestimentoHistoricoResponse.model_validate(h)
            for h in historicos
        ]

    # ============================================================================
    # CENARIOS & SIMULACAO
    # ============================================================================

    def create_cenario(
        self,
        data: schemas.InvestimentoCenarioCreate
    ) -> schemas.InvestimentoCenarioResponse:
        """Cria novo cenário de simulação"""
        cenario = InvestimentoCenario(
            user_id=data.user_id,
            nome_cenario=data.nome_cenario,
            descricao=data.descricao,
            patrimonio_inicial=data.patrimonio_inicial,
            rendimento_mensal_pct=data.rendimento_mensal_pct,
            aporte_mensal=data.aporte_mensal,
            periodo_meses=data.periodo_meses
        )

        # Adicionar aportes extraordinários
        for aporte_data in data.aportes_extraordinarios:
            aporte = AporteExtraordinario(**aporte_data.model_dump())
            cenario.aportes_extraordinarios.append(aporte)

        cenario = self.repository.create_cenario(cenario)
        return schemas.InvestimentoCenarioResponse.model_validate(cenario)

    def simular_cenario(
        self,
        cenario_id: int,
        user_id: int
    ) -> Optional[schemas.SimulacaoCompleta]:
        """Executa simulação completa de um cenário"""
        cenario = self.repository.get_cenario_by_id(cenario_id, user_id)
        if not cenario:
            return None

        # Calcular projeções mês a mês
        projecoes = []
        patrimonio_atual = cenario.patrimonio_inicial
        total_aportes = Decimal('0')

        for mes in range(1, cenario.periodo_meses + 1):
            # Rendimento do mês
            rendimento_mes = patrimonio_atual * cenario.rendimento_mensal_pct

            # Aporte regular
            aporte_mes = cenario.aporte_mensal

            # Verificar aporte extraordinário
            aporte_extra = Decimal('0')
            for aporte in cenario.aportes_extraordinarios:
                if aporte.mes_referencia == mes:
                    aporte_extra = aporte.valor

            # Atualizar patrimônio
            patrimonio_atual = patrimonio_atual + rendimento_mes + aporte_mes + aporte_extra
            total_aportes += aporte_mes + aporte_extra

            projecoes.append(
                schemas.ProjecaoCenario(
                    mes=mes,
                    patrimonio=patrimonio_atual,
                    rendimento_mes=rendimento_mes,
                    aporte_mes=aporte_mes,
                    aporte_extraordinario=aporte_extra
                )
            )

        patrimonio_final = patrimonio_atual
        rendimento_total = patrimonio_final - cenario.patrimonio_inicial - total_aportes

        return schemas.SimulacaoCompleta(
            cenario=schemas.InvestimentoCenarioResponse.model_validate(cenario),
            projecoes=projecoes,
            patrimonio_final=patrimonio_final,
            rendimento_total=rendimento_total,
            total_aportes=total_aportes
        )

    def list_cenarios(
        self,
        user_id: int,
        ativo: Optional[bool] = True
    ) -> List[schemas.InvestimentoCenarioResponse]:
        """Lista cenários do usuário"""
        cenarios = self.repository.list_cenarios(user_id, ativo)

        return [
            schemas.InvestimentoCenarioResponse.model_validate(c)
            for c in cenarios
        ]

    # ============================================================================
    # PLANEJAMENTO
    # ============================================================================

    def upsert_planejamento(
        self,
        data: schemas.InvestimentoPlanejamentoCreate
    ) -> schemas.InvestimentoPlanejamentoResponse:
        """Cria ou atualiza planejamento mensal"""
        planejamento = InvestimentoPlanejamento(**data.model_dump())
        planejamento = self.repository.upsert_planejamento(planejamento)

        return schemas.InvestimentoPlanejamentoResponse.model_validate(planejamento)

    def get_planejamento_periodo(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[schemas.InvestimentoPlanejamentoResponse]:
        """Lista planejamento por período"""
        planejamentos = self.repository.list_planejamento(
            user_id, ano_inicio, ano_fim
        )

        return [
            schemas.InvestimentoPlanejamentoResponse.model_validate(p)
            for p in planejamentos
        ]
