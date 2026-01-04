#!/usr/bin/env python3
"""
Teste final do CascadeClassifier Level 3 com modelo BasePadrao criado
"""

import sys
import os

# Adicionar paths necessários
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio')
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend')

from cascade_classifier import CascadeClassifier

def test_cascade_level3_final():
    """Teste final do Level 3 com CascadeClassifier"""
    
    print("🎯 TESTE FINAL - CascadeClassifier Level 3")
    print("=" * 60)
    
    # Dados de teste
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
            'Estabelecimento': 'CONTA VIVO',
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
        }
    ]
    
    try:
        # Criar mock de session que conecta ao banco real
        import sqlite3
        
        class MockSession:
            def __init__(self):
                self.db_path = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db'
                
            def query(self, model):
                return MockQuery(self.db_path, model)
        
        class MockQuery:
            def __init__(self, db_path, model):
                self.db_path = db_path
                self.model = model
                self.filters = []
                
            def filter(self, *conditions):
                new_query = MockQuery(self.db_path, self.model)
                new_query.filters = self.filters + list(conditions)
                return new_query
                
            def first(self):
                """Simular query do SQLAlchemy usando SQLite direto"""
                if 'BasePadrao' in str(self.model):
                    conn = sqlite3.connect(self.db_path)
                    conn.row_factory = sqlite3.Row
                    
                    # Construir query baseada nos filtros
                    where_clauses = []
                    params = []
                    
                    for condition in self.filters:
                        condition_str = str(condition)
                        if 'user_id' in condition_str:
                            where_clauses.append('user_id = ?')
                            params.append(1)  # user_id = 1
                        elif 'padrao_estabelecimento' in condition_str:
                            if '[' in condition_str and ']' in condition_str:
                                # Padrão segmentado
                                start = condition_str.find("'") + 1
                                end = condition_str.rfind("'")
                                padrao = condition_str[start:end]
                                where_clauses.append('padrao_estabelecimento = ?')
                                params.append(padrao)
                            elif 'like' in condition_str.lower():
                                # Padrão LIKE
                                start = condition_str.find("'") + 1
                                end = condition_str.rfind("'")
                                padrao = condition_str[start:end].replace('%', '')
                                where_clauses.append('padrao_estabelecimento LIKE ?')
                                params.append(f'{padrao}%')
                            else:
                                # Padrão exato simples
                                start = condition_str.find("'") + 1
                                end = condition_str.rfind("'")
                                padrao = condition_str[start:end]
                                where_clauses.append('padrao_estabelecimento = ?')
                                params.append(padrao)
                        elif 'confianca' in condition_str:
                            where_clauses.append('confianca = ?')
                            params.append('alta')
                        elif 'status' in condition_str:
                            where_clauses.append('status = ?')
                            params.append('ativo')
                    
                    where_sql = ' AND '.join(where_clauses)
                    sql = f"SELECT * FROM base_padroes WHERE {where_sql} LIMIT 1"
                    
                    cursor = conn.cursor()
                    cursor.execute(sql, params)
                    result = cursor.fetchone()
                    
                    if result:
                        # Simular objeto BasePadrao
                        class MockPadrao:
                            def __init__(self, row):
                                self.padrao_estabelecimento = row['padrao_estabelecimento']
                                self.grupo_sugerido = row['grupo_sugerido']
                                self.subgrupo_sugerido = row['subgrupo_sugerido']
                                self.tipo_gasto_sugerido = row['tipo_gasto_sugerido']
                                self.contagem = row['contagem']
                        
                        conn.close()
                        return MockPadrao(result)
                    
                    conn.close()
                
                return None
        
        # Criar classifier
        mock_session = MockSession()
        classifier = CascadeClassifier(user_id=1, db_session=mock_session)
        
        # Testar cada transação
        successos = 0
        total = len(transacoes_teste)
        
        for i, transacao in enumerate(transacoes_teste, 1):
            print(f"\n📱 TESTE {i}: {transacao['Estabelecimento']} - R$ {transacao['Valor']}")
            print("-" * 50)
            
            resultado = classifier._nivel_3_base_padroes(transacao)
            
            if resultado:
                print("✅ CLASSIFICADO PELO LEVEL 3:")
                print(f"   📁 GRUPO: {resultado['GRUPO']}")
                print(f"   📂 SUBGRUPO: {resultado['SUBGRUPO']}")
                print(f"   💰 TipoGasto: {resultado['TipoGasto']}")
                print(f"   🤖 MarcacaoIA: {resultado['MarcacaoIA']}")
                print(f"   🎯 Origem: {resultado['origem_classificacao']}")
                successos += 1
            else:
                print("❌ NÃO CLASSIFICADO PELO LEVEL 3")
        
        # Resultado final
        print(f"\n" + "=" * 60)
        print(f"📊 RESULTADO FINAL: {successos}/{total} sucessos ({successos/total*100:.1f}%)")
        
        if successos >= 2:  # Pelo menos 2 dos 3 CONTA VIVO
            print("🎉 TESTE APROVADO! Level 3 com padrões segmentados está funcionando!")
        else:
            print("❌ TESTE REPROVADO. Level 3 ainda com problemas.")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cascade_level3_final()