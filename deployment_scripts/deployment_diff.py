#!/usr/bin/env python3
"""
Deployment Diff Tool
Compara arquivos locais vs servidor remoto e lista mudanças

Versão: 1.0.0
Data: 02/01/2026
"""

import os
import sys
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Arquivos/pastas a INCLUIR no deployment
DEPLOY_INCLUDE = [
    'app/',
    'templates/',
    'static/',
    'scripts/',
    'requirements.txt',
    'run.py',
    'VERSION.md',
    'CHANGELOG.md',
    'README.md',
]

# Arquivos/pastas a EXCLUIR do deployment
DEPLOY_EXCLUDE = [
    'venv/',
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'flask_session/',
    'uploads_temp/',
    '_temp_scripts/',
    '_csvs_historico/',
    'financas.db',
    'financas.db.backup_*',
    '*.log',
    '.DS_Store',
    'Thumbs.db',
    '.git/',
    '.github/',
    '.vscode/',
    '.idea/',
    '.env*',
    'changes/',
    '*.csv',
    '*.xls',
    '*.xlsx',
    '*.ofx',
    '.copilot-rules.md',
    'BUGS.md',
    'TODO_*.md',
    'IMPLEMENTACAO_*.md',
    'VM_INFO_CHECKLIST.md',
    'database_health_report_*.txt',
    'deployment_diff_*.md',
]


def calculate_file_hash(filepath):
    """Calcula hash MD5 de um arquivo"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def should_include_file(filepath, root_dir):
    """Verifica se arquivo deve ser incluído no deployment"""
    rel_path = os.path.relpath(filepath, root_dir)
    
    # Verificar exclusões
    for pattern in DEPLOY_EXCLUDE:
        if pattern.endswith('/'):
            # Diretório
            if rel_path.startswith(pattern.rstrip('/')):
                return False
        elif '*' in pattern:
            # Wildcard
            import fnmatch
            if fnmatch.fnmatch(rel_path, pattern):
                return False
        else:
            # Arquivo específico
            if rel_path == pattern or os.path.basename(rel_path) == pattern:
                return False
    
    # Verificar inclusões
    for pattern in DEPLOY_INCLUDE:
        if pattern.endswith('/'):
            # Diretório
            if rel_path.startswith(pattern.rstrip('/')):
                return True
        else:
            # Arquivo específico
            if rel_path == pattern:
                return True
    
    return False


def scan_local_files(root_dir):
    """Escaneia arquivos locais que devem ser deployados"""
    files = {}
    
    for pattern in DEPLOY_INCLUDE:
        if pattern.endswith('/'):
            # Diretório
            dir_path = os.path.join(root_dir, pattern.rstrip('/'))
            if os.path.exists(dir_path):
                for root, dirs, filenames in os.walk(dir_path):
                    # Remover diretórios excluídos da busca
                    dirs[:] = [d for d in dirs if not any(
                        d == ex.rstrip('/') or d.startswith('__pycache__')
                        for ex in DEPLOY_EXCLUDE if ex.endswith('/')
                    )]
                    
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        if should_include_file(filepath, root_dir):
                            rel_path = os.path.relpath(filepath, root_dir)
                            files[rel_path] = {
                                'path': filepath,
                                'hash': calculate_file_hash(filepath),
                                'size': os.path.getsize(filepath),
                                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                            }
        else:
            # Arquivo específico
            filepath = os.path.join(root_dir, pattern)
            if os.path.exists(filepath):
                files[pattern] = {
                    'path': filepath,
                    'hash': calculate_file_hash(filepath),
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                }
    
    return files


def compare_with_server(local_files, server_manifest_path):
    """Compara arquivos locais com manifest do servidor"""
    changes = {
        'new': [],
        'modified': [],
        'deleted': [],
        'unchanged': []
    }
    
    # Carregar manifest do servidor
    server_files = {}
    if os.path.exists(server_manifest_path):
        try:
            with open(server_manifest_path, 'r') as f:
                server_files = json.load(f)
        except:
            print(f"⚠️  Could not read server manifest: {server_manifest_path}")
    
    # Comparar
    local_paths = set(local_files.keys())
    server_paths = set(server_files.keys())
    
    # Novos arquivos
    for path in local_paths - server_paths:
        changes['new'].append({
            'path': path,
            'size': local_files[path]['size'],
            'modified': local_files[path]['modified']
        })
    
    # Arquivos deletados
    for path in server_paths - local_paths:
        changes['deleted'].append({
            'path': path,
            'size': server_files[path].get('size', 0)
        })
    
    # Arquivos modificados ou iguais
    for path in local_paths & server_paths:
        local_hash = local_files[path]['hash']
        server_hash = server_files[path].get('hash', '')
        
        if local_hash != server_hash:
            changes['modified'].append({
                'path': path,
                'size_before': server_files[path].get('size', 0),
                'size_after': local_files[path]['size'],
                'modified': local_files[path]['modified']
            })
        else:
            changes['unchanged'].append(path)
    
    return changes


def analyze_file_changes(filepath):
    """Analisa mudanças em um arquivo específico (para arquivos de código)"""
    if not filepath.endswith(('.py', '.html', '.css', '.js', '.json', '.md', '.txt')):
        return None
    
    try:
        # Usar git diff se disponível
        result = subprocess.run(
            ['git', 'diff', '--', filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.split('\n')
            added = len([l for l in lines if l.startswith('+')])
            removed = len([l for l in lines if l.startswith('-')])
            return {
                'added_lines': added,
                'removed_lines': removed,
                'has_diff': True
            }
    except:
        pass
    
    return None


def generate_diff_report(changes, local_files, output_file=None):
    """Gera relatório de mudanças em markdown"""
    lines = []
    
    lines.append("# 🚀 Deployment Diff Report")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Status:** Ready for deployment")
    lines.append("")
    
    # Sumário
    lines.append("## 📊 Summary")
    lines.append("")
    lines.append(f"- **New files:** {len(changes['new'])}")
    lines.append(f"- **Modified files:** {len(changes['modified'])}")
    lines.append(f"- **Deleted files:** {len(changes['deleted'])}")
    lines.append(f"- **Unchanged files:** {len(changes['unchanged'])}")
    lines.append("")
    
    total_changes = len(changes['new']) + len(changes['modified']) + len(changes['deleted'])
    
    if total_changes == 0:
        lines.append("✅ **No changes detected - server is up to date!**")
        lines.append("")
    else:
        lines.append(f"⚠️  **Total changes to deploy:** {total_changes}")
        lines.append("")
    
    # Novos arquivos
    if changes['new']:
        lines.append("## ➕ New Files")
        lines.append("")
        lines.append("| File | Size | Modified |")
        lines.append("|------|------|----------|")
        for item in sorted(changes['new'], key=lambda x: x['path']):
            size_kb = item['size'] / 1024
            lines.append(f"| `{item['path']}` | {size_kb:.1f} KB | {item['modified'][:10]} |")
        lines.append("")
    
    # Arquivos modificados
    if changes['modified']:
        lines.append("## 📝 Modified Files")
        lines.append("")
        lines.append("| File | Size Change | Modified | Details |")
        lines.append("|------|-------------|----------|---------|")
        for item in sorted(changes['modified'], key=lambda x: x['path']):
            size_before_kb = item['size_before'] / 1024
            size_after_kb = item['size_after'] / 1024
            size_diff = size_after_kb - size_before_kb
            size_diff_str = f"+{size_diff:.1f}" if size_diff >= 0 else f"{size_diff:.1f}"
            
            # Analisar mudanças se for código
            detail = ""
            filepath = local_files[item['path']]['path']
            diff_info = analyze_file_changes(filepath)
            if diff_info and diff_info['has_diff']:
                detail = f"+{diff_info['added_lines']}/-{diff_info['removed_lines']} lines"
            
            lines.append(f"| `{item['path']}` | {size_diff_str} KB | {item['modified'][:10]} | {detail} |")
        lines.append("")
    
    # Arquivos deletados
    if changes['deleted']:
        lines.append("## ❌ Deleted Files")
        lines.append("")
        lines.append("| File | Size |")
        lines.append("|------|------|")
        for item in sorted(changes['deleted'], key=lambda x: x['path']):
            size_kb = item['size'] / 1024
            lines.append(f"| `{item['path']}` | {size_kb:.1f} KB |")
        lines.append("")
    
    # Arquivos críticos modificados
    critical_files = [
        'app/models.py',
        'app/config.py',
        'app/__init__.py',
        'requirements.txt',
        'run.py'
    ]
    
    critical_modified = [item for item in changes['modified'] if item['path'] in critical_files]
    if critical_modified:
        lines.append("## ⚠️  Critical Files Modified")
        lines.append("")
        lines.append("These files require special attention:")
        lines.append("")
        for item in critical_modified:
            lines.append(f"- `{item['path']}`")
            if item['path'] == 'requirements.txt':
                lines.append("  - **Action required:** Run `pip install -r requirements.txt` on server")
            elif item['path'] == 'app/models.py':
                lines.append("  - **Action required:** Check if database migration is needed")
            elif item['path'] == 'app/config.py':
                lines.append("  - **Action required:** Review configuration changes")
        lines.append("")
    
    # Recomendações
    lines.append("## 💡 Deployment Checklist")
    lines.append("")
    lines.append("Before deploying:")
    lines.append("- [ ] Run database health check: `python scripts/database_health_check.py`")
    lines.append("- [ ] Run pre-deployment tests: `python tests/deployment_health_check.py`")
    lines.append("- [ ] Backup current database on server")
    lines.append("- [ ] Review critical file changes above")
    lines.append("- [ ] Ensure VM has sufficient disk space")
    lines.append("")
    lines.append("After deploying:")
    lines.append("- [ ] Restart application server (Gunicorn/uWSGI)")
    lines.append("- [ ] Verify application is running")
    lines.append("- [ ] Check logs for errors")
    lines.append("- [ ] Test critical functionality")
    if critical_modified:
        lines.append("- [ ] Install new dependencies if `requirements.txt` changed")
        if any(item['path'] == 'app/models.py' for item in critical_modified):
            lines.append("- [ ] Run database migrations if schema changed")
    lines.append("")
    
    # Comandos úteis
    lines.append("## 🔧 Useful Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("# Backup database on server")
    lines.append("python scripts/backup_database.py")
    lines.append("")
    lines.append("# Deploy files to server")
    lines.append("python scripts/deploy.py --target production")
    lines.append("")
    lines.append("# Restart application")
    lines.append("sudo systemctl restart financial-app")
    lines.append("")
    lines.append("# View logs")
    lines.append("tail -f /opt/financial-app/logs/app.log")
    lines.append("```")
    lines.append("")
    
    lines.append("---")
    lines.append("*Generated by Deployment Diff Tool*")
    
    report = '\n'.join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Diff report saved to: {output_file}")
    else:
        print(report)
    
    return report


def save_manifest(local_files, manifest_path):
    """Salva manifest de arquivos locais"""
    with open(manifest_path, 'w') as f:
        json.dump(local_files, f, indent=2)
    print(f"✅ Local manifest saved to: {manifest_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare local files with server for deployment')
    parser.add_argument('--root', default='.', help='Root directory of the project')
    parser.add_argument('--server-manifest', default='server_manifest.json',
                        help='Path to server manifest file')
    parser.add_argument('--output', default=None,
                        help='Output file for diff report (default: console)')
    parser.add_argument('--save-manifest', action='store_true',
                        help='Save local manifest for future comparisons')
    
    args = parser.parse_args()
    
    # Escanear arquivos locais
    print("🔍 Scanning local files...")
    local_files = scan_local_files(args.root)
    print(f"   Found {len(local_files)} files to deploy")
    
    # Comparar com servidor
    print("📊 Comparing with server...")
    changes = compare_with_server(local_files, args.server_manifest)
    
    total_changes = len(changes['new']) + len(changes['modified']) + len(changes['deleted'])
    print(f"   Detected {total_changes} changes")
    
    # Gerar relatório
    output_file = args.output
    if output_file is None and total_changes > 0:
        output_file = f"deployment_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    generate_diff_report(changes, local_files, output_file)
    
    # Salvar manifest local se solicitado
    if args.save_manifest:
        manifest_file = 'local_manifest.json'
        save_manifest(local_files, manifest_file)
    
    # Exit code
    if total_changes > 0:
        return 1  # Changes detected
    else:
        return 0  # No changes


if __name__ == '__main__':
    sys.exit(main())
