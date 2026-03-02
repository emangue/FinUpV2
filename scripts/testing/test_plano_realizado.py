#!/usr/bin/env python3
"""Testa cashflow e projeção para verificar valores Real (realizado) em janeiro."""
import sys
import os

# Carregar .env do backend
backend_dir = os.path.join(os.path.dirname(__file__), "../../app_dev/backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Registrar modelos (evita KeyError UploadHistory)
from app.domains.upload.history_models import UploadHistory  # noqa: F401
from app.domains.transactions.models import JournalEntry  # noqa: F401

from app.core.database import SessionLocal
from app.domains.plano.service import PlanoService

db = SessionLocal()
user_id = int(os.environ.get("TEST_USER_ID", "1"))

print(f"User ID: {user_id}")

svc = PlanoService(db)

# Cashflow 2026
cf = svc.get_cashflow(user_id, 2026)
print("\n--- Cashflow Jan 2026 ---")
jan = next((m for m in cf["meses"] if m["mes_referencia"] == "2026-01"), None)
if jan:
    for k, v in jan.items():
        print(f"  {k}: {v}")
else:
    print("  Mês não encontrado")

# Projeção
proj = svc.get_projecao(user_id, 2026, 12, 0)
print("\n--- Projeção base ---")
print(f"  patrimonio_inicial: {proj['patrimonio_inicial']}")
jan_serie = next((s for s in proj["serie"] if s["mes_referencia"] == "2026-01"), None)
if jan_serie:
    print(f"  Jan acumulado (Real esperado): {jan_serie['acumulado']}")
    print(f"  Jan saldo_mes: {jan_serie['saldo_mes']}")

if jan and jan.get("use_realizado"):
    print(f"\n✅ use_realizado=True → Real deve mostrar {jan_serie['acumulado'] if jan_serie else 'N/A'}")
else:
    print("\n❌ use_realizado=False para Jan")

db.close()
