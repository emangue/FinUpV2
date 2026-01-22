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
        """Lista investimentos com filtros - retorna apenas produtos com histórico no último mês"""
        # Descobrir qual é o último mês disponível
        ultimo_mes = self.db.query(
            func.max(InvestimentoHistorico.anomes)
        ).filter(
            InvestimentoHistorico.investimento_id.in_(
                self.db.query(InvestimentoPortfolio.id).filter(
                    InvestimentoPortfolio.user_id == user_id
                )
            )
        ).scalar()
        
        if not ultimo_mes:
            return []
        
        # Buscar investimentos que têm histórico no último mês
        query = self.db.query(InvestimentoPortfolio).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoPortfolio.id.in_(
                self.db.query(InvestimentoHistorico.investimento_id).filter(
                    InvestimentoHistorico.anomes == ultimo_mes
                )
            )
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
        """
        Retorna resumo consolidado do portfólio baseado no ÚLTIMO MÊS disponível
        
        Total Investido = Soma de ATIVOS do último mês
        Valor Atual = Soma de PASSIVOS do último mês (valores negativos)
        Rendimento Total = PATRIMÔNIO LÍQUIDO (Ativos + Passivos)
        Produtos Ativos = Quantidade de produtos com histórico no último mês
        """
        # Descobrir qual é o último mês disponível
        ultimo_mes = self.db.query(
            func.max(InvestimentoHistorico.anomes)
        ).filter(
            InvestimentoHistorico.investimento_id.in_(
                self.db.query(InvestimentoPortfolio.id).filter(
                    InvestimentoPortfolio.user_id == user_id
                )
            )
        ).scalar()
        
        if not ultimo_mes:
            # Sem histórico - retornar zeros
            return {
                'total_investido': Decimal('0'),
                'valor_atual': Decimal('0'),
                'rendimento_total': Decimal('0'),
                'rendimento_percentual': 0.0,
                'quantidade_produtos': 0,
                'produtos_ativos': 0
            }
        
        # Buscar valores do último mês agrupados por classe_ativo
        resultado = self.db.query(
            InvestimentoPortfolio.classe_ativo,
            func.count(InvestimentoHistorico.id).label('quantidade'),
            func.sum(InvestimentoHistorico.valor_total).label('total')
        ).join(
            InvestimentoHistorico,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes == ultimo_mes
        ).group_by(
            InvestimentoPortfolio.classe_ativo
        ).all()
        
        # Separar ativos e passivos
        total_ativos = Decimal('0')
        total_passivos = Decimal('0')
        quantidade_total = 0
        
        for row in resultado:
            classe = row.classe_ativo
            valor = row.total or Decimal('0')
            quantidade_total += row.quantidade
            
            if classe == 'Ativo':
                total_ativos += valor
            elif classe == 'Passivo':
                total_passivos += valor
        
        # Patrimônio Líquido = Ativos + Passivos (passivos já são negativos)
        patrimonio_liquido = total_ativos + total_passivos
        
        # Calcular percentual (se houver ativos)
        percentual = 0.0
        if total_ativos > 0:
            # Rendimento = quanto o patrimônio cresceu em relação aos ativos
            percentual = float((patrimonio_liquido / total_ativos) * 100)
        
        return {
            'total_investido': total_ativos,  # Soma de Ativos
            'valor_atual': total_passivos,     # Soma de Passivos (negativos)
            'rendimento_total': patrimonio_liquido,  # Patrimônio Líquido
            'rendimento_percentual': percentual,
            'quantidade_produtos': quantidade_total,
            'produtos_ativos': quantidade_total  # Produtos com histórico no último mês
        }

        return {
            'total_investido': total_investido,
            'valor_atual': valor_atual,
            'rendimento_total': rendimento_total,
            'rendimento_percentual': float(rendimento_total / total_investido * 100) if total_investido > 0 else 0.0,
            'quantidade_produtos': len(investimentos),
            'produtos_ativos': sum(1 for inv in investimentos if inv.ativo)
        }

    def get_rendimento_por_tipo(self, user_id: int) -> List[Dict[str, Any]]:
        """Retorna rendimento agrupado por tipo de investimento baseado no último mês"""
        # Descobrir qual é o último mês disponível
        ultimo_mes = self.db.query(
            func.max(InvestimentoHistorico.anomes)
        ).filter(
            InvestimentoHistorico.investimento_id.in_(
                self.db.query(InvestimentoPortfolio.id).filter(
                    InvestimentoPortfolio.user_id == user_id
                )
            )
        ).scalar()
        
        if not ultimo_mes:
            return []
        
        # Buscar valores do último mês agrupados por tipo_investimento
        results = self.db.query(
            InvestimentoPortfolio.tipo_investimento,
            func.count(InvestimentoHistorico.id).label('quantidade'),
            func.sum(InvestimentoHistorico.valor_total).label('total_investido')
        ).join(
            InvestimentoHistorico,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes == ultimo_mes
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
