import re

def extrair_parcela_do_estabelecimento(estabelecimento: str):
    """
    Extrai informação de parcela do estabelecimento
    Suporta formatos: "LOJA (3/12)" ou "LOJA 3/12" ou "LOJA3/12" (colado)
    """
    # Tenta formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        # Validação básica
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    # Tenta formato sem parênteses: "LOJA 3/12" OU "LOJA3/12" (colado)
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        # Validação básica
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    return None

# Testar casos
casos = [
    "EBN    *VPD TRAVEL09/10",  # Caso problema
    "LOJA 03/12",               # Com espaço
    "LOJA (03/12)",             # Com parênteses
    "LOJA03/12",                # Colado
    "NETFLIX 1/3",              # Outro exemplo
    "SEM PARCELA",              # Sem parcela
]

print("=== TESTE DE DETECÇÃO DE PARCELAS ===\n")
for caso in casos:
    resultado = extrair_parcela_do_estabelecimento(caso)
    if resultado:
        print(f"✅ {caso}")
        print(f"   Estabelecimento: '{resultado['estabelecimento_base']}'")
        print(f"   Parcela: {resultado['parcela']}/{resultado['total']}")
    else:
        print(f"❌ {caso} - Não detectado")
    print()