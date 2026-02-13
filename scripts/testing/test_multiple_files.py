#!/usr/bin/env python3
"""
Teste de cobertura da base genérica com múltiplos arquivos CSV/XLS
Valida assertividade em faturas e extratos
"""

import sqlite3
import csv
import sys
from pathlib import Path
from collections import defaultdict

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class MultiFileGenericTester:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """Carrega regras de classificação genérica do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_regra, keywords, grupo, subgrupo, prioridade
            FROM generic_classification_rules
            WHERE ativo = 1
            ORDER BY prioridade DESC, id ASC
        """)
        
        rules = []
        for row in cursor.fetchall():
            rules.append({
                'id': row[0],
                'nome': row[1],
                'keywords': [k.strip() for k in row[2].upper().split(',')],
                'grupo': row[3],
                'subgrupo': row[4],
                'prioridade': row[5]
            })
        
        conn.close()
        return rules
    
    def classify_transaction(self, estabelecimento: str):
        """Classifica uma transação baseado no estabelecimento"""
        search_text = estabelecimento.upper()
        
        for rule in self.rules:
            for keyword in rule['keywords']:
                if keyword in search_text:
                    return rule['grupo'], rule['subgrupo']
        
        return None, None
    
    def test_csv_file(self, file_path: str, exclude_pix: bool = False):
        """Testa um arquivo CSV"""
        if not Path(file_path).exists():
            return None
        
        total = 0
        classified = 0
        details = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Tentar diferentes formatos de coluna
                    estabelecimento = (
                        row.get('Estabelecimento') or 
                        row.get('estabelecimento') or
                        row.get('Lançamento') or
                        row.get('lançamento') or  # Itaú usa minúsculo
                        row.get('lancamento') or
                        row.get('Descrição') or
                        row.get('descrição') or
                        row.get('descricao') or
                        ''
                    )
                    
                    if not estabelecimento or estabelecimento.strip() == '':
                        continue
                    
                    # Skip PIX/transferências se solicitado
                    if exclude_pix:
                        estab_upper = estabelecimento.upper()
                        if any(keyword in estab_upper for keyword in [
                            'PIX', 'TRANSFERENCIA', 'TRANSFERÊNCIA', 
                            'TRANSF', 'TED', 'DOC'
                        ]):
                            continue
                    
                    total += 1
                    grupo, subgrupo = self.classify_transaction(estabelecimento)
                    
                    if grupo:
                        classified += 1
                        details.append({
                            'estabelecimento': estabelecimento,
                            'grupo': grupo,
                            'subgrupo': subgrupo,
                            'classified': True
                        })
                    else:
                        details.append({
                            'estabelecimento': estabelecimento,
                            'grupo': None,
                            'subgrupo': None,
                            'classified': False
                        })
        except Exception as e:
            print(f"⚠️  Erro ao processar {file_path}: {e}")
            return None
        
        return {
            'total': total,
            'classified': classified,
            'percentage': (classified / total * 100) if total > 0 else 0,
            'details': details
        }
    
    def test_xls_file(self, file_path: str, exclude_pix: bool = False):
        """Testa um arquivo XLS usando pandas"""
        if not HAS_PANDAS:
            print("⚠️  pandas não instalado - não é possível ler arquivos XLS")
            return None
        
        if not Path(file_path).exists():
            return None
        
        total = 0
        classified = 0
        details = []
        
        try:
            # Ler XLS - tentar diferentes skiprows
            df = None
            for skip in [0, 7, 6, 8]:
                try:
                    df_temp = pd.read_excel(file_path, skiprows=skip)
                    # Verificar se tem coluna útil
                    for col in ['lançamento', 'lancamento', 'Lançamento', 'descrição', 'descricao']:
                        if col in df_temp.columns:
                            df = df_temp
                            break
                    if df is not None:
                        break
                except:
                    continue
            
            if df is None:
                print(f"⚠️  Não foi possível ler estrutura de {file_path}")
                return None
            
            # Tentar encontrar coluna de descrição
            col_desc = None
            for col in ['lançamento', 'lancamento', 'Lançamento', 'Lancamento', 
                       'descrição', 'descricao', 'Descrição', 'Descricao',
                       'estabelecimento', 'Estabelecimento']:
                if col in df.columns:
                    col_desc = col
                    break
            
            if not col_desc:
                print(f"⚠️  Coluna de descrição não encontrada em {file_path}")
                return None
            
            for _, row in df.iterrows():
                estabelecimento = str(row[col_desc]) if pd.notna(row[col_desc]) else ''
                
                if not estabelecimento or estabelecimento.strip() == '' or estabelecimento == 'nan':
                    continue
                
                # Skip linhas de cabeçalho/totais
                if estabelecimento.upper() in ['LANÇAMENTOS', 'SALDO ANTERIOR', 'SALDO FINAL', 'DATA']:
                    continue
                
                # Skip PIX/transferências se solicitado
                if exclude_pix:
                    estab_upper = estabelecimento.upper()
                    if any(keyword in estab_upper for keyword in [
                        'PIX', 'TRANSFERENCIA', 'TRANSFERÊNCIA', 
                        'TRANSF', 'TED', 'DOC'
                    ]):
                        continue
                
                total += 1
                grupo, subgrupo = self.classify_transaction(estabelecimento)
                
                if grupo:
                    classified += 1
                    details.append({
                        'estabelecimento': estabelecimento,
                        'grupo': grupo,
                        'subgrupo': subgrupo,
                        'classified': True
                    })
                else:
                    details.append({
                        'estabelecimento': estabelecimento,
                        'grupo': None,
                        'subgrupo': None,
                        'classified': False
                    })
        
        except Exception as e:
            print(f"⚠️  Erro ao processar {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        return {
            'total': total,
            'classified': classified,
            'percentage': (classified / total * 100) if total > 0 else 0,
            'details': details
        }
    
    def test_multiple_files(self, file_patterns: list):
        """Testa múltiplos arquivos"""
        results = {}
        
        for pattern in file_patterns:
            files = list(Path('.').rglob(pattern))
            for file_path in files:
                result = self.test_csv_file(str(file_path))
                if result:
                    results[str(file_path)] = result
        
        return results


def main():
    """Função principal"""
    db_path = "app_dev/backend/database/financas_dev.db"
    
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    tester = MultiFileGenericTester(db_path)
    
    print(f"✅ {len(tester.rules)} regras carregadas\n")
    print("="*100)
    print("🧪 TESTE DE MÚLTIPLOS ARQUIVOS - BASE GENÉRICA")
    print("="*100)
    
    exclude_pix = True  # Excluir PIX/transferências da análise
    
    # Testar faturas CSV
    print("\n📄 TESTANDO FATURAS (CSV):\n")
    
    faturas = [
        '_arquivos_historicos/_csvs_historico/fatura-202508.csv',
        '_arquivos_historicos/_csvs_historico/fatura-202509.csv',
        '_arquivos_historicos/_csvs_historico/fatura_itau-202510.csv',
        '_arquivos_historicos/_csvs_historico/fatura_itau-202511.csv',
        '_arquivos_historicos/_csvs_historico/fatura_itau-202512.csv',
    ]
    
    total_geral = 0
    classified_geral = 0
    all_unclassified = []
    
    for fatura in faturas:
        if not Path(fatura).exists():
            continue
            
        result = tester.test_csv_file(fatura, exclude_pix=exclude_pix)
        if result:
            filename = Path(fatura).name
            total_geral += result['total']
            classified_geral += result['classified']
            
            print(f"📊 {filename:<35} {result['classified']:>3}/{result['total']:<3} ({result['percentage']:>5.1f}%)")
            
            # Coletar não classificados
            for detail in result['details']:
                if not detail['classified']:
                    all_unclassified.append({
                        'file': filename,
                        'estabelecimento': detail['estabelecimento']
                    })
    
    # Testar extrato XLS
    print("\n\n📄 TESTANDO EXTRATO (XLS):\n")
    
    extrato_path = '_arquivos_historicos/_csvs_historico/Extrato Conta Corrente-221220252316.xls'
    if Path(extrato_path).exists():
        if HAS_PANDAS:
            result = tester.test_xls_file(extrato_path, exclude_pix=exclude_pix)
            if result:
                filename = Path(extrato_path).name
                total_geral += result['total']
                classified_geral += result['classified']
                
                print(f"📊 {filename:<35} {result['classified']:>3}/{result['total']:<3} ({result['percentage']:>5.1f}%)")
                
                # Coletar não classificados
                for detail in result['details']:
                    if not detail['classified']:
                        all_unclassified.append({
                            'file': filename,
                            'estabelecimento': detail['estabelecimento']
                        })
        else:
            print("⚠️  pandas não instalado - instale com: pip install pandas openpyxl xlrd")
    else:
        print(f"⚠️  Arquivo não encontrado: {extrato_path}")
    
    # Estatísticas gerais
    percentage_geral = (classified_geral / total_geral * 100) if total_geral > 0 else 0
    
    print("\n" + "="*100)
    print(f"📈 RESUMO GERAL")
    if exclude_pix:
        print(f"⚠️  PIX/Transferências EXCLUÍDAS da análise (foco em compras/serviços)")
    print(f"\nTotal de transações: {total_geral}")
    print(f"✅ Classificadas: {classified_geral}/{total_geral} ({percentage_geral:.1f}%)")
    print(f"❌ Não classificadas: {total_geral - classified_geral}")
    
    # Top estabelecimentos não classificados
    if all_unclassified:
        from collections import Counter
        estabelecimentos_count = Counter([u['estabelecimento'] for u in all_unclassified])
        
        print(f"\n🔍 TOP 15 ESTABELECIMENTOS NÃO CLASSIFICADOS:")
        print("-" * 100)
        for estab, count in estabelecimentos_count.most_common(15):
            print(f"  [{count}x] {estab}")
    
    print("="*100)
    
    # Avaliação
    if percentage_geral >= 70:
        print(f"\n🎯 META ATINGIDA! (≥70%)")
    elif percentage_geral >= 60:
        print(f"\n✅ BOM! Próximo de 70%")
    elif percentage_geral >= 50:
        print(f"\n⚠️  REGULAR - Precisa melhorar")
    else:
        print(f"\n❌ BAIXO - Necessário ajustes críticos")


if __name__ == "__main__":
    main()
