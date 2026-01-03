#!/usr/bin/env python3
"""
Script de Verificação: Separação Dev vs Prod

Verifica se dev e prod estão completamente isolados.
"""

import os
from pathlib import Path
from typing import List, Dict

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

def print_header(msg):
    print(f"\n{Colors.BOLD}{msg}{Colors.END}")

class SeparationChecker:
    """Verifica separação dev vs prod"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dev = project_root / 'app_dev'
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
    
    def check_all(self):
        """Executa todas as verificações"""
        print_header("🔍 Verificando Separação Dev vs Prod")
        
        checks = [
            ("Banco de dados separado", self.check_database),
            ("Uploads separados", self.check_uploads),
            ("Static separado", self.check_static),
            ("Sessions separadas", self.check_sessions),
            ("Configurações separadas", self.check_configs),
            ("Node_modules separado", self.check_node_modules),
            ("Utils separados", self.check_utils),
            ("Templates separados", self.check_templates),
            ("Run scripts separados", self.check_run_scripts),
        ]
        
        for check_name, check_func in checks:
            self.checks_total += 1
            try:
                if check_func():
                    print_success(check_name)
                    self.checks_passed += 1
                else:
                    print_error(check_name)
            except Exception as e:
                print_error(f"{check_name}: {str(e)}")
                self.errors.append(f"{check_name}: {str(e)}")
    
    def check_database(self) -> bool:
        """Verifica se bancos estão separados"""
        db_dev = self.app_dev / 'financas_dev.db'
        db_prod = self.project_root / 'app' / 'financas.db'
        
        if not db_dev.exists():
            self.errors.append("Banco dev não existe: app_dev/financas_dev.db")
            return False
        
        if not db_prod.exists():
            self.warnings.append("Banco prod não existe: app/financas.db")
        
        # Verifica que são arquivos diferentes
        if db_dev.exists() and db_prod.exists():
            dev_size = db_dev.stat().st_size
            prod_size = db_prod.stat().st_size
            print_info(f"   Dev: {dev_size / 1024:.1f} KB | Prod: {prod_size / 1024:.1f} KB")
        
        return True
    
    def check_uploads(self) -> bool:
        """Verifica se uploads estão separados"""
        uploads_dev = self.app_dev / 'uploads_temp'
        uploads_prod = self.project_root / 'app' / 'uploads_temp'
        
        if not uploads_dev.exists():
            self.errors.append("Pasta uploads_temp dev não existe")
            return False
        
        if not uploads_dev.is_dir():
            self.errors.append("uploads_temp dev não é um diretório")
            return False
        
        # Conta arquivos em cada pasta
        dev_files = len(list(uploads_dev.iterdir())) if uploads_dev.exists() else 0
        prod_files = len(list(uploads_prod.iterdir())) if uploads_prod.exists() else 0
        
        print_info(f"   Dev: {dev_files} arquivos | Prod: {prod_files} arquivos")
        
        return True
    
    def check_static(self) -> bool:
        """Verifica se static está separado"""
        static_dev = self.app_dev / 'static'
        static_prod = self.project_root / 'app' / 'static'
        
        if not static_dev.exists():
            self.errors.append("Pasta static dev não existe")
            return False
        
        if not static_dev.is_dir():
            self.errors.append("static dev não é um diretório")
            return False
        
        return True
    
    def check_sessions(self) -> bool:
        """Verifica se sessions estão separadas"""
        sessions_dev = self.app_dev / 'flask_session'
        sessions_prod = self.project_root / 'app' / 'flask_session'
        
        if not sessions_dev.exists():
            self.errors.append("Pasta flask_session dev não existe")
            return False
        
        if not sessions_dev.is_dir():
            self.errors.append("flask_session dev não é um diretório")
            return False
        
        return True
    
    def check_configs(self) -> bool:
        """Verifica se configs estão usando recursos separados"""
        config_dev = self.app_dev / 'backend' / 'config_dev.py'
        
        if not config_dev.exists():
            self.errors.append("config_dev.py não existe")
            return False
        
        with open(config_dev, 'r') as f:
            content = f.read()
            
            # Verifica se usa financas_dev.db
            if 'financas_dev.db' not in content:
                self.errors.append("config_dev.py não usa financas_dev.db")
                return False
            
            # Verifica se não usa financas.db do root
            if "dirname(__file__)), 'financas.db')" in content:
                self.errors.append("config_dev.py ainda usa financas.db do root!")
                return False
        
        return True
    
    def check_node_modules(self) -> bool:
        """Verifica se node_modules está dentro de app_dev"""
        node_modules_dev = self.app_dev / 'frontend' / 'node_modules'
        
        if not node_modules_dev.exists():
            self.warnings.append("node_modules não instalado (execute npm install)")
        
        return True
    
    def check_utils(self) -> bool:
        """Verifica se utils está dentro de cada app"""
        utils_dev = self.app_dev / 'backend' / 'utils'
        utils_prod = self.project_root / 'app' / 'utils'
        
        if not utils_dev.exists():
            self.errors.append("Pasta utils dev não existe em app_dev/backend/")
            return False
        
        if not utils_prod.exists():
            self.errors.append("Pasta utils prod não existe em app/")
            return False
        
        # Verifica arquivos importantes
        required_files = ['hasher.py', 'normalizer.py', 'deduplicator.py']
        for file in required_files:
            if not (utils_dev / file).exists():
                self.errors.append(f"app_dev/backend/utils/{file} não existe")
                return False
        
        # Verifica processors
        processors_dev = utils_dev / 'processors' / 'preprocessors'
        if not processors_dev.exists():
            self.errors.append("Processadores não existem em app_dev")
            return False
        
        # Conta processadores
        dev_processors = len(list(processors_dev.glob('*.py'))) if processors_dev.exists() else 0
        print_info(f"   Processadores dev: {dev_processors} arquivos")
        
        return True
    
    def check_templates(self) -> bool:
        """Verifica se templates está dentro de cada app"""
        templates_dev = self.app_dev / 'templates'
        templates_prod = self.project_root / 'app' / 'templates'
        
        if not templates_dev.exists():
            self.warnings.append("Templates dev não existe (pode não ser necessário para API)")
        
        if not templates_prod.exists():
            self.warnings.append("Templates prod não existe")
        
        return True
    
    def check_run_scripts(self) -> bool:
        """Verifica se cada app tem seu próprio run.py"""
        run_dev = self.app_dev / 'run.py'
        run_prod = self.project_root / 'app' / 'run.py'
        
        if not run_dev.exists():
            self.errors.append("run.py não existe em app_dev/")
            return False
        
        if not run_prod.exists():
            self.errors.append("run.py não existe em app/")
            return False
        
        return True
    
    def print_summary(self):
        """Imprime resumo"""
        print_header("📊 Resumo da Verificação")
        print(f"{Colors.BOLD}{self.checks_passed}/{self.checks_total}{Colors.END} verificações passaram")
        
        if self.errors:
            print(f"\n{Colors.RED}Erros encontrados ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Avisos ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.errors and not self.warnings:
            print_success("\n✅ Separação completa! Dev e Prod 100% isolados.")
        elif not self.errors:
            print_success("\n✅ Separação OK! Apenas avisos.")
        else:
            print_error("\n❌ Separação incompleta! Corrija os erros.")
        
        return len(self.errors) == 0

def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent
    
    checker = SeparationChecker(project_root)
    checker.check_all()
    success = checker.print_summary()
    
    if success:
        print_info("\n✅ Pronto para deploy!")
        return 0
    else:
        print_error("\n❌ Corrija problemas antes de fazer deploy")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
