#!/usr/bin/env python3
"""
Script: Migração Gradual de Documentação
Autor: GitHub Copilot + Emanuel Guerra
Data: 23/01/2026

OBJETIVO: Migrar copilot-instructions.md (2693 linhas) para estrutura organizada

ESTRUTURA NOVA:
- docs/rules/           (Regras detalhadas)
- docs/guides/          (Guias práticos)
- docs/reference/       (Referência técnica)
- .github/copilot-instructions.md (CORE - apenas crítico)
"""

import os
from pathlib import Path

# Base path
BASE_PATH = Path(__file__).parent.parent.parent

# Paths
DOCS_PATH = BASE_PATH / "docs"
COPILOT_INSTRUCTIONS = BASE_PATH / ".github" / "copilot-instructions.md"

def create_structure():
    """Cria estrutura de diretórios"""
    print("📁 Criando estrutura de diretórios...")
    
    dirs = [
        DOCS_PATH / "rules",
        DOCS_PATH / "guides",
        DOCS_PATH / "reference",
        DOCS_PATH / "workflows"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path.relative_to(BASE_PATH)}")

def create_files():
    """Cria arquivos vazios com templates"""
    print("\n📄 Criando arquivos com templates...")
    
    files = {
        # Rules
        "docs/rules/CRITICAL.md": """# 🔴 Regras CRÍTICAS - Nunca Violar

**Última atualização:** 23/01/2026

Estas regras são INVIOLÁVEIS. Qualquer violação pode causar:
- 🔴 Vazamento de dados entre usuários
- 🔴 Perda de sincronização git
- 🔴 Quebra de deploy
- 🔴 Dados corrompidos

---

## 1. Git Sync (OBRIGATÓRIO) {#git-sync}

### Fluxo:
Local → Git → Servidor (NUNCA editar servidor diretamente!)

[Conteúdo será migrado de copilot-instructions.md]

---

## 2. Database Único (OBRIGATÓRIO) {#database}

[Conteúdo será migrado...]

---

## 3. Filtros de Data (OBRIGATÓRIO) {#date-filters}

[Conteúdo será migrado...]
""",
        
        "docs/rules/security.md": """# 🔒 Segurança - Guia Completo

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## JWT Obrigatório
[...]

## Secrets Management
[...]

## Rate Limiting
[...]

## CORS
[...]
""",
        
        "docs/rules/architecture.md": """# 🏗️ Arquitetura Modular

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Backend - Domains (DDD)
[...]

## Frontend - Features
[...]

## Regras de Importação
[...]
""",
        
        "docs/guides/quick-start.md": """# 🚀 Quick Start - Iniciar Projeto

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Pré-requisitos
[...]

## 1. Clone do Repositório
[...]

## 2. Setup Backend
[...]

## 3. Setup Frontend
[...]
""",
        
        "docs/guides/deploy.md": """# 🚢 Deploy - Guia Completo

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Deploy Local → Produção
[...]

## Rollback
[...]

## Troubleshooting Deploy
[...]
""",
        
        "docs/guides/troubleshooting.md": """# 🔧 Troubleshooting - Problemas Comuns

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Backend não inicia
[...]

## Frontend erro 401
[...]

## Portas ocupadas
[...]
""",
        
        "docs/reference/accounts.md": """# 👤 Contas de Teste - Referência

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Produção
[...]

## Local
[...]

## Como criar nova conta
[...]
""",
        
        "docs/reference/environment.md": """# 🌍 Variáveis de Ambiente - Referência

**Última atualização:** 23/01/2026

[Conteúdo será migrado de copilot-instructions.md]

## Backend (.env)
[...]

## Frontend (.env.local)
[...]

## Python Virtual Environments
[...]
""",
        
        "docs/INDEX.md": """# 📚 Índice de Documentação

**Última atualização:** 23/01/2026

Este é o índice completo da documentação do projeto.

---

## 🔴 Regras Críticas

Leia PRIMEIRO antes de modificar qualquer código:

- [CRITICAL.md](rules/CRITICAL.md) - Regras invioláveis (Git Sync, Database, Filtros)
- [security.md](rules/security.md) - Segurança (JWT, Secrets, Rate Limiting)
- [architecture.md](rules/architecture.md) - Arquitetura (Domains, Features, Isolamento)

---

## 🚀 Guias Práticos

Passo-a-passo para tarefas comuns:

- [quick-start.md](guides/quick-start.md) - Iniciar projeto do zero
- [deploy.md](guides/deploy.md) - Deploy em produção
- [troubleshooting.md](guides/troubleshooting.md) - Resolver problemas comuns
- [testing.md](guides/testing.md) - Testar isolamento e autenticação

---

## 📖 Referência Técnica

Consulta rápida:

- [api-endpoints.md](reference/api-endpoints.md) - Lista completa de APIs
- [database-schema.md](reference/database-schema.md) - Schema do banco
- [accounts.md](reference/accounts.md) - Contas de teste
- [environment.md](reference/environment.md) - Variáveis de ambiente

---

## 🔍 Busca Rápida

**Tenho um problema com...**

- **Autenticação/Login** → [security.md](rules/security.md)
- **Deploy** → [deploy.md](guides/deploy.md)
- **Backend não inicia** → [troubleshooting.md](guides/troubleshooting.md)
- **Estrutura de domínios** → [architecture.md](rules/architecture.md)
- **Sincronização git** → [CRITICAL.md](rules/CRITICAL.md#git-sync)
- **Database** → [CRITICAL.md](rules/CRITICAL.md#database)

---

## 📋 Workflow Completo

1. Ler requisição do usuário
2. Identificar categoria (feature, bug, deploy)
3. Consultar documento correspondente
4. Implementar seguindo padrões
5. Testar isoladamente
6. Commitar e fazer deploy se necessário

---

**Ver também:** [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Resumo CORE
"""
    }
    
    for file_path, content in files.items():
        full_path = BASE_PATH / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not full_path.exists():
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ {file_path}")
        else:
            print(f"   ⚠️  {file_path} (já existe, ignorado)")

def backup_current():
    """Faz backup do copilot-instructions.md atual"""
    print("\n💾 Fazendo backup do copilot-instructions.md atual...")
    
    if COPILOT_INSTRUCTIONS.exists():
        backup_path = BASE_PATH / "_arquivos_historicos" / "copilot-instructions_v1_backup_23_01_2026.md"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(COPILOT_INSTRUCTIONS, backup_path)
        print(f"   ✅ Backup criado: {backup_path.relative_to(BASE_PATH)}")
    else:
        print("   ⚠️  Arquivo não encontrado")

def analyze_current():
    """Analisa arquivo atual"""
    print("\n📊 Analisando copilot-instructions.md atual...")
    
    if not COPILOT_INSTRUCTIONS.exists():
        print("   ❌ Arquivo não encontrado")
        return
    
    with open(COPILOT_INSTRUCTIONS, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        content = ''.join(lines)
    
    print(f"   Linhas: {len(lines)}")
    print(f"   Palavras: {len(content.split())}")
    print(f"   Caracteres: {len(content)}")
    print(f"   Tokens (estimado): {len(content.split()) * 1.3:.0f}")
    
    # Seções principais
    print("\n   📋 Seções identificadas:")
    sections = [
        "SINCRONIZAÇÃO GIT",
        "SEGURANÇA",
        "ESTRUTURA DE PASTAS",
        "FILTROS DE DATA",
        "BANCO DE DADOS ÚNICO",
        "MIGRATIONS",
        "AMBIENTE ESPELHO",
        "SAFE DEPLOY",
        "CHANGELOG",
        "ARQUITETURA MODULAR",
        "FRONTEND",
        "Iniciar/Parar Servidores"
    ]
    
    for section in sections:
        if section in content:
            print(f"      ✅ {section}")

def show_migration_plan():
    """Mostra plano de migração"""
    print("\n" + "="*80)
    print("📋 PLANO DE MIGRAÇÃO")
    print("="*80)
    
    plan = """
FASE 1: Estrutura (FEITO)
- ✅ Criar diretórios docs/rules, docs/guides, docs/reference
- ✅ Criar arquivos com templates
- ✅ Criar INDEX.md

FASE 2: Migração de Conteúdo (MANUAL - 2-3 horas)
- [ ] Copiar seção "SINCRONIZAÇÃO GIT" → docs/rules/CRITICAL.md
- [ ] Copiar seção "SEGURANÇA" → docs/rules/security.md
- [ ] Copiar seção "ARQUITETURA MODULAR" → docs/rules/architecture.md
- [ ] Copiar seção "Iniciar/Parar Servidores" → docs/guides/quick-start.md
- [ ] Copiar seção "SAFE DEPLOY" → docs/guides/deploy.md
- [ ] Copiar "Contas de Teste" → docs/reference/accounts.md
- [ ] Copiar "PYTHON VIRTUAL ENVIRONMENT" → docs/reference/environment.md

FASE 3: Criar CORE (MANUAL - 1 hora)
- [ ] Usar template de docs/EXEMPLO_COPILOT_INSTRUCTIONS_V2.md
- [ ] Substituir .github/copilot-instructions.md pelo novo CORE
- [ ] Adicionar links para docs/

FASE 4: Validação (30 min)
- [ ] Testar com Copilot
- [ ] Verificar se responde corretamente
- [ ] Ajustar links se necessário

FASE 5: Cleanup (30 min)
- [ ] Commitar mudanças
- [ ] Atualizar README.md
- [ ] Documentar mudança em CHANGELOG.md
"""
    
    print(plan)
    print("\n" + "="*80)

def main():
    print("🔧 MIGRAÇÃO DE DOCUMENTAÇÃO")
    print("="*80)
    print(f"Base Path: {BASE_PATH}")
    print("="*80)
    
    # 1. Analisar atual
    analyze_current()
    
    # 2. Backup
    backup_current()
    
    # 3. Criar estrutura
    create_structure()
    
    # 4. Criar arquivos
    create_files()
    
    # 5. Plano
    show_migration_plan()
    
    print("\n✅ FASE 1 COMPLETA - Estrutura criada!")
    print("\n📋 PRÓXIMO PASSO:")
    print("   1. Revisar arquivos criados em docs/")
    print("   2. Começar migração manual de conteúdo")
    print("   3. Usar docs/EXEMPLO_COPILOT_INSTRUCTIONS_V2.md como template para CORE")
    print(f"\n💡 DICA: Abra {COPILOT_INSTRUCTIONS.relative_to(BASE_PATH)} e docs/ lado a lado")
    print("   para copiar conteúdo seção por seção\n")

if __name__ == "__main__":
    main()
