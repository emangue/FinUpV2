# 🤝 Guia de Contribuição - Sistema de Gestão Financeira

Bem-vindo ao guia de contribuição do projeto! Este documento explica como trabalhar no projeto de forma segura e organizada, utilizando nosso sistema de versionamento.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Configuração Inicial](#configuração-inicial)
3. [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
4. [Sistema de Versionamento](#sistema-de-versionamento)
5. [Documentação de Mudanças](#documentação-de-mudanças)
6. [Git Workflow](#git-workflow)
7. [Testes](#testes)
8. [Code Review](#code-review)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### Princípios do Projeto

- ✅ **Rastreabilidade completa** - Toda mudança é documentada
- ✅ **Rollback fácil** - Podemos voltar qualquer mudança mal feita
- ✅ **Versionamento semântico** - Major.Minor.Patch
- ✅ **Documentação automática** - Scripts geram docs automaticamente
- ✅ **Proteção de produção** - Hooks impedem commits acidentais

### Arquivos Críticos

Estes arquivos **requerem versionamento obrigatório**:

- `app/models.py` - Schema do banco de dados
- `app/config.py` - Configurações da aplicação
- `app/utils/hasher.py` - Geração de IDs e hashes
- `app/utils/normalizer.py` - Normalização de dados
- `app/utils/deduplicator.py` - Detecção de duplicatas
- `app/blueprints/*/routes.py` - Lógica de negócio das rotas
- `app/blueprints/upload/processors/*.py` - Processadores de arquivos

---

## ⚙️ Configuração Inicial

### 1. Clone e Setup

```bash
# Clone o repositório
git clone <url-do-repo>
cd ProjetoFinancasV3

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Verifique versão atual
python scripts/version_manager.py status
```

### 2. Configure Git Hooks

```bash
# Torne o script executável
chmod +x scripts/version_manager.py

# Instale hooks (se disponível)
# ./scripts/install_hooks.sh
```

### 3. Leia a Documentação

**Obrigatório antes de começar:**

- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Instruções completas
- [VERSION.md](VERSION.md) - Versão atual do projeto
- [CHANGELOG.md](CHANGELOG.md) - Histórico de mudanças
- [BUGS.md](BUGS.md) - Bugs conhecidos e resolvidos

---

## 🔄 Workflow de Desenvolvimento

### Fluxo Padrão (Arquivos Críticos)

```bash
# 1️⃣ Iniciar mudança
python scripts/version_manager.py start app/models.py

# Output:
# 🔧 Iniciando mudança em: app/models.py
# ✅ VERSION.md atualizado: 2.1.0-dev
# ✅ app/__init__.py atualizado: 2.1.0-dev
# ✅ app/models.py atualizado: 2.1.0-dev
# 🌿 Branch criada: dev/models-2025-12-27

# 2️⃣ Fazer modificações
# Edite o código normalmente...

# 3️⃣ Testar completamente
python run.py  # Teste manual
python -m pytest  # Testes automatizados

# 4️⃣ Finalizar mudança
python scripts/version_manager.py finish app/models.py "Adiciona campo Categoria ao JournalEntry"

# Output:
# ✅ Finalizando mudança em: app/models.py
# ✅ VERSION.md atualizado: 2.1.1
# ✅ app/__init__.py atualizado: 2.1.1
# ✅ app/models.py atualizado: 2.1.1
# 📄 Documentação gerada: 2025-12-27_models_adiciona-campo-categoria.md
# 📦 Commit criado: feat(models): Adiciona campo Categoria ao JournalEntry [v2.1.1]
# 🎉 Mudança finalizada com sucesso!
```

### Fluxo Simplificado (Arquivos Não-Críticos)

Para arquivos não-críticos (templates, CSS, JS, docs):

```bash
# Edite normalmente
nano templates/dashboard.html

# Commit direto
git add templates/dashboard.html
git commit -m "style: Melhora layout do dashboard"
git push
```

---

## 🔢 Sistema de Versionamento

### Versionamento Semântico

Seguimos [Semantic Versioning 2.0.0](https://semver.org/):

**Formato:** `MAJOR.MINOR.PATCH`

#### MAJOR (X.0.0)

Quando fazer release major:

- ❌ **Breaking changes** - Mudanças incompatíveis
- 🗄️ **Schema do banco** - Remoção de campos, mudança de tipos
- 🔌 **API pública** - Mudanças em rotas/endpoints
- 🏗️ **Refatoração massiva** - Reestruturação completa

**Exemplos:**
- Mudança de SQLite para PostgreSQL
- Remoção do campo `TipoTransacao` do modelo
- Mudança de Flask para FastAPI

#### MINOR (x.Y.0)

Quando fazer release minor:

- ✨ **Novas funcionalidades** - Features adicionadas
- ➕ **Novos campos** - Adição não-breaking ao banco
- 🔧 **Novos blueprints** - Novos módulos
- 📊 **Novas rotas** - Endpoints adicionais

**Exemplos:**
- Adicionar campo `Categoria` ao `JournalEntry`
- Criar blueprint de relatórios
- Implementar exportação para Excel

#### PATCH (x.y.Z)

Quando fazer release patch:

- 🐛 **Bug fixes** - Correções de bugs
- ⚡ **Performance** - Otimizações
- 📝 **Documentação** - Melhorias em docs
- 🎨 **UI/UX** - Ajustes visuais

**Exemplos:**
- Corrigir bug de duplicação
- Otimizar query N+1
- Atualizar README

### Estados de Versão

| Estado | Formato | Descrição | Commit? |
|--------|---------|-----------|---------|
| **Stable** | `2.1.0` | Versão estável, testada e aprovada | ✅ Sim |
| **Development** | `2.1.0-dev` | Mudanças em progresso | ❌ Não |
| **Test** | `2.1.0-test` | Pronto para testes finais | ❌ Não |

**Regra de Ouro:** Nunca commite versões `-dev` ou `-test` na branch main!

---

## 📝 Documentação de Mudanças

### Estrutura de Documentação

```
changes/
├── TEMPLATE.md                                    # Template padrão
├── 2025-12-27_models_adiciona-campo-categoria.md
├── 2025-12-27_hasher_otimiza-performance.md
└── _history/
    └── 2.1.0/
        ├── 2025-12-26_models_corrige-bug-x.md
        └── 2025-12-26_routes_adiciona-rota-y.md
```

### Gerando Documentação

**Automático:**

```bash
# Ao finalizar mudança, documentação é gerada automaticamente
python scripts/version_manager.py finish app/models.py "Descrição"
```

**Manual:**

```bash
# Copiar template
cp changes/TEMPLATE.md changes/2025-12-27_models_minha-mudanca.md

# Editar arquivo preenchendo seções
nano changes/2025-12-27_models_minha-mudanca.md
```

### Seções Importantes

Garanta que estas seções estejam preenchidas:

- ✅ **Descrição** - O que foi feito e por quê
- ✅ **Arquivos Modificados** - Lista completa
- ✅ **Mudanças Realizadas** - Detalhes técnicos
- ✅ **Testes** - Como validar a mudança
- ✅ **Impacto** - Breaking changes? Migração necessária?
- ✅ **Rollback** - Como reverter se necessário

---

## 🌿 Git Workflow

### Branches

```
main (produção)
│
├── dev/models-2025-12-27     # Mudança em models.py
├── dev/hasher-2025-12-27     # Mudança em hasher.py
├── hotfix/bug-123            # Correção urgente
└── feature/relatorios        # Nova funcionalidade grande
```

### Convenção de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição> [vX.Y.Z]

Exemplos:
feat(models): Adiciona campo Categoria ao JournalEntry [v2.1.1]
fix(hasher): Corrige colisão de hash em VPD [v2.0.1]
docs(readme): Atualiza instruções de instalação
style(dashboard): Melhora layout da tabela de transações
perf(upload): Otimiza bulk insert de parcelas [v2.0.2]
refactor(blueprints): Modulariza rotas do admin [v2.1.0]
test(models): Adiciona testes unitários para JournalEntry
chore(deps): Atualiza Flask para 3.0.1
```

**Tipos:**
- `feat` - Nova funcionalidade
- `fix` - Correção de bug
- `docs` - Documentação
- `style` - Formatação, UI/UX
- `perf` - Melhoria de performance
- `refactor` - Refatoração sem mudança de comportamento
- `test` - Adição/modificação de testes
- `chore` - Tarefas de manutenção

### Comandos Git Úteis

```bash
# Ver status atual
git status
python scripts/version_manager.py status

# Ver mudanças
git diff
git diff --staged

# Ver histórico
git log --oneline --graph --all
git tag -l "v*" --sort=-version:refname

# Voltar mudança específica
git checkout v2.1.0 -- app/models.py

# Criar hotfix
git checkout -b hotfix/bug-importante
# ... fazer correção ...
python scripts/version_manager.py release patch
git push origin hotfix/bug-importante
```

---

## 🧪 Testes

### Antes de Finalizar Mudança

```bash
# 1. Testes manuais
python run.py
# Navegar pela aplicação e testar funcionalidade

# 2. Validar dados no banco
sqlite3 app/instance/journal.db
sqlite> SELECT * FROM journal_entries LIMIT 5;

# 3. Testes automatizados (se disponíveis)
python -m pytest tests/ -v

# 4. Verificar logs
tail -f logs/app.log

# 5. Verificar imports e syntax
python -m py_compile app/models.py
```

### Checklist de Testes

- [ ] Funcionalidade principal testada
- [ ] Casos extremos (edge cases) validados
- [ ] Dados no banco verificados
- [ ] Sem warnings ou erros no console
- [ ] Performance aceitável
- [ ] Compatibilidade com funcionalidades existentes
- [ ] Rollback testado e funciona

---

## 👀 Code Review

### Auto-Review Checklist

Antes de commitar, revise seu próprio código:

- [ ] **Código limpo** - Sem código comentado ou debug prints
- [ ] **Nomenclatura** - Nomes descritivos para variáveis/funções
- [ ] **Docstrings** - Funções importantes documentadas
- [ ] **Versionamento** - Versões atualizadas em arquivos críticos
- [ ] **Formatação** - Código formatado consistentemente
- [ ] **Segurança** - Sem credenciais hardcoded
- [ ] **Performance** - Sem queries N+1 ou loops desnecessários
- [ ] **Documentação** - Arquivo em `changes/` completo

---

## 🚨 Troubleshooting

### Problema: Esqueci de rodar `start` antes de modificar

**Solução:**

```bash
# 1. Verifique o que foi modificado
git diff app/models.py

# 2. Se mudança é boa, crie documentação manualmente
cp changes/TEMPLATE.md changes/2025-12-27_models_descricao.md
nano changes/2025-12-27_models_descricao.md

# 3. Atualize versão manualmente nos docstrings
# Edite o arquivo e mude "Versão: 2.1.0" para "Versão: 2.1.1"

# 4. Commit normalmente
git add .
git commit -m "feat(models): Descrição [v2.1.1]"
```

### Problema: Pre-commit hook está bloqueando commit

**Causa:** Você está tentando commitar versão `-dev` ou `-test`

**Solução:**

```bash
# 1. Verifique status
python scripts/version_manager.py status

# 2. Finalize a mudança corretamente
python scripts/version_manager.py finish app/models.py "Descrição"

# 3. Agora pode commitar
git push
```

### Problema: Preciso desfazer mudança em progresso

**Solução:**

```bash
# 1. Descartar mudanças não commitadas
git checkout -- app/models.py

# OU reverter para última versão estável
python scripts/version_manager.py rollback v2.1.0

# 2. Resetar versão para stable
# Edite VERSION.md manualmente removendo -dev
```

### Problema: Mudança quebrou a aplicação

**Solução Rápida:**

```bash
# Rollback completo para última versão funcionando
python scripts/version_manager.py rollback v2.1.0

# Ou rollback apenas do arquivo problemático
git checkout v2.1.0 -- app/models.py

# Restart aplicação
python run.py
```

**Solução Permanente:**

1. Identifique o problema na documentação em `changes/`
2. Reverta as mudanças manualmente
3. Teste novamente
4. Faça novo commit com correção

---

## 🎯 Quick Reference

### Comandos Mais Usados

```bash
# Ver versão e status
python scripts/version_manager.py status

# Iniciar mudança em arquivo crítico
python scripts/version_manager.py start app/models.py

# Finalizar mudança
python scripts/version_manager.py finish app/models.py "Descrição"

# Criar release
python scripts/version_manager.py release patch  # ou minor, major

# Rollback
python scripts/version_manager.py rollback v2.1.0

# Ver histórico git
git log --oneline --graph
git tag -l "v*" --sort=-version:refname
```

### Estrutura de Arquivos Importantes

```
ProjetoFinancasV3/
├── .github/
│   └── copilot-instructions.md    # Instruções para AI (LEIA!)
├── .copilot-rules.md               # Resumo das regras
├── VERSION.md                      # Versão atual
├── CHANGELOG.md                    # Histórico de releases
├── CONTRIBUTING.md                 # Este arquivo
├── changes/
│   ├── TEMPLATE.md                 # Template de documentação
│   └── 2025-12-27_*.md            # Mudanças pendentes
├── scripts/
│   └── version_manager.py          # Script principal
└── app/
    ├── __init__.py                 # Contém __version__
    ├── models.py                   # 🔒 CRÍTICO
    └── utils/
        └── hasher.py               # 🔒 CRÍTICO
```

---

## 📞 Suporte

**Precisa de ajuda?**

1. Leia [.github/copilot-instructions.md](.github/copilot-instructions.md) primeiro
2. Consulte [BUGS.md](BUGS.md) para bugs conhecidos
3. Verifique [CHANGELOG.md](CHANGELOG.md) para mudanças recentes
4. Abra uma issue descrevendo o problema

---

**Última atualização:** 27/12/2025  
**Versão do guia:** 1.0.0
