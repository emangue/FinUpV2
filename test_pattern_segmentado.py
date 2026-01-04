#!/usr/bin/env python3
"""
Teste de padrões segmentados
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app_dev', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Conectar ao banco
engine = create_engine('sqlite:///app_dev/backend/database/financas_dev.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Importar models
from models import BasePadrao

# Importar utilitários
from codigos_apoio.normalizer import normalizar_estabelecimento, get_faixa_valor

def test_pattern_segmented():
    """Testa busca por padrões segmentados"""
    
    # Transação teste
    estabelecimento = "CONTA VIVO"
    valor = -128.0
    
    # Normalizar estabelecimento
    estab_norm = normalizar_estabelecimento(estabelecimento)
    faixa_valor = get_faixa_valor(valor)
    padrao_segmentado = f"{estab_norm} [{faixa_valor}]"
    
    print(f"🔍 Testando padrão segmentado: '{padrao_segmentado}'")
    print(f"   Estabelecimento: {estabelecimento}")
    print(f"   Normalizado: {estab_norm}")
    print(f"   Valor: {valor}")
    print(f"   Faixa: {faixa_valor}")
    
    # 1. Buscar padrão segmentado EXATO
    padrao_exato = session.query(BasePadrao).filter(
        BasePadrao.padrao_estabelecimento == padrao_segmentado,
        BasePadrao.confianca == 'alta'
    ).first()
    
    if padrao_exato:
        print(f"   ✅ PADRÃO SEGMENTADO ENCONTRADO:")
        print(f"      ID: {padrao_exato.id}")
        print(f"      Padrão: {padrao_exato.padrao_estabelecimento}")
        print(f"      Grupo: {padrao_exato.grupo_sugerido}")
        print(f"      Subgrupo: {padrao_exato.subgrupo_sugerido}")
        print(f"      TipoGasto: {padrao_exato.tipo_gasto_sugerido}")
        print(f"      Confiança: {padrao_exato.confianca}")
        print(f"      Contagem: {padrao_exato.contagem}")
        return True
    
    # 2. Buscar padrão simples
    padrao_simples = session.query(BasePadrao).filter(
        BasePadrao.padrao_estabelecimento == estab_norm,
        BasePadrao.confianca == 'alta'
    ).first()
    
    if padrao_simples:
        print(f"   ⚠️  PADRÃO SIMPLES ENCONTRADO (sem segmentação):")
        print(f"      ID: {padrao_simples.id}")
        print(f"      Padrão: {padrao_simples.padrao_estabelecimento}")
        print(f"      Grupo: {padrao_simples.grupo_sugerido}")
        return True
    
    # 3. Verificar todos os padrões CONTA VIVO disponíveis
    todos_padroes = session.query(BasePadrao).filter(
        BasePadrao.padrao_estabelecimento.like('%CONTA VIVO%')
    ).all()
    
    print(f"   📊 PADRÕES CONTA VIVO DISPONÍVEIS: {len(todos_padroes)}")
    for p in todos_padroes:
        print(f"      - '{p.padrao_estabelecimento}' (confiança: {p.confianca}, contagem: {p.contagem})")
    
    if not todos_padroes:
        print(f"   ❌ NENHUM PADRÃO CONTA VIVO ENCONTRADO NO BANCO!")
    
    return False


if __name__ == '__main__':
    print("🧪 TESTE DE PADRÕES SEGMENTADOS")
    print("=" * 60)
    
    resultado = test_pattern_segmented()
    
    session.close()
    
    if resultado:
        print("\n✅ TESTE PASSOU - Padrão encontrado!")
    else:
        print("\n❌ TESTE FALHOU - Padrão não encontrado")