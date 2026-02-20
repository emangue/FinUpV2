"""
Service do domínio Investimentos.
Toda lógica de negócio isolada aqui.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from .repository import InvestimentoRepository


def _normalizar_valores_mes(valor_total, valor_unitario, quantidade):
    """
    Garante valor_total = valor_unitario * quantidade.
    O valor correto é o total: se valor_unitario for None/0 mas valor_total existir,
    deriva valor_unitario = valor_total / (quantidade ou 1).
    """
    qty = float(quantidade) if quantidade is not None and quantidade > 0 else 1.0
    vt = valor_total
    vu = valor_unitario
    if vt is not None and vt != 0 and (vu is None or vu == 0):
        vu = vt / qty
    elif vu is not None and vu != 0 and (vt is None or vt == 0):
        vt = vu * qty
    return vt, vu, qty


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
        """Cria novo investimento com validações. Se ano/anomes fornecidos, cria historico."""
        # Verificar se balance_id já existe
        existing = self.repository.get_by_balance_id(data.balance_id, data.user_id)
        if existing:
            raise ValueError(f"Investimento com balance_id '{data.balance_id}' já existe")

        # Criar investimento
        investimento = InvestimentoPortfolio(**data.model_dump())
        investimento = self.repository.create(investimento)

        # Se ano e anomes fornecidos, criar historico para o mês
        if data.ano is not None and data.anomes is not None:
            from calendar import monthrange
            ano, anomes = data.ano, data.anomes
            mes = anomes % 100
            _, last_day = monthrange(ano, mes)
            data_ref = date(ano, mes, last_day)
            qty = float(data.quantidade or 1.0) or 1.0
            valor_unit = float(data.valor_unitario_inicial or 0)
            valor_total = float(data.valor_total_inicial or 0)
            # Garantir valor_total = valor_unitario * quantidade (valor_total é a fonte)
            if valor_total and (not valor_unit or valor_unit == 0):
                valor_unit = valor_total / qty
            elif valor_unit and (not valor_total or valor_total == 0):
                valor_total = valor_unit * qty
            hist = InvestimentoHistorico(
                investimento_id=investimento.id,
                ano=ano,
                mes=mes,
                anomes=anomes,
                data_referencia=data_ref,
                quantidade=qty,
                valor_unitario=Decimal(str(valor_unit)),
                valor_total=Decimal(str(valor_total)),
                aporte_mes=Decimal('0'),
            )
            self.repository.create_historico(hist)

        return schemas.InvestimentoPortfolioResponse.model_validate(investimento)

    def copiar_mes_anterior(
        self, user_id: int, anomes_destino: int
    ) -> int:
        """Copia investimentos do mês anterior para o mês destino. Retorna quantidade copiada."""
        return self.repository.copiar_mes_anterior(user_id, anomes_destino)

    def get_investimento(
        self,
        investimento_id: int,
        user_id: int,
        anomes: Optional[int] = None
    ) -> Optional[Union[schemas.InvestimentoPortfolioResponse, schemas.InvestimentoComHistoricoResponse]]:
        """Busca investimento por ID. Se anomes informado, retorna valores do histórico do mês."""
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return None

        if anomes is not None:
            historico = self.repository.get_historico_by_investimento_and_anomes(
                investimento_id, anomes
            )
            vt = float(historico.valor_total) if historico and historico.valor_total else None
            vu = float(historico.valor_unitario) if historico and historico.valor_unitario else None
            q = float(historico.quantidade) if historico and historico.quantidade else None
            vt, vu, q = _normalizar_valores_mes(vt, vu, q)
            return schemas.InvestimentoComHistoricoResponse(
                **schemas.InvestimentoPortfolioResponse.model_validate(investimento).model_dump(),
                valor_total_mes=Decimal(str(vt)) if vt is not None else None,
                valor_unitario_mes=Decimal(str(vu)) if vu is not None else None,
                quantidade_mes=q,
            )

        return schemas.InvestimentoPortfolioResponse.model_validate(investimento)

    def list_investimentos(
        self,
        user_id: int,
        tipo_investimento: Optional[str] = None,
        ativo: Optional[bool] = True,
        anomes: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.InvestimentoPortfolioResponse]:
        """Lista investimentos com filtros. anomes: YYYYMM para filtrar por mês."""
        if anomes is not None:
            # Usar valores do histórico (mesma fonte de ativos/passivos)
            rows = self.repository.list_all_com_historico(
                user_id=user_id,
                anomes=anomes,
                tipo_investimento=tipo_investimento,
                ativo=ativo,
                skip=skip,
                limit=limit
            )
            result = []
            for r in rows:
                vt = float(r['valor_total_mes']) if r['valor_total_mes'] else None
                vu = float(r['valor_unitario_mes']) if r['valor_unitario_mes'] else None
                q = float(r['quantidade_mes']) if r['quantidade_mes'] else None
                vt, vu, q = _normalizar_valores_mes(vt, vu, q)
                result.append(
                    schemas.InvestimentoComHistoricoResponse(
                        **schemas.InvestimentoPortfolioResponse.model_validate(r['portfolio']).model_dump(),
                        valor_total_mes=Decimal(str(vt)) if vt is not None else None,
                        valor_unitario_mes=Decimal(str(vu)) if vu is not None else None,
                        quantidade_mes=q,
                    )
                )
            return result

        investimentos = self.repository.list_all(
            user_id=user_id,
            tipo_investimento=tipo_investimento,
            ativo=ativo,
            anomes=None,
            skip=skip,
            limit=limit
        )
        return [
            schemas.InvestimentoComHistoricoResponse(
                **schemas.InvestimentoPortfolioResponse.model_validate(inv).model_dump(),
                valor_total_mes=None,
                valor_unitario_mes=None,
                quantidade_mes=None,
            )
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

    def get_distribuicao_por_tipo(
        self,
        user_id: int,
        classe_ativo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retorna distribuição do portfólio por tipo. classe_ativo: 'Ativo' | 'Passivo' ou None"""
        return self.repository.get_rendimento_por_tipo(user_id, classe_ativo)

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

    def get_patrimonio_timeline(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[schemas.PatrimonioMensal]:
        """Retorna série temporal de ativos, passivos e PL por mês"""
        items = self.repository.get_patrimonio_timeline(
            user_id, ano_inicio, ano_fim
        )
        return [schemas.PatrimonioMensal(**r) for r in items]

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

    def update_historico_mes(
        self,
        investimento_id: int,
        anomes: int,
        user_id: int,
        data: schemas.InvestimentoHistoricoUpdate
    ) -> Optional[schemas.InvestimentoHistoricoResponse]:
        """Atualiza valores do histórico. Garante valor_total = valor_unitario * quantidade."""
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return None

        historico = self.repository.get_historico_by_investimento_and_anomes(
            investimento_id, anomes
        )
        if not historico:
            return None

        dump = data.model_dump(exclude_unset=True)
        for field, value in dump.items():
            setattr(historico, field, value)

        # Garantir valor_total = valor_unitario * quantidade ao salvar
        qty = historico.quantidade or 1.0
        vu = float(historico.valor_unitario) if historico.valor_unitario else None
        vt = float(historico.valor_total) if historico.valor_total else None
        if vt is not None or vu is not None:
            vt, vu, qty = _normalizar_valores_mes(vt, vu, float(qty))
            historico.quantidade = qty
            historico.valor_unitario = Decimal(str(vu)) if vu is not None else None
            historico.valor_total = Decimal(str(vt)) if vt is not None else None

        historico = self.repository.update_historico(historico)
        return schemas.InvestimentoHistoricoResponse.model_validate(historico)

    def delete_historico_mes(
        self, investimento_id: int, anomes: int, user_id: int
    ) -> bool:
        """Remove o histórico (patrimônio) de um investimento para um mês específico."""
        investimento = self.repository.get_by_id(investimento_id, user_id)
        if not investimento:
            return False
        return self.repository.delete_historico_by_investimento_and_anomes(
            investimento_id, anomes
        )

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
