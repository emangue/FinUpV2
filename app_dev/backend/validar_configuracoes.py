#!/usr/bin/env python3
"""
VALIDAÇÃO COMPLETA - Telas de Configurações
"""
import requests
import json
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

print("=" * 100)
print("🔍 VALIDAÇÃO: Telas de Configurações")
print("=" * 100)

# Setup
engine = create_engine(str(settings.DATABASE_URL))
Session = sessionmaker(bind=engine)
db = Session()
inspector = inspect(engine)

# 1. Verificar tabelas no banco
print("\n📊 PASSO 1: Verificar tabelas no banco de dados")
print("-" * 100)

tabelas_esperadas = ['base_marcacoes']
tabelas_existentes = inspector.get_table_names()

for tabela in tabelas_esperadas:
    if tabela in tabelas_existentes:
        print(f"✅ Tabela '{tabela}' existe")
        
        # Ver estrutura
        colunas = inspector.get_columns(tabela)
        print(f"   Colunas: {', '.join([c['name'] for c in colunas])}")
    else:
        print(f"❌ Tabela '{tabela}' NÃO existe")

# 2. Testar endpoint de categories no backend
print("\n🔌 PASSO 2: Testar endpoint de categories (backend)")
print("-" * 100)

try:
    response = requests.get('http://localhost:8000/api/v1/categories/')
    
    if response.ok:
        data = response.json()
        print(f"✅ Backend respondendo: HTTP {response.status_code}")
        print(f"✅ Categorias retornadas: {len(data.get('categories', []))}")
        
        if data.get('categories'):
            exemplo = data['categories'][0]
            print(f"✅ Exemplo de categoria:")
            print(f"   GRUPO: {exemplo['GRUPO']}")
            print(f"   SUBGRUPO: {exemplo['SUBGRUPO']}")
            print(f"   TipoGasto: {exemplo['TipoGasto']}")
    else:
        print(f"❌ Backend erro: HTTP {response.status_code}")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"❌ Erro ao conectar backend: {e}")

# 3. Testar proxy frontend
print("\n🌐 PASSO 3: Testar proxy frontend (/api/marcacoes)")
print("-" * 100)

try:
    # O frontend espera /api/marcacoes mas o backend tem /api/v1/categories
    response = requests.get('http://localhost:3000/api/marcacoes')
    
    if response.ok:
        data = response.json()
        print(f"✅ Proxy funcionando: HTTP {response.status_code}")
        print(f"✅ Dados retornados: {len(data) if isinstance(data, list) else 'objeto'}")
    else:
        print(f"⚠️ Proxy respondeu: HTTP {response.status_code}")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"❌ Erro ao conectar proxy: {e}")

# 4. Verificar mapeamento de rotas
print("\n🗺️  PASSO 4: Verificar mapeamento de rotas")
print("-" * 100)

mapeamentos = {
    "Frontend → Backend": {
        "/api/marcacoes": "/api/v1/categories/",
        "/api/compatibility/manage": "❌ NÃO EXISTE no backend",
    }
}

for descricao, mapa in mapeamentos.items():
    print(f"\n{descricao}:")
    for front, back in mapa.items():
        if "❌" in back:
            print(f"   {front} → {back}")
        else:
            print(f"   ✅ {front} → {back}")

# 5. DIAGNÓSTICO
print("\n" + "=" * 100)
print("📋 DIAGNÓSTICO FINAL")
print("=" * 100)

problemas = []

# Problema 1: Route mismatch
problemas.append({
    "tipo": "⚠️ ROTA INCORRETA",
    "descricao": "Frontend chama /api/marcacoes mas backend usa /categories",
    "impacto": "Página de Configurações não carrega dados",
    "solucao": "Alterar frontend para usar /api/categories OU criar alias no backend"
})

# Problema 2: Compatibilidade não existe
problemas.append({
    "tipo": "❌ ENDPOINT INEXISTENTE",
    "descricao": "Frontend chama /api/compatibility/manage mas não existe no backend",
    "impacto": "Aba 'Disponibilidade de Arquivos' não funciona",
    "solucao": "Criar domínio 'compatibility' no backend ou remover do frontend"
})

for i, p in enumerate(problemas, 1):
    print(f"\n🔴 PROBLEMA {i}: {p['tipo']}")
    print(f"   Descrição: {p['descricao']}")
    print(f"   Impacto: {p['impacto']}")
    print(f"   Solução: {p['solucao']}")

# Teste direto no banco
print("\n📊 PASSO 5: Dados reais no banco")
print("-" * 100)

from app.domains.categories.models import BaseMarcacao
from sqlalchemy import func

total_marcacoes = db.query(func.count(BaseMarcacao.id)).scalar()
print(f"Total de marcações no banco: {total_marcacoes}")

if total_marcacoes > 0:
    exemplos = db.query(BaseMarcacao).limit(3).all()
    print(f"\nExemplos:")
    for m in exemplos:
        print(f"  - {m.GRUPO} / {m.SUBGRUPO} / {m.TipoGasto}")

db.close()

print("\n" + "=" * 100)
print("FIM DA VALIDAÇÃO")
print("=" * 100)
