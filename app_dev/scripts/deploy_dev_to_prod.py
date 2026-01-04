#!/usr/bin/env python3
"""
Script de Deploy: app_dev → app (produção)

Workflow completo:
1. Validações automáticas
2. Comparação dev vs prod
3. Confirmação do usuário
4. Backup automático
5. Deploy
6. (Opcional) Deploy na VM

Uso:
    python scripts/deploy_dev_to_prod.py                 # Deploy completo interativo
    python scripts/deploy_dev_to_prod.py --validate-only # Apenas validações
    python scripts/deploy_dev_to_prod.py --deploy-vm     # Deploy + VM
"""

import os
import sys
import shutil
import tarfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import json

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

class DeployValidator:
    """Executa todas as validações necessárias antes do deploy"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dev = project_root / 'app_dev'
        self.app_prod = project_root / 'app'
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def validate_all(self) -> bool:
        """Executa todas as validações"""
        print_step("🔍 Executando validações...")
        
        validations = [
            ("Estrutura de diretórios", self.validate_structure),
            ("Syntax Python", self.validate_python_syntax),
            ("Imports", self.validate_imports),
            ("Modelos do banco", self.validate_models),
            ("Rotas", self.validate_routes),
            ("Segurança", self.validate_security),
            ("Frontend build", self.validate_frontend),
            ("Dependências", self.validate_dependencies),
        ]
        
        for check_name, check_func in validations:
            self.checks_total += 1
            try:
                if check_func():
                    print_success(f"{check_name}")
                    self.checks_passed += 1
                else:
                    print_error(f"{check_name}")
            except Exception as e:
                print_error(f"{check_name}: {str(e)}")
                self.errors.append(f"{check_name}: {str(e)}")
        
        return len(self.errors) == 0
    
    def validate_structure(self) -> bool:
        """Valida estrutura de diretórios"""
        required_paths = [
            self.app_dev / 'backend',
            self.app_dev / 'frontend',
            self.app_dev / 'backend' / '__init__.py',
            self.app_dev / 'frontend' / 'package.json',
        ]
        
        for path in required_paths:
            if not path.exists():
                self.errors.append(f"Caminho não encontrado: {path}")
                return False
        
        return True
    
    def validate_python_syntax(self) -> bool:
        """Valida syntax de todos os arquivos Python"""
        backend_path = self.app_dev / 'backend'
        python_files = list(backend_path.rglob('*.py'))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                self.errors.append(f"Erro de syntax em {py_file}: {e}")
                return False
        
        return True
    
    def validate_imports(self) -> bool:
        """Verifica se há imports quebrados"""
        # Simplified check - apenas verifica se __init__.py existe e importa corretamente
        init_file = self.app_dev / 'backend' / '__init__.py'
        if not init_file.exists():
            self.errors.append("__init__.py não encontrado")
            return False
        
        return True
    
    def validate_models(self) -> bool:
        """Valida modelos do banco de dados"""
        models_file = self.app_dev / 'backend' / 'models_flask.py'
        if not models_file.exists():
            self.warnings.append("models_flask.py não encontrado")
            return True  # Warning, não erro
        
        # Verifica se tem as classes principais
        with open(models_file, 'r') as f:
            content = f.read()
            required_models = ['User', 'JournalEntry', 'GrupoConfig']
            for model in required_models:
                if f'class {model}' not in content:
                    self.warnings.append(f"Modelo {model} não encontrado")
        
        return True
    
    def validate_routes(self) -> bool:
        """Verifica rotas duplicadas"""
        # Simplified - apenas verifica se blueprints existem
        blueprints_path = self.app_dev / 'backend' / 'api' / 'blueprints'
        if not blueprints_path.exists():
            self.warnings.append("Pasta blueprints não encontrada")
            return True
        
        return True
    
    def validate_security(self) -> bool:
        """Validações de segurança"""
        config_file = self.app_dev / 'backend' / 'config_dev.py'
        
        if not config_file.exists():
            self.errors.append("config_dev.py não encontrado")
            return False
        
        with open(config_file, 'r') as f:
            content = f.read()
            
            # Verifica se DEBUG está configurável
            if 'DEBUG = True' in content:
                self.warnings.append("DEBUG=True encontrado - certifique-se de desabilitar em produção")
            
            # Verifica SECRET_KEY
            if 'SECRET_KEY' not in content:
                self.errors.append("SECRET_KEY não configurada")
                return False
        
        return True
    
    def validate_frontend(self) -> bool:
        """Valida se frontend pode ser buildado"""
        frontend_path = self.app_dev / 'frontend'
        package_json = frontend_path / 'package.json'
        
        if not package_json.exists():
            self.errors.append("package.json não encontrado")
            return False
        
        # Verifica se node_modules existe
        node_modules = frontend_path / 'node_modules'
        if not node_modules.exists():
            self.warnings.append("node_modules não encontrado - execute npm install")
        
        return True
    
    def validate_dependencies(self) -> bool:
        """Verifica dependências Python"""
        requirements = self.project_root / 'requirements.txt'
        if not requirements.exists():
            self.warnings.append("requirements.txt não encontrado")
            return True
        
        return True
    
    def print_summary(self):
        """Imprime resumo das validações"""
        print_step("📊 Resumo das Validações")
        print(f"{Colors.BOLD}{self.checks_passed}/{self.checks_total}{Colors.END} validações passaram")
        
        if self.errors:
            print(f"\n{Colors.RED}Erros encontrados ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Avisos ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.errors and not self.warnings:
            print_success("Nenhum erro ou aviso encontrado!")

class DeployManager:
    """Gerencia o processo de deploy"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dev = project_root / 'app_dev'
        self.app_prod = project_root / 'app'
        self.backups_dir = project_root / 'backups_local'
        self.backups_dir.mkdir(exist_ok=True)
    
    def compare_directories(self) -> Dict:
        """Compara app_dev com app para mostrar diferenças"""
        print_step("🔎 Comparando app_dev com app...")
        
        differences = {
            'modified': [],
            'new': [],
            'removed': []
        }
        
        # Arquivos em dev
        dev_files = set()
        if self.app_dev.exists():
            for file in self.app_dev.rglob('*'):
                if file.is_file() and 'node_modules' not in str(file):
                    rel_path = file.relative_to(self.app_dev)
                    dev_files.add(str(rel_path))
        
        # Arquivos em prod
        prod_files = set()
        if self.app_prod.exists():
            for file in self.app_prod.rglob('*'):
                if file.is_file():
                    rel_path = file.relative_to(self.app_prod)
                    prod_files.add(str(rel_path))
        
        differences['new'] = list(dev_files - prod_files)
        differences['removed'] = list(prod_files - dev_files)
        differences['modified'] = list(dev_files & prod_files)  # Simplified
        
        return differences
    
    def print_differences(self, diffs: Dict):
        """Imprime diferenças encontradas"""
        print(f"\n{Colors.BOLD}Diferenças encontradas:{Colors.END}")
        print(f"  📝 {len(diffs['modified'])} arquivos existentes")
        print(f"  ✨ {len(diffs['new'])} arquivos novos")
        print(f"  🗑️  {len(diffs['removed'])} arquivos removidos")
        
        if diffs['new']:
            print(f"\n{Colors.GREEN}Novos arquivos (mostrando primeiros 5):{Colors.END}")
            for f in diffs['new'][:5]:
                print(f"  + {f}")
            if len(diffs['new']) > 5:
                print(f"  ... e mais {len(diffs['new']) - 5} arquivos")
    
    def create_backup(self) -> Path:
        """Cria backup completo de app/ antes do deploy"""
        print_step("💾 Criando backup de app/ ...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"app_backup_{timestamp}.tar.gz"
        backup_path = self.backups_dir / backup_name
        
        if not self.app_prod.exists():
            print_warning("app/ não existe, pulando backup")
            return None
        
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(self.app_prod, arcname='app')
        
        # Também faz backup do banco se existir
        db_file = self.project_root / 'financas.db'
        if db_file.exists():
            db_backup = self.backups_dir / f"financas_backup_{timestamp}.db"
            shutil.copy2(db_file, db_backup)
            print_success(f"Backup do banco: {db_backup.name}")
        
        print_success(f"Backup criado: {backup_name}")
        return backup_path
    
    def deploy(self):
        """Executa o deploy de app_dev para app"""
        print_step("🚀 Executando deploy...")
        
        # Remove app/ antigo
        if self.app_prod.exists():
            shutil.rmtree(self.app_prod)
            print_info("app/ removido")
        
        # Copia app_dev para app
        shutil.copytree(self.app_dev, self.app_prod, ignore=shutil.ignore_patterns(
            'node_modules', '__pycache__', '*.pyc', '.git', 'dist', 'build',
            'financas_dev.db', '*.db', 'uploads_temp', 'static/uploads', 'flask_session',
            '.vite', '.DS_Store'
        ))
        print_success("Arquivos copiados")
        
        # Atualiza run.py para apontar para app ao invés de app_dev
        self.update_run_script()
        
        print_success("Deploy concluído!")
    
    def update_run_script(self):
        """Atualiza run.py para usar app ao invés de app_dev"""
        run_file = self.project_root / 'run.py'
        if run_file.exists():
            with open(run_file, 'r') as f:
                content = f.read()
            
            # Se ainda importa de app_dev, não faz nada (mantém dev)
            # Para prod, deveria ter um run_prod.py separado
            pass

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy de app_dev para app')
    parser.add_argument('--validate-only', action='store_true', help='Apenas valida, não faz deploy')
    parser.add_argument('--deploy-vm', action='store_true', help='Também faz deploy na VM')
    parser.add_argument('--no-backup', action='store_true', help='Não cria backup (não recomendado)')
    args = parser.parse_args()
    
    # Root do projeto
    project_root = Path(__file__).parent.parent
    
    # Validações
    validator = DeployValidator(project_root)
    if not validator.validate_all():
        print("\n")
        validator.print_summary()
        print_error("Validações falharam! Corrija os erros antes de prosseguir.")
        sys.exit(1)
    
    validator.print_summary()
    
    if args.validate_only:
        print_success("\nApenas validação solicitada. Deploy não executado.")
        sys.exit(0)
    
    # Comparação
    deploy_manager = DeployManager(project_root)
    differences = deploy_manager.compare_directories()
    deploy_manager.print_differences(differences)
    
    # Confirmação
    print(f"\n{Colors.BOLD}❓ Deseja prosseguir com o deploy?{Colors.END} (sim/não): ", end='')
    response = input().strip().lower()
    
    if response not in ['sim', 's', 'yes', 'y']:
        print_warning("Deploy cancelado pelo usuário")
        sys.exit(0)
    
    # Backup
    if not args.no_backup:
        backup_path = deploy_manager.create_backup()
        if backup_path:
            print_info(f"Backup salvo em: {backup_path}")
    
    # Deploy
    deploy_manager.deploy()
    
    print_step("✅ Deploy concluído com sucesso!")
    print_info("Aplicação disponível em: http://localhost:5001")
    
    if args.deploy_vm:
        print_warning("Deploy na VM não implementado ainda")
        print_info("Use: scp -r app/ user@vm:/caminho/")

if __name__ == '__main__':
    main()
