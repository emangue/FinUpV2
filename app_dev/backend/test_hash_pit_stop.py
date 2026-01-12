import sys
sys.path.insert(0, '.')

from app.shared.utils.hasher import generate_id_transacao

# Dados da transação PIT STOP
data = "23/11/2025"
estabelecimento = "PIT STOP BEBIDAS"
valor = -42.29

print("🔍 Testando geração de IdTransacao para PIT STOP")
print("=" * 60)
print(f"Data: {data}")
print(f"Estabelecimento: {estabelecimento}")
print(f"Valor: {valor}")
print()

# Testar várias sequências
for seq in [1, 2, 3]:
    id_trans = generate_id_transacao(data, estabelecimento, valor, sequencia=seq)
    print(f"Sequencia {seq}: {id_trans}")

print()
print("🎯 Valores encontrados no banco:")
print(f"Journal_entries: 16152610384312802180")
print(f"Preview_transacoes: 9559958248188266241")
