#!/usr/bin/env python3
"""
Wrapper para executar auditorias no banco de dados correto
"""
import subprocess
import sys

DB_PATH = 'app/financas.db'

print("🔍 Executando Auditorias no Banco de Dados\n")
print(f"📂 Banco: {DB_PATH}\n")
print("=" * 80)

# 1. Health Check
print("\n1️⃣  DATABASE HEALTH CHECK")
print("-" * 80)
result = subprocess.run([
    sys.executable,
    'scripts/database_health_check.py',
    '--db', DB_PATH,
    '--output', 'file'
], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# 2. Format Validation
print("\n2️⃣  DATA FORMAT VALIDATION")
print("-" * 80)
result = subprocess.run([
    sys.executable,
    'scripts/validate_data_formats.py',
    '--db', DB_PATH,
    '--output', 'file'
], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# 3. TipoGasto Analysis
print("\n3️⃣  TIPOGASTO MISSING ANALYSIS")
print("-" * 80)
result = subprocess.run([
    sys.executable,
    'scripts/analyze_tipogasto_missing.py',
    '--db', DB_PATH,
    '--output', 'file'
], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n" + "=" * 80)
print("✅ Todas as auditorias concluídas!")
print("📊 Verifique os arquivos gerados no diretório atual")
