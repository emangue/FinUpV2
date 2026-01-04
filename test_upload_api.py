#!/usr/bin/env python3
"""
Teste de upload via API para validar padrões segmentados Level 3
"""

import requests
import json

# Preparar dados de teste com CONTA VIVO 
dados_teste = [
    {
        'Data': '2025-12-27',
        'Estabelecimento': 'CONTA VIVO TELECOMUNICACOES',
        'Valor': -75.0,
        'TipoTransacao': 'Débito'
    },
    {
        'Data': '2025-12-27', 
        'Estabelecimento': 'CONTA VIVO',
        'Valor': -128.0,
        'TipoTransacao': 'Débito'
    }
]

print('🧪 Testando upload via API com padrões segmentados...')
print(f'📤 Dados:')
for i, item in enumerate(dados_teste, 1):
    print(f"  {i}. {item['Estabelecimento']} - R$ {item['Valor']}")

try:
    response = requests.post(
        'http://localhost:3000/api/upload/process', 
        json=dados_teste,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f'📊 Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print('✅ RESULTADO DO UPLOAD:')
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f'❌ Erro: {response.text}')
        
except Exception as e:
    print(f'❌ Erro na requisição: {e}')