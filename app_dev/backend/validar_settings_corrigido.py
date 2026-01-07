#!/usr/bin/env python3
"""
Validação Completa da Tela de Configurações - PÓS-CORREÇÃO
==========================================================
Testa se as telas de configurações estão corretamente conectadas ao banco após correções.
"""

import sys
import sqlite3
from pathlib import Path
import requests

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "backend" / "database" / "financas_dev.db"
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

print("=" * 70)
print("VALIDAÇÃO PÓS-CORREÇÃO - Tela de Configurações")
print("=" * 70)

# =====================================================================
# 1. VERIFICAR BANCO DE DADOS
# =====================================================================
print("\n[1/5] 🗄️  Verificando banco de dados...")
if not DB_PATH.exists():
    print(f"❌ ERRO: Banco não encontrado em {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Verificar tabela base_marcacoes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='base_marcacoes'")
if cursor.fetchone():
    print("✅ Tabela 'base_marcacoes' existe")
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) FROM base_marcacoes")
    count = cursor.fetchone()[0]
    print(f"   Total de categorias: {count}")
    
    # Verificar colunas
    cursor.execute("PRAGMA table_info(base_marcacoes)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"   Colunas: {', '.join(columns)}")
    
    # Exemplos
    cursor.execute("SELECT GRUPO, SUBGRUPO, TipoGasto FROM base_marcacoes LIMIT 3")
    print("   Exemplos:")
    for row in cursor.fetchall():
        print(f"      - {row[0]} / {row[1]} / {row[2]}")
else:
    print("❌ Tabela 'base_marcacoes' NÃO encontrada")

conn.close()

# =====================================================================
# 2. TESTAR BACKEND - ENDPOINT DE CATEGORIES
# =====================================================================
print("\n[2/5] 🔌 Testando backend /api/v1/categories...")
try:
    response = requests.get(f"{BACKEND_URL}/api/v1/categories/", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', len(data.get('categories', [])))
        print(f"✅ Backend /api/v1/categories/ respondendo")
        print(f"   Status: {response.status_code}")
        print(f"   Total de categorias retornadas: {total}")
        
        # Verificar estrutura
        categories = data.get('categories', [])
        if categories:
            first = categories[0]
            print(f"   Estrutura: {list(first.keys())}")
            print(f"   Exemplo: {first.get('GRUPO')}/{first.get('SUBGRUPO')}")
    else:
        print(f"⚠️ Backend respondeu com status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print(f"❌ Backend não está rodando em {BACKEND_URL}")
    print("   Execute: ./quick_start.sh")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")

# =====================================================================
# 3. TESTAR PROXY - ROTA CORRIGIDA /api/categories
# =====================================================================
print("\n[3/5] 🌐 Testando proxy Next.js /api/categories...")
try:
    response = requests.get(f"{FRONTEND_URL}/api/categories", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', len(data.get('categories', [])))
        print(f"✅ Proxy /api/categories funcionando")
        print(f"   Status: {response.status_code}")
        print(f"   Total de categorias: {total}")
    elif response.status_code == 404:
        print(f"⚠️ Proxy retornou 404")
        print(f"   Verifique se o proxy está configurado para /api/categories")
    else:
        print(f"⚠️ Status inesperado: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print(f"❌ Frontend não está rodando em {FRONTEND_URL}")
    print("   Execute: ./quick_start.sh")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")

# =====================================================================
# 4. VERIFICAR ROTAS ANTIGAS (DEVEM RETORNAR 404)
# =====================================================================
print("\n[4/5] 🗑️  Verificando rotas antigas (devem estar desativadas)...")

# Rota antiga /api/marcacoes
try:
    response = requests.get(f"{FRONTEND_URL}/api/marcacoes", timeout=5)
    if response.status_code == 404:
        print("✅ /api/marcacoes corretamente removida (404)")
    else:
        print(f"⚠️ /api/marcacoes ainda responde (status {response.status_code})")
except:
    print("✅ /api/marcacoes não acessível (correto)")

# Rota de compatibility
try:
    response = requests.get(f"{FRONTEND_URL}/api/compatibility/manage", timeout=5)
    if response.status_code == 404:
        print("✅ /api/compatibility/manage desativada (404) - funcionalidade em mock")
    else:
        print(f"⚠️ /api/compatibility/manage responde (status {response.status_code})")
except:
    print("✅ /api/compatibility/manage não acessível (temporariamente em mock)")

# =====================================================================
# 5. DIAGNÓSTICO FINAL
# =====================================================================
print("\n[5/5] 📊 Diagnóstico Final")
print("=" * 70)

# Verificar se tudo está OK
checks = {
    "Banco de dados": DB_PATH.exists(),
    "Backend rodando": False,
    "Frontend rodando": False,
    "Categorias no banco": False
}

# Re-testar conectividade
try:
    requests.get(f"{BACKEND_URL}/api/health", timeout=2)
    checks["Backend rodando"] = True
except:
    pass

try:
    response = requests.get(f"{FRONTEND_URL}/api/categories", timeout=2)
    checks["Frontend rodando"] = response.status_code == 200
except:
    pass

# Verificar banco
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM base_marcacoes")
checks["Categorias no banco"] = cursor.fetchone()[0] > 0
conn.close()

# Exibir resultado
print("\nSTATUS DOS COMPONENTES:")
for component, status in checks.items():
    icon = "✅" if status else "❌"
    print(f"{icon} {component}: {'OK' if status else 'FALHA'}")

# Mensagem final
all_ok = all(checks.values())
if all_ok:
    print("\n🎉 TUDO FUNCIONANDO! A tela de configurações está corretamente conectada.")
    print("\n📝 PRÓXIMOS PASSOS:")
    print("   1. Acesse http://localhost:3000/settings")
    print("   2. Teste adicionar/editar categorias")
    print("   3. Bancos compatíveis estão em modo MOCK (backend pendente)")
else:
    print("\n⚠️ AÇÕES NECESSÁRIAS:")
    if not checks["Backend rodando"]:
        print("   - Iniciar backend: cd app_dev && ./quick_start.sh")
    if not checks["Frontend rodando"]:
        print("   - Iniciar frontend: cd app_dev && ./quick_start.sh")
    if not checks["Banco de dados"]:
        print("   - Inicializar banco: cd app_dev && python init_db.py")

print("\n" + "=" * 70)
