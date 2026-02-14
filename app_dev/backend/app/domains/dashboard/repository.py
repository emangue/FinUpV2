"""
Domínio Dashboard - Repository
Queries SQL para estatísticas
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, case
from datetime import datetime
from typing import Optional, List, Dict

from app.domains.transactions.models import JournalEntry
from app.domains.budget.models import BudgetPlanning


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_last_month_with_data(self, user_id: int):
        """Retorna último ano e mês com dados para o usuário"""
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
    
    def _build_date_filter(self, year: int, month: Optional[int] = None):
        """Constrói filtro usando MesFatura
        
        Args:
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        year_str = str(year)
        
        # Se month=None, filtrar ano inteiro usando coluna Ano
        if month is None:
            return JournalEntry.Ano == year_str
        
        # Com mês específico, usar MesFatura (formato YYYYMM)
        mes_fatura = f"{year}{month:02d}"
        return JournalEntry.MesFatura == mes_fatura
    
    def get_metrics(self, user_id: int, year: int, month: Optional[int] = None) -> Dict:
        """Calcula métricas principais
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        # Filtro base - SEMPRE filtrar por IgnorarDashboard = 0
        date_filter = self._build_date_filter(year, month)
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
        
        if prev_month is not None:
            # Buscar despesas do mês anterior
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
            
            # Calcular variação percentual
            if prev_total_despesas > 0:
                change_percentage = ((total_despesas - prev_total_despesas) / prev_total_despesas) * 100
            elif total_despesas > 0:
                change_percentage = 100.0  # Sem gasto anterior, mas tem gasto agora = 100% aumento
            else:
                change_percentage = 0.0
        
        return {
            "total_despesas": total_despesas,
            "total_receitas": total_receitas,
            "total_cartoes": total_cartoes,
            "saldo_periodo": saldo_periodo,
            "num_transacoes": num_transacoes,
            "change_percentage": round(change_percentage, 1) if change_percentage is not None else None
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
