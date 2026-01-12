import hashlib

# Gerar IdParcela como na base_parcelas (método original)
def gerar_id_original(estabelecimento, valor, total):
    chave = f"{estabelecimento}|{valor:.2f}|{total}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]

# Dados da base_parcelas
print("=== COMPARAÇÃO DE GERAÇÃO IdParcela ===\n")

casos = [
    ("EBN VPD TRAVEL", 332.19, 10, "fe5f6b5a6acd3a81"),
    ("EBN VPD TRAVEL", 388.90, 10, "e11fde956855a2ef"),
]

for estab, valor, total, id_esperado in casos:
    # Método original (base_parcelas)
    id_original = gerar_id_original(estab, valor, total)
    
    # Método atual (marker.py) - com estabelecimento extraído
    estab_extraido = "EBN    *VPD TRAVEL"  # Como vem do lançamento
    id_atual = gerar_id_original(estab_extraido, valor, total)
    
    print(f"Valor: R$ {valor:.2f}")
    print(f"  Base_parcelas: '{estab}' -> {id_original}")
    print(f"  Esperado: {id_esperado}")
    print(f"  Marker.py: '{estab_extraido}' -> {id_atual}")
    print(f"  Match Original: {'✅' if id_original == id_esperado else '❌'}")
    print(f"  Match Atual: {'✅' if id_atual == id_esperado else '❌'}")
    
    # Testar possíveis normalizações
    from app_dev.backend.app.shared.utils import normalizar_estabelecimento
    try:
        estab_normalizado = normalizar_estabelecimento(estab_extraido)
        id_normalizado = gerar_id_original(estab_normalizado, valor, total)
        print(f"  Normalizado: '{estab_normalizado}' -> {id_normalizado}")
        print(f"  Match Norm: {'✅' if id_normalizado == id_esperado else '❌'}")
    except:
        print(f"  Normalizado: ERRO")
    print()

print("\n=== CHAVES TESTADAS ===")
print(f"Chave original: 'EBN VPD TRAVEL|332.19|10'")
print(f"Chave atual:    'EBN    *VPD TRAVEL|332.19|10'")
print(f"Diferença: Espaços extras e '*' no meio")