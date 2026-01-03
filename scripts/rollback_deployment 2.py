#!/usr/bin/env python3
"""
Script de Rollback: Restaura backup anterior de app/

Uso:
    python scripts/rollback_deployment.py --list                 # Lista backups disponíveis
    python scripts/rollback_deployment.py --restore <filename>   # Restaura backup específico
    python scripts/rollback_deployment.py                        # Restaura backup mais recente
"""

import os
import sys
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Cores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_step(msg):
    print(f"\n{Colors.BOLD}{msg}{Colors.END}")

class RollbackManager:
    """Gerencia rollback de deploys"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_prod = project_root / 'app'
        self.backups_dir = project_root / 'backups_local'
        
        if not self.backups_dir.exists():
            print_error(f"Diretório de backups não encontrado: {self.backups_dir}")
            sys.exit(1)
    
    def list_backups(self) -> List[Tuple[Path, datetime, int]]:
        """Lista todos os backups disponíveis"""
        backups = []
        
        for backup_file in self.backups_dir.glob('app_backup_*.tar.gz'):
            # Extrai timestamp do nome
            filename = backup_file.name
            try:
                # app_backup_20251228_143025.tar.gz
                timestamp_str = filename.replace('app_backup_', '').replace('.tar.gz', '')
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                size = backup_file.stat().st_size
                backups.append((backup_file, timestamp, size))
            except ValueError:
                continue
        
        # Ordena por data (mais recente primeiro)
        backups.sort(key=lambda x: x[1], reverse=True)
        return backups
    
    def print_backups_list(self, backups: List[Tuple[Path, datetime, int]]):
        """Imprime lista formatada de backups"""
        print_step("📦 Backups disponíveis:")
        
        if not backups:
            print_warning("Nenhum backup encontrado!")
            return
        
        for i, (backup_path, timestamp, size) in enumerate(backups, 1):
            size_mb = size / (1024 * 1024)
            date_str = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            
            marker = "🌟" if i == 1 else "  "
            print(f"{marker} [{i}] {backup_path.name}")
            print(f"      Data: {date_str} | Tamanho: {size_mb:.2f} MB")
    
    def get_backup_by_name(self, filename: str) -> Path:
        """Obtém caminho do backup por nome do arquivo"""
        backup_path = self.backups_dir / filename
        
        if not backup_path.exists():
            print_error(f"Backup não encontrado: {filename}")
            sys.exit(1)
        
        return backup_path
    
    def restore_backup(self, backup_path: Path):
        """Restaura backup especificado"""
        print_step(f"♻️  Restaurando backup: {backup_path.name}")
        
        # Confirmação
        print(f"\n{Colors.YELLOW}⚠️  ATENÇÃO:{Colors.END} Esta ação vai substituir o app/ atual!")
        print(f"{Colors.BOLD}❓ Deseja continuar?{Colors.END} (sim/não): ", end='')
        response = input().strip().lower()
        
        if response not in ['sim', 's', 'yes', 'y']:
            print_warning("Rollback cancelado pelo usuário")
            sys.exit(0)
        
        # Cria backup do estado atual antes de restaurar (segurança extra)
        if self.app_prod.exists():
            print_info("Criando backup de segurança do estado atual...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_backup = self.backups_dir / f"app_before_rollback_{timestamp}.tar.gz"
            
            with tarfile.open(safety_backup, "w:gz") as tar:
                tar.add(self.app_prod, arcname='app')
            
            print_success(f"Backup de segurança criado: {safety_backup.name}")
        
        # Remove app/ atual
        if self.app_prod.exists():
            shutil.rmtree(self.app_prod)
            print_info("app/ removido")
        
        # Extrai backup
        print_info("Extraindo backup...")
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(self.project_root)
        
        print_success("Backup restaurado com sucesso!")
        
        # Procura backup do banco correspondente
        self.restore_database_backup(backup_path)
        
        print_step("✅ Rollback concluído!")
        print_info("Aplicação restaurada. Reinicie o servidor se necessário.")
    
    def restore_database_backup(self, app_backup_path: Path):
        """Restaura backup do banco de dados correspondente"""
        # Extrai timestamp do backup de app
        filename = app_backup_path.name
        timestamp_str = filename.replace('app_backup_', '').replace('.tar.gz', '')
        
        # Procura backup do banco com mesmo timestamp
        db_backup = self.backups_dir / f"financas_backup_{timestamp_str}.db"
        
        if not db_backup.exists():
            print_warning(f"Backup do banco não encontrado: {db_backup.name}")
            print_info("Banco de dados não foi restaurado")
            return
        
        print_info("Restaurando banco de dados...")
        db_file = self.project_root / 'financas.db'
        
        # Backup do banco atual
        if db_file.exists():
            safety_db = self.project_root / f"financas_before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_file, safety_db)
            print_info(f"Backup de segurança do banco: {safety_db.name}")
        
        # Restaura banco
        shutil.copy2(db_backup, db_file)
        print_success("Banco de dados restaurado!")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback de deploy')
    parser.add_argument('--list', action='store_true', help='Lista todos os backups disponíveis')
    parser.add_argument('--restore', type=str, help='Nome do arquivo de backup para restaurar')
    args = parser.parse_args()
    
    # Root do projeto
    project_root = Path(__file__).parent.parent
    
    # Manager
    rollback_manager = RollbackManager(project_root)
    
    # Lista backups
    backups = rollback_manager.list_backups()
    
    if args.list:
        rollback_manager.print_backups_list(backups)
        sys.exit(0)
    
    # Restaura backup específico
    if args.restore:
        backup_path = rollback_manager.get_backup_by_name(args.restore)
        rollback_manager.restore_backup(backup_path)
        sys.exit(0)
    
    # Sem argumentos: restaura mais recente
    if not backups:
        print_error("Nenhum backup disponível!")
        sys.exit(1)
    
    most_recent = backups[0][0]
    print_info(f"Restaurando backup mais recente: {most_recent.name}")
    rollback_manager.restore_backup(most_recent)

if __name__ == '__main__':
    main()
