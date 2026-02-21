"""
Repository do domínio Investimentos.
Todas as queries SQL isoladas aqui.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from calendar import monthrange
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract, desc
from decimal import Decimal

from .models import (
    InvestimentoPortfolio,
    InvestimentoHistorico,
    InvestimentoCenario,
    AporteExtraordinario,
    InvestimentoPlanejamento,
    CenarioProjecao,
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
        anomes: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InvestimentoPortfolio]:
        """Lista investimentos com filtros. anomes: filtrar por mês (YYYYMM). Se None, usa último mês."""
        # Determinar mês de referência
        if anomes is not None:
            mes_ref = anomes
        else:
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
            mes_ref = ultimo_mes

        # Buscar investimentos que têm histórico no mês de referência
        # OU portfolio.anomes == mes_ref (para investimentos criados direto no mês)
        subq_historico = self.db.query(InvestimentoHistorico.investimento_id).filter(
            InvestimentoHistorico.anomes == mes_ref
        ).distinct()
        query = self.db.query(InvestimentoPortfolio).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoPortfolio.id.in_(subq_historico)
        )

        if tipo_investimento:
            query = query.filter(InvestimentoPortfolio.tipo_investimento == tipo_investimento)

        if ativo is not None:
            query = query.filter(InvestimentoPortfolio.ativo == ativo)

        return query.order_by(InvestimentoPortfolio.corretora, InvestimentoPortfolio.nome_produto).offset(skip).limit(limit).all()

    def list_all_com_historico(
        self,
        user_id: int,
        anomes: int,
        tipo_investimento: Optional[str] = None,
        ativo: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Lista investimentos com valores do histórico do mês (mesma fonte de ativos/passivos)."""
        rows = self.db.query(
            InvestimentoPortfolio,
            InvestimentoHistorico.valor_total,
            InvestimentoHistorico.valor_unitario,
            InvestimentoHistorico.quantidade,
        ).join(
            InvestimentoHistorico,
            (InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id) &
            (InvestimentoHistorico.anomes == anomes)
        ).filter(
            InvestimentoPortfolio.user_id == user_id
        )
        if tipo_investimento:
            rows = rows.filter(InvestimentoPortfolio.tipo_investimento == tipo_investimento)
        if ativo is not None:
            rows = rows.filter(InvestimentoPortfolio.ativo == ativo)
        rows = rows.order_by(
            InvestimentoPortfolio.corretora,
            InvestimentoPortfolio.nome_produto
        ).offset(skip).limit(limit).all()

        return [
            {
                'portfolio': p,
                'valor_total_mes': vt,
                'valor_unitario_mes': vu,
                'quantidade_mes': q,
            }
            for p, vt, vu, q in rows
        ]

    def list_all_for_anomes(
        self, user_id: int, anomes: int
    ) -> List[tuple]:
        """Retorna (InvestimentoPortfolio, InvestimentoHistorico) para investimentos com histórico no anomes."""
        return self.db.query(
            InvestimentoPortfolio,
            InvestimentoHistorico
        ).join(
            InvestimentoHistorico,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoPortfolio.ativo == True,
            InvestimentoHistorico.anomes == anomes
        ).all()

    def copiar_mes_anterior(
        self, user_id: int, anomes_destino: int
    ) -> int:
        """Copia todos investimentos do mês anterior para o mês destino. Retorna quantidade copiada."""
        ano_dest = anomes_destino // 100
        mes_dest = anomes_destino % 100
        # Mês anterior
        if mes_dest == 1:
            anomes_origem = (ano_dest - 1) * 100 + 12
        else:
            anomes_origem = ano_dest * 100 + (mes_dest - 1)

        rows = self.list_all_for_anomes(user_id, anomes_origem)
        if not rows:
            return 0

        # Último dia do mês destino
        _, last_day = monthrange(ano_dest, mes_dest)
        data_ref = date(ano_dest, mes_dest, last_day)

        count = 0
        for portfolio, historico in rows:
            # Novo balance_id único (user_id evita colisão entre usuários)
            new_balance_id = f"copy-{user_id}-{portfolio.id}-{anomes_destino}"
            if self.get_by_balance_id(new_balance_id, user_id):
                continue  # Já existe, pular

            # Criar novo portfolio (cópia)
            new_portfolio = InvestimentoPortfolio(
                user_id=user_id,
                balance_id=new_balance_id,
                nome_produto=portfolio.nome_produto,
                corretora=portfolio.corretora,
                tipo_investimento=portfolio.tipo_investimento,
                classe_ativo=portfolio.classe_ativo,
                emissor=portfolio.emissor,
                ano=ano_dest,
                anomes=anomes_destino,
                percentual_cdi=portfolio.percentual_cdi,
                data_aplicacao=portfolio.data_aplicacao,
                data_vencimento=portfolio.data_vencimento,
                quantidade=historico.quantidade or portfolio.quantidade,
                valor_unitario_inicial=historico.valor_unitario or portfolio.valor_unitario_inicial,
                valor_total_inicial=historico.valor_total or portfolio.valor_total_inicial,
                ativo=True,
            )
            new_portfolio = self.create(new_portfolio)

            # Criar historico - garantir valor_total = valor_unitario * quantidade
            qty = float(historico.quantidade or 1) or 1.0
            vt = float(historico.valor_total or 0)
            vu = float(historico.valor_unitario or 0)
            if vt and (not vu or vu == 0):
                vu = vt / qty
            elif vu and (not vt or vt == 0):
                vt = vu * qty
            new_historico = InvestimentoHistorico(
                investimento_id=new_portfolio.id,
                ano=ano_dest,
                mes=mes_dest,
                anomes=anomes_destino,
                data_referencia=data_ref,
                quantidade=qty,
                valor_unitario=Decimal(str(vu)),
                valor_total=Decimal(str(vt)),
                aporte_mes=historico.aporte_mes or Decimal('0'),
                rendimento_mes=historico.rendimento_mes,
                rendimento_acumulado=historico.rendimento_acumulado,
            )
            self.create_historico(new_historico)
            count += 1

        return count

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

    def get_historico_by_investimento_and_anomes(
        self, investimento_id: int, anomes: int
    ) -> Optional[InvestimentoHistorico]:
        """Busca histórico de um investimento para um mês específico"""
        return self.db.query(InvestimentoHistorico).filter(
            InvestimentoHistorico.investimento_id == investimento_id,
            InvestimentoHistorico.anomes == anomes
        ).first()

    def update_historico(self, historico: InvestimentoHistorico) -> InvestimentoHistorico:
        """Atualiza registro de histórico"""
        self.db.commit()
        self.db.refresh(historico)
        return historico

    def delete_historico_by_investimento_and_anomes(
        self, investimento_id: int, anomes: int
    ) -> bool:
        """Remove registro de histórico de um investimento para um mês específico."""
        deleted = self.db.query(InvestimentoHistorico).filter(
            InvestimentoHistorico.investimento_id == investimento_id,
            InvestimentoHistorico.anomes == anomes
        ).delete()
        self.db.commit()
        return deleted > 0

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

    def get_rendimento_por_tipo(
        self,
        user_id: int,
        classe_ativo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retorna rendimento agrupado por tipo de investimento baseado no último mês.
        classe_ativo: 'Ativo' | 'Passivo' para filtrar, ou None para todos."""
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
        
        query = self.db.query(
            InvestimentoPortfolio.tipo_investimento,
            func.count(InvestimentoHistorico.id).label('quantidade'),
            func.sum(InvestimentoHistorico.valor_total).label('total_investido')
        ).join(
            InvestimentoHistorico,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes == ultimo_mes
        )
        if classe_ativo:
            query = query.filter(
                InvestimentoPortfolio.classe_ativo == classe_ativo.strip()
            )
        return [
            {
                'tipo': r.tipo_investimento,
                'quantidade': r.quantidade,
                'total_investido': r.total_investido or Decimal('0')
            }
            for r in query.group_by(InvestimentoPortfolio.tipo_investimento).all()
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

    def get_patrimonio_timeline(
        self,
        user_id: int,
        ano_inicio: int,
        ano_fim: int
    ) -> List[Dict[str, Any]]:
        """Retorna série temporal de ativos, passivos e PL por mês"""
        results = self.db.query(
            InvestimentoPortfolio.classe_ativo,
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.anomes,
            func.sum(InvestimentoHistorico.valor_total).label('total')
        ).join(
            InvestimentoPortfolio,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.ano >= ano_inicio,
            InvestimentoHistorico.ano <= ano_fim
        ).group_by(
            InvestimentoPortfolio.classe_ativo,
            InvestimentoHistorico.ano,
            InvestimentoHistorico.mes,
            InvestimentoHistorico.anomes
        ).order_by(
            InvestimentoHistorico.anomes
        ).all()

        # Agrupar por anomes
        by_anomes: Dict[int, Dict] = {}
        for r in results:
            anomes = r.anomes
            if anomes not in by_anomes:
                by_anomes[anomes] = {'ano': r.ano, 'mes': r.mes, 'anomes': anomes, 'ativos': 0.0, 'passivos': 0.0}
            classe = (r.classe_ativo or '').strip()
            valor = float(r.total or 0)
            if classe.lower() == 'ativo':
                by_anomes[anomes]['ativos'] += valor
            elif classe.lower() == 'passivo':
                by_anomes[anomes]['passivos'] += valor

        return [
            {
                'ano': v['ano'],
                'mes': v['mes'],
                'anomes': v['anomes'],
                'ativos': v['ativos'],
                'passivos': v['passivos'],
                'patrimonio_liquido': v['ativos'] + v['passivos']
            }
            for v in sorted(by_anomes.values(), key=lambda x: x['anomes'])
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

    def delete_projecao_by_cenario(self, cenario_id: int) -> int:
        """Remove todas as projeções de um cenário. Retorna quantidade removida."""
        deleted = self.db.query(CenarioProjecao).filter(
            CenarioProjecao.cenario_id == cenario_id
        ).delete()
        self.db.commit()
        return deleted

    def bulk_create_projecao(
        self,
        cenario_id: int,
        projecoes: List[Dict[str, Any]]
    ) -> int:
        """Insere projeções em lote. projecoes = [{mes_num, anomes, patrimonio, aporte}, ...]"""
        objs = [
            CenarioProjecao(
                cenario_id=cenario_id,
                mes_num=p['mes_num'],
                anomes=p['anomes'],
                patrimonio=Decimal(str(p['patrimonio'])),
                aporte=Decimal(str(p.get('aporte', 0))),
            )
            for p in projecoes
        ]
        self.db.bulk_save_objects(objs)
        self.db.commit()
        return len(objs)

    def get_projecao_by_cenario(
        self,
        cenario_id: int,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Retorna projeções de um cenário (validando ownership)"""
        cenario = self.get_cenario_by_id(cenario_id, user_id)
        if not cenario:
            return []
        rows = self.db.query(CenarioProjecao).filter(
            CenarioProjecao.cenario_id == cenario_id
        ).order_by(CenarioProjecao.mes_num).all()
        return [
            {
                'mes_num': r.mes_num,
                'anomes': r.anomes,
                'patrimonio': float(r.patrimonio),
                'aporte': float(r.aporte) if r.aporte is not None else 0,
            }
            for r in rows
        ]

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
