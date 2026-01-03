#!/usr/bin/env python3
"""
Script de Atualização de Código - Novas Colunas
Version: 1.0.0
Date: 2026-01-03

Atualiza código do backend para usar novas colunas:
- origem → banco_origem
- DT_Fatura → MesFatura  
- forma_classificacao + MarcacaoIA → origem_classificacao
- banco → removido (redundante)
- Outros campos obsoletos removidos

Este script faz buscas e substituições em massa nos arquivos Python.
"""

import os
import re
from pathlib import Path

# Definir mapeamentos
REPLACEMENTS = {
    # Coluna DT_Fatura → MesFatura
    "'DT_Fatura':": "'MesFatura':",
    '"DT_Fatura":': '"MesFatura":',
    '.DT_Fatura': '.MesFatura',
    'DT_Fatura =': 'MesFatura =',
    "dt_fatura = trans_dict.get('DT_Fatura')": "mes_fatura = trans_dict.get('MesFatura')",
    
    # Coluna origem → banco_origem  
    "'origem':": "'banco_origem':",
    '"origem":': '"banco_origem":',
    '.origem ': '.banco_origem ',
    
    # Classificação: forma_classificacao → origem_classificacao
    "'forma_classificacao':": "'origem_classificacao':",
    '"forma_classificacao":': '"origem_classificacao":',
    '.forma_classificacao': '.origem_classificacao',
    'forma_classificacao =': 'origem_classificacao =',
    "forma_classificacao.startswith('Automática": "origem_classificacao.startswith('Automática",
    
    # Valores da classificação (atualizar formato)
    "'Não Classificada'": "'Não Classificada'",  # Mantém igual
    "'Manual'": "'Manual'",  # Mantém igual
    
    # MarcacaoIA removido (substituir por origem_classificacao quando necessário)
    "'MarcacaoIA': None": "'origem_classificacao': 'Não Classificada'",
    '"MarcacaoIA": None': '"origem_classificacao": "Não Classificada"',
    "'MarcacaoIA':": "'origem_classificacao':",
    '"MarcacaoIA":': '"origem_classificacao":',
}

# Caminhos específicos para atualizar
PATHS_TO_UPDATE = [
    'app/blueprints/upload/processors/extrato_conta.py',
    'app/blueprints/upload/processors/fatura_cartao.py',
    'app/blueprints/upload/validators.py',
    'app/blueprints/upload/routes.py',
    'app/blueprints/dashboard/routes.py',
    'app/utils/deduplicator.py',
]

def update_file(filepath):
    """Atualiza um arquivo com as substituições"""
    print(f"\n📝 Processando: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ⚠️  Arquivo não encontrado: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # Aplicar cada substituição
    for old, new in REPLACEMENTS.items():
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes += count
            if count > 0:
                print(f"   ✅ '{old}' → '{new}' ({count}x)")
    
    # Salvar se houve mudanças
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   💾 Arquivo salvo com {changes} alterações")
        return True
    else:
        print(f"   ℹ️  Nenhuma alteração necessária")
        return False

def main():
    print("=" * 80)
    print("ATUALIZANDO CÓDIGO PARA NOVAS COLUNAS")
    print("=" * 80)
    
    updated_files = []
    skipped_files = []
    
    for filepath in PATHS_TO_UPDATE:
        if update_file(filepath):
            updated_files.append(filepath)
        else:
            skipped_files.append(filepath)
    
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    print(f"✅ Arquivos atualizados: {len(updated_files)}")
    for f in updated_files:
        print(f"   - {f}")
    
    print(f"\nℹ️  Arquivos sem mudanças: {len(skipped_files)}")
    for f in skipped_files:
        print(f"   - {f}")
    
    print("\n⚠️  ATENÇÃO:")
    print("   1. Revise os arquivos atualizados")
    print("   2. Teste os processors com CSVs históricos")
    print("   3. Verifique que classificações automáticas funcionam")
    print("=" * 80)

if __name__ == "__main__":
    main()
