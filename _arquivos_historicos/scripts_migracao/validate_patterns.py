#!/usr/bin/env python3
"""
Validação: Padrões gerados vs Base existente
Analisa formatos e detecta inconsistências
"""

import sys
sys.path.insert(0, 'app_dev/backend')

from app.core.database import SessionLocal
from app.domains.patterns.models import BasePadroes

db = SessionLocal()

print('🔍 ANÁLISE: Formatos de Padrões na Base\n')
print('=' * 80)

# Buscar diferentes formatos
formats = {}

padroes = db.query(BasePadroes).filter(BasePadroes.user_id == 1).limit(100).all()

for p in padroes:
    estab = p.padrao_estabelecimento
    
    # Detectar formato
    if '|FAIXA:' in estab:
        fmt = 'FAIXA_SEGMENTADA'  # pattern_generator
    elif estab.count('|') == 2 and '|' in estab:
        parts = estab.split('|')
        if len(parts) == 3 and parts[1].isdigit():
            fmt = 'PARCELA'  # valor|count
        else:
            fmt = 'OUTRO_PIPE'
    elif ' [' in estab and ']' in estab:
        fmt = 'FAIXA_BRACKETS'  # classifier (antigo)
    else:
        fmt = 'SIMPLES'
    
    if fmt not in formats:
        formats[fmt] = []
    
    if len(formats[fmt]) < 5:  # Max 5 exemplos por formato
        formats[fmt].append(estab)

# Mostrar exemplos de cada formato
print('\n📋 FORMATOS ENCONTRADOS:\n')
for fmt, exemplos in formats.items():
    total = sum(1 for p in padroes if p.padrao_estabelecimento in exemplos or 
                ('|FAIXA:' in p.padrao_estabelecimento if fmt == 'FAIXA_SEGMENTADA' else False))
    print(f'  {fmt}:')
    for ex in exemplos:
        print(f'    - {ex}')
    print()

# Contar total por formato
print('\n📊 CONTAGEM TOTAL:')
total_faixa = db.query(BasePadroes).filter(
    BasePadroes.user_id == 1,
    BasePadroes.padrao_estabelecimento.like('%|FAIXA:%')
).count()

total_brackets = db.query(BasePadroes).filter(
    BasePadroes.user_id == 1,
    BasePadroes.padrao_estabelecimento.like('% [%]%')
).count()

total_parcela = db.query(BasePadroes).filter(
    BasePadroes.user_id == 1,
    BasePadroes.padrao_estabelecimento.like('%|%|%')
).count()

total_all = db.query(BasePadroes).filter(BasePadroes.user_id == 1).count()

print(f'  FAIXA_SEGMENTADA (|FAIXA:): {total_faixa}')
print(f'  FAIXA_BRACKETS ([ ]): {total_brackets}')
print(f'  PARCELA (|valor|count): {total_parcela}')
print(f'  TOTAL: {total_all}')

# Problema detectado
print('\n⚠️  PROBLEMA DETECTADO:')
print('  - pattern_generator.py usa: "ESTABELECIMENTO|FAIXA:500-1K"')
print('  - classifier.py usa: "ESTABELECIMENTO [500-1K]"')
print('\n  ❌ Os formatos NÃO são compatíveis!')
print('  ❌ Classifier não vai encontrar padrões gerados!')

db.close()
