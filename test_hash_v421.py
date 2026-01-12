#!/usr/bin/env python3
"""
Teste: Validar que user_id está sendo considerado no hash
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.shared.utils.hasher import generate_id_transacao

# Mesma transação para 2 usuários diferentes
data = "23/11/2025"
estabelecimento = "PIT STOP BEBIDAS"
valor = -42.29

hash_user1 = generate_id_transacao(
    data=data,
    estabelecimento=estabelecimento,
    valor=valor,
    user_id=1,
    sequencia=1
)

hash_user2 = generate_id_transacao(
    data=data,
    estabelecimento=estabelecimento,
    valor=valor,
    user_id=2,
    sequencia=1
)

print(f"✅ v4.2.1 (com user_id):")
print(f"   Data: {data}")
print(f"   Estabelecimento: {estabelecimento}")
print(f"   Valor: {valor}")
print()
print(f"🔹 User 1 (seq=1): {hash_user1}")
print(f"🔹 User 2 (seq=1): {hash_user2}")
print()
print(f"🎯 Hashes diferentes? {hash_user1 != hash_user2}")
print(f"   {'✅ CORRETO - Usuários isolados!' if hash_user1 != hash_user2 else '❌ ERRO - Colisão!'}")
