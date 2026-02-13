#!/usr/bin/env python3
"""
Teste consolidado de cobertura da base genérica
Testa: Faturas CSV, Extrato XLS, MercadoPago XLSX
"""

import pandas as pd
import sqlite3
from pathlib import Path
from collections import Counter

class GenericClassifierTester:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """Carrega regras de classificação genérica do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT keywords, grupo, subgrupo, prioridade
            FROM generic_classification_rules
            WHERE ativo = 1
            ORDER BY prioridade DESC, id ASC
        """)
        
        rules = []
        for row in cursor.fetchall():
            rules.append({
                'keywords': [k.strip() for k in row[0].upper().split(',')],
                'grupo': row[1],
                'subgrupo': row[2],
                'prioridade': row[3]
            })
        
        conn.close()
        return rules
    
    def classify(self, estabelecimento: str):
        """Classifica uma transação baseado no estabelecimento"""
        search_text = estabelecimento.upper()
        
        for rule in self.rules:
            for keyword in rule['keywords']:
                if keyword in search_text:
                    return rule['grupo'], rule['subgrupo']
        
        return None, None
    
    def test_file(self, file_path: str, exclude_pix: bool = True):
        """Testa um arquivo (detecta formato automaticamente)"""
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠️  Arquivo não encontrado: {file_path}")
            return None
        
        # Detectar tipo de arquivo
        if path.suffix == '.xlsx' and 'MP' in path.name:
            return self._test_mercadopago(file_path, exclude_pix)
        elif path.suffix == '.xls' and 'Extrato' in path.name:
            return self._test_extrato_itau(file_path, exclude_pix)
        elif path.suffix == '.csv':
            return self._test_fatura_csv(file_path, exclude_pix)
        else:
            print(f"⚠️  Formato não reconhecido: {file_path}")
            return None
    
    def _test_fatura_csv(self, file_path: str, exclude_pix: bool):
        """Testa fatura CSV (Itaú)"""
        import csv
        
        transactions = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lanc = row.get('lançamento') or row.get('Lançamento') or ''
                if not lanc:
                    continue
                
                if exclude_pix and any(k in lanc.upper() for k in ['PIX', 'TRANSF', 'TED', 'DOC']):
                    continue
                
                transactions.append(lanc)
        
        return self._classify_and_report(transactions, Path(file_path).name)
    
    def _test_extrato_itau(self, file_path: str, exclude_pix: bool):
        """Testa extrato XLS (Itaú)"""
        df = pd.read_excel(file_path, skiprows=7)
        
        # Tentar diferentes formatos de cabeçalho
        for skip in [7, 8]:
            df_temp = pd.read_excel(file_path, skiprows=skip)
            if 'lançamento' in [c.lower() for c in df_temp.columns]:
                df = df_temp
                break
        
        transactions = []
        col_lanc = None
        for col in df.columns:
            if 'lançamento' in str(col).lower() or 'lancamento' in str(col).lower():
                col_lanc = col
                break
        
        if not col_lanc:
            return None
        
        for _, row in df.iterrows():
            lanc = str(row[col_lanc]) if pd.notna(row[col_lanc]) else ''
            if not lanc or lanc == 'nan':
                continue
            if lanc.upper() in ['LANÇAMENTOS', 'SALDO ANTERIOR', 'SALDO FINAL']:
                continue
            if 'SALDO TOTAL' in lanc.upper():
                continue
            
            if exclude_pix and any(k in lanc.upper() for k in ['PIX', 'TRANSF', 'TED', 'DOC']):
                continue
            
            transactions.append(lanc)
        
        return self._classify_and_report(transactions, Path(file_path).name)
    
    def _test_mercadopago(self, file_path: str, exclude_pix: bool):
        """Testa MercadoPago XLSX"""
        df = pd.read_excel(file_path, skiprows=2)
        df.columns = ['date', 'transaction_type', 'reference_id', 'amount', 'balance']
        df = df[1:].reset_index(drop=True)  # Remover cabeçalho duplicado
        
        transactions = []
        for _, row in df.iterrows():
            lanc = str(row['transaction_type']) if pd.notna(row['transaction_type']) else ''
            if not lanc or lanc == 'nan':
                continue
            
            # Skip transferências e reservas internas (como no processor)
            if any(k in lanc.upper() for k in ['PIX RECEBIDA', 'PIX ENVIADA', 'TRANSFERENCIA RECEBIDA', 'TRANSFERENCIA ENVIADA', 'DINHEIRO RESERVADO', 'DINHEIRO RETIRADO', 'RESERVA POR']):
                continue
            
            transactions.append(lanc)
        
        return self._classify_and_report(transactions, Path(file_path).name)
    
    def _classify_and_report(self, transactions: list, filename: str):
        """Classifica transações e gera relatório"""
        classified = 0
        unclassified = []
        
        for lanc in transactions:
            grupo, subgrupo = self.classify(lanc)
            if grupo:
                classified += 1
            else:
                unclassified.append(lanc)
        
        total = len(transactions)
        percentage = (classified / total * 100) if total > 0 else 0
        
        return {
            'filename': filename,
            'total': total,
            'classified': classified,
            'percentage': percentage,
            'unclassified': unclassified
        }


def main():
    """Função principal"""
    db_path = "app_dev/backend/database/financas_dev.db"
    
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    tester = GenericClassifierTester(db_path)
    
    print(f"✅ {len(tester.rules)} regras carregadas\n")
    print("="*100)
    print("🎯 TESTE CONSOLIDADO - BASE GENÉRICA (SEM PIX/TRANSFERÊNCIAS)")
    print("="*100)
    
    files_to_test = [
        ('📄 FATURAS CSV (Itaú):', [
            '_arquivos_historicos/_csvs_historico/fatura-202508.csv',
            '_arquivos_historicos/_csvs_historico/fatura-202509.csv',
            '_arquivos_historicos/_csvs_historico/fatura_itau-202510.csv',
            '_arquivos_historicos/_csvs_historico/fatura_itau-202511.csv',
            '_arquivos_historicos/_csvs_historico/fatura_itau-202512.csv',
        ]),
        ('📄 EXTRATO XLS (Itaú):', [
            '_arquivos_historicos/_csvs_historico/Extrato Conta Corrente-221220252316.xls',
        ]),
        ('📄 MERCADOPAGO XLSX:', [
            '_arquivos_historicos/_csvs_historico/MP202504.xlsx',
        ]),
    ]
    
    grand_total = 0
    grand_classified = 0
    all_results = []
    
    for section_name, files in files_to_test:
        print(f"\n{section_name}\n")
        
        for file_path in files:
            result = tester.test_file(file_path, exclude_pix=True)
            if result:
                print(f"  {result['filename']:<45} {result['classified']:>3}/{result['total']:<3} ({result['percentage']:>5.1f}%)")
                grand_total += result['total']
                grand_classified += result['classified']
                all_results.append(result)
    
    # Resumo final
    grand_percentage = (grand_classified / grand_total * 100) if grand_total > 0 else 0
    
    print("\n" + "="*100)
    print(f"📊 RESUMO CONSOLIDADO\n")
    print(f"  Total de transações: {grand_total}")
    print(f"  ✅ Classificadas: {grand_classified}/{grand_total} ({grand_percentage:.1f}%)")
    print(f"  ❌ Não classificadas: {grand_total - grand_classified}")
    
    # Top não classificados geral
    all_unclassified = []
    for result in all_results:
        all_unclassified.extend(result['unclassified'])
    
    if all_unclassified:
        counter = Counter(all_unclassified)
        print(f"\n🔍 TOP 10 TRANSAÇÕES NÃO CLASSIFICADAS (GERAL):")
        print("-" * 100)
        for lanc, count in counter.most_common(10):
            print(f"  [{count}x] {lanc[:80]}")
    
    print("="*100)
    
    # Avaliação
    if grand_percentage >= 70:
        print(f"\n🎯 META ATINGIDA! (≥70%)")
    elif grand_percentage >= 60:
        print(f"\n✅ BOM! Próximo de 70%")
    else:
        print(f"\n⚠️  Precisa melhorar")


if __name__ == "__main__":
    main()
