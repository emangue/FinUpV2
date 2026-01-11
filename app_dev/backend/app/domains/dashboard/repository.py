"""
Domínio Dashboard - Repository
Queries SQL para estatísticas
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, case
from datetime import datetime
from typing import Optional, List, Dict

from app.domains.transactions.models import JournalEntry


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def _build_date_filter(self, year: int, month: Optional[int] = None):
        """Constrói filtro para data usando coluna Ano e Data
        
        Args:
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        year_str = str(year)
        
        # Se month=None, filtrar ano inteiro usando coluna Ano
        if month is None:
            return JournalEntry.Ano == year_str
        
        # Com mês específico, filtrar por Ano E mês na Data
        # Ex: Ano='2025' AND Data LIKE '%/01/%' (para janeiro)
        month_str = f"{month:02d}"  # Garante 2 dígitos
        
        # Padrões possíveis: DD/MM/YYYY ou D/M/YYYY
        patterns = [
            JournalEntry.Data.like(f'%/{month_str}/%'),  # %/01/%
            JournalEntry.Data.like(f'%/{month}/%')       # %/1/%
        ]
        
        return and_(
            JournalEntry.Ano == year_str,
            or_(*patterns)
        )
    
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
        """Retorna dados para gráfico de área (receitas vs despesas por mês do ano)"""
        # Query agrupada por mês do ano - FILTRAR IgnorarDashboard = 0
        results = self.db.query(
            func.substr(JournalEntry.Data, 4, 2).label('month'),  # Extrai MM de DD/MM/YYYY
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
            JournalEntry.Data.like(f'%/{year}'),  # Filtra pelo ano
            JournalEntry.IgnorarDashboard == 0  # Apenas transações que aparecem no dashboard
        ).group_by(
            func.substr(JournalEntry.Data, 4, 2)
        ).order_by(
            func.substr(JournalEntry.Data, 4, 2)
        ).all()
        
        # Mapear número do mês para nome
        month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        return [
            {
                "date": month_names[int(row.month) - 1] if row.month else "Unknown",
                "receitas": float(row.receitas or 0),
                "despesas": float(row.despesas or 0)
            }
            for row in results
        ]
    
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
