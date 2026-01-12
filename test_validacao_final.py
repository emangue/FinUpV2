#!/usr/bin/env python3
"""
Validação final: Hashes do upload batem com banco após regeneração
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.shared.utils.hasher import generate_id_transacao
from app.domains.upload.processors.marker import normalizar_formato_parcela

user_id = 1

print("🧪 VALIDAÇÃO FINAL - Upload vs Banco\n")

# Caso 1: FATURA - AngeloMatosDaSilv 01/05
print("1️⃣ FATURA: AngeloMatosDaSilv 01/05")
estab_fatura = "AngeloMatosDaSilv 01/05"
estab_normalizado = normalizar_formato_parcela(estab_fatura)  # → (1/5)
hash_upload = generate_id_transacao("01/11/2025", estab_normalizado, -99.8, user_id, 1)
hash_banco = "9108038764649343886"
print(f"   CSV:         {estab_fatura}")
print(f"   Normalizado: {estab_normalizado}")
print(f"   Hash upload: {hash_upload}")
print(f"   Hash banco:  {hash_banco}")
print(f"   ✅ Match?    {hash_upload == hash_banco}")
print()

# Caso 2: EXTRATO - PIX TRANSF JOAO BA04/10  
print("2️⃣ EXTRATO: PIX TRANSF JOAO BA04/10")
estab_extrato = "PIX TRANSF JOAO BA04/10"
# Extrato: não normaliza
hash_upload2 = generate_id_transacao("06/10/2025", estab_extrato, -100.0, user_id, 1)
hash_banco2 = "16483207458926948245"
print(f"   CSV:         {estab_extrato}")
print(f"   Hash upload: {hash_upload2}")
print(f"   Hash banco:  {hash_banco2}")
print(f"   ✅ Match?    {hash_upload2 == hash_banco2}")
print()

if hash_upload == hash_banco and hash_upload2 == hash_banco2:
    print("🎉 PERFEITO! Upload e banco usam mesma lógica!")
else:
    print("❌ ERRO! Hashes não batem!")
