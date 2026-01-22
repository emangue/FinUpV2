#!/usr/bin/env python3
"""
🔍 VALIDADOR DE VERSÃO DO PROJETO

Detecta a versão atual da pasta (V5, V6, etc.) e verifica se todos os 
arquivos de configuração estão usando a versão correta.

Uso:
    python check_version.py              # Apenas valida
    python check_version.py --fix        # Valida e corrige automaticamente
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def detect_current_version() -> str:
    """
    Detecta a versão atual baseada no nome da pasta
    
    Returns:
        str: Versão detectada (ex: "V5", "V6")
    """
    current_dir = Path.cwd()
    
    # Procura por padrão ProjetoFinancasVX
    match = re.search(r'ProjetoFinancas(V\d+)', str(current_dir))
    
    if match:
        return match.group(1)
    
    # Se não encontrar, tenta detectar pelo nome da pasta
    if 'ProjetoFinancas' in str(current_dir):
        print(f"{Colors.YELLOW}⚠️  Não consegui detectar a versão automaticamente{Colors.RESET}")
        print(f"    Diretório atual: {current_dir}")
        return None
    
    print(f"{Colors.RED}❌ Este script deve ser executado dentro de uma pasta ProjetoFinancasVX{Colors.RESET}")
    return None

def get_project_root() -> Path:
    """Retorna o path raiz do projeto"""
    current_dir = Path.cwd()
    
    # Procura pela pasta ProjetoFinancasVX
    for part in current_dir.parts:
        if 'ProjetoFinancas' in part and part.startswith('ProjetoFinancas'):
            idx = current_dir.parts.index(part)
            return Path(*current_dir.parts[:idx+1])
    
    return current_dir

def get_files_to_check() -> List[Tuple[Path, str]]:
    """
    Retorna lista de arquivos que devem ter referências à versão
    
    Returns:
        List[Tuple[Path, str]]: Lista de (caminho_arquivo, tipo)
    """
    root = get_project_root()
    
    files = [
        (root / "quick_start.sh", "bash"),
        (root / "quick_stop.sh", "bash"),
        (root / "backup_daily.sh", "bash"),
        (root / "app_dev" / "backend" / ".env", "env"),
        (root / "app_dev" / "backend" / "app" / "core" / "config.py", "python"),
        (root / "app_dev" / "frontend" / "src" / "lib" / "db-config.ts", "typescript"),
    ]
    
    return [(f, t) for f, t in files if f.exists()]

def check_file_version(file_path: Path, current_version: str) -> Dict:
    """
    Verifica se um arquivo tem referências a versões incorretas
    
    Args:
        file_path: Path do arquivo
        current_version: Versão atual (ex: "V5")
    
    Returns:
        Dict com informações sobre inconsistências encontradas
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procura por todas as versões mencionadas
    pattern = r'ProjetoFinancas(V\d+)'
    matches = re.finditer(pattern, content)
    
    wrong_versions = []
    for match in matches:
        found_version = match.group(1)
        if found_version != current_version:
            # Pega linha onde aparece
            line_num = content[:match.start()].count('\n') + 1
            line_content = content.split('\n')[line_num - 1].strip()
            
            wrong_versions.append({
                'version': found_version,
                'line': line_num,
                'content': line_content
            })
    
    return {
        'file': file_path,
        'issues': wrong_versions,
        'correct': len(wrong_versions) == 0
    }

def print_report(results: List[Dict], current_version: str):
    """Imprime relatório de validação"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}🔍 RELATÓRIO DE VALIDAÇÃO DE VERSÃO{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    print(f"📁 Versão atual detectada: {Colors.BLUE}{Colors.BOLD}{current_version}{Colors.RESET}\n")
    
    correct_files = [r for r in results if r['correct']]
    wrong_files = [r for r in results if not r['correct']]
    
    # Arquivos corretos
    if correct_files:
        print(f"{Colors.GREEN}✅ Arquivos corretos ({len(correct_files)}):{Colors.RESET}")
        for result in correct_files:
            rel_path = result['file'].relative_to(get_project_root())
            print(f"   ✓ {rel_path}")
        print()
    
    # Arquivos com problemas
    if wrong_files:
        print(f"{Colors.RED}❌ Arquivos com versão incorreta ({len(wrong_files)}):{Colors.RESET}\n")
        
        for result in wrong_files:
            rel_path = result['file'].relative_to(get_project_root())
            print(f"   {Colors.BOLD}{rel_path}{Colors.RESET}")
            
            for issue in result['issues']:
                print(f"      Linha {issue['line']}: Encontrado {Colors.YELLOW}{issue['version']}{Colors.RESET} (deveria ser {Colors.GREEN}{current_version}{Colors.RESET})")
                print(f"      {Colors.BLUE}└─{Colors.RESET} {issue['content'][:80]}...")
            print()
    
    # Resumo
    print(f"{Colors.BOLD}{'─'*70}{Colors.RESET}")
    print(f"📊 Resumo: {Colors.GREEN}{len(correct_files)} corretos{Colors.RESET}, {Colors.RED}{len(wrong_files)} incorretos{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    return len(wrong_files) == 0

def main():
    """Função principal"""
    print(f"\n{Colors.BOLD}🔍 Validador de Versão - Sistema de Finanças{Colors.RESET}\n")
    
    # Detecta versão atual
    current_version = detect_current_version()
    if not current_version:
        return 1
    
    print(f"✓ Versão detectada: {Colors.BLUE}{Colors.BOLD}{current_version}{Colors.RESET}")
    print(f"✓ Projeto raiz: {Colors.BLUE}{get_project_root()}{Colors.RESET}\n")
    
    # Obtém arquivos para verificar
    files_to_check = get_files_to_check()
    print(f"📝 Verificando {len(files_to_check)} arquivos...\n")
    
    # Verifica cada arquivo
    results = []
    for file_path, file_type in files_to_check:
        result = check_file_version(file_path, current_version)
        results.append(result)
    
    # Imprime relatório
    all_correct = print_report(results, current_version)
    
    # Mensagem final
    if all_correct:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Todas as referências estão corretas!{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}💡 Para corrigir automaticamente, execute:{Colors.RESET}")
        print(f"   {Colors.BLUE}python fix_version.py{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    exit(main())
