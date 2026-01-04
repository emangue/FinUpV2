#!/usr/bin/env python3
"""
Master Deployment Script
Integra todos os checks, testes e deployment automatizado

Versão: 1.0.0
Data: 02/01/2026
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(message):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def run_command(cmd, description, exit_on_error=True):
    """Executa comando e retorna resultado"""
    print(f"\n🔄 {description}...")
    
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print_success(f"{description} - OK")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print_error(f"{description} - FAILED")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            
            if exit_on_error:
                sys.exit(1)
            return False
            
    except Exception as e:
        print_error(f"{description} - ERROR: {e}")
        if exit_on_error:
            sys.exit(1)
        return False


def check_prerequisites():
    """Verifica pré-requisitos locais"""
    print_header("Checking Prerequisites")
    
    checks = [
        ('VERSION.md exists', os.path.exists('VERSION.md')),
        ('financas.db exists', os.path.exists('financas.db')),
        ('app/ directory exists', os.path.isdir('app')),
        ('requirements.txt exists', os.path.exists('requirements.txt')),
        ('venv activated', sys.prefix != sys.base_prefix),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print_success(check_name)
        else:
            print_error(check_name)
            all_passed = False
    
    return all_passed


def run_database_health_check():
    """Executa verificação de saúde do banco"""
    print_header("Database Health Check")
    
    cmd = f"{sys.executable} scripts/database_health_check.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    
    if result.returncode == 0:
        print_success("Database health check passed")
        return True
    elif result.returncode == 1:
        print_warning("Database has warnings but can be deployed")
        return True
    else:
        print_error("Database has critical issues - deployment blocked")
        return False


def run_deployment_tests():
    """Executa testes de deployment"""
    print_header("Running Deployment Tests")
    
    cmd = f"{sys.executable} tests/deployment_health_check.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    
    if result.returncode == 0:
        print_success("All deployment tests passed")
        return True
    elif result.returncode == 1:
        print_warning("Some tests have warnings")
        response = input("\n⚠️  Continue despite warnings? (yes/no): ")
        return response.lower() in ['yes', 'y']
    else:
        print_error("Critical tests failed - deployment blocked")
        return False


def generate_diff_report():
    """Gera relatório de diferenças"""
    print_header("Generating Deployment Diff")
    
    cmd = f"{sys.executable} scripts/deployment_diff.py --save-manifest"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    
    return result.returncode in [0, 1]  # 0 = no changes, 1 = changes detected


def create_backup():
    """Cria backup pré-deployment"""
    print_header("Creating Pre-Deployment Backup")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    cmd = f"{sys.executable} scripts/backup_database.py backup --tag pre-deploy-{timestamp}"
    
    return run_command(cmd, "Creating backup")


def deploy_to_server(vm_config):
    """Deploy para o servidor"""
    print_header("Deploying to Server")
    
    if not vm_config:
        print_error("VM configuration not provided")
        print_info("Please fill in VM_INFO_CHECKLIST.md and provide connection details")
        return False
    
    # Backup no servidor
    print_info("Creating backup on server...")
    ssh_backup_cmd = f"ssh {vm_config['user']}@{vm_config['host']} 'cd {vm_config['app_path']} && source venv/bin/activate && python scripts/backup_database.py backup --tag remote-pre-deploy-{datetime.now().strftime('%Y%m%d')}'"
    
    run_command(ssh_backup_cmd, "Remote backup", exit_on_error=False)
    
    # Rsync files
    print_info("Syncing files to server...")
    
    exclude_file = '.deployignore'
    if not os.path.exists(exclude_file):
        # Criar arquivo de exclusões
        with open(exclude_file, 'w') as f:
            f.write('\n'.join([
                'venv/',
                '*.db',
                'flask_session/',
                '__pycache__/',
                '*.pyc',
                '_temp_scripts/',
                'changes/',
                '.git/',
                '.env.production',
                '*.log'
            ]))
    
    rsync_cmd = f"rsync -avz --exclude-from='{exclude_file}' ./ {vm_config['user']}@{vm_config['host']}:{vm_config['app_path']}/"
    
    if not run_command(rsync_cmd, "File sync", exit_on_error=False):
        print_error("File sync failed - check SSH connection")
        return False
    
    # Instalar dependências se requirements.txt mudou
    print_info("Installing dependencies on server...")
    ssh_install_cmd = f"ssh {vm_config['user']}@{vm_config['host']} 'cd {vm_config['app_path']} && source venv/bin/activate && pip install -r requirements.txt'"
    
    run_command(ssh_install_cmd, "Install dependencies", exit_on_error=False)
    
    # Restart application
    print_info("Restarting application...")
    ssh_restart_cmd = f"ssh {vm_config['user']}@{vm_config['host']} 'sudo systemctl restart financial-app'"
    
    if not run_command(ssh_restart_cmd, "Application restart", exit_on_error=False):
        print_warning("Could not restart application automatically - may need manual restart")
    
    # Verificar status
    print_info("Checking application status...")
    ssh_status_cmd = f"ssh {vm_config['user']}@{vm_config['host']} 'sudo systemctl status financial-app --no-pager'"
    
    run_command(ssh_status_cmd, "Application status check", exit_on_error=False)
    
    print_success("Deployment completed!")
    
    return True


def post_deployment_checks(vm_config):
    """Verificações pós-deployment"""
    print_header("Post-Deployment Checks")
    
    if not vm_config:
        print_info("Manual checks required:")
        print("  1. SSH to server and check logs")
        print("  2. Test application in browser")
        print("  3. Verify user login works")
        return True
    
    # Check if application is responding
    import urllib.request
    
    domain = vm_config.get('domain', vm_config.get('host'))
    protocol = 'https' if vm_config.get('ssl', False) else 'http'
    
    try:
        url = f"{protocol}://{domain}"
        print_info(f"Checking {url}...")
        
        response = urllib.request.urlopen(url, timeout=10)
        if response.status == 200:
            print_success("Application is responding")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status}")
            return False
    except Exception as e:
        print_warning(f"Could not check application: {e}")
        print_info("Please manually verify application is running")
        return False


def main():
    parser = argparse.ArgumentParser(description='Master Deployment Script')
    parser.add_argument('--target', choices=['local', 'production'], default='local',
                        help='Deployment target (default: local)')
    parser.add_argument('--check-only', action='store_true',
                        help='Only run checks, do not deploy')
    parser.add_argument('--skip-tests', action='store_true',
                        help='Skip deployment tests (not recommended)')
    parser.add_argument('--vm-user', help='VM SSH user')
    parser.add_argument('--vm-host', help='VM hostname or IP')
    parser.add_argument('--vm-path', default='/opt/financial-app',
                        help='Application path on VM (default: /opt/financial-app)')
    
    args = parser.parse_args()
    
    print_header("🚀 Financial Management System - Deployment Script")
    print(f"Target: {args.target}")
    print(f"Mode: {'Check Only' if args.check_only else 'Full Deployment'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        print_error("Prerequisites check failed")
        return 1
    
    # Health check do banco
    if not run_database_health_check():
        print_error("Database health check failed - fix issues before deploying")
        return 2
    
    # Testes de deployment
    if not args.skip_tests:
        if not run_deployment_tests():
            print_error("Deployment tests failed")
            return 3
    else:
        print_warning("Skipping deployment tests (not recommended)")
    
    # Gerar diff report
    generate_diff_report()
    
    # Backup local
    if not create_backup():
        print_error("Failed to create local backup")
        return 4
    
    # Se apenas check, parar aqui
    if args.check_only:
        print_header("✅ All Checks Passed - Ready for Deployment")
        print_info("Run without --check-only to deploy")
        return 0
    
    # Confirmar deployment
    if args.target == 'production':
        print_warning("You are about to deploy to PRODUCTION")
        response = input("\n⚠️  Are you sure? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print_info("Deployment cancelled")
            return 0
        
        # VM config
        vm_config = None
        if args.vm_user and args.vm_host:
            vm_config = {
                'user': args.vm_user,
                'host': args.vm_host,
                'app_path': args.vm_path,
                'ssl': True  # Assume SSL for production
            }
        else:
            print_error("VM configuration required for production deployment")
            print_info("Provide --vm-user and --vm-host")
            return 5
        
        # Deploy
        if not deploy_to_server(vm_config):
            print_error("Deployment failed")
            return 6
        
        # Post-deployment checks
        post_deployment_checks(vm_config)
    
    else:
        print_info("Local deployment - no remote sync needed")
    
    print_header("🎉 Deployment Complete!")
    
    print("\n📋 Next Steps:")
    print("  1. Review deployment logs above")
    print("  2. Test application in browser")
    print("  3. Monitor logs for first few hours")
    print("  4. Update CHANGELOG.md with deployment notes")
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(255)
