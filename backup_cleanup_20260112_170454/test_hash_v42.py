#!/usr/bin/env python3
"""
Teste: Gerar hash para PIT STOP BEBIDAS e verificar se bate com banco
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.shared.utils.hasher import generate_id_transacao

# Caso do banco
data = "23/11/2025"
estabelecimento = "PIT STOP BEBIDAS"
valor = -42.29

# Gerar hash (seq=1, pois é primeira ocorrência no arquivo)
hash_gerado = generate_id_transacao(
    data=data,
    estabelecimento=estabelecimento,
    valor=valor,  # VALOR EXATO (com sinal negativo)
    sequencia=1
)

print(f"✅ v4.2.0 (estabelecimento completo + valor exato):")
print(f"   Data: {data}")
print(f"   Estabelecimento: {estabelecimento}")
print(f"   Valor: {valor}")
print(f"   Sequencia: 1")
print(f"   Hash gerado: {hash_gerado}")
print()
print(f"🔍 Banco tem: 16152610384312802180")
print(f"   Match? {hash_gerado == '16152610384312802180'}")
