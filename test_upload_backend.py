#!/usr/bin/env python3
"""
Teste de upload direto no backend FastAPI para validar padrões segmentados Level 3
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
    },
    {
        'Data': '2025-12-27', 
        'Estabelecimento': 'AMAZON.COM.BR',
        'Valor': -45.0,
        'TipoTransacao': 'Débito'
    }
]

print('🧪 Testando upload DIRETO no backend FastAPI...')
print(f'📤 Dados:')
for i, item in enumerate(dados_teste, 1):
    print(f"  {i}. {item['Estabelecimento']} - R$ {item['Valor']}")

try:
    # Testar direto no backend FastAPI (porta 8000)
    response = requests.post(
        'http://localhost:8000/upload/process', 
        json={
            'data': dados_teste,
            'source': 'test_level3',
            'user_id': 1,  # User ID padrão
            'metadata': {'test': True}
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f'\n📊 Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print('✅ RESULTADO DO UPLOAD:')
        
        # Mostrar estatísticas de classificação
        if 'classification_stats' in result:
            stats = result['classification_stats']
            print('\n📊 ESTATÍSTICAS DE CLASSIFICAÇÃO:')
            for nivel, count in stats.items():
                if count > 0:
                    print(f"   ✅ {nivel}: {count}")
            
            # Verificar se Level 3 funcionou
            if stats.get('nivel_3_base_padroes', 0) > 0:
                print(f'\n🎯 SUCESSO! Level 3 (Base_Padroes) classificou {stats["nivel_3_base_padroes"]} transações')
            else:
                print(f'\n⚠️  Level 3 (Base_Padroes) ainda em 0 classificações')
        
        # Mostrar detalhes das transações processadas
        if 'processed' in result:
            print('\n📋 TRANSAÇÕES PROCESSADAS:')
            for i, trans in enumerate(result['processed'], 1):
                grupo = trans.get('GRUPO', 'N/A')
                subgrupo = trans.get('SUBGRUPO', 'N/A')
                origem = trans.get('origem_classificacao', 'N/A')
                marca = trans.get('MarcacaoIA', 'N/A')
                print(f"   {i}. {trans.get('Estabelecimento', '')}")
                print(f"      📁 {grupo} > {subgrupo}")
                print(f"      🤖 {origem} | {marca}")
                print()
        
    else:
        print(f'❌ Erro: {response.text}')
        
except Exception as e:
    print(f'❌ Erro na requisição: {e}')