#!/usr/bin/env python3
"""
Teste: Normalização condicional (fatura vs extrato)
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.shared.utils.hasher import generate_id_transacao
from app.domains.upload.processors.marker import normalizar_formato_parcela

data = "06/10/2025"
valor = -100.0
user_id = 1

print("🧪 Teste: Normalização Condicional\n")

# Caso 1: EXTRATO - "PIX TRANSF JOAO BA04/10" (BA04 é parte do nome!)
print("1️⃣ EXTRATO: PIX TRANSF JOAO BA04/10")
estab_extrato = "PIX TRANSF JOAO BA04/10"
# Extrato: NÃO normalizar (manter original)
hash_extrato = generate_id_transacao(data, estab_extrato, valor, user_id, 1)
print(f"   Original:  {estab_extrato}")
print(f"   Hash:      {hash_extrato}")
print(f"   Esperado:  16483207458926948245")
print(f"   Match?     {hash_extrato == '16483207458926948245'}")
print()

# Caso 2: FATURA - "AngeloMatosDaSilv 01/05" (01/05 é parcela!)
print("2️⃣ FATURA: AngeloMatosDaSilv 01/05")
estab_fatura = "AngeloMatosDaSilv 01/05"
# Fatura: Normalizar ("01/05" → "(1/5)")
estab_normalizado = normalizar_formato_parcela(estab_fatura)
hash_fatura = generate_id_transacao(data="01/11/2025", estabelecimento=estab_normalizado, valor=-99.8, user_id=user_id, sequencia=1)
print(f"   Original:    {estab_fatura}")
print(f"   Normalizado: {estab_normalizado}")
print(f"   Hash:        {hash_fatura}")
print(f"   Esperado:    9108038764649343886")
print(f"   Match?       {hash_fatura == '9108038764649343886'}")
print()

print("✅ Estratégia:")
print("   • Extrato: Manter texto original")
print("   • Fatura:  Normalizar formato de parcela")
