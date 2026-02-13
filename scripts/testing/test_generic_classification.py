#!/usr/bin/env python3
"""
Script de Teste - Base Genérica de Classificação

Processa uma fatura real e mostra:
1. Quantas transações foram classificadas automaticamente
2. Quais estabelecimentos NÃO foram classificados
3. Taxa de cobertura (%)
4. Sugestões de novas regras baseadas em gaps

Uso:
    python test_generic_classification.py fatura-202512.csv
"""

import sys
import csv
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class GenericRule:
    """Representa uma regra de classificação genérica"""
    id: int
    nome_regra: str
    keywords: str
    grupo: str
    subgrupo: str
    tipo_gasto: str
    prioridade: int
    case_sensitive: bool
    match_completo: bool
    
    def get_keywords_list(self) -> List[str]:
        """Retorna lista de keywords"""
        return [k.strip().upper() for k in self.keywords.split(',')]
    
    def matches(self, text: str) -> bool:
        """Verifica se o texto match com alguma keyword"""
        search_text = text if self.case_sensitive else text.upper()
        
        for keyword in self.get_keywords_list():
            if self.match_completo:
                if keyword == search_text:
                    return True
            else:
                if keyword in search_text:
                    return True
        return False


@dataclass
class Transaction:
    """Representa uma transação da fatura"""
    data: str
    estabelecimento: str
    valor: float
    grupo_matched: str = ""
    subgrupo_matched: str = ""
    rule_matched: str = ""
    prioridade_matched: int = 0


class GenericClassificationTester:
    """Testa a base genérica de classificação"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rules: List[GenericRule] = []
        self.load_rules()
    
    def load_rules(self):
        """Carrega regras ativas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_regra, keywords, grupo, subgrupo, tipo_gasto,
                   prioridade, case_sensitive, match_completo
            FROM generic_classification_rules
            WHERE ativo = 1
            ORDER BY prioridade DESC, id ASC
        """)
        
        for row in cursor.fetchall():
            self.rules.append(GenericRule(
                id=row[0],
                nome_regra=row[1],
                keywords=row[2],
                grupo=row[3],
                subgrupo=row[4],
                tipo_gasto=row[5],
                prioridade=row[6],
                case_sensitive=bool(row[7]),
                match_completo=bool(row[8])
            ))
        
        conn.close()
        print(f"✅ {len(self.rules)} regras carregadas do banco\n")
    
    def classify_transaction(self, estabelecimento: str) -> Tuple[str, str, str, int]:
        """
        Classifica uma transação baseado no estabelecimento
        
        Returns:
            (grupo, subgrupo, nome_regra, prioridade)
        """
        # Testar regras por ordem de prioridade
        for rule in self.rules:
            if rule.matches(estabelecimento):
                return (
                    rule.grupo,
                    rule.subgrupo,
                    rule.nome_regra,
                    rule.prioridade
                )
        
        return ("", "", "", 0)
    
    def load_csv_fatura(self, csv_path: str) -> List[Transaction]:
        """Carrega transações de um CSV de fatura"""
        transactions = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Tentar detectar formato
            first_line = f.readline()
            f.seek(0)
            
            # Detectar delimitador
            delimiter = ';' if ';' in first_line else ','
            
            # CSV com header (detectar colunas)
            if any(col in first_line.upper() for col in ['DATA', 'ESTABELECIMENTO', 'VALOR', 'LANÇAMENTO', 'LANCAMENTO']):
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    try:
                        # Tentar diferentes nomes de colunas
                        estabelecimento = (
                            row.get('ESTABELECIMENTO') or 
                            row.get('Estabelecimento') or
                            row.get('lançamento') or
                            row.get('lancamento') or
                            row.get('LANÇAMENTO') or
                            row.get('LANCAMENTO') or
                            ''
                        )
                        
                        data_value = (
                            row.get('DATA') or
                            row.get('Data') or
                            row.get('data') or
                            ''
                        )
                        
                        valor_str = (
                            row.get('VALOR') or 
                            row.get('Valor') or
                            row.get('valor') or
                            '0'
                        )
                        
                        # Normalizar valor
                        valor_str = valor_str.replace('.', '').replace(',', '.')
                        valor = abs(float(valor_str))  # Usar valor absoluto
                        
                        if estabelecimento:
                            transactions.append(Transaction(
                                data=data_value,
                                estabelecimento=estabelecimento,
                                valor=valor
                            ))
                    except (ValueError, KeyError) as e:
                        print(f"⚠️ Linha ignorada: {e}")
                        continue
            else:
                # Formato genérico CSV sem header
                reader = csv.reader(f, delimiter=delimiter)
                next(reader, None)  # Skip first line
                for row in reader:
                    if len(row) >= 3:
                        try:
                            valor_str = row[2].replace('.', '').replace(',', '.')
                            transactions.append(Transaction(
                                data=row[0],
                                estabelecimento=row[1],
                                valor=abs(float(valor_str))
                            ))
                        except (ValueError, IndexError):
                            continue
        
        return transactions
    
    def test_file(self, csv_path: str):
        """Testa um arquivo CSV de fatura"""
        print(f"📄 Processando: {Path(csv_path).name}")
        print("=" * 80)
        
        # Carregar transações
        transactions = self.load_csv_fatura(csv_path)
        print(f"\n📊 Total de transações: {len(transactions)}")
        
        if not transactions:
            print("❌ Nenhuma transação carregada! Verifique o formato do CSV.")
            return
        
        # Classificar todas
        classified_count = 0
        unclassified = []
        
        for txn in transactions:
            grupo, subgrupo, rule, prioridade = self.classify_transaction(txn.estabelecimento)
            
            if grupo:
                classified_count += 1
                txn.grupo_matched = grupo
                txn.subgrupo_matched = subgrupo
                txn.rule_matched = rule
                txn.prioridade_matched = prioridade
            else:
                unclassified.append(txn)
        
        # Calcular taxa de cobertura
        coverage = (classified_count / len(transactions)) * 100
        
        # Relatório
        print(f"\n{'='*80}")
        print(f"✅ Classificadas automaticamente: {classified_count}/{len(transactions)} ({coverage:.1f}%)")
        print(f"❌ Não classificadas: {len(unclassified)}/{len(transactions)} ({100-coverage:.1f}%)")
        print(f"{'='*80}\n")
        
        # Mostrar não classificadas
        if unclassified:
            print("🔍 TRANSAÇÕES NÃO CLASSIFICADAS:\n")
            
            # Agrupar por estabelecimento
            estab_counter = Counter([t.estabelecimento for t in unclassified])
            
            print(f"{'Qtd':<5} {'Valor Total':<15} {'Estabelecimento':<60}")
            print("-" * 80)
            
            for estab, count in estab_counter.most_common(20):
                # Calcular valor total
                total = sum(t.valor for t in unclassified if t.estabelecimento == estab)
                print(f"{count:<5} R$ {total:>10,.2f}   {estab[:57]}")
            
            if len(estab_counter) > 20:
                print(f"\n... e mais {len(estab_counter) - 20} estabelecimentos únicos")
        
        # Sugestões de novas regras
        print(f"\n\n{'='*80}")
        print("💡 SUGESTÕES DE NOVAS REGRAS (baseado em estabelecimentos não classificados):\n")
        
        if unclassified:
            # Agrupar por padrões comuns
            suggestions = self.generate_suggestions(unclassified)
            
            for i, (pattern, count, sample) in enumerate(suggestions[:10], 1):
                print(f"{i}. Padrão: '{pattern}' ({count} ocorrências)")
                print(f"   Exemplo: {sample}")
                print(f"   Sugestão: Adicionar keyword '{pattern}' em alguma categoria\n")
        else:
            print("✅ Nenhuma sugestão - todas as transações foram classificadas!")
        
        print(f"{'='*80}\n")
    
    def generate_suggestions(self, unclassified: List[Transaction]) -> List[Tuple[str, int, str]]:
        """Gera sugestões de novas regras baseado em padrões"""
        suggestions = []
        
        # Extrair palavras-chave comuns (primeiras 2-3 palavras)
        patterns = []
        for txn in unclassified:
            words = txn.estabelecimento.split()
            if len(words) >= 2:
                pattern = ' '.join(words[:2])
                patterns.append((pattern.upper(), txn.estabelecimento))
            elif len(words) == 1:
                patterns.append((words[0].upper(), txn.estabelecimento))
        
        # Contar padrões
        pattern_counter = Counter([p[0] for p in patterns])
        
        # Gerar sugestões (padrões com 2+ ocorrências)
        for pattern, count in pattern_counter.most_common(20):
            if count >= 2:
                # Pegar exemplo
                sample = next(p[1] for p in patterns if p[0] == pattern)
                suggestions.append((pattern, count, sample))
        
        return suggestions


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python test_generic_classification.py <arquivo.csv>")
        print("\nExemplo:")
        print("  python test_generic_classification.py fatura-202512.csv")
        print("\nArquivos disponíveis em:")
        print("  _arquivos_historicos/_csvs_historico/")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Validar arquivo
    if not Path(csv_path).exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        
        # Tentar buscar em _arquivos_historicos
        alt_path = Path("_arquivos_historicos/_csvs_historico") / Path(csv_path).name
        if alt_path.exists():
            csv_path = str(alt_path)
            print(f"✅ Arquivo encontrado em: {csv_path}\n")
        else:
            sys.exit(1)
    
    # Path do banco
    db_path = "app_dev/backend/database/financas_dev.db"
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        sys.exit(1)
    
    # Executar teste
    tester = GenericClassificationTester(db_path)
    tester.test_file(csv_path)


if __name__ == "__main__":
    main()
