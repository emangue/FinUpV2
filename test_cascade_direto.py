#!/usr/bin/env python3
"""
Teste direto do CascadeClassifier com padrões segmentados
Sem usar API - direto no código para verificar Level 3
"""

import sys
import os

# Adicionar paths necessários
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio')
sys.path.insert(0, '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend')

import sqlite3
from cascade_classifier import CascadeClassifier

def test_cascade_level3():
    """Teste direto do Level 3 com padrões segmentados"""
    
    # Mock de sessão de banco - usar SQLite direto
    db_path = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db'
    
    print("🧪 TESTE DIRETO - CascadeClassifier Level 3")
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
            'Estabelecimento': 'CONTA VIVO FIBRA',
            'EstabelecimentoBase': 'CONTA VIVO',
            'Valor': -155.0,
            'TipoTransacao': 'Débito'
        }
    ]
    
    try:
        # Criar mock de sessão de banco
        class MockSession:
            def __init__(self, db_path):
                self.conn = sqlite3.connect(db_path)
                self.conn.row_factory = sqlite3.Row
                
            def query(self, model):
                return MockQuery(self.conn, model)
                
        class MockQuery:
            def __init__(self, conn, model):
                self.conn = conn
                self.model = model
                self.filters = []
                
            def filter(self, *conditions):
                # Simular filtros SQLAlchemy
                new_query = MockQuery(self.conn, self.model)
                new_query.filters = self.filters + list(conditions)
                return new_query
                
            def first(self):
                # Simular resultado de query
                if 'base_padroes' in str(self.model).lower():
                    # Buscar padrões na base real
                    cursor = self.conn.cursor()
                    
                    # Extrair o padrão da condição (muito simplificado)
                    for condition in self.filters:
                        condition_str = str(condition)
                        if 'padrao_estabelecimento' in condition_str and 'CONTA VIVO' in condition_str:
                            if '[50-100]' in condition_str:
                                cursor.execute("""
                                    SELECT * FROM base_padroes 
                                    WHERE padrao_estabelecimento = 'CONTA VIVO [50-100]'
                                    AND confianca = 'alta' AND status = 'ativo'
                                    LIMIT 1
                                """)
                            elif '[100-200]' in condition_str:
                                cursor.execute("""
                                    SELECT * FROM base_padroes 
                                    WHERE padrao_estabelecimento = 'CONTA VIVO [100-200]'
                                    AND confianca = 'alta' AND status = 'ativo'
                                    LIMIT 1
                                """)
                            else:
                                cursor.execute("""
                                    SELECT * FROM base_padroes 
                                    WHERE padrao_estabelecimento = 'CONTA VIVO'
                                    AND confianca = 'alta' AND status = 'ativo'
                                    LIMIT 1
                                """)
                            
                            result = cursor.fetchone()
                            if result:
                                # Simular objeto BasePadrao
                                class MockPadrao:
                                    def __init__(self, row):
                                        self.padrao_estabelecimento = row[2]  # padrao_estabelecimento
                                        self.grupo_sugerido = row[3]         # grupo_sugerido
                                        self.subgrupo_sugerido = row[4]      # subgrupo_sugerido  
                                        self.tipo_gasto_sugerido = row[5]    # tipo_gasto_sugerido
                                        self.contagem = row[6]               # contagem
                                        
                                return MockPadrao(result)
                
                return None
        
        # Criar classifier
        mock_session = MockSession(db_path)
        classifier = CascadeClassifier(user_id=1, db_session=mock_session)
        
        # Testar cada transação
        for i, transacao in enumerate(transacoes_teste, 1):
            print(f"\n📱 TESTE {i}: {transacao['Estabelecimento']} - R$ {transacao['Valor']}")
            print("-" * 50)
            
            resultado = classifier._nivel_3_base_padroes(transacao)
            
            if resultado:
                print("✅ CLASSIFICADO:")
                print(f"   📁 GRUPO: {resultado['GRUPO']}")
                print(f"   📂 SUBGRUPO: {resultado['SUBGRUPO']}")
                print(f"   💰 TipoGasto: {resultado['TipoGasto']}")
                print(f"   🤖 MarcacaoIA: {resultado['MarcacaoIA']}")
            else:
                print("❌ NÃO CLASSIFICADO")
        
        # Mostrar estatísticas
        print(f"\n📊 ESTATÍSTICAS:")
        for nivel, count in classifier.stats.items():
            if count > 0:
                print(f"   ✅ {nivel}: {count}")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cascade_level3()