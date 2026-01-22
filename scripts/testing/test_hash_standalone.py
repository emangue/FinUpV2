"""
Teste standalone de geração de IdTransacao (sem imports do app)
"""

def fnv1a_64_hash(text):
    """Gera hash FNV-1a 64-bit"""
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    
    return str(h)


def generate_id_transacao(data, estabelecimento, valor, user_id, sequencia=None):
    """Gera IdTransacao usando FNV-1a 64-bit"""
    if sequencia is None:
        sequencia = 1
    
    # UPPERCASE e trim
    estab_upper = str(estabelecimento).upper().strip()
    
    # Valor EXATO com 2 casas decimais
    valor_exato = float(valor)
    valor_str = f"{valor_exato:.2f}"
    
    # Chave: UserID|Data|Estabelecimento|Valor
    chave = f"{user_id}|{data}|{estab_upper}|{valor_str}"
    
    # Hash base
    hash_atual = fnv1a_64_hash(chave)
    
    # Hash recursivo para duplicados
    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual


# Dados da transação existente na base
data = "09/10/2025"
estabelecimento = "Transferência Pix enviada Emanuel Leandro"
valor = -600.00
user_id = 1
id_existente = "11402580468824100981"

print("🔍 TESTANDO GERAÇÃO DE IdTransacao:")
print("="*80)
print(f"\nData:            {data}")
print(f"Estabelecimento: {estabelecimento}")
print(f"Valor:           {valor}")
print(f"User ID:         {user_id}")
print(f"ID Existente:    {id_existente}\n")

print("📊 Hashes gerados por sequência:")
print("-"*80)
for seq in range(1, 6):
    hash_id = generate_id_transacao(data, estabelecimento, valor, user_id, seq)
    match = "✅ MATCH!" if hash_id == id_existente else ""
    print(f"  Sequência {seq}: {hash_id} {match}")

print("\n" + "="*80)
print("🔍 TESTANDO VARIAÇÕES:")
print("-"*80 + "\n")

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
    print(f"  {nome:20s}: {hash_id} {match}")

# Testar a chave exata
print("\n" + "="*80)
print("🔑 CHAVE GERADA:")
print("-"*80)
chave = f"{user_id}|{data}|{estabelecimento.upper().strip()}|{valor:.2f}"
print(f"  {chave}")
print(f"\n  Hash: {fnv1a_64_hash(chave)}")
