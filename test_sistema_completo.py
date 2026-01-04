#!/usr/bin/env python3
"""
Teste completo do sistema de upload com Level 3 funcionando
"""

import sys
import os

# Adicionar paths necessários
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio')
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend')

from cascade_classifier import CascadeClassifier

def test_sistema_completo():
    """Teste do sistema completo de classificação"""
    
    print("🎯 TESTE SISTEMA COMPLETO - Todos os 6 Níveis")
    print("=" * 70)
    
    # Dados de teste variados para testar todos os níveis
    transacoes_teste = [
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'CONTA VIVO TELECOMUNICACOES',
            'EstabelecimentoBase': 'CONTA VIVO',
            'Valor': -75.0,
            'TipoTransacao': 'Débito'
        },
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'CONTA VIVO FIBRA',
            'EstabelecimentoBase': 'CONTA VIVO', 
            'Valor': -128.0,
            'TipoTransacao': 'Débito'
        },
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'AMAZON.COM.BR',
            'EstabelecimentoBase': 'AMAZON',
            'Valor': -45.0,
            'TipoTransacao': 'Débito'
        },
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'PAGAMENTO CARTAO VISA',
            'EstabelecimentoBase': 'PAGAMENTO',
            'Valor': -1200.0,
            'TipoTransacao': 'Débito'
        },
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'PIX RECEBIDO',
            'EstabelecimentoBase': 'PIX',
            'Valor': 500.0,
            'TipoTransacao': 'Crédito'
        },
        {
            'Data': '2025-12-27',
            'Estabelecimento': 'LOJA DESCONHECIDA XYZ',
            'EstabelecimentoBase': 'LOJA DESCONHECIDA',
            'Valor': -89.99,
            'TipoTransacao': 'Débito'
        }
    ]
    
    try:
        # Mock de session simples
        class MockSession:
            pass
        
        # Criar classifier
        classifier = CascadeClassifier(user_id=1, db_session=MockSession())
        
        # Estatísticas
        stats = {
            'nivel_0_id_parcela': 0,
            'nivel_1_fatura_cartao': 0, 
            'nivel_2_ignorar': 0,
            'nivel_3_base_padroes': 0,
            'nivel_4_journal_entries': 0,
            'nivel_5_palavras_chave': 0,
            'nivel_6_nao_encontrado': 0
        }
        
        classificados = 0
        
        for i, transacao in enumerate(transacoes_teste, 1):
            print(f"\n📱 TRANSAÇÃO {i}: {transacao['Estabelecimento']}")
            print(f"   💰 Valor: R$ {transacao['Valor']:.2f}")
            print("-" * 60)
            
            # Testar classificação completa
            resultado = classifier.classify(transacao)
            
            if resultado:
                nivel = resultado.get('origem_classificacao', 'Desconhecido')
                print(f"   ✅ CLASSIFICADO - {nivel}")
                print(f"   📁 {resultado.get('GRUPO', 'N/A')} > {resultado.get('SUBGRUPO', 'N/A')}")
                print(f"   💸 {resultado.get('TipoGasto', 'N/A')}")
                print(f"   🤖 {resultado.get('MarcacaoIA', 'N/A')}")
                classificados += 1
                
                # Contabilizar por nível
                if nivel == 'IdParcela':
                    stats['nivel_0_id_parcela'] += 1
                elif nivel == 'Fatura_Cartao':
                    stats['nivel_1_fatura_cartao'] += 1
                elif nivel == 'Ignorar':
                    stats['nivel_2_ignorar'] += 1
                elif nivel == 'Base_Padroes':
                    stats['nivel_3_base_padroes'] += 1
                elif nivel == 'Journal_Entries':
                    stats['nivel_4_journal_entries'] += 1
                elif nivel == 'Palavras_Chave':
                    stats['nivel_5_palavras_chave'] += 1
                else:
                    stats['nivel_6_nao_encontrado'] += 1
            else:
                print(f"   ❌ NÃO CLASSIFICADO")
                stats['nivel_6_nao_encontrado'] += 1
        
        # Relatório final
        print(f"\n" + "=" * 70)
        print(f"📊 RELATÓRIO FINAL")
        print(f"=" * 70)
        print(f"🎯 Classificados: {classificados}/{len(transacoes_teste)} ({classificados/len(transacoes_teste)*100:.1f}%)")
        print(f"\n📈 DISTRIBUIÇÃO POR NÍVEL:")
        
        for nivel, count in stats.items():
            if count > 0:
                nivel_nome = nivel.replace('nivel_', '').replace('_', ' ').title()
                print(f"   ✅ {nivel_nome}: {count}")
        
        # Verificar se Level 3 funcionou
        if stats['nivel_3_base_padroes'] >= 2:
            print(f"\n🎉 SUCESSO! Level 3 (Base_Padroes) classificou {stats['nivel_3_base_padroes']} transações!")
            print(f"🚀 Sistema de padrões segmentados está operacional!")
        else:
            print(f"\n⚠️  Level 3 ainda precisando ajustes ({stats['nivel_3_base_padroes']} classificações)")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sistema_completo()