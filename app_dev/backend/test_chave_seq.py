#!/usr/bin/env python3
"""Teste da lógica de chave_unica"""

# Transação 3862: PIX TRANSF EMANUEL30/09 | -1000.0
trans1_lancamento = "PIX TRANSF EMANUEL30/09"
trans1_valor = 1000.00
chave1_old = f"30/09/2025|{trans1_lancamento}|{trans1_valor:.2f}"
chave1_new = f"30/09/2025|{trans1_lancamento.upper()}|{trans1_valor:.2f}"

# Transação 3864: PIX TRANSF Emanuel30/09 | 6000.0
trans2_lancamento = "PIX TRANSF Emanuel30/09"
trans2_valor = 6000.00
chave2_old = f"30/09/2025|{trans2_lancamento}|{trans2_valor:.2f}"
chave2_new = f"30/09/2025|{trans2_lancamento.upper()}|{trans2_valor:.2f}"

print("=== LÓGICA ANTIGA (case-sensitive) ===")
print(f"Trans 1: {chave1_old}")
print(f"Trans 2: {chave2_old}")
print(f"São iguais? {chave1_old == chave2_old}")
print()

print("=== LÓGICA NOVA (case-insensitive) ===")
print(f"Trans 1: {chave1_new}")
print(f"Trans 2: {chave2_new}")
print(f"São iguais? {chave1_new == chave2_new}")
print()

print("=== ANÁLISE ===")
print(f"Valores diferentes: {trans1_valor} != {trans2_valor}")
print(f"NUNCA deveriam ser consideradas duplicatas!")
