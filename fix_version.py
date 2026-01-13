#!/usr/bin/env python3
"""
🔧 CORRETOR AUTOMÁTICO DE VERSÃO DO PROJETO

Detecta a versão atual da pasta e atualiza TODOS os arquivos de configuração
para usar a versão correta.

Uso:
    python fix_version.py                    # Executa correção
    python fix_version.py --dry-run          # Mostra o que seria feito sem executar
    python fix_version.py --backup           # Cria backup antes de modificar

Arquivos que são atualizados:
    - quick_start.sh
    - quick_stop.sh  
    - backup_daily.sh
    - app_dev/backend/.env
    - app_dev/backend/app/core/config.py
    - app_dev/frontend/src/lib/db-config.ts
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def detect_current_version() -> str:
    """Detecta a versão atual baseada no nome da pasta"""
    current_dir = Path.cwd()
    match = re.search(r'ProjetoFinancas(V\d+)', str(current_dir))
    
    if match:
        return match.group(1)
    
    print(f"{Colors.RED}❌ Não consegui detectar a versão automaticamente{Colors.RESET}")
    print(f"    Diretório atual: {current_dir}")
    print(f"    Esperado: .../ProjetoFinancasVX/...")
    return None

def get_project_root() -> Path:
    """Retorna o path raiz do projeto"""
    current_dir = Path.cwd()
    
    for part in current_dir.parts:
        if 'ProjetoFinancas' in part and part.startswith('ProjetoFinancas'):
            idx = current_dir.parts.index(part)
            return Path(*current_dir.parts[:idx+1])
    
    return current_dir

def get_files_to_fix() -> List[Tuple[Path, str]]:
    """
    Retorna lista de arquivos que devem ser corrigidos
    
    Returns:
        List[Tuple[Path, str]]: Lista de (caminho_arquivo, descrição)
    """
    root = get_project_root()
    
    files = [
        (root / "quick_start.sh", "Script de inicialização"),
        (root / "quick_stop.sh", "Script de parada"),
        (root / "backup_daily.sh", "Script de backup"),
        (root / "app_dev" / "backend" / ".env", "Variáveis de ambiente"),
        (root / "app_dev" / "backend" / "app" / "core" / "config.py", "Config backend"),
        (root / "app_dev" / "frontend" / "src" / "lib" / "db-config.ts", "Config frontend"),
    ]
    
    return [(f, desc) for f, desc in files if f.exists()]

def backup_file(file_path: Path) -> Path:
    """
    Cria backup de um arquivo antes de modificá-lo
    
    Returns:
        Path: Caminho do arquivo de backup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f'.backup_{timestamp}{file_path.suffix}')
    shutil.copy2(file_path, backup_path)
    return backup_path

def fix_file_version(file_path: Path, current_version: str, dry_run: bool = False) -> Dict:
    """
    Corrige as referências de versão em um arquivo
    
    Args:
        file_path: Path do arquivo
        current_version: Versão atual correta (ex: "V5")
        dry_run: Se True, não modifica o arquivo
    
    Returns:
        Dict com informações sobre as modificações
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Padrão para encontrar ProjetoFinancasVX
    pattern = r'ProjetoFinancas(V\d+)'
    
    # Substitui TODAS as ocorrências por ProjetoFinancas{current_version}
    def replace_version(match):
        old_version = match.group(1)
        if old_version != current_version:
            return f'ProjetoFinancas{current_version}'
        return match.group(0)
    
    new_content, num_replacements = re.subn(pattern, replace_version, original_content)
    
    # Conta quantas versões diferentes foram encontradas
    old_versions = set(re.findall(r'ProjetoFinancas(V\d+)', original_content))
    old_versions.discard(current_version)
    
    if not dry_run and new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return {
        'file': file_path,
        'modified': new_content != original_content,
        'replacements': num_replacements,
        'old_versions': list(old_versions)
    }

def print_changes(results: List[Dict], current_version: str, dry_run: bool):
    """Imprime relatório das mudanças"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}🔧 {'SIMULAÇÃO DE ' if dry_run else ''}CORREÇÃO DE VERSÃO{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    print(f"📁 Versão correta: {Colors.GREEN}{Colors.BOLD}{current_version}{Colors.RESET}\n")
    
    modified_files = [r for r in results if r['modified']]
    unchanged_files = [r for r in results if not r['modified']]
    
    # Arquivos que foram/serão modificados
    if modified_files:
        print(f"{Colors.YELLOW}📝 Arquivos {'que seriam ' if dry_run else ''}modificados ({len(modified_files)}):{Colors.RESET}\n")
        
        for result in modified_files:
            rel_path = result['file'].relative_to(get_project_root())
            print(f"   {Colors.BOLD}{rel_path}{Colors.RESET}")
            
            if result['old_versions']:
                old_vers = ', '.join([f"{Colors.RED}{v}{Colors.RESET}" for v in result['old_versions']])
                print(f"      {old_vers} → {Colors.GREEN}{current_version}{Colors.RESET}")
            
            print(f"      {Colors.CYAN}└─{Colors.RESET} {result['replacements']} substituições")
            print()
    
    # Arquivos que já estavam corretos
    if unchanged_files:
        print(f"{Colors.GREEN}✅ Arquivos já corretos ({len(unchanged_files)}):{Colors.RESET}")
        for result in unchanged_files:
            rel_path = result['file'].relative_to(get_project_root())
            print(f"   ✓ {rel_path}")
        print()
    
    # Resumo
    print(f"{Colors.BOLD}{'─'*70}{Colors.RESET}")
    print(f"📊 Resumo: {Colors.YELLOW}{len(modified_files)} {'seriam ' if dry_run else ''}modificados{Colors.RESET}, {Colors.GREEN}{len(unchanged_files)} já corretos{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    return modified_files

def main():
    """Função principal"""
    dry_run = '--dry-run' in sys.argv
    create_backup = '--backup' in sys.argv
    
    print(f"\n{Colors.BOLD}🔧 Corretor Automático de Versão{Colors.RESET}")
    if dry_run:
        print(f"{Colors.YELLOW}   (Modo simulação - nenhum arquivo será modificado){Colors.RESET}")
    print()
    
    # Detecta versão atual
    current_version = detect_current_version()
    if not current_version:
        return 1
    
    print(f"✓ Versão detectada: {Colors.GREEN}{Colors.BOLD}{current_version}{Colors.RESET}")
    print(f"✓ Projeto raiz: {Colors.BLUE}{get_project_root()}{Colors.RESET}\n")
    
    # Obtém arquivos para corrigir
    files_to_fix = get_files_to_fix()
    print(f"📝 Verificando {len(files_to_fix)} arquivos...\n")
    
    # Cria backups se solicitado
    if create_backup and not dry_run:
        print(f"{Colors.CYAN}💾 Criando backups...{Colors.RESET}")
        for file_path, _ in files_to_fix:
            backup_path = backup_file(file_path)
            print(f"   ✓ {backup_path.name}")
        print()
    
    # Corrige cada arquivo
    results = []
    for file_path, description in files_to_fix:
        result = fix_file_version(file_path, current_version, dry_run)
        result['description'] = description
        results.append(result)
    
    # Imprime relatório
    modified = print_changes(results, current_version, dry_run)
    
    # Mensagem final
    if not modified:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Todas as referências já estão corretas!{Colors.RESET}\n")
        return 0
    
    if dry_run:
        print(f"{Colors.YELLOW}💡 Para aplicar as correções, execute sem --dry-run:{Colors.RESET}")
        print(f"   {Colors.BLUE}python fix_version.py{Colors.RESET}\n")
        return 0
    
    print(f"{Colors.GREEN}{Colors.BOLD}✅ Correções aplicadas com sucesso!{Colors.RESET}\n")
    print(f"{Colors.CYAN}💡 Recomendações:{Colors.RESET}")
    print(f"   1. Reinicie os servidores: {Colors.BLUE}./quick_stop.sh && ./quick_start.sh{Colors.RESET}")
    print(f"   2. Valide novamente: {Colors.BLUE}python check_version.py{Colors.RESET}\n")
    
    return 0

if __name__ == "__main__":
    exit(main())
