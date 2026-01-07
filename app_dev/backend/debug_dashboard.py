#!/usr/bin/env python3
"""
Script para debug do dashboard - comparar totais do gráfico vs métricas
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.transactions.models import JournalEntry
from sqlalchemy import func, or_, case

# Criar engine e session
engine = create_engine(str(settings.DATABASE_URL))
Session = sessionmaker(bind=engine)
db = Session()

# Simular o filtro do backend para o ano de 2025 (todo o ano)
year = 2025

# Query do gráfico (chart-data) - agrupado por mês
print('=== DADOS DO GRÁFICO (chart-data) - ANO TODO ===')
results = db.query(
    func.substr(JournalEntry.Data, 4, 2).label('month'),
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
    JournalEntry.user_id == 1,
    JournalEntry.Data.like(f'%/{year}'),
    JournalEntry.IgnorarDashboard == 0
).group_by(
    func.substr(JournalEntry.Data, 4, 2)
).order_by(
    func.substr(JournalEntry.Data, 4, 2)
).all()

month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

total_receitas_grafico = 0
total_despesas_grafico = 0

for row in results:
    month_name = month_names[int(row.month) - 1] if row.month else 'Unknown'
    receitas = float(row.receitas or 0)
    despesas = float(row.despesas or 0)
    total_receitas_grafico += receitas
    total_despesas_grafico += despesas
    print(f'{month_name}: Receitas=R$ {receitas:,.2f}, Despesas=R$ {despesas:,.2f}')

print(f'\n✅ TOTAL GRÁFICO - Receitas: R$ {total_receitas_grafico:,.2f}')
print(f'✅ TOTAL GRÁFICO - Despesas: R$ {total_despesas_grafico:,.2f}')
print(f'✅ SALDO GRÁFICO: R$ {(total_receitas_grafico - total_despesas_grafico):,.2f}')

# Query das métricas com month=None (ano todo) - NOVA LÓGICA
print('\n=== MÉTRICAS (metrics endpoint) - month=None (ANO TODO) ===')
date_filter_anual = JournalEntry.Data.like(f'%/{year}')

base_query_anual = db.query(JournalEntry).filter(
    JournalEntry.user_id == 1,
    date_filter_anual,
    JournalEntry.IgnorarDashboard == 0
)

total_despesas_metrics_anual = base_query_anual.filter(
    JournalEntry.CategoriaGeral == 'Despesa'
).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0

total_receitas_metrics_anual = base_query_anual.filter(
    JournalEntry.CategoriaGeral == 'Receita'
).with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0.0

print(f'📊 Receitas Ano Todo: R$ {total_receitas_metrics_anual:,.2f}')
print(f'📊 Despesas Ano Todo: R$ {total_despesas_metrics_anual:,.2f}')
print(f'📊 Saldo Ano Todo: R$ {(total_receitas_metrics_anual - total_despesas_metrics_anual):,.2f}')

# Comparação
print('\n=== VERIFICAÇÃO DA SOLUÇÃO ===')
if abs(total_receitas_grafico - total_receitas_metrics_anual) < 0.01 and abs(total_despesas_grafico - total_despesas_metrics_anual) < 0.01:
    print(f'✅ SOLUÇÃO IMPLEMENTADA COM SUCESSO!')
    print(f'   - GRÁFICO: R$ {total_receitas_grafico:,.2f} receitas / R$ {total_despesas_grafico:,.2f} despesas')
    print(f'   - MÉTRICAS (month=None): R$ {total_receitas_metrics_anual:,.2f} receitas / R$ {total_despesas_metrics_anual:,.2f} despesas')
    print(f'   - ✅ Valores BATEM PERFEITAMENTE!')
else:
    print(f'⚠️ Ainda há diferença:')
    print(f'   - GRÁFICO: R$ {total_receitas_grafico:,.2f} receitas / R$ {total_despesas_grafico:,.2f} despesas')
    print(f'   - MÉTRICAS: R$ {total_receitas_metrics_anual:,.2f} receitas / R$ {total_despesas_metrics_anual:,.2f} despesas')

db.close()
