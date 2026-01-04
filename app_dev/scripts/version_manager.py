#!/usr/bin/env python3
"""
Version Manager - Gerenciador de Versionamento do Projeto

Script para gerenciar o ciclo de vida de versões e documentação de mudanças.

Uso:
    python scripts/version_manager.py start <arquivo>
    python scripts/version_manager.py finish <arquivo> "descrição"
    python scripts/version_manager.py status
    python scripts/version_manager.py rollback <tag>
    python scripts/version_manager.py release [major|minor|patch]
"""
import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path


# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "VERSION.md"
CHANGELOG_FILE = PROJECT_ROOT / "CHANGELOG.md"
CHANGES_DIR = PROJECT_ROOT / "changes"
APP_INIT = PROJECT_ROOT / "app" / "__init__.py"

# Arquivos críticos que requerem versionamento
CRITICAL_FILES = [
    "app/models.py",
    "app/config.py",
    "app/utils/hasher.py",
    "app/utils/normalizer.py",
    "app/utils/deduplicator.py",
    "app/blueprints/upload/routes.py",
    "app/blueprints/dashboard/routes.py",
    "app/blueprints/admin/routes.py",
]


def get_current_version():
    """Lê a versão atual do VERSION.md"""
    if not VERSION_FILE.exists():
        return "0.0.0", "stable"
    
    content = VERSION_FILE.read_text()
    
    # Busca pela linha **Versão Atual:** `X.Y.Z`
    match = re.search(r'\*\*Versão Atual:\*\* `([^`]+)`', content)
    if not match:
        return "0.0.0", "stable"
    
    version = match.group(1)
    
    # Detecta status (dev, test, stable)
    if '-dev' in version:
        return version.replace('-dev', ''), 'dev'
    elif '-test' in version:
        return version.replace('-test', ''), 'test'
    else:
        return version, 'stable'


def update_version_file(version, status='stable'):
    """Atualiza VERSION.md com nova versão e status"""
    if status == 'dev':
        version_display = f"{version}-dev"
        status_emoji = "🟡"
    elif status == 'test':
        version_display = f"{version}-test"
        status_emoji = "🟠"
    else:
        version_display = version
        status_emoji = "🟢"
    
    content = VERSION_FILE.read_text()
    
    # Atualiza versão
    content = re.sub(
        r'\*\*Versão Atual:\*\* `[^`]+`',
        f'**Versão Atual:** `{version_display}`',
        content
    )
    
    # Atualiza status
    content = re.sub(
        r'\*\*Status:\*\* `[^`]+` .',
        f'**Status:** `{status}` {status_emoji}',
        content
    )
    
    # Atualiza data
    today = datetime.now().strftime("%d/%m/%Y")
    content = re.sub(
        r'\*\*Data da Última Atualização:\*\* \d{2}/\d{2}/\d{4}',
        f'**Data da Última Atualização:** {today}',
        content
    )
    
    VERSION_FILE.write_text(content)
    print(f"✅ VERSION.md atualizado: {version_display}")


def update_app_version(version, status='stable'):
    """Atualiza __version__ em app/__init__.py"""
    if status == 'dev':
        version_display = f"{version}-dev"
    elif status == 'test':
        version_display = f"{version}-test"
    else:
        version_display = version
    
    content = APP_INIT.read_text()
    content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{version_display}"',
        content
    )
    APP_INIT.write_text(content)
    print(f"✅ app/__init__.py atualizado: {version_display}")


def update_file_version(filepath, version, status='stable'):
    """Atualiza versão no docstring de um arquivo"""
    file_path = PROJECT_ROOT / filepath
    if not file_path.exists():
        print(f"⚠️  Arquivo não encontrado: {filepath}")
        return
    
    if status == 'dev':
        version_display = f"{version}-dev"
    elif status == 'test':
        version_display = f"{version}-test"
    else:
        version_display = version
    
    content = file_path.read_text()
    
    # Atualiza linha "Versão: X.Y.Z"
    content = re.sub(
        r'Versão: [^\n]+',
        f'Versão: {version_display}',
        content,
        count=1
    )
    
    # Atualiza data
    today = datetime.now().strftime("%d/%m/%Y")
    content = re.sub(
        r'Data: \d{2}/\d{2}/\d{4}',
        f'Data: {today}',
        content,
        count=1
    )
    
    # Atualiza status
    content = re.sub(
        r'Status: \w+',
        f'Status: {status}',
        content,
        count=1
    )
    
    file_path.write_text(content)
    print(f"✅ {filepath} atualizado: {version_display}")


def start_change(filepath):
    """Inicia mudança em um arquivo (marca como -dev)"""
    print(f"\n🔧 Iniciando mudança em: {filepath}\n")
    
    # Verifica se é arquivo crítico
    if not any(filepath.endswith(cf) for cf in CRITICAL_FILES):
        print(f"⚠️  Arquivo não é crítico. Versão não obrigatória.")
        print(f"Arquivos críticos: {', '.join(CRITICAL_FILES)}")
        return
    
    # Pega versão atual
    version, current_status = get_current_version()
    
    if current_status != 'stable':
        print(f"⚠️  Já existe mudança em progresso (status: {current_status})")
        print("Finalize a mudança atual antes de iniciar outra.")
        return
    
    # Marca como -dev
    update_version_file(version, 'dev')
    update_app_version(version, 'dev')
    update_file_version(filepath, version, 'dev')
    
    # Tenta criar branch git
    try:
        file_name = Path(filepath).stem
        branch_name = f"dev/{file_name}-{datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(['git', 'checkout', '-b', branch_name], 
                      cwd=PROJECT_ROOT, check=False, capture_output=True)
        print(f"🌿 Branch criada: {branch_name}")
    except:
        print("⚠️  Não foi possível criar branch git")
    
    print(f"\n✅ Mudança iniciada!")
    print(f"   Versão: {version}-dev")
    print(f"   Arquivo: {filepath}")
    print(f"\n📝 Próximos passos:")
    print(f"   1. Fazer modificações no código")
    print(f"   2. Testar completamente")
    print(f"   3. Rodar: python scripts/version_manager.py finish {filepath} \"descrição\"")


def finish_change(filepath, description):
    """Finaliza mudança em um arquivo (remove -dev, gera doc)"""
    print(f"\n✅ Finalizando mudança em: {filepath}\n")
    
    # Pega versão atual
    version, current_status = get_current_version()
    
    if current_status == 'stable':
        print("⚠️  Nenhuma mudança em progresso (-dev ou -test)")
        return
    
    # Incrementa patch
    major, minor, patch = map(int, version.split('.'))
    new_version = f"{major}.{minor}.{patch + 1}"
    
    # Atualiza para stable
    update_version_file(new_version, 'stable')
    update_app_version(new_version, 'stable')
    update_file_version(filepath, new_version, 'stable')
    
    # Gera documentação em changes/
    generate_change_doc(filepath, version, new_version, description)
    
    # Commit git
    try:
        file_name = Path(filepath).stem
        commit_msg = f"feat({file_name}): {description} [v{new_version}]"
        
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_ROOT, check=False)
        subprocess.run(['git', 'commit', '-m', commit_msg], 
                      cwd=PROJECT_ROOT, check=False)
        print(f"📦 Commit criado: {commit_msg}")
    except:
        print("⚠️  Não foi possível criar commit git")
    
    print(f"\n🎉 Mudança finalizada com sucesso!")
    print(f"   Versão: {version} → {new_version}")
    print(f"   Documentação: changes/{datetime.now().strftime('%Y-%m-%d')}_{Path(filepath).stem}*.md")
    print(f"\n💡 Para fazer release, rode:")
    print(f"   python scripts/version_manager.py release patch")


def generate_change_doc(filepath, old_version, new_version, description):
    """Gera arquivo de documentação em changes/"""
    CHANGES_DIR.mkdir(exist_ok=True)
    
    file_name = Path(filepath).stem
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Slug da descrição
    slug = re.sub(r'[^a-z0-9]+', '-', description.lower())[:50]
    doc_filename = f"{today}_{file_name}_{slug}.md"
    doc_path = CHANGES_DIR / doc_filename
    
    # Template
    template = f"""# Mudança: {description}

**Arquivo:** `{filepath}`  
**Versão:** `{old_version}` → `{new_version}`  
**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}  
**Autor:** Sistema Automático

---

## 📝 Descrição

{description}

## 📂 Arquivos Modificados

- `{filepath}`

## 🔄 Mudanças Realizadas

<!-- Descrever mudanças detalhadamente -->

- [ ] Adicionar detalhes das mudanças aqui

## 🧪 Testes Realizados

<!-- Descrever testes executados -->

- [ ] Adicionar testes aqui

## 💥 Impacto

<!-- Descrever possíveis impactos -->

- [ ] Breaking changes? Sim/Não
- [ ] Requer migração de banco? Sim/Não
- [ ] Afeta outras funcionalidades? Sim/Não

## 🔙 Rollback

Para reverter esta mudança:

```bash
# Checkout para versão anterior
git checkout v{old_version} -- {filepath}

# Ou rollback completo
python scripts/version_manager.py rollback v{old_version}
```

## 🔗 Relacionado

- Issue: #
- PR: #
- Documentação: 

---

**Nota:** Este arquivo foi gerado automaticamente. Complete as seções pendentes.
"""
    
    doc_path.write_text(template)
    print(f"📄 Documentação gerada: {doc_filename}")


def status():
    """Mostra status atual do versionamento"""
    version, status_type = get_current_version()
    
    if status_type == 'dev':
        version_display = f"{version}-dev 🟡"
    elif status_type == 'test':
        version_display = f"{version}-test 🟠"
    else:
        version_display = f"{version} 🟢"
    
    print(f"\n📊 Status do Versionamento\n")
    print(f"   Versão atual: {version_display}")
    print(f"   Status: {status_type}")
    
    # Verifica mudanças pendentes em changes/
    if CHANGES_DIR.exists():
        changes = list(CHANGES_DIR.glob("*.md"))
        if changes:
            print(f"\n📝 Mudanças documentadas ({len(changes)}):")
            for change in sorted(changes)[-5:]:
                print(f"   - {change.name}")
    
    # Verifica últimas tags git
    try:
        result = subprocess.run(
            ['git', 'tag', '-l', 'v*', '--sort=-version:refname'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout:
            tags = result.stdout.strip().split('\n')[:5]
            print(f"\n🏷️  Últimas versões (git tags):")
            for tag in tags:
                print(f"   - {tag}")
    except:
        pass
    
    print()


def rollback(tag):
    """Faz rollback para uma versão específica"""
    print(f"\n⏮️  Rollback para: {tag}\n")
    
    try:
        # Checkout para tag
        subprocess.run(['git', 'checkout', tag], cwd=PROJECT_ROOT, check=True)
        print(f"✅ Rollback realizado com sucesso!")
        print(f"   Versão: {tag}")
        print(f"\n⚠️  Você está em 'detached HEAD state'")
        print(f"   Para voltar à main: git checkout main")
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao fazer rollback. Verifique se a tag '{tag}' existe.")
        print(f"   Tags disponíveis: git tag -l 'v*'")


def release(bump_type='patch'):
    """Cria novo release (major, minor ou patch)"""
    version, status_type = get_current_version()
    
    if status_type != 'stable':
        print("❌ Não é possível criar release com mudanças em progresso")
        print("   Finalize todas as mudanças primeiro")
        return
    
    # Incrementa versão
    major, minor, patch = map(int, version.split('.'))
    
    if bump_type == 'major':
        new_version = f"{major + 1}.0.0"
    elif bump_type == 'minor':
        new_version = f"{major}.{minor + 1}.0"
    else:  # patch
        new_version = f"{major}.{minor}.{patch + 1}"
    
    print(f"\n🚀 Criando release: v{new_version}\n")
    
    # Atualiza versão
    update_version_file(new_version, 'stable')
    update_app_version(new_version, 'stable')
    
    # Agrega mudanças no CHANGELOG
    aggregate_changelog(new_version)
    
    # Commit e tag
    try:
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_ROOT, check=False)
        subprocess.run(
            ['git', 'commit', '-m', f'release: v{new_version}'],
            cwd=PROJECT_ROOT,
            check=False
        )
        subprocess.run(
            ['git', 'tag', '-a', f'v{new_version}', '-m', f'Release v{new_version}'],
            cwd=PROJECT_ROOT,
            check=False
        )
        print(f"✅ Release criado: v{new_version}")
        print(f"📦 Tag git: v{new_version}")
    except:
        print("⚠️  Erro ao criar commit/tag git")
    
    # Move changes/ para histórico
    if CHANGES_DIR.exists():
        history_dir = CHANGES_DIR / "_history" / new_version
        history_dir.mkdir(parents=True, exist_ok=True)
        
        for change_file in CHANGES_DIR.glob("*.md"):
            if change_file.name != "TEMPLATE.md":
                change_file.rename(history_dir / change_file.name)
        
        print(f"📁 Mudanças arquivadas em: changes/_history/{new_version}/")
    
    print(f"\n🎉 Release v{new_version} concluído!")
    print(f"\n💡 Próximos passos:")
    print(f"   git push origin main")
    print(f"   git push origin v{new_version}")


def aggregate_changelog(version):
    """Agrega mudanças de changes/ no CHANGELOG.md"""
    if not CHANGES_DIR.exists():
        return
    
    changes = sorted(CHANGES_DIR.glob("*.md"))
    if not changes or all(c.name == "TEMPLATE.md" for c in changes):
        return
    
    # Lê CHANGELOG atual
    changelog_content = CHANGELOG_FILE.read_text() if CHANGELOG_FILE.exists() else ""
    
    # Prepara nova seção
    today = datetime.now().strftime("%d/%m/%Y")
    new_section = f"\n## [{version}] - {today}\n\n"
    
    # Agrega mudanças
    for change_file in changes:
        if change_file.name == "TEMPLATE.md":
            continue
        
        content = change_file.read_text()
        
        # Extrai descrição
        desc_match = re.search(r'# Mudança: (.+)', content)
        if desc_match:
            new_section += f"- {desc_match.group(1)}\n"
    
    # Insere no CHANGELOG (após primeira seção)
    insert_pos = changelog_content.find("\n## [")
    if insert_pos > 0:
        changelog_content = (
            changelog_content[:insert_pos] +
            new_section +
            changelog_content[insert_pos:]
        )
    else:
        changelog_content = new_section + changelog_content
    
    CHANGELOG_FILE.write_text(changelog_content)
    print(f"📝 CHANGELOG.md atualizado")


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python scripts/version_manager.py start <arquivo>")
        print("  python scripts/version_manager.py finish <arquivo> \"descrição\"")
        print("  python scripts/version_manager.py status")
        print("  python scripts/version_manager.py rollback <tag>")
        print("  python scripts/version_manager.py release [major|minor|patch]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        if len(sys.argv) < 3:
            print("Uso: python scripts/version_manager.py start <arquivo>")
            sys.exit(1)
        start_change(sys.argv[2])
    
    elif command == 'finish':
        if len(sys.argv) < 4:
            print("Uso: python scripts/version_manager.py finish <arquivo> \"descrição\"")
            sys.exit(1)
        finish_change(sys.argv[2], sys.argv[3])
    
    elif command == 'status':
        status()
    
    elif command == 'rollback':
        if len(sys.argv) < 3:
            print("Uso: python scripts/version_manager.py rollback <tag>")
            sys.exit(1)
        rollback(sys.argv[2])
    
    elif command == 'release':
        bump_type = sys.argv[2] if len(sys.argv) > 2 else 'patch'
        if bump_type not in ['major', 'minor', 'patch']:
            print("Tipo de release deve ser: major, minor ou patch")
            sys.exit(1)
        release(bump_type)
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
