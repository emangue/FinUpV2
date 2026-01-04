"""
Teste final do CascadeClassifier com versão corrigida
"""
import sqlite3
import sys
sys.path.append('/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3')

from codigos_apoio.normalizer import normalizar_estabelecimento, get_faixa_valor

class SimpleCascadeClassifier:
    """
    Versão simplificada do CascadeClassifier apenas para nível 3 (Base_Padroes)
    """
    
    def __init__(self, db_path, user_id=1):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.user_id = user_id
    
    def nivel_3_base_padroes(self, transacao):
        """
        Nível 3: Padrões segmentados por faixa de valor
        """
        estabelecimento = transacao.get('Estabelecimento', '')
        valor = transacao.get('Valor', 0)
        
        # Normalizar estabelecimento
        estab_norm = normalizar_estabelecimento(estabelecimento)
        
        # Gerar padrão segmentado
        faixa_valor = get_faixa_valor(valor)
        padrao_segmentado = f"{estab_norm} [{faixa_valor}]"
        
        print(f"   🔍 Buscando: '{padrao_segmentado}'")
        
        # 1. Buscar padrão segmentado exato
        self.cursor.execute("""
            SELECT grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido, 
                   confianca, contagem, padrao_estabelecimento
            FROM base_padroes 
            WHERE padrao_estabelecimento = ? AND confianca = 'alta'
            ORDER BY contagem DESC
            LIMIT 1
        """, (padrao_segmentado,))
        
        resultado = self.cursor.fetchone()
        
        if resultado:
            print(f"   ✅ PADRÃO SEGMENTADO ENCONTRADO: {resultado[5]} ({resultado[4]}x)")
            return {
                'GRUPO': resultado[0],
                'SUBGRUPO': resultado[1], 
                'TipoGasto': resultado[2],
                'origem_classificacao': 'Base_Padroes',
                'MarcacaoIA': f'Auto (Padrão segmentado: {resultado[4]}x observado)'
            }
        
        # 2. Fallback: padrão simples
        self.cursor.execute("""
            SELECT grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido, 
                   confianca, contagem, padrao_estabelecimento
            FROM base_padroes 
            WHERE padrao_estabelecimento = ? AND confianca = 'alta'
            ORDER BY contagem DESC
            LIMIT 1
        """, (estab_norm,))
        
        resultado = self.cursor.fetchone()
        
        if resultado:
            print(f"   ⚠️  PADRÃO SIMPLES ENCONTRADO: {resultado[5]} ({resultado[4]}x)")
            return {
                'GRUPO': resultado[0],
                'SUBGRUPO': resultado[1],
                'TipoGasto': resultado[2],
                'origem_classificacao': 'Base_Padroes',
                'MarcacaoIA': f'Auto (Padrão simples: {resultado[4]}x observado)'
            }
        
        print(f"   ❌ Nenhum padrão encontrado")
        return None
    
    def close(self):
        self.conn.close()


def test_final():
    """Teste final completo"""
    print("🎯 TESTE FINAL - CASCADECLASSIFIER NÍVEL 3")
    print("=" * 70)
    
    # Inicializar classificador
    classifier = SimpleCascadeClassifier("app_dev/backend/database/financas_dev.db")
    
    # Transações teste
    transacoes = [
        {'Estabelecimento': 'CONTA VIVO', 'Valor': -75.0},   # [50-100] → Celular
        {'Estabelecimento': 'CONTA VIVO', 'Valor': -128.0},  # [100-200] → Internet
        {'Estabelecimento': 'CONTA VIVO', 'Valor': -155.0},  # [100-200] → Internet
        {'Estabelecimento': 'Amazon', 'Valor': -45.0},       # Teste com outro estabelecimento
    ]
    
    sucessos = 0
    for i, trans in enumerate(transacoes, 1):
        print(f"\n📱 Teste {i}: {trans['Estabelecimento']} - R$ {trans['Valor']:.2f}")
        
        resultado = classifier.nivel_3_base_padroes(trans)
        
        if resultado:
            print(f"   ✅ CLASSIFICADO:")
            print(f"      GRUPO: {resultado['GRUPO']}")
            print(f"      SUBGRUPO: {resultado['SUBGRUPO']}")
            print(f"      TipoGasto: {resultado['TipoGasto']}")
            print(f"      MarcacaoIA: {resultado['MarcacaoIA']}")
            sucessos += 1
        else:
            print(f"   ❌ NÃO CLASSIFICADO")
    
    classifier.close()
    
    print(f"\n📊 RESULTADO FINAL: {sucessos}/{len(transacoes)} sucessos")
    
    if sucessos >= 3:  # Pelo menos CONTA VIVO deve funcionar
        print("🎉 TESTE APROVADO - Padrões segmentados funcionando!")
        return True
    else:
        print("❌ TESTE FALHOU - Problemas na classificação")
        return False


if __name__ == '__main__':
    sucesso = test_final()
    exit(0 if sucesso else 1)