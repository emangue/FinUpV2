#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.transactions.models import JournalEntry
from sqlalchemy import func

engine = create_engine(str(settings.DATABASE_URL))
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("🔍 ANÁLISE: Transações por CategoriaGeral (2025)")
print("=" * 80)

# Contar por CategoriaGeral
categorias = db.query(
    JournalEntry.CategoriaGeral,
    func.count(JournalEntry.IdTransacao).label('count'),
    func.sum(func.abs(JournalEntry.Valor)).label('total')
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 0
).group_by(
    JournalEntry.CategoriaGeral
).all()

print("\nTransações com IgnorarDashboard=0 (switch LIGADO):\n")
total_geral = 0
for cat in categorias:
    print(f"  {cat.CategoriaGeral}: {cat.count} transações, R$ {cat.total:,.2f}")
    total_geral += cat.total

print(f"\n  TOTAL: R$ {total_geral:,.2f}")

# Verificar o que o dashboard REALMENTE mostra
print("\n" + "-" * 80)
print("📊 O que o DASHBOARD mostra:")
print("-" * 80)

despesas = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 0,
    JournalEntry.CategoriaGeral == 'Despesa'
).scalar() or 0.0

receitas = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/2025'),
    JournalEntry.IgnorarDashboard == 0,
    JournalEntry.CategoriaGeral == 'Receita'
).scalar() or 0.0

print(f"\n  Receitas: R$ {receitas:,.2f}")
print(f"  Despesas: R$ {despesas:,.2f}")
print(f"  TOTAL mostrado: R$ {(receitas + despesas):,.2f}")

diferenca = total_geral - (receitas + despesas)
if diferenca > 0:
    print(f"\n⚠️ DIFERENÇA: R$ {diferenca:,.2f} NÃO APARECE no dashboard!")
    print(f"   Porque são Investimentos/Transferências/outras categorias")

# Exemplo da TED
print("\n" + "=" * 80)
print("📄 Exemplo: TED de março/2024")
print("=" * 80)

ted = db.query(JournalEntry).filter(
    JournalEntry.Data == '15/03/2024',
    JournalEntry.Estabelecimento.like('%TED%EMANUEL%')
).first()

if ted:
    print(f"\n  Estabelecimento: {ted.Estabelecimento}")
    print(f"  Valor: R$ {ted.Valor:,.2f}")
    print(f"  CategoriaGeral: {ted.CategoriaGeral}")
    print(f"  IgnorarDashboard: {ted.IgnorarDashboard}")
    
    if ted.CategoriaGeral not in ['Receita', 'Despesa']:
        print(f"\n  ❌ NUNCA vai aparecer no dashboard!")
        print(f"     CategoriaGeral = '{ted.CategoriaGeral}'")
        print(f"     Dashboard só mostra: 'Receita' e 'Despesa'")

db.close()
