#!/usr/bin/env python3
"""
Teste: Verificar normalização de formato de parcela
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.shared.utils.hasher import generate_id_transacao
from app.domains.upload.processors.marker import normalizar_formato_parcela

# Caso do banco
data = "01/11/2025"
valor = -99.8
user_id = 1

# Testar normalização
formatos = [
    "AngeloMatosDaSilv (1/5)",      # Formato banco
    "AngeloMatosDaSilv 01/05",      # Formato CSV
    "AngeloMatosDaSilv 1/5",        # Variação
]

print("🔧 Testando normalização de formato:")
print()

for formato in formatos:
    normalizado = normalizar_formato_parcela(formato)
    print(f"Original:    {formato}")
    print(f"Normalizado: {normalizado}")
    
    hash_gerado = generate_id_transacao(
        data=data,
        estabelecimento=normalizado,
        valor=valor,
        user_id=user_id,
        sequencia=1
    )
    print(f"Hash:        {hash_gerado}")
    print(f"Match?       {hash_gerado == '9108038764649343886'}")
    print()

print("🗄️ Hash esperado: 9108038764649343886")
