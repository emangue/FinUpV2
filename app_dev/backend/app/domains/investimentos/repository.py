"""
Repository do domínio Investimentos.
Todas as queries SQL isoladas aqui.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, desc
from decimal import Decimal

from .models import (
    InvestimentoPortfolio,
    InvestimentoHistorico,
    InvestimentoCenario,
    AporteExtraordinario,
    InvestimentoPlanejamento
)


class InvestimentoRepository:
    """Repository para operações de investimentos"""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================================
    # PORTFOLIO OPERATIONS
    # ============================================================================

    def get_by_id(self, investimento_id: int, user_id: int) -> Optional[InvestimentoPortfolio]:
        """Busca investimento por ID e user_id"""
        return self.db.query(InvestimentoPortfolio).filter(
            InvestimentoPortfolio.id == investimento_id,
            InvestimentoPortfolio.user_id == user_id
        ).first()

    def get_by_balance_id(self, balance_id: str, user_id: int) -> Optional[InvestimentoPortfolio]:
        """Busca investimento por balance_id único"""
        return self.db.query(InvestimentoPortfolio).filter(
            InvestimentoPortfolio.balance_id == balance_id,
            InvestimentoPortfolio.user_id == user_id
        ).first()

    def list_all(
        self,
        user_id: int,
        tipo_investimento: Optional[str] = None,
        ativo: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[InvestimentoPortfolio]:
        """Lista investimentos com filtros"""
        query = self.db.query(InvestimentoPortfolio).filter(
            InvestimentoPortfolio.user_id == user_id
        )

        if tipo_investimento:
            query = query.filter(InvestimentoPortfolio.tipo_investimento == tipo_investimento)

        if ativo is not None:
            query = query.filter(InvestimentoPortfolio.ativo == ativo)

        return query.order_by(InvestimentoPortfolio.corretora, InvestimentoPortfolio.nome_produto).offset(skip).limit(limit).all()

    def create(self, investimento: InvestimentoPortfolio) -> InvestimentoPortfolio:
        """Cria novo investimento"""
        self.db.add(investimento)
        self.db.commit()
        self.db.refresh(investimento)
        return investimento

    def update(self, investimento: InvestimentoPortfolio) -> InvestimentoPortfolio:
        """Atualiza investimento existente"""
        self.db.commit()
        self.db.refresh(investimento)
        return investimento

    def delete(self, investimento_id: int, user_id: int) -> bool:
        """Deleta investimento (soft delete)"""
        investimento = self.get_by_id(investimento_id, user_id)
        if investimento:
            investimento.ativo = False
            self.db.commit()
            return True
        return False

    # ============================================================================
    # HISTORICO OPERATIONS
    # ============================================================================

    def get_historico_by_investimento(
        self,
        investimento_id: int,
        ano_inicio: Optional[int] = None,
        ano_fim: Optional[int] = None
    ) -> List[InvestimentoHistorico]:
        """Busca histórico de um investimento"""
        query = self.db.query(InvestimentoHistorico).filter(
            InvestimentoHistorico.investimento_id == investimento_id
        )

        if ano_inicio:
            query = query.filter(InvestimentoHistorico.ano >= ano_inicio)
        if ano_fim:
            query = query.filter(InvestimentoHistorico.ano <= ano_fim)

        return query.order_by(InvestimentoHistorico.anomes).all()

    def get_historico_by_periodo(
        self,
        user_id: int,
        anomes_inicio: int,
        anomes_fim: int
    ) -> List[Dict[str, Any]]:
        """Busca histórico de todos investimentos em um período"""
        return self.db.query(
            InvestimentoHistorico,
            InvestimentoPortfolio
        ).join(
            InvestimentoPortfolio,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes >= anomes_inicio,
            InvestimentoHistorico.anomes <= anomes_fim
        ).order_by(
            InvestimentoHistorico.anomes,
            InvestimentoPortfolio.corretora,
            InvestimentoPortfolio.nome_produto
        ).all()

    def get_ultimo_historico(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Busca o patrimônio total do mês mais recente somando todos os investimentos"""
        # Primeiro, encontra o anomes mais recente
        ultimo_anomes = self.db.query(
            func.max(InvestimentoHistorico.anomes)
        ).join(
            InvestimentoPortfolio,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id
        ).scalar()
        
        if not ultimo_anomes:
            return None
        
        # Soma todos os valores do mês mais recente
        resultado = self.db.query(
            func.sum(InvestimentoHistorico.valor_total).label('valor_total'),
            InvestimentoHistorico.anomes,
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.data_referencia
        ).join(
            InvestimentoPortfolio,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes == ultimo_anomes
        ).group_by(
            InvestimentoHistorico.anomes,
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.data_referencia
        ).first()
        
        if not resultado:
            return None
        
        # Retorna como dict para ser compatível com o schema
        # Inclui campos obrigatórios com valores padrão para compatibilidade
        from datetime import datetime
        from decimal import Decimal
        return {
            'id': 0,  # ID agregado não existe, usar 0
            'investimento_id': 0,  # Agregação de múltiplos investimentos
            'valor_total': Decimal(str(resultado.valor_total or 0)),
            'anomes': resultado.anomes,
            'ano': resultado.ano,
            'mes': resultado.mes,
            'data_referencia': resultado.data_referencia,
            'quantidade': None,
            'valor_unitario': None,
            'aporte_mes': Decimal('0.00'),
            'rendimento_mes': None,
            'rendimento_acumulado': None,
            'created_at': datetime.now(),
            'updated_at': None
        }

    def create_historico(self, historico: InvestimentoHistorico) -> InvestimentoHistorico:
        """Cria registro de histórico"""
        self.db.add(historico)
        self.db.commit()
        self.db.refresh(historico)
        return historico

    def bulk_create_historico(self, historicos: List[InvestimentoHistorico]) -> int:
        """Cria múltiplos registros de histórico"""
        self.db.bulk_save_objects(historicos)
        self.db.commit()
        return len(historicos)

    # ============================================================================
    # AGREGAÇÕES E RELATÓRIOS
    # ============================================================================

    def get_portfolio_resumo(self, user_id: int) -> Dict[str, Any]:
        """Retorna resumo consolidado do portfólio"""
        investimentos = self.list_all(user_id, ativo=True)

        total_investido = sum(
            inv.valor_total_inicial or Decimal('0') for inv in investimentos
        )

        # Pegar último valor de cada investimento
        valores_atuais = []
        for inv in investimentos:
            ultimo = self.db.query(InvestimentoHistorico).filter(
                InvestimentoHistorico.investimento_id == inv.id
            ).order_by(desc(InvestimentoHistorico.anomes)).first()

            if ultimo and ultimo.valor_total:
                valores_atuais.append(ultimo.valor_total)
            elif inv.valor_total_inicial:
                valores_atuais.append(inv.valor_total_inicial)

        valor_atual = sum(valores_atuais) if valores_atuais else Decimal('0')
        rendimento_total = valor_atual - total_investido

        return {
            'total_investido': total_investido,
            'valor_atual': valor_atual,
            'rendimento_total': rendimento_total,
            'rendimento_percentual': float(rendimento_total / total_investido * 100) if total_investido > 0 else 0.0,
            'quantidade_produtos': len(investimentos),
            'produtos_ativos': sum(1 for inv in investimentos if inv.ativo)
        }

    def get_rendimento_por_tipo(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna rendimento agrupado por tipo de investimento"""
        results = self.db.query(
            InvestimentoPortfolio.tipo_investimento,
            func.count(InvestimentoPortfolio.id).label('quantidade'),
            func.sum(InvestimentoPortfolio.valor_total_inicial).label('total_investido')
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoPortfolio.ativo == True
        ).group_by(
            InvestimentoPortfolio.tipo_investimento
        ).all()

        return [
            {
                'tipo': r.tipo_investimento,
                'quantidade': r.quantidade,
                'total_investido': r.total_investido or Decimal('0')
            }
            for r in results
        ]

    def get_rendimentos_mensais(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[Dict[str, Any]]:
        """Retorna série temporal de rendimentos mensais"""
        results = self.db.query(
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.anomes,
            func.sum(InvestimentoHistorico.rendimento_mes).label('rendimento_total'),
            func.sum(InvestimentoHistorico.valor_total).label('patrimonio_total'),
            func.sum(InvestimentoHistorico.aporte_mes).label('aporte_total')
        ).join(
            InvestimentoPortfolio,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.ano >= ano_inicio,
            InvestimentoHistorico.ano <= ano_fim
        ).group_by(
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.anomes
        ).order_by(
            InvestimentoHistorico.anomes
        ).all()

        return [
            {
                'ano': r.ano,
                'mes': r.mes,
                'anomes': r.anomes,
                'rendimento_mes': r.rendimento_total or Decimal('0'),
                'patrimonio_final': r.patrimonio_total or Decimal('0'),
                'aporte_mes': r.aporte_total or Decimal('0')
            }
            for r in results
        ]

    # ============================================================================
    # CENARIOS OPERATIONS
    # ============================================================================

    def get_cenario_by_id(self, cenario_id: int, user_id: int) -> Optional[InvestimentoCenario]:
        """Busca cenário por ID"""
        return self.db.query(InvestimentoCenario).filter(
            InvestimentoCenario.id == cenario_id,
            InvestimentoCenario.user_id == user_id
        ).first()

    def list_cenarios(self, user_id: int, ativo: Optional[bool] = True) -> List[InvestimentoCenario]:
        """Lista cenários do usuário"""
        query = self.db.query(InvestimentoCenario).filter(
            InvestimentoCenario.user_id == user_id
        )

        if ativo is not None:
            query = query.filter(InvestimentoCenario.ativo == ativo)

        return query.order_by(desc(InvestimentoCenario.created_at)).all()

    def create_cenario(self, cenario: InvestimentoCenario) -> InvestimentoCenario:
        """Cria novo cenário"""
        self.db.add(cenario)
        self.db.commit()
        self.db.refresh(cenario)
        return cenario

    def update_cenario(self, cenario: InvestimentoCenario) -> InvestimentoCenario:
        """Atualiza cenário"""
        self.db.commit()
        self.db.refresh(cenario)
        return cenario

    def delete_cenario(self, cenario_id: int, user_id: int) -> bool:
        """Deleta cenário (soft delete)"""
        cenario = self.get_cenario_by_id(cenario_id, user_id)
        if cenario:
            cenario.ativo = False
            self.db.commit()
            return True
        return False

    # ============================================================================
    # PLANEJAMENTO OPERATIONS
    # ============================================================================

    def get_planejamento(self, user_id: int, ano: int, mes: int) -> Optional[InvestimentoPlanejamento]:
        """Busca planejamento de um mês específico"""
        anomes = ano * 100 + mes
        return self.db.query(InvestimentoPlanejamento).filter(
            InvestimentoPlanejamento.user_id == user_id,
            InvestimentoPlanejamento.anomes == anomes
        ).first()

    def list_planejamento(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[InvestimentoPlanejamento]:
        """Lista planejamento por período"""
        return self.db.query(InvestimentoPlanejamento).filter(
            InvestimentoPlanejamento.user_id == user_id,
            InvestimentoPlanejamento.ano >= ano_inicio,
            InvestimentoPlanejamento.ano <= ano_fim
        ).order_by(InvestimentoPlanejamento.anomes).all()

    def upsert_planejamento(self, planejamento: InvestimentoPlanejamento) -> InvestimentoPlanejamento:
        """Cria ou atualiza planejamento"""
        existing = self.get_planejamento(
            planejamento.user_id,
            planejamento.ano,
            planejamento.mes
        )

        if existing:
            for key, value in planejamento.__dict__.items():
                if key not in ['_sa_instance_state', 'id', 'created_at']:
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(planejamento)
            self.db.commit()
            self.db.refresh(planejamento)
            return planejamento
