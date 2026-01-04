#!/usr/bin/env python3
"""
Teste simplificado do Level 3 usando SQL direto
"""

import sqlite3
import sys
import os

# Adicionar paths
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio')

from normalizer import normalizar, normalizar_estabelecimento, get_faixa_valor

def test_nivel_3_sql_direto():
    """Teste Level 3 usando SQL direto"""
    
    db_path = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db'
    
    print("🧪 TESTE LEVEL 3 - SQL DIRETO")
    print("=" * 50)
    
    # Dados de teste
    transacoes_teste = [
        {
            'EstabelecimentoBase': 'CONTA VIVO',
            'Valor': -75.0,
            'desc': 'CONTA VIVO TELECOMUNICACOES'
        },
        {
            'EstabelecimentoBase': 'CONTA VIVO',
            'Valor': -128.0,
            'desc': 'CONTA VIVO'
        },
        {
            'EstabelecimentoBase': 'CONTA VIVO',
            'Valor': -155.0,
            'desc': 'CONTA VIVO FIBRA'
        }
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        for i, transacao in enumerate(transacoes_teste, 1):
            print(f"\n📱 TESTE {i}: {transacao['desc']} - R$ {transacao['Valor']}")
            print("-" * 40)
            
            # Normalizar estabelecimento
            estab_base = transacao['EstabelecimentoBase']
            estab_norm = normalizar(estab_base)
            
            # Gerar faixa de valor
            valor = transacao['Valor']
            faixa_valor = get_faixa_valor(valor)
            padrao_segmentado = f"{estab_norm} [{faixa_valor}]"
            
            print(f"   🔍 Estabelecimento normalizado: '{estab_norm}'")
            print(f"   💰 Valor: {valor:.2f} → Faixa: {faixa_valor}")
            print(f"   🎯 Padrão segmentado: '{padrao_segmentado}'")
            
            # 1. Buscar padrão segmentado
            cursor = conn.cursor()
            cursor.execute("""
                SELECT padrao_estabelecimento, grupo_sugerido, subgrupo_sugerido, 
                       tipo_gasto_sugerido, contagem
                FROM base_padroes 
                WHERE padrao_estabelecimento = ? 
                AND confianca = 'alta' 
                AND status = 'ativo'
            """, (padrao_segmentado,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                print(f"   ✅ PADRÃO SEGMENTADO ENCONTRADO!")
                print(f"      📁 GRUPO: {resultado[1]}")
                print(f"      📂 SUBGRUPO: {resultado[2]}")  
                print(f"      💰 TipoGasto: {resultado[3]}")
                print(f"      📊 Contagem: {resultado[4]}x")
            else:
                print(f"   ❌ Padrão segmentado '{padrao_segmentado}' não encontrado")
                
                # 2. Tentar padrão simples
                cursor.execute("""
                    SELECT padrao_estabelecimento, grupo_sugerido, subgrupo_sugerido,
                           tipo_gasto_sugerido, contagem
                    FROM base_padroes 
                    WHERE padrao_estabelecimento = ?
                    AND confianca = 'alta'
                    AND status = 'ativo'
                """, (estab_norm,))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    print(f"   ✅ PADRÃO SIMPLES ENCONTRADO!")
                    print(f"      📁 GRUPO: {resultado[1]}")
                    print(f"      📂 SUBGRUPO: {resultado[2]}")
                    print(f"      💰 TipoGasto: {resultado[3]}")
                    print(f"      📊 Contagem: {resultado[4]}x")
                else:
                    print(f"   ❌ Nenhum padrão encontrado para '{estab_norm}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nivel_3_sql_direto()