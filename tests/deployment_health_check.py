#!/usr/bin/env python3
"""
Pre-Deployment Health Check Suite
Testa todas as capabilities críticas do sistema antes do deployment

Versão: 1.0.0
Data: 02/01/2026
"""

import sys
import os
from pathlib import Path

# Adicionar root ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from datetime import datetime
import hashlib


class TestResult:
    def __init__(self, name, passed, message="", critical=False):
        self.name = name
        self.passed = passed
        self.message = message
        self.critical = critical
    
    def __str__(self):
        status = "✅ PASS" if self.passed else ("🚨 FAIL" if self.critical else "⚠️  WARN")
        return f"{status} - {self.name}" + (f": {self.message}" if self.message else "")


class DeploymentHealthCheck:
    def __init__(self, db_path='financas.db'):
        self.db_path = db_path
        self.results = []
        self.conn = None
    
    def connect_db(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            self.results.append(TestResult(
                "Database Connection",
                False,
                f"Could not connect: {e}",
                critical=True
            ))
            return False
    
    def test_database_exists(self):
        """Verifica se banco de dados existe"""
        exists = os.path.exists(self.db_path)
        self.results.append(TestResult(
            "Database File Exists",
            exists,
            self.db_path if exists else "Database file not found",
            critical=True
        ))
        return exists
    
    def test_tables_exist(self):
        """Verifica se todas as tabelas necessárias existem"""
        required_tables = [
            'users',
            'user_relationships',
            'journal_entries',
            'base_parcelas',
            'base_padroes',
            'base_marcacoes',
            'grupo_config',
            'estabelecimento_logo',
            'duplicados_temp',
            'audit_log'
        ]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        passed = len(missing_tables) == 0
        message = f"Found {len(existing_tables)}/{len(required_tables)} tables"
        if missing_tables:
            message += f" - Missing: {', '.join(missing_tables)}"
        
        self.results.append(TestResult(
            "Required Tables",
            passed,
            message,
            critical=True
        ))
        return passed
    
    def test_admin_user_exists(self):
        """Verifica se existe pelo menos um usuário admin"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND ativo = 1")
        admin_count = cursor.fetchone()[0]
        
        passed = admin_count > 0
        self.results.append(TestResult(
            "Admin User Exists",
            passed,
            f"Found {admin_count} active admin user(s)",
            critical=True
        ))
        return passed
    
    def test_user_isolation(self):
        """Verifica se isolamento por user_id está funcionando"""
        cursor = self.conn.cursor()
        
        # Verificar se journal_entries tem user_id
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        has_user_id = 'user_id' in columns
        
        if not has_user_id:
            self.results.append(TestResult(
                "User Isolation (user_id column)",
                False,
                "journal_entries does not have user_id column",
                critical=True
            ))
            return False
        
        # Verificar se existem transações com user_id NULL
        cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE user_id IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total_count = cursor.fetchone()[0]
        
        if total_count > 0:
            null_pct = (null_count / total_count * 100)
            passed = null_pct < 5  # Menos de 5% NULL é aceitável
            message = f"{null_count}/{total_count} transactions ({null_pct:.1f}%) without user_id"
            
            self.results.append(TestResult(
                "User Isolation (data integrity)",
                passed,
                message,
                critical=False
            ))
            return passed
        else:
            self.results.append(TestResult(
                "User Isolation (no data to check)",
                True,
                "No transactions in database yet",
                critical=False
            ))
            return True
    
    def test_classification_data(self):
        """Verifica se dados de classificação estão disponíveis"""
        cursor = self.conn.cursor()
        
        # BaseMarcacao (combinações válidas)
        cursor.execute("SELECT COUNT(*) FROM base_marcacoes")
        marcacao_count = cursor.fetchone()[0]
        
        passed = marcacao_count > 0
        self.results.append(TestResult(
            "Classification Data (BaseMarcacao)",
            passed,
            f"Found {marcacao_count} valid classification combinations",
            critical=True
        ))
        
        # GrupoConfig (configuração de grupos)
        cursor.execute("SELECT COUNT(*) FROM grupo_config WHERE ativo = 1")
        grupo_count = cursor.fetchone()[0]
        
        passed = grupo_count > 0
        self.results.append(TestResult(
            "Classification Data (GrupoConfig)",
            passed,
            f"Found {grupo_count} active groups",
            critical=True
        ))
        
        return marcacao_count > 0 and grupo_count > 0
    
    def test_password_hashing(self):
        """Verifica se senhas estão hasheadas"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM users LIMIT 5")
        hashes = cursor.fetchall()
        
        if not hashes:
            self.results.append(TestResult(
                "Password Hashing (no users)",
                True,
                "No users to check",
                critical=False
            ))
            return True
        
        # Verificar se hashes parecem válidos (pbkdf2:sha256)
        all_hashed = all(
            hash_val[0] and 
            len(hash_val[0]) > 20 and 
            ('pbkdf2' in hash_val[0] or '$' in hash_val[0])
            for hash_val in hashes if hash_val[0]
        )
        
        self.results.append(TestResult(
            "Password Hashing",
            all_hashed,
            "All passwords properly hashed" if all_hashed else "Some passwords not properly hashed",
            critical=True
        ))
        return all_hashed
    
    def test_id_generation(self):
        """Verifica se sistema de geração de IDs está funcionando"""
        # Importar hasher
        try:
            from app.utils.hasher import generate_id_transacao
            
            # Testar geração
            test_data = '01/01/2026'
            test_estabelecimento = 'TESTE'
            test_valor = 100.50
            
            id1 = generate_id_transacao(test_data, test_estabelecimento, test_valor)
            id2 = generate_id_transacao(test_data, test_estabelecimento, test_valor)
            
            # IDs iguais para mesmo input
            consistency = (id1 == id2)
            
            # ID é uma string numérica (FNV-1a retorna decimal)
            valid_format = id1.isdigit() and len(id1) > 10
            
            passed = consistency and valid_format
            message = "ID generation working correctly" if passed else "ID generation has issues"
            
            self.results.append(TestResult(
                "ID Generation System",
                passed,
                message,
                critical=True
            ))
            return passed
            
        except Exception as e:
            self.results.append(TestResult(
                "ID Generation System",
                False,
                f"Error testing ID generation: {e}",
                critical=True
            ))
            return False
    
    def test_file_structure(self):
        """Verifica estrutura de arquivos necessária"""
        required_files = [
            'app/__init__.py',
            'app/models.py',
            'app/config.py',
            'app/extensions.py',
            'run.py',
            'requirements.txt',
            'VERSION.md'
        ]
        
        required_dirs = [
            'app/blueprints',
            'app/utils',
            'templates',
            'static',
            'scripts'
        ]
        
        missing_files = []
        missing_dirs = []
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        for dir_path in required_dirs:
            if not os.path.isdir(dir_path):
                missing_dirs.append(dir_path)
        
        passed = len(missing_files) == 0 and len(missing_dirs) == 0
        
        message = "All required files and directories present"
        if missing_files:
            message = f"Missing files: {', '.join(missing_files)}"
        if missing_dirs:
            message += f" | Missing dirs: {', '.join(missing_dirs)}"
        
        self.results.append(TestResult(
            "File Structure",
            passed,
            message,
            critical=True
        ))
        return passed
    
    def test_flask_imports(self):
        """Verifica se imports do Flask funcionam"""
        try:
            import flask
            from flask_login import LoginManager
            from flask_session import Session
            import pandas
            import sqlalchemy
            
            self.results.append(TestResult(
                "Flask Dependencies",
                True,
                "All required packages importable",
                critical=True
            ))
            return True
        except ImportError as e:
            self.results.append(TestResult(
                "Flask Dependencies",
                False,
                f"Missing dependency: {e}",
                critical=True
            ))
            return False
    
    def test_blueprints_registered(self):
        """Verifica se blueprints estão registrados"""
        try:
            from app import create_app
            
            app = create_app()
            
            # Verificar blueprints
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            required_blueprints = ['auth', 'dashboard', 'upload', 'admin']
            
            missing = [bp for bp in required_blueprints if bp not in blueprint_names]
            
            passed = len(missing) == 0
            message = f"Found blueprints: {', '.join(blueprint_names)}"
            if missing:
                message = f"Missing blueprints: {', '.join(missing)}"
            
            self.results.append(TestResult(
                "Blueprint Registration",
                passed,
                message,
                critical=True
            ))
            return passed
            
        except Exception as e:
            self.results.append(TestResult(
                "Blueprint Registration",
                False,
                f"Error loading app: {e}",
                critical=True
            ))
            return False
    
    def test_data_integrity(self):
        """Verifica integridade básica dos dados"""
        cursor = self.conn.cursor()
        
        # Transações com valores inconsistentes
        cursor.execute("""
            SELECT COUNT(*) FROM journal_entries 
            WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01
        """)
        inconsistent = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        total = cursor.fetchone()[0]
        
        if total > 0:
            inconsistent_pct = (inconsistent / total * 100)
            passed = inconsistent_pct < 1  # Menos de 1% com inconsistência
            message = f"{inconsistent}/{total} transactions ({inconsistent_pct:.2f}%) with value inconsistencies"
            
            self.results.append(TestResult(
                "Data Integrity (values)",
                passed,
                message,
                critical=False
            ))
        else:
            self.results.append(TestResult(
                "Data Integrity (no data)",
                True,
                "No transactions to check",
                critical=False
            ))
        
        return True
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 80)
        print("🔍 DEPLOYMENT HEALTH CHECK")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.db_path}")
        print("")
        
        # Testes que não precisam de DB
        self.test_file_structure()
        self.test_flask_imports()
        self.test_blueprints_registered()
        
        # Testes de banco de dados
        if self.test_database_exists() and self.connect_db():
            self.test_tables_exist()
            self.test_admin_user_exists()
            self.test_user_isolation()
            self.test_classification_data()
            self.test_password_hashing()
            self.test_data_integrity()
            self.conn.close()
        
        # Testes de sistema
        self.test_id_generation()
        
        # Resultados
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS")
        print("=" * 80)
        
        for result in self.results:
            print(result)
        
        print("")
        
        # Sumário
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        critical_failed = sum(1 for r in self.results if not r.passed and r.critical)
        
        print("=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Critical failures: {critical_failed}")
        print("")
        
        if critical_failed > 0:
            print("🚨 DEPLOYMENT BLOCKED - Critical tests failed!")
            print("   Fix critical issues before deploying.")
            return 2
        elif failed > 0:
            print("⚠️  DEPLOYMENT WITH WARNINGS - Some non-critical tests failed")
            print("   Review warnings before deploying.")
            return 1
        else:
            print("✅ DEPLOYMENT READY - All tests passed!")
            return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-deployment health check')
    parser.add_argument('--db', default='financas.db', help='Database path')
    
    args = parser.parse_args()
    
    checker = DeploymentHealthCheck(db_path=args.db)
    exit_code = checker.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
