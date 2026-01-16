#!/usr/bin/env python3
"""
FASE 5: ATUALIZAR GENERIC_RULES_CLASSIFIER
===========================================

Atualiza as 39 regras de classificação genérica para usar os 5 valores
simplificados de TipoGasto (Fixo, Ajustável, Investimentos, Transferência, Receita)

Mapeia baseado no GRUPO de cada regra, consultando base_grupos_config
"""

import sys
import sqlite3
from pathlib import Path
import re
from datetime import datetime
import shutil

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"
CLASSIFIER_PATH = PROJECT_ROOT / "app_dev" / "backend" / "app" / "domains" / "upload" / "processors" / "generic_rules_classifier.py"


def carregar_mapeamento_grupos():
    """Carrega mapeamento GRUPO → tipo_gasto_padrao de base_grupos_config"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome_grupo, tipo_gasto_padrao FROM base_grupos_config")
    mapeamento = dict(cursor.fetchall())
    conn.close()
    
    return mapeamento


def obter_tipo_gasto_correto(grupo: str, mapeamento: dict) -> str:
    """
    Determina TipoGasto correto baseado no GRUPO
    
    Args:
        grupo: Nome do grupo (ex: "Viagens", "Casa")
        mapeamento: Dict de base_grupos_config
        
    Returns:
        TipoGasto simplificado (Fixo, Ajustável, Investimentos, Transferência, Receita)
    """
    # Tentar mapear diretamente
    if grupo in mapeamento:
        return mapeamento[grupo]
    
    # Fallbacks para grupos especiais não configurados
    if 'investimento' in grupo.lower():
        return 'Investimentos'
    if 'transferencia' in grupo.lower() or 'transferência' in grupo.lower():
        return 'Transferência'
    
    # Default: Ajustável
    return 'Ajustável'


def atualizar_regras_no_arquivo():
    """
    Lê generic_rules_classifier.py e atualiza valores de tipo_gasto
    mantendo a mesma estrutura de código
    """
    print("="*80)
    print("FASE 5: ATUALIZAR GENERIC_RULES_CLASSIFIER")
    print("="*80)
    
    # 1. Carregar mapeamento
    print("\n1️⃣  Carregando mapeamento de base_grupos_config...")
    mapeamento = carregar_mapeamento_grupos()
    print(f"   ✅ {len(mapeamento)} grupos mapeados\n")
    
    # 2. Backup do arquivo
    print("2️⃣  Criando backup do arquivo...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CLASSIFIER_PATH.parent / f"generic_rules_classifier.py.backup_fase5_{timestamp}"
    shutil.copy2(CLASSIFIER_PATH, backup_path)
    print(f"   ✅ Backup: {backup_path.name}\n")
    
    # 3. Ler arquivo original
    print("3️⃣  Lendo arquivo original...")
    with open(CLASSIFIER_PATH, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # 4. Identificar e substituir todos os tipo_gasto antigos
    print("4️⃣  Atualizando regras...\n")
    
    # Padrão: tipo_gasto='VALOR_ANTIGO'
    pattern = r"grupo='([^']+)',\s*subgrupo='[^']+',\s*tipo_gasto='([^']+)'"
    
    regras_atualizadas = 0
    valores_antigos_encontrados = set()
    
    def substituir_tipo_gasto(match):
        nonlocal regras_atualizadas, valores_antigos_encontrados
        
        grupo = match.group(1)
        tipo_gasto_antigo = match.group(2)
        
        # Determinar novo valor baseado no grupo
        tipo_gasto_novo = obter_tipo_gasto_correto(grupo, mapeamento)
        
        # Log apenas se mudou
        if tipo_gasto_antigo != tipo_gasto_novo:
            regras_atualizadas += 1
            valores_antigos_encontrados.add(tipo_gasto_antigo)
            print(f"   • {grupo:30s}: '{tipo_gasto_antigo}' → '{tipo_gasto_novo}'")
        
        # Retornar texto atualizado mantendo formatação
        return match.group(0).replace(f"tipo_gasto='{tipo_gasto_antigo}'", f"tipo_gasto='{tipo_gasto_novo}'")
    
    conteudo_atualizado = re.sub(pattern, substituir_tipo_gasto, conteudo)
    
    # 5. Salvar arquivo atualizado
    print(f"\n5️⃣  Salvando arquivo atualizado...")
    with open(CLASSIFIER_PATH, 'w', encoding='utf-8') as f:
        f.write(conteudo_atualizado)
    print("   ✅ Arquivo salvo\n")
    
    # 6. Resumo
    print("="*80)
    print("✅ RESUMO")
    print("="*80)
    print(f"Regras atualizadas: {regras_atualizadas}")
    print(f"Valores antigos encontrados: {len(valores_antigos_encontrados)}")
    if valores_antigos_encontrados:
        print("\nValores substituídos:")
        for valor in sorted(valores_antigos_encontrados):
            print(f"  • {valor}")
    
    print("\n🎉 MIGRAÇÃO CONCLUÍDA!")
    print("\n⏭️  PRÓXIMO: Testar classificação com upload de arquivo")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(atualizar_regras_no_arquivo())
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
