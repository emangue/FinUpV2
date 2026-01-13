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
        
        # Total de despesas (CategoriaGeral = 'Despesa')
        total_despesas = base_query.filter(
            JournalEntry.CategoriaGeral == 'Despesa'
        ).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0
        
        # Total de receitas (CategoriaGeral = 'Receita')
        total_receitas = base_query.filter(
            JournalEntry.CategoriaGeral == 'Receita'
        ).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0
        
        # Total de cartões (TipoTransacao = 'Cartão de Crédito')
        total_cartoes = base_query.filter(
            JournalEntry.TipoTransacao == 'Cartão de Crédito'
        ).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0
        
        # Número de transações
        num_transacoes = base_query.count()
        
        # Saldo do período (Receitas - Despesas)
        saldo_periodo = total_receitas - total_despesas
        
        return {
            "total_despesas": abs(total_despesas),
            "total_receitas": total_receitas,
            "total_cartoes": total_cartoes,
            "saldo_periodo": saldo_periodo,
            "num_transacoes": num_transacoes
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
                        (JournalEntry.CategoriaGeral == 'Receita', func.abs(JournalEntry.Valor)),
                        else_=0
                    )
                ).label('receitas'),
                func.sum(
                    case(
                        (JournalEntry.CategoriaGeral == 'Despesa', func.abs(JournalEntry.Valor)),
                        else_=0
                    )
                ).label('despesas')
            ).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.IgnorarDashboard == 0
            ).first()
            
            months_data.append({
                "date": month_names[target_month - 1],
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
        total_despesas = self.db.query(
            func.sum(func.abs(JournalEntry.Valor))
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0
        ).scalar() or 1.0  # Evita divisão por zero
        
        # Despesas por categoria
        results = self.db.query(
            JournalEntry.GRUPO.label('categoria'),
            func.sum(func.abs(JournalEntry.Valor)).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.GRUPO.isnot(None)
        ).group_by(
            JournalEntry.GRUPO
        ).order_by(
            func.sum(func.abs(JournalEntry.Valor)).desc()
        ).all()
        
        return [
            {
                "categoria": row.categoria or "Sem categoria",
                "total": float(row.total),
                "percentual": round((float(row.total) / total_despesas) * 100, 2)
            }
            for row in results
        ]
    
    def get_budget_vs_actual(self, user_id: int, year: int, month: Optional[int] = None) -> Dict:
        """Comparação Realizado vs Planejado por TipoGasto
        
        Args:
            user_id: ID do usuário
            year: Ano
            month: Mês (1-12) ou None para YTD (Year to Date - todo o ano)
        
        Returns:
            Dict com items (lista de comparações) e totais
        """
        # Se month=None, buscar todo o ano (YTD)
        if month is None:
            # Filtro de data para o ano inteiro
            date_filter = self._build_date_filter(year, None)
            
            # 1. Buscar valores planejados de todos os meses do ano
            budgets = self.db.query(
                BudgetPlanning.tipo_gasto,
                func.sum(BudgetPlanning.valor_planejado).label('total_planejado')
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia.like(f'{year}-%')
            ).group_by(
                BudgetPlanning.tipo_gasto
            ).all()
            
            # Criar dict de planejados
            planejado_dict = {b.tipo_gasto: float(b.total_planejado) for b in budgets}
        else:
            # Mês específico
            mes_referencia = f"{year}-{month:02d}"
            date_filter = self._build_date_filter(year, month)
            
            # 1. Buscar valores planejados do mês
            budgets = self.db.query(
                BudgetPlanning.tipo_gasto,
                BudgetPlanning.valor_planejado
            ).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_referencia
            ).all()
            
            # Criar dict de planejados
            planejado_dict = {b.tipo_gasto: float(b.valor_planejado) for b in budgets}
        
        # 2. Buscar valores realizados agrupados por TipoGasto
        realizados = self.db.query(
            JournalEntry.TipoGasto,
            func.sum(func.abs(JournalEntry.Valor)).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.TipoGasto.isnot(None)
        ).group_by(
            JournalEntry.TipoGasto
        ).all()
        
        # Criar dict de realizados
        realizado_dict = {r.TipoGasto: float(r.total) for r in realizados}
        
        # 3. Combinar ambos (união de todos os TipoGasto)
        all_tipos = set(planejado_dict.keys()) | set(realizado_dict.keys())
        
        items = []
        total_realizado = 0.0
        total_planejado = 0.0
        
        for tipo_gasto in sorted(all_tipos):
            realizado = realizado_dict.get(tipo_gasto, 0.0)
            planejado = planejado_dict.get(tipo_gasto, 0.0)
            
            # Calcular percentual (evitar divisão por zero)
            if planejado > 0:
                percentual = round((realizado / planejado) * 100, 1)
            else:
                percentual = 0.0 if realizado == 0 else 999.9  # Indica que não tem planejado
            
            diferenca = realizado - planejado
            
            items.append({
                "tipo_gasto": tipo_gasto,
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
