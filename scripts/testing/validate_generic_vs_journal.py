#!/usr/bin/env python3
"""
Script de Validação - Compara classificação genérica com journal_entries

Carrega transações já classificadas do journal_entries e testa se a
base genérica classificaria da mesma forma (assertividade).

Uso:
    python validate_generic_vs_journal.py
"""

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
    prioridade: int
    case_sensitive: bool
    match_completo: bool
    
    def get_keywords_list(self) -> List[str]:
        """Retorna lista de keywords"""
        keywords = [k.strip().upper() for k in self.keywords.split(',')]
        return keywords
    
    def matches(self, text: str) -> bool:
        """Verifica se o texto match com alguma keyword"""
        search_text = text if self.case_sensitive else text.upper()
        
        for keyword in self.get_keywords_list():
            if keyword in search_text:
                return True
        return False


class GenericVsJournalValidator:
    """Valida assertividade da base genérica"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rules: List[GenericRule] = []
        self.load_rules()
    
    def load_rules(self):
        """Carrega regras ativas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_regra, keywords, grupo, subgrupo,
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
                prioridade=row[5],
                case_sensitive=bool(row[6]),
                match_completo=bool(row[7])
            ))
        
        conn.close()
        print(f"✅ {len(self.rules)} regras carregadas\n")
    
    def classify_transaction(self, estabelecimento: str) -> Tuple[str, str]:
        """Classifica uma transação baseado no estabelecimento"""
        for rule in self.rules:
            if rule.matches(estabelecimento):
                return (rule.grupo, rule.subgrupo)
        return ("", "")
    
    def validate_sample(self, limit: int = 200):
        """Valida amostra de transações do journal_entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar amostra de transações já classificadas (user_id=1, ano 2025)
        cursor.execute("""
            SELECT Estabelecimento, Grupo, Subgrupo, COUNT(*) as qtd
            FROM journal_entries
            WHERE user_id = 1 
              AND Ano = 2025
              AND Grupo IS NOT NULL 
              AND Grupo != ''
              AND CategoriaGeral = 'Despesa'
            GROUP BY Estabelecimento, Grupo, Subgrupo
            ORDER BY qtd DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"📊 Analisando {len(results)} estabelecimentos únicos do journal_entries\n")
        print("=" * 100)
        
        # Estatísticas
        total = 0
        matches_grupo = 0
        matches_subgrupo = 0
        mismatches = []
        
        for estab, grupo_real, subgrupo_real, qtd in results:
            total += qtd
            
            # Classificar com base genérica
            grupo_pred, subgrupo_pred = self.classify_transaction(estab)
            
            if grupo_pred:
                if grupo_pred == grupo_real:
                    matches_grupo += qtd
                    if subgrupo_pred == subgrupo_real:
                        matches_subgrupo += qtd
                    else:
                        mismatches.append({
                            'estab': estab,
                            'qtd': qtd,
                            'real': f"{grupo_real} > {subgrupo_real}",
                            'pred': f"{grupo_pred} > {subgrupo_pred}",
                            'tipo': 'Grupo OK, Subgrupo diferente'
                        })
                else:
                    mismatches.append({
                        'estab': estab,
                        'qtd': qtd,
                        'real': f"{grupo_real} > {subgrupo_real}",
                        'pred': f"{grupo_pred} > {subgrupo_pred}",
                        'tipo': 'Grupo diferente'
                    })
            else:
                mismatches.append({
                    'estab': estab,
                    'qtd': qtd,
                    'real': f"{grupo_real} > {subgrupo_real}",
                    'pred': "NÃO CLASSIFICADO",
                    'tipo': 'Sem match'
                })
        
        # Relatório
        acc_grupo = (matches_grupo / total * 100) if total > 0 else 0
        acc_subgrupo = (matches_subgrupo / total * 100) if total > 0 else 0
        
        print(f"\n{'='*100}")
        print(f"📈 ASSERTIVIDADE DA BASE GENÉRICA\n")
        print(f"Total de transações analisadas: {total}")
        print(f"✅ Grupo correto: {matches_grupo}/{total} ({acc_grupo:.1f}%)")
        print(f"✅ Grupo + Subgrupo correto: {matches_subgrupo}/{total} ({acc_subgrupo:.1f}%)")
        print(f"❌ Diferenças: {total - matches_grupo} transações")
        print(f"{'='*100}\n")
        
        # Top divergências
        if mismatches:
            print(f"🔍 TOP 20 DIVERGÊNCIAS (ordenadas por quantidade):\n")
            print(f"{'Qtd':<5} {'Tipo':<30} {'Estabelecimento':<40}")
            print(f"      {'Real':<40} vs {'Previsto':<40}")
            print("-" * 100)
            
            mismatches_sorted = sorted(mismatches, key=lambda x: x['qtd'], reverse=True)
            for m in mismatches_sorted[:20]:
                print(f"{m['qtd']:<5} {m['tipo']:<30} {m['estab'][:37]}")
                print(f"      {m['real']:<40} vs {m['pred']:<40}\n")
        
        # Detalhar casos sem match para análise
        sem_match_casos = [m for m in mismatches if m['tipo'] == 'Sem match']
        if sem_match_casos:
            print(f"\n{'='*100}")
            print(f"🔍 DETALHAMENTO DOS {sum(c['qtd'] for c in sem_match_casos)} CASOS SEM MATCH ({len(sem_match_casos)} estabelecimentos distintos)")
            print(f"{'='*100}\n")
            
            # Agrupar por categoria real
            from collections import defaultdict
            por_categoria = defaultdict(list)
            for caso in sem_match_casos:
                por_categoria[caso['real']].append({
                    'estab': caso['estab'],
                    'qtd': caso['qtd']
                })
            
            # Mostrar top categorias não cobertas
            for categoria, casos in sorted(por_categoria.items(), key=lambda x: -sum(c['qtd'] for c in x[1]))[:15]:
                total_cat = sum(c['qtd'] for c in casos)
                print(f"📌 {categoria} ({total_cat} transações, {len(casos)} estabelecimentos):")
                for caso in sorted(casos, key=lambda x: -x['qtd'])[:8]:
                    print(f"   • [{caso['qtd']}x] {caso['estab']}")
                if len(casos) > 8:
                    print(f"   ... e mais {len(casos)-8} estabelecimentos")
                print()
        
        return acc_grupo, acc_subgrupo, mismatches


def main():
    """Função principal"""
    db_path = "app_dev/backend/database/financas_dev.db"
    
    if not Path(db_path).exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    validator = GenericVsJournalValidator(db_path)
    acc_grupo, acc_subgrupo, mismatches = validator.validate_sample(limit=200)
    
    print("\n" + "="*100)
    print("📊 RESUMO FINAL\n")
    print(f"✅ Assertividade Grupo: {acc_grupo:.1f}%")
    print(f"✅ Assertividade Grupo+Subgrupo: {acc_subgrupo:.1f}%")
    
    if acc_subgrupo >= 70:
        print(f"\n🎯 META ATINGIDA! (≥70%)")
    elif acc_subgrupo >= 60:
        print(f"\n✅ BOM! Próximo de 70%")
    else:
        print(f"\n⚠️  Ainda precisa de ajustes para atingir 70%")
    
    print("="*100)


if __name__ == "__main__":
    main()
