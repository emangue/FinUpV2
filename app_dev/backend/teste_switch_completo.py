#!/usr/bin/env python3
"""
TESTE COMPLETO E VISUAL - Prova que o switch está funcionando
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.transactions.models import JournalEntry
from sqlalchemy import func
import requests
import time

print("=" * 100)
print("🧪 TESTE COMPLETO - SWITCH DASHBOARD")
print("=" * 100)

# Setup
engine = create_engine(str(settings.DATABASE_URL))
Session = sessionmaker(bind=engine)
db = Session()

# 1. Buscar uma transação de DESPESA para testar
print("\n📍 PASSO 1: Buscando transação para teste...")
print("-" * 100)

transacao_teste = db.query(JournalEntry).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/03/2024'),
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.Valor < 0
).first()

if not transacao_teste:
    print("❌ Nenhuma transação encontrada!")
    db.close()
    exit(1)

print(f"✅ Transação selecionada:")
print(f"   ID: {transacao_teste.IdTransacao}")
print(f"   Data: {transacao_teste.Data}")
print(f"   Estabelecimento: {transacao_teste.Estabelecimento}")
print(f"   Valor: R$ {abs(transacao_teste.Valor):,.2f}")
print(f"   IgnorarDashboard ATUAL: {transacao_teste.IgnorarDashboard}")

valor_transacao = abs(transacao_teste.Valor)
id_transacao = transacao_teste.IdTransacao

# 2. Verificar total do dashboard ANTES
print(f"\n📊 PASSO 2: Verificando total do dashboard ANTES (março/2024)...")
print("-" * 100)

total_antes = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/03/2024'),
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0
).scalar() or 0.0

response_antes = requests.get('http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3')
if response_antes.ok:
    metrics_antes = response_antes.json()
    dashboard_antes = metrics_antes['total_despesas']
    print(f"✅ Dashboard API: R$ {dashboard_antes:,.2f}")
    print(f"✅ Query direta: R$ {total_antes:,.2f}")
    
    if abs(dashboard_antes - total_antes) < 0.01:
        print(f"✅ Valores BATEM!")
    else:
        print(f"⚠️ DIFERENÇA: R$ {abs(dashboard_antes - total_antes):,.2f}")
else:
    print(f"❌ Erro na API: {response_antes.status_code}")
    db.close()
    exit(1)

# 3. GARANTIR que a transação APARECE no dashboard (IgnorarDashboard=0)
print(f"\n🔧 PASSO 3: Garantindo que transação APARECE no dashboard...")
print("-" * 100)

if transacao_teste.IgnorarDashboard != 0:
    transacao_teste.IgnorarDashboard = 0
    db.commit()
    print(f"✅ Atualizado para IgnorarDashboard=0 (APARECE)")
    time.sleep(1)
    
    # Verificar via API
    response_garantia = requests.get('http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3')
    if response_garantia.ok:
        dashboard_garantia = response_garantia.json()['total_despesas']
        print(f"✅ Dashboard após garantia: R$ {dashboard_garantia:,.2f}")
    
    dashboard_antes = dashboard_garantia  # Atualizar referência
else:
    print(f"✅ Transação já estava com IgnorarDashboard=0")

# 4. DESLIGAR o switch via API (IgnorarDashboard=1)
print(f"\n🔴 PASSO 4: DESLIGANDO switch via API (remover do dashboard)...")
print("-" * 100)

response_update = requests.patch(
    f'http://localhost:8000/api/v1/transactions/update/{id_transacao}',
    json={'IgnorarDashboard': 1}
)

if response_update.ok:
    data_update = response_update.json()
    print(f"✅ API respondeu: IgnorarDashboard = {data_update['IgnorarDashboard']}")
else:
    print(f"❌ Erro no UPDATE: {response_update.status_code}")
    db.close()
    exit(1)

time.sleep(1)

# 5. Verificar banco de dados diretamente
print(f"\n🔍 PASSO 5: Verificando banco de dados diretamente...")
print("-" * 100)

db.expire_all()  # Limpar cache do SQLAlchemy
transacao_apos = db.query(JournalEntry).filter(
    JournalEntry.IdTransacao == id_transacao
).first()

print(f"   IgnorarDashboard no banco: {transacao_apos.IgnorarDashboard}")

if transacao_apos.IgnorarDashboard == 1:
    print(f"✅ CONFIRMADO: Campo atualizado no banco!")
else:
    print(f"❌ ERRO: Campo NÃO foi atualizado no banco!")

# 6. Verificar total do dashboard DEPOIS
print(f"\n📊 PASSO 6: Verificando total do dashboard DEPOIS...")
print("-" * 100)

total_depois = db.query(
    func.sum(func.abs(JournalEntry.Valor))
).filter(
    JournalEntry.user_id == 1,
    JournalEntry.Data.like('%/03/2024'),
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0
).scalar() or 0.0

response_depois = requests.get('http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3')
if response_depois.ok:
    metrics_depois = response_depois.json()
    dashboard_depois = metrics_depois['total_despesas']
    print(f"✅ Dashboard API: R$ {dashboard_depois:,.2f}")
    print(f"✅ Query direta: R$ {total_depois:,.2f}")
else:
    print(f"❌ Erro na API: {response_depois.status_code}")

# 7. COMPARAÇÃO FINAL
print(f"\n" + "=" * 100)
print(f"🎯 RESULTADO FINAL")
print("=" * 100)

diferenca_esperada = valor_transacao
diferenca_real = dashboard_antes - dashboard_depois

print(f"\n📊 Valores no Dashboard:")
print(f"   ANTES:     R$ {dashboard_antes:,.2f}")
print(f"   DEPOIS:    R$ {dashboard_depois:,.2f}")
print(f"   DIFERENÇA: R$ {diferenca_real:,.2f}")

print(f"\n💰 Valor da transação: R$ {valor_transacao:,.2f}")

print(f"\n🧮 Validação:")
if abs(diferenca_real - diferenca_esperada) < 0.01:
    print(f"✅ ✅ ✅ PERFEITO! A diferença ({diferenca_real:.2f}) BATE com o valor da transação ({valor_transacao:.2f})")
    print(f"✅ ✅ ✅ SWITCH ESTÁ FUNCIONANDO CORRETAMENTE!")
else:
    print(f"⚠️ ATENÇÃO: Diferença real ({diferenca_real:.2f}) != Valor esperado ({valor_transacao:.2f})")
    print(f"   Discrepância: R$ {abs(diferenca_real - diferenca_esperada):,.2f}")

# 8. REVERTER para deixar o banco como estava
print(f"\n🔄 PASSO 7: Revertendo transação para estado original...")
print("-" * 100)

response_reverter = requests.patch(
    f'http://localhost:8000/api/v1/transactions/update/{id_transacao}',
    json={'IgnorarDashboard': 0}
)

if response_reverter.ok:
    print(f"✅ Transação revertida para IgnorarDashboard=0")
    
    time.sleep(1)
    response_final = requests.get('http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3')
    if response_final.ok:
        dashboard_final = response_final.json()['total_despesas']
        print(f"✅ Dashboard voltou para: R$ {dashboard_final:,.2f}")
        
        if abs(dashboard_final - dashboard_antes) < 0.01:
            print(f"✅ CONFIRMADO: Voltou ao valor original!")

db.close()

print(f"\n" + "=" * 100)
print(f"FIM DO TESTE")
print("=" * 100)
