#!/usr/bin/env python3
"""
Script para testar se o campo IgnorarDashboard está funcionando corretamente
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.transactions.models import JournalEntry
from sqlalchemy import func

# Criar engine e session
engine = create_engine(str(settings.DATABASE_URL))
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("TESTE: Campo IgnorarDashboard")
print("=" * 80)

# 1. Verificar se o campo existe e tem valores
print("\n1. Estatísticas do campo IgnorarDashboard:")
print("-" * 80)

total_transacoes = db.query(func.count(JournalEntry.IdTransacao)).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025')
).scalar()

ignoradas = db.query(func.count(JournalEntry.IdTransacao)).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 1
).scalar()

nao_ignoradas = db.query(func.count(JournalEntry.IdTransacao)).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 0
).scalar()

null_values = db.query(func.count(JournalEntry.IdTransacao)).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard.is_(None)
).scalar()

print(f"Total de transações (2025): {total_transacoes}")
print(f"  - IgnorarDashboard = 0 (aparecem no dash): {nao_ignoradas}")
print(f"  - IgnorarDashboard = 1 (não aparecem): {ignoradas}")
print(f"  - IgnorarDashboard = NULL: {null_values}")

# 2. Comparar totais COM e SEM filtro IgnorarDashboard
print("\n2. Comparação de totais COM e SEM filtro:")
print("-" * 80)

# SEM filtro (todas as transações)
total_sem_filtro = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.CategoriaGeral == 'Despesa'
).scalar() or 0.0

# COM filtro (apenas IgnorarDashboard = 0)
total_com_filtro = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0
).scalar() or 0.0

diferenca = total_sem_filtro - total_com_filtro

print(f"Despesas SEM filtro IgnorarDashboard: R$ {total_sem_filtro:,.2f}")
print(f"Despesas COM filtro (IgnorarDashboard=0): R$ {total_com_filtro:,.2f}")
print(f"Diferença (valores ignorados): R$ {diferenca:,.2f}")

if diferenca > 0:
    print(f"\n✅ FILTRO FUNCIONANDO! {diferenca:,.2f} reais sendo ignorados no dashboard")
else:
    print(f"\n⚠️ ATENÇÃO: Nenhuma transação marcada como ignorada!")

# 3. Buscar exemplo de transação ignorada
print("\n3. Exemplos de transações ignoradas:")
print("-" * 80)

exemplos_ignorados = db.query(JournalEntry).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 1
).limit(5).all()

if exemplos_ignorados:
    for t in exemplos_ignorados:
        print(f"  - {t.Data}: {t.Estabelecimento} | R$ {t.Valor:,.2f} | Dashboard={t.IgnorarDashboard}")
else:
    print("  Nenhuma transação com IgnorarDashboard=1 encontrada")

# 4. Buscar exemplos de transações que aparecem no dashboard
print("\n4. Exemplos de transações QUE aparecem no dashboard:")
print("-" * 80)

exemplos_nao_ignorados = db.query(JournalEntry).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 0,
    JournalEntry.CategoriaGeral == 'Despesa'
).limit(3).all()

if exemplos_nao_ignorados:
    for t in exemplos_nao_ignorados:
        print(f"  - {t.Data}: {t.Estabelecimento} | R$ {t.Valor:,.2f} | Dashboard={t.IgnorarDashboard}")

# 5. Verificar se o dashboard está usando o filtro
print("\n5. Query do Dashboard (simulação):")
print("-" * 80)

from app.domains.dashboard.repository import DashboardRepository
dashboard_repo = DashboardRepository(db)

metrics = dashboard_repo.get_metrics(user_id=1, year=2025, month=None)

print(f"Métricas do Dashboard (ano 2025 completo):")
print(f"  - Total Despesas: R$ {metrics['total_despesas']:,.2f}")
print(f"  - Total Receitas: R$ {metrics['total_receitas']:,.2f}")
print(f"  - Número de transações: {metrics['num_transacoes']}")

if abs(metrics['total_despesas'] - total_com_filtro) < 0.01:
    print(f"\n✅ DASHBOARD USANDO FILTRO CORRETAMENTE!")
    print(f"   Dashboard: R$ {metrics['total_despesas']:,.2f}")
    print(f"   Esperado:  R$ {total_com_filtro:,.2f}")
else:
    print(f"\n❌ DASHBOARD NÃO ESTÁ USANDO FILTRO!")
    print(f"   Dashboard: R$ {metrics['total_despesas']:,.2f}")
    print(f"   Esperado:  R$ {total_com_filtro:,.2f}")
    print(f"   Diferença: R$ {abs(metrics['total_despesas'] - total_com_filtro):,.2f}")

db.close()

print("\n" + "=" * 80)
print("FIM DO TESTE")
print("=" * 80)
