"""
Domínio Dashboard - Repository
Queries SQL para estatísticas
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, case
from datetime import datetime
from typing import Optional, List, Dict

from app.domains.transactions.models import JournalEntry
from app.domains.budget.models import BudgetPlanning
from app.domains.grupos.models import BaseGruposConfig
from app.domains.investimentos.models import InvestimentoPortfolio, InvestimentoHistorico, InvestimentoPlanejamento
from app.domains.investimentos.repository import InvestimentoRepository


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db
        self.investimento_repo = InvestimentoRepository(db)

    def _get_patrimonio_por_mes(self, user_id: int, anomes: int):
        """
        Retorna ativos, passivos e patrimônio líquido para um mês específico (YYYYMM).
        Usa sempre o mês solicitado; se não houver dados, retorna None (evita duplicação).
        """
        investimento_ids = self.db.query(InvestimentoPortfolio.id).filter(
            InvestimentoPortfolio.user_id == user_id
        )

        resultado = self.db.query(
            InvestimentoPortfolio.classe_ativo,
            func.sum(InvestimentoHistorico.valor_total).label('total')
        ).join(
            InvestimentoHistorico,
            InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
        ).filter(
            InvestimentoPortfolio.user_id == user_id,
            InvestimentoHistorico.anomes == anomes
        ).group_by(
            InvestimentoPortfolio.classe_ativo
        ).all()
        if not resultado:
            return None
        total_ativos = 0.0
        total_passivos = 0.0
        for row in resultado:
            classe = (row.classe_ativo or '').strip()
            valor = float(row.total or 0)
            if classe.lower() == 'ativo':
                total_ativos += valor
            elif classe.lower() == 'passivo':
                total_passivos += valor
        return {
            "ativos": total_ativos,
            "passivos": total_passivos,
            "patrimonio_liquido": total_ativos + total_passivos,
        }
    
    def get_last_month_with_data(self, user_id: int, source: str = "transactions"):
        """Retorna último ano e mês com dados para o usuário.
        source: transactions=journal_entries, patrimonio=investimentos_historico
        """
        if source == "patrimonio":
            # Último mês com dados em investimentos_historico (ativos/passivos)
            result = self.db.query(
                func.max(InvestimentoHistorico.anomes)
            ).join(
                InvestimentoPortfolio,
                InvestimentoHistorico.investimento_id == InvestimentoPortfolio.id
            ).filter(
                InvestimentoPortfolio.user_id == user_id
            ).scalar()
            if result:
                anomes = int(result)
                year = anomes // 100
                month = anomes % 100
                return {"year": year, "month": month}
        else:
            # transactions: último mês em journal_entries
            result = self.db.query(
                JournalEntry.Ano,
                JournalEntry.Mes
            ).filter(
                JournalEntry.user_id == user_id
            ).order_by(
                JournalEntry.Ano.desc(),
                JournalEntry.Mes.desc()
            ).first()
            if result:
                return {"year": int(result.Ano), "month": int(result.Mes)}
        return {"year": datetime.now().year, "month": datetime.now().month}
    
    def _build_date_filter(self, year: int, month: Optional[int] = None, ytd_month: Optional[int] = None):
        """Constrói filtro usando MesFatura/Ano/Mes
        
        Args:
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro / YTD
            ytd_month: Se informado com month=None, filtra Jan..ytd_month (YTD)
        """
        if month is not None:
            # Mês específico
            mes_fatura = f"{year}{month:02d}"
            return JournalEntry.MesFatura == mes_fatura
        if ytd_month is not None:
            # YTD: Jan até ytd_month
            return and_(JournalEntry.Ano == year, JournalEntry.Mes <= ytd_month)
        # Ano inteiro
        return JournalEntry.Ano == year
    
    def get_metrics(
        self,
        user_id: int,
        year: int,
        month: Optional[int] = None,
        ytd_month: Optional[int] = None
    ) -> Dict:
        """Calcula métricas principais
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro / YTD
            ytd_month: Se informado com month=None, soma Jan..ytd_month (YTD)
        """
        # Filtro base - SEMPRE filtrar por IgnorarDashboard = 0
        date_filter = self._build_date_filter(year, month, ytd_month)
        base_query = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.IgnorarDashboard == 0  # Apenas transações que aparecem no dashboard
        )
        
        # Total de despesas (CategoriaGeral = 'Despesa') - soma valores negativos
        despesas_raw = base_query.filter(
            JournalEntry.CategoriaGeral == 'Despesa'
        ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0
        total_despesas = abs(despesas_raw)  # Aplicar abs() só para exibição
        
        # Total de receitas (CategoriaGeral = 'Receita') - soma valores positivos
        total_receitas = base_query.filter(
            JournalEntry.CategoriaGeral == 'Receita'
        ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0
        
        # Total de cartões (TipoTransacao = 'Cartão de Crédito')
        total_cartoes = base_query.filter(
            JournalEntry.TipoTransacao == 'Cartão de Crédito'
        ).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0
        
        # Número de transações
        num_transacoes = base_query.count()
        
        # Saldo do período (Receitas + Despesas, onde Despesas são negativas)
        saldo_periodo = total_receitas + despesas_raw
        
        # Calcular variação percentual vs mês anterior (apenas se month é específico)
        change_percentage = None
        if month is not None and month > 1:
            # Mês anterior mesmo ano
            prev_month = month - 1
            prev_year = year
        elif month == 1:
            # Janeiro - comparar com dezembro do ano anterior
            prev_month = 12
            prev_year = year - 1
        else:
            # month=None (ano inteiro) - não calcula variação
            prev_month = None
            prev_year = None
        
        receitas_change_percentage = None
        despesas_vs_plano_percent = None

        if prev_month is not None:
            prev_date_filter = self._build_date_filter(prev_year, prev_month)
            prev_query = self.db.query(JournalEntry).filter(
                JournalEntry.user_id == user_id,
                prev_date_filter,
                JournalEntry.IgnorarDashboard == 0
            )
            prev_despesas_raw = prev_query.filter(
                JournalEntry.CategoriaGeral == 'Despesa'
            ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0
            prev_total_despesas = abs(prev_despesas_raw)
            prev_total_receitas = prev_query.filter(
                JournalEntry.CategoriaGeral == 'Receita'
            ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0

            if prev_total_despesas > 0:
                change_percentage = ((total_despesas - prev_total_despesas) / prev_total_despesas) * 100
            elif total_despesas > 0:
                change_percentage = 100.0
            else:
                change_percentage = 0.0

            if prev_total_receitas > 0:
                receitas_change_percentage = ((total_receitas - prev_total_receitas) / prev_total_receitas) * 100
            elif total_receitas > 0:
                receitas_change_percentage = 100.0
            else:
                receitas_change_percentage = 0.0

        if month is not None:
            mes_referencia = f"{year}-{month:02d}"
            total_planejado = self.db.query(
                func.sum(BudgetPlanning.valor_planejado)
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_referencia,
                BudgetPlanning.ativo == True  # PostgreSQL: boolean; SQLite: 0/1
            ).scalar() or 0.0
            if total_planejado > 0:
                despesas_vs_plano_percent = round((total_despesas / total_planejado) * 100, 1)

        # Patrimônio: usa mesma lógica do meufinup (investimentos/resumo) - último mês disponível
        # Garante os mesmos números: Ativos, Passivos, PL
        ativos_mes = 0.0
        passivos_mes = 0.0
        patrimonio_liquido_mes = 0.0
        ativos_change_percentage = None
        passivos_change_percentage = None
        patrimonio_change_percentage = None
        patrimonio_vs_plano_percent = None

        try:
            resumo = self.investimento_repo.get_portfolio_resumo(user_id)
            if resumo:
                ativos_mes = float(resumo.get("total_investido") or 0)
                passivos_mes = float(resumo.get("valor_atual") or 0)
                patrimonio_liquido_mes = float(resumo.get("rendimento_total") or 0)

                # Calcular vs mês anterior: precisamos do ultimo_mes usado
                ultimo_anomes = self.db.query(
                    func.max(InvestimentoHistorico.anomes)
                ).filter(
                    InvestimentoHistorico.investimento_id.in_(
                        self.db.query(InvestimentoPortfolio.id).filter(
                            InvestimentoPortfolio.user_id == user_id
                        )
                    )
                ).scalar()
                if ultimo_anomes:
                    # Mês anterior ao ultimo
                    uy, um = divmod(ultimo_anomes, 100)
                    if um > 1:
                        prev_anomes = ultimo_anomes - 1
                    else:
                        prev_anomes = (uy - 1) * 100 + 12
                    prev_res = self._get_patrimonio_por_mes(user_id, prev_anomes)
                    if prev_res:
                        prev_ativos = float(prev_res.get("ativos") or 0)
                        prev_passivos = float(prev_res.get("passivos") or 0)
                        prev_pl = float(prev_res.get("patrimonio_liquido") or 0)
                        if prev_ativos != 0:
                            ativos_change_percentage = ((ativos_mes - prev_ativos) / abs(prev_ativos)) * 100
                        elif ativos_mes != 0:
                            ativos_change_percentage = 100.0
                        if prev_passivos != 0:
                            passivos_change_percentage = ((passivos_mes - prev_passivos) / abs(prev_passivos)) * 100
                        elif passivos_mes != 0:
                            passivos_change_percentage = 100.0
                        if prev_pl != 0:
                            patrimonio_change_percentage = ((patrimonio_liquido_mes - prev_pl) / abs(prev_pl)) * 100
                        elif patrimonio_liquido_mes != 0:
                            patrimonio_change_percentage = 100.0

                    # vs Plan: meta_patrimonio do InvestimentoPlanejamento (usar anomes do último mês)
                    meta = self.db.query(InvestimentoPlanejamento.meta_patrimonio).filter(
                        InvestimentoPlanejamento.user_id == user_id,
                        InvestimentoPlanejamento.anomes == ultimo_anomes
                    ).first()
                    if meta and meta.meta_patrimonio is not None and float(meta.meta_patrimonio) > 0:
                        patrimonio_vs_plano_percent = round(
                            (patrimonio_liquido_mes / float(meta.meta_patrimonio)) * 100, 1
                        )
        except Exception as e:
            logging.warning("Dashboard get_metrics: erro ao calcular patrimônio: %s", e, exc_info=True)

        return {
            "total_despesas": total_despesas,
            "total_receitas": total_receitas,
            "total_cartoes": total_cartoes,
            "saldo_periodo": saldo_periodo,
            "num_transacoes": num_transacoes,
            "change_percentage": round(change_percentage, 1) if change_percentage is not None else None,
            "receitas_change_percentage": round(receitas_change_percentage, 1) if receitas_change_percentage is not None else None,
            "despesas_vs_plano_percent": despesas_vs_plano_percent,
            "ativos_mes": ativos_mes,
            "passivos_mes": passivos_mes,
            "patrimonio_liquido_mes": patrimonio_liquido_mes,
            "ativos_change_percentage": round(ativos_change_percentage, 1) if ativos_change_percentage is not None else None,
            "passivos_change_percentage": round(passivos_change_percentage, 1) if passivos_change_percentage is not None else None,
            "patrimonio_change_percentage": round(patrimonio_change_percentage, 1) if patrimonio_change_percentage is not None else None,
            "patrimonio_vs_plano_percent": patrimonio_vs_plano_percent,
        }
    
    def get_chart_data(self, user_id: int, year: int, month: int) -> List[Dict]:
        """Retorna dados para gráfico de área (receitas vs despesas) - sempre 12 meses de histórico
        
        Retorna os últimos 12 meses até o mês especificado, incluindo ano anterior se necessário.
        Se month=1 (janeiro), retorna fev/ano-1 até jan/ano atual.
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        # Determinar o mês de referência (último mês a ser incluído)
        reference_date = datetime(year, month if month > 0 else 12, 1)
        
        # Calcular os últimos 12 meses
        months_data = []
        month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for i in range(11, -1, -1):  # 11 meses atrás até o mês atual
            target_date = reference_date - relativedelta(months=i)
            target_month = target_date.month
            target_year = target_date.year
            
            # Query para o mês específico usando MesFatura
            mes_fatura = f"{target_year}{target_month:02d}"
            
            result = self.db.query(
                func.sum(
                    case(
                        (JournalEntry.CategoriaGeral == 'Receita', JournalEntry.Valor),
                        else_=0
                    )
                ).label('receitas'),
                func.abs(
                    func.sum(
                        case(
                            (JournalEntry.CategoriaGeral == 'Despesa', JournalEntry.Valor),
                            else_=0
                        )
                    )
                ).label('despesas')
            ).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.IgnorarDashboard == 0
            ).first()
            
            months_data.append({
                "date": f"{target_year}-{target_month:02d}-01",  # Formato YYYY-MM-01
                "receitas": float(result.receitas or 0) if result else 0.0,
                "despesas": float(result.despesas or 0) if result else 0.0,
                "year": target_year,  # Adicionar ano para referência
                "month": target_month
            })
        
        return months_data
    
    def get_chart_data_yearly(
        self,
        user_id: int,
        years: List[int],
        ytd_month: Optional[int] = None
    ) -> List[Dict]:
        """Retorna dados para gráfico por ano (receitas vs despesas).
        
        Args:
            user_id: ID do usuário
            years: Lista de anos a retornar (ex: [2023, 2024, 2025])
            ytd_month: Se informado, soma apenas Jan..ytd_month de cada ano (YTD).
                       Se None, soma o ano inteiro.
        """
        years_data = []
        for target_year in sorted(years):
            base_filter = [
                JournalEntry.user_id == user_id,
                JournalEntry.Ano == target_year,
                JournalEntry.IgnorarDashboard == 0
            ]
            if ytd_month is not None:
                base_filter.append(JournalEntry.Mes <= ytd_month)
            
            result = self.db.query(
                func.sum(
                    case(
                        (JournalEntry.CategoriaGeral == 'Receita', JournalEntry.Valor),
                        else_=0
                    )
                ).label('receitas'),
                func.abs(
                    func.sum(
                        case(
                            (JournalEntry.CategoriaGeral == 'Despesa', JournalEntry.Valor),
                            else_=0
                        )
                    )
                ).label('despesas')
            ).filter(*base_filter).first()
            
            years_data.append({
                "date": f"{target_year}-01-01",
                "receitas": float(result.receitas or 0) if result else 0.0,
                "despesas": float(result.despesas or 0) if result else 0.0,
                "year": target_year
            })
        
        return years_data
    
    def get_category_expenses(self, user_id: int, year: int, month: Optional[int] = None) -> List[Dict]:
        """Retorna despesas agrupadas por categoria
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        date_filter = self._build_date_filter(year, month)
        
        # Total geral de despesas (para calcular percentual) - FILTRAR IgnorarDashboard = 0
        # Somar valores e depois aplicar abs() para evitar somar positivos e negativos separadamente
        total_despesas_raw = self.db.query(
            func.sum(JournalEntry.Valor)
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0
        ).scalar() or 0.0
        total_despesas = abs(total_despesas_raw) if total_despesas_raw != 0 else 1.0  # Evita divisão por zero
        
        # Despesas por categoria - somar primeiro, depois aplicar abs()
        results = self.db.query(
            JournalEntry.GRUPO.label('categoria'),
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.GRUPO.isnot(None)
        ).group_by(
            JournalEntry.GRUPO
        ).order_by(
            func.abs(func.sum(JournalEntry.Valor)).desc()
        ).all()
        
        return [
            {
                "categoria": row.categoria or "Sem categoria",
                "total": abs(float(row.total)),  # Aplicar abs() aqui para exibir como positivo
                "percentual": round((abs(float(row.total)) / total_despesas) * 100, 2)
            }
            for row in results
        ]
    
    def get_budget_vs_actual(self, user_id: int, year: int, month: Optional[int] = None) -> Dict:
        """Comparação Realizado vs Planejado por Grupo
        
        Args:
            user_id: ID do usuário
            year: Ano
            month: Mês (1-12) ou None para YTD (Year to Date - todo o ano)
        
        Returns:
            Dict com items (lista de comparações) e totais
        """
        # Se month=None, buscar todo o ano (YTD)
        if month is None:
            # 1. Buscar valores planejados de todos os meses do ano
            budgets = self.db.query(
                BudgetPlanning.grupo,
                func.sum(BudgetPlanning.valor_planejado).label('total_planejado')
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia.like(f'{year}-%')
            ).group_by(
                BudgetPlanning.grupo
            ).all()
            
            # Criar dict de planejados
            planejado_dict = {b.grupo: float(b.total_planejado) for b in budgets}
        else:
            # Mês específico
            mes_referencia = f"{year}-{month:02d}"
            
            # 1. Buscar valores planejados do mês
            budgets = self.db.query(
                BudgetPlanning.grupo,
                BudgetPlanning.valor_planejado
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_referencia
            ).all()
            
            # Criar dict de planejados
            planejado_dict = {b.grupo: float(b.valor_planejado) for b in budgets}
        
        # 2. Buscar valores realizados agrupados por Grupo
        # REGRA: NUNCA usar campo Data (string) para filtros - usar Ano/Mes (integer)
        realizados_filters = [
            JournalEntry.user_id == user_id,
            JournalEntry.Ano == year,
            JournalEntry.CategoriaGeral == 'Despesa',  # FILTRO CRÍTICO: Apenas despesas
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.GRUPO.isnot(None)
        ]
        
        # Se month=None, buscar todo o ano; se month especificado, filtrar mês
        if month is not None:
            mes_fatura = f"{year}{month:02d}"  # Formato YYYYMM
            realizados_filters.append(JournalEntry.MesFatura == mes_fatura)
            
        realizados = self.db.query(
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(*realizados_filters).group_by(
            JournalEntry.GRUPO
        ).all()
        
        # Criar dict de realizados (converter para positivo apenas na exibição)
        realizado_dict = {r.GRUPO: abs(float(r.total)) for r in realizados}
        
        # 3. Combinar ambos (união de todos os Grupos)
        all_grupos = set(planejado_dict.keys()) | set(realizado_dict.keys())
        
        items = []
        total_realizado = 0.0
        total_planejado = 0.0
        
        for grupo in sorted(all_grupos):
            realizado = realizado_dict.get(grupo, 0.0)
            planejado = planejado_dict.get(grupo, 0.0)
            
            # Calcular percentual (evitar divisão por zero)
            if planejado > 0:
                percentual = round((realizado / planejado) * 100, 1)
            else:
                percentual = 0.0 if realizado == 0 else 999.9  # Indica que não tem planejado
            
            diferenca = realizado - planejado
            
            items.append({
                "grupo": grupo,
                "realizado": realizado,
                "planejado": planejado,
                "percentual": percentual,
                "diferenca": diferenca
            })
            
            total_realizado += realizado
            total_planejado += planejado
        
        # Percentual geral
        if total_planejado > 0:
            percentual_geral = round((total_realizado / total_planejado) * 100, 1)
        else:
            percentual_geral = 0.0
        
        return {
            "items": items,
            "total_realizado": total_realizado,
            "total_planejado": total_planejado,
            "percentual_geral": percentual_geral
        }
    
    def get_subgrupos_by_tipo(self, user_id: int, year: int, month: int, grupo: str):
        """Busca subgrupos de um tipo de gasto específico com valores.
        Usa MesFatura apenas (igual ao budget) para consistência com valor realizado.
        """
        from sqlalchemy import func
        from app.domains.transactions.models import JournalEntry
        
        # Filtros alinhados com budget._calcular_valor_realizado_grupo
        filters = [
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0
        ]
        if month is not None:
            mes_fatura = f"{year}{month:02d}"  # YYYYMM
            filters.append(JournalEntry.MesFatura == mes_fatura)
        
        # Query para buscar subgrupos e somar valores
        query = (
            self.db.query(
                JournalEntry.SUBGRUPO.label('subgrupo'),
                func.sum(JournalEntry.Valor).label('valor')
            )
            .filter(*filters)
            .group_by(JournalEntry.SUBGRUPO)
        )
        
        results = query.all()
        
        # Ordenar por valor absoluto (maior primeiro) para exibição
        results = sorted(results, key=lambda x: abs(x.valor), reverse=True)
        
        # Calcular total para percentuais - somar primeiro, depois aplicar abs()
        total = sum(r.valor for r in results)  # Soma com sinal (negativo)
        total_abs = abs(total)  # Aplicar abs() no total final
        
        # Formatar resposta (exibe valores como positivos, mas percentual baseado no total real)
        subgrupos = []
        for row in results:
            subgrupos.append({
                "subgrupo": row.subgrupo or "Sem subgrupo",
                "valor": abs(float(row.valor)),  # Exibe como positivo
                "percentual": round((abs(row.valor) / total_abs * 100), 1) if total_abs > 0 else 0.0
            })
        
        return subgrupos
    
    def get_planejado_by_tipo(self, user_id: int, year: int, month: int, grupo: str):
        """Busca o valor planejado para um grupo específico"""
        from sqlalchemy import func
        from app.domains.budget.models import BudgetPlanning
        
        # Construir mes_referencia no formato YYYY-MM
        if month is not None:
            mes_referencia = f"{year}-{month:02d}"
            filters = [
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_referencia,
                BudgetPlanning.grupo == grupo
            ]
        else:
            # Se month é None, buscar todos os meses do ano
            filters = [
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia.like(f"{year}-%"),
                BudgetPlanning.grupo == grupo
            ]
        
        # Query para somar valor planejado
        query = (
            self.db.query(func.sum(BudgetPlanning.valor_planejado))
            .filter(*filters)
        )
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def get_credit_card_expenses(self, user_id: int, year: int, month: Optional[int] = None) -> List[Dict]:
        """Retorna despesas agrupadas por cartão de crédito
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        
        Returns:
            Lista de dicts com: cartao, total, percentual, num_transacoes
        """
        # Filtro base
        date_filter = self._build_date_filter(year, month)
        
        # Query agrupada por cartão - apenas transações com NomeCartao não nulo
        query = (
            self.db.query(
                JournalEntry.NomeCartao.label('cartao'),
                func.abs(func.sum(JournalEntry.Valor)).label('total'),
                func.count(JournalEntry.id).label('num_transacoes')
            )
            .filter(
                JournalEntry.user_id == user_id,
                date_filter,
                JournalEntry.IgnorarDashboard == 0,
                JournalEntry.CategoriaGeral == 'Despesa',  # Apenas despesas
                JournalEntry.NomeCartao.isnot(None),  # Apenas com cartão
                JournalEntry.NomeCartao != ''  # Não vazio
            )
            .group_by(JournalEntry.NomeCartao)
            .order_by(func.abs(func.sum(JournalEntry.Valor)).desc())
        )
        
        results = query.all()
        
        if not results:
            return []
        
        # Calcular total geral para percentuais
        total_geral = sum(r.total for r in results)
        
        # Formatar resposta
        return [
            {
                'cartao': r.cartao,
                'total': float(r.total),
                'percentual': round((r.total / total_geral * 100), 1) if total_geral > 0 else 0.0,
                'num_transacoes': int(r.num_transacoes)
            }
            for r in results
        ]
    
    def get_orcamento_investimentos(self, user_id: int, year: int, month: Optional[int] = None) -> Dict:
        """Investimentos vs Plano: realizado (journal CategoriaGeral=Investimentos) vs planejado (budget grupos Investimentos)
        
        Returns:
            total_investido, total_planejado, items: [{ grupo, valor, plano }]
        """
        # Grupos com categoria_geral = Investimentos
        grupos_inv = self.db.query(BaseGruposConfig.nome_grupo).filter(
            BaseGruposConfig.categoria_geral == 'Investimentos'
        ).all()
        nomes_inv = [r.nome_grupo for r in grupos_inv]
        
        if month is not None:
            mes_ref = f"{year}-{month:02d}"
            mes_fatura = f"{year}{month:02d}"
        else:
            mes_ref = None
            mes_fatura = None
        
        planejado_dict = {}
        if nomes_inv:
            q_budget = self.db.query(
                BudgetPlanning.grupo,
                BudgetPlanning.valor_planejado
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.grupo.in_(nomes_inv)
            )
            if mes_ref:
                q_budget = q_budget.filter(BudgetPlanning.mes_referencia == mes_ref)
            else:
                q_budget = q_budget.filter(BudgetPlanning.mes_referencia.like(f'{year}-%'))
            budgets = q_budget.all()
            for b in budgets:
                g = b.grupo
                planejado_dict[g] = planejado_dict.get(g, 0.0) + float(b.valor_planejado)
        # Realizado: journal_entries CategoriaGeral=Investimentos (valor negativo = aplicação)
        filters = [
            JournalEntry.user_id == user_id,
            JournalEntry.CategoriaGeral == 'Investimentos',
            JournalEntry.IgnorarDashboard == 0,
        ]
        if mes_fatura:
            filters.append(JournalEntry.MesFatura == mes_fatura)
        else:
            filters.append(JournalEntry.Ano == year)
        
        realizados = self.db.query(
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(*filters).group_by(JournalEntry.GRUPO).all()
        
        realizado_dict = {r.GRUPO: abs(float(r.total)) for r in realizados if r.GRUPO}
        
        all_grupos = set(planejado_dict.keys()) | set(realizado_dict.keys())
        items = []
        total_investido = 0.0
        total_planejado = 0.0
        for g in sorted(all_grupos):
            val = realizado_dict.get(g, 0.0)
            plano = planejado_dict.get(g, 0.0)
            items.append({'grupo': g, 'valor': val, 'plano': plano})
            total_investido += val
            total_planejado += plano
        
        return {
            'total_investido': total_investido,
            'total_planejado': total_planejado,
            'items': items
        }
    
    def get_income_sources(self, user_id: int, year: int, month: Optional[int] = None) -> List[Dict]:
        """Retorna breakdown de receitas por fonte (grupo)
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        
        Returns:
            Lista de dicts com: fonte (grupo), total, percentual, num_transacoes
        """
        # Filtro base
        date_filter = self._build_date_filter(year, month)
        
        # Query agrupada por GRUPO - apenas receitas
        query = (
            self.db.query(
                JournalEntry.GRUPO.label('fonte'),
                func.sum(JournalEntry.Valor).label('total'),
                func.count(JournalEntry.id).label('num_transacoes')
            )
            .filter(
                JournalEntry.user_id == user_id,
                date_filter,
                JournalEntry.IgnorarDashboard == 0,
                JournalEntry.CategoriaGeral == 'Receita',  # Apenas receitas
                JournalEntry.GRUPO.isnot(None),  # Apenas com grupo
                JournalEntry.GRUPO != ''  # Não vazio
            )
            .group_by(JournalEntry.GRUPO)
            .order_by(func.sum(JournalEntry.Valor).desc())
        )
        
        results = query.all()
        
        if not results:
            return []
        
        # Calcular total geral para percentuais
        total_geral = sum(r.total for r in results)
        
        # Formatar resposta
        return [
            {
                'fonte': r.fonte or 'Sem Categoria',
                'total': float(r.total),
                'percentual': round((r.total / total_geral * 100), 1) if total_geral > 0 else 0.0,
                'num_transacoes': int(r.num_transacoes)
            }
            for r in results
        ]
