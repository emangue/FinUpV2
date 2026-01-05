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
    
    def _build_date_filter(self, year: int, month: int):
        """Constrói filtro para data no formato DD/MM/YYYY"""
        # Filtros para cobrir todos os formatos possíveis de data
        # Ex: 01/01/2025, 1/1/2025, 31/12/2025
        month_str = f"{month:02d}"  # Garante 2 dígitos
        year_str = str(year)
        
        # Padrões possíveis: DD/MM/YYYY ou D/M/YYYY
        patterns = [
            JournalEntry.Data.like(f'%/{month_str}/{year_str}'),  # %/01/2025
            JournalEntry.Data.like(f'%/{month}/{year_str}')       # %/1/2025
        ]
        
        return or_(*patterns)
    
    def get_metrics(self, user_id: int, year: int, month: int) -> Dict:
        """Calcula métricas principais"""
        # Filtro base
        date_filter = self._build_date_filter(year, month)
        base_query = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            date_filter
        )
        
        # Total de despesas (tipo DEBITO com valor negativo)
        total_despesas = base_query.filter(
            JournalEntry.TipoTransacao == 'DEBITO',
            JournalEntry.Valor < 0
        ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0
        
        # Total de receitas (tipo CREDITO com valor positivo)
        total_receitas = base_query.filter(
            JournalEntry.TipoTransacao == 'CREDITO',
            JournalEntry.Valor > 0
        ).with_entities(func.sum(JournalEntry.Valor)).scalar() or 0.0
        
        # Total de cartões (tipo CARTAO_CREDITO)
        total_cartoes = base_query.filter(
            JournalEntry.TipoTransacao == 'CARTAO_CREDITO'
        ).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0
        
        # Número de transações
        num_transacoes = base_query.count()
        
        # Saldo do período
        saldo_periodo = total_receitas + total_despesas  # despesas já é negativo
        
        return {
            "total_despesas": abs(total_despesas),
            "total_receitas": total_receitas,
            "total_cartoes": total_cartoes,
            "saldo_periodo": saldo_periodo,
            "num_transacoes": num_transacoes
        }
    
    def get_chart_data(self, user_id: int, year: int, month: int) -> List[Dict]:
        """Retorna dados para gráfico de área (receitas vs despesas por mês do ano)"""
        # Query agrupada por mês do ano
        results = self.db.query(
            func.substr(JournalEntry.Data, 4, 2).label('month'),  # Extrai MM de DD/MM/YYYY
            func.sum(
                case(
                    (JournalEntry.TipoTransacao == 'CREDITO', JournalEntry.Valor),
                    else_=0
                )
            ).label('receitas'),
            func.sum(
                case(
                    (JournalEntry.TipoTransacao != 'CREDITO', func.abs(JournalEntry.Valor)),
                    else_=0
                )
            ).label('despesas')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Data.like(f'%/{year}')  # Filtra pelo ano
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
    
    def get_category_expenses(self, user_id: int, year: int, month: int) -> List[Dict]:
        """Retorna despesas agrupadas por categoria"""
        date_filter = self._build_date_filter(year, month)
        
        # Total geral de despesas (para calcular percentual)
        total_despesas = self.db.query(
            func.sum(func.abs(JournalEntry.Valor))
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.TipoTransacao != 'CREDITO'
        ).scalar() or 1.0  # Evita divisão por zero
        
        # Despesas por categoria
        results = self.db.query(
            JournalEntry.GRUPO.label('categoria'),
            func.sum(func.abs(JournalEntry.Valor)).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            date_filter,
            JournalEntry.TipoTransacao != 'CREDITO',
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
