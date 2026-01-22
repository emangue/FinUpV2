"""
Testa geração de IdTransacao para transação Mercado Pago
"""
import sys
sys.path.insert(0, 'app_dev/backend')

from app.shared.utils.hasher import generate_id_transacao

# Dados da transação existente na base
data = "09/10/2025"
estabelecimento = "Transferência Pix enviada Emanuel Leandro"
valor = -600.00
user_id = 1
id_existente = "11402580468824100981"

# Testar diferentes sequências
print("🔍 TESTANDO GERAÇÃO DE IdTransacao:\n")
print(f"Data:            {data}")
print(f"Estabelecimento: {estabelecimento}")
print(f"Valor:           {valor}")
print(f"User ID:         {user_id}")
print(f"ID Existente:    {id_existente}\n")

print("📊 Hashes gerados por sequência:")
for seq in range(1, 6):
    hash_id = generate_id_transacao(data, estabelecimento, valor, user_id, seq)
    match = "✅ MATCH!" if hash_id == id_existente else ""
    print(f"  Sequência {seq}: {hash_id} {match}")

print("\n" + "="*80)
print("🔍 TESTANDO VARIAÇÕES (upper, lower, espaços):\n")

# Variações de caso
variacoes = [
    ("Original", estabelecimento),
    ("UPPERCASE", estabelecimento.upper()),
    ("lowercase", estabelecimento.lower()),
    ("Espaços extras", "Transferência  Pix  enviada  Emanuel  Leandro"),
    ("Sem acentos", "Transferencia Pix enviada Emanuel Leandro"),
]

for nome, estab in variacoes:
    hash_id = generate_id_transacao(data, estab, valor, user_id, 1)
    match = "✅ MATCH!" if hash_id == id_existente else ""
    print(f"{nome:20s}: {hash_id} {match}")
