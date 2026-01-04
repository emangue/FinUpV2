# 🤖 Instruções GitHub Copilot - Sistema de Versionamento

## ⚠️ REGRAS OBRIGATÓRIAS - SEMPRE SEGUIR

### 1. Antes de Modificar Qualquer Código

**SEMPRE verificar a versão atual do arquivo/módulo antes de fazer mudanças:**

```bash
# Verificar versão global do projeto
cat VERSION.md

# Verificar versão de arquivo específico (docstring no topo)
head -20 app/models.py | grep -i version
```

### 2. Ao Iniciar Modificações em Arquivos Críticos

**Arquivos Críticos que requerem versionamento:**
- `app/models.py` (schema do banco)
- `app/utils/hasher.py` (lógica de hash)
- `app/utils/processors/*.py` (processadores)
- `app/blueprints/*/routes.py` (rotas e lógica de negócio)
- `app/config.py` (configurações)

**Procedimento Obrigatório:**

1. **Marcar como desenvolvimento:**
   ```bash
   python scripts/version_manager.py start <caminho_do_arquivo>
   ```
   - Atualiza versão para `-dev` (ex: `2.1.0` → `2.1.0-dev`)
   - Cria branch git automática (ex: `dev/models-2025-12-27`)
   - Registra início da mudança

2. **Fazer as modificações necessárias**

3. **Testar completamente** (marcar como `-test` se necessário)

4. **Finalizar mudança:**
   ```bash
   python scripts/version_manager.py finish <caminho_do_arquivo> "Descrição da mudança"
   ```
   - Remove sufixo `-dev`/`-test`
   - Gera documentação automática em `changes/`
   - Cria commit git
   - Merge na branch principal

### 3. Nunca Commitar Versões de Desenvolvimento

**🚫 BLOQUEADO via git hook pre-commit:**
- Versões terminando em `-dev`
- Versões terminando em `-test`
- Mudanças em arquivos críticos sem documentação em `changes/`

### 4. Documentação Obrigatória de Mudanças

**Toda mudança em arquivo crítico deve gerar arquivo em `changes/`:**

Formato: `YYYY-MM-DD_nome-arquivo_descricao-curta.md`

Exemplo: `2025-12-27_models_adiciona-campo-categoria.md`

**Template automático gerado pelo `version_manager.py finish`**

### 5. Rollback de Mudanças

**Para reverter mudanças mal feitas:**

```bash
# Ver versões disponíveis
git tag -l "v*"

# Rollback para versão específica
python scripts/version_manager.py rollback v2.1.0

# Ou rollback manual via git
git checkout v2.1.0 -- <arquivo_especifico>
```

### 6. Releases de Novas Versões

**Quando um conjunto de mudanças está completo e testado:**

```bash
# Release patch (2.1.0 → 2.1.1) - bug fixes
python scripts/version_manager.py release patch

# Release minor (2.1.0 → 2.2.0) - novas features
python scripts/version_manager.py release minor

# Release major (2.1.0 → 3.0.0) - breaking changes
python scripts/version_manager.py release major
```

**O script automaticamente:**
- Incrementa versão em `VERSION.md` e `app/__init__.py`
- Agrega todos os arquivos de `changes/` no `CHANGELOG.md`
- Cria commit de release
- Cria tag git semântica (ex: `v2.2.0`)
- Limpa pasta `changes/` (move para histórico)

---

## 📋 Workflow Completo - Checklist

### Ao Receber Pedido de Modificação

- [ ] 1. Ler `VERSION.md` para ver versão atual
- [ ] 2. Identificar se arquivo é crítico (lista acima)
- [ ] 3. Se crítico: rodar `version_manager.py start <arquivo>`
- [ ] 4. Fazer modificações no código
- [ ] 5. Testar mudanças
- [ ] 6. Rodar `version_manager.py finish <arquivo> "descrição"`
- [ ] 7. Verificar que documentação foi gerada em `changes/`
- [ ] 8. Confirmar com usuário se mudança está OK
- [ ] 9. Se conjunto completo: perguntar se quer fazer release

### Exemplo Prático

**Usuário pede:** "Adicionar campo 'Categoria' no modelo JournalEntry"

**Resposta do AI:**

```bash
# 1. Iniciar mudança
python scripts/version_manager.py start app/models.py

# 2. [AI faz modificações em models.py]

# 3. Finalizar mudança
python scripts/version_manager.py finish app/models.py "Adiciona campo Categoria ao modelo JournalEntry para melhor classificação de transações"
```

**AI confirma:**
- ✅ Versão atualizada: `2.1.0-dev` → `2.1.1`
- ✅ Documentação gerada: `changes/2025-12-27_models_adiciona-campo-categoria.md`
- ✅ Commit criado: "feat(models): Adiciona campo Categoria ao JournalEntry [v2.1.1]"

---

## 🎯 Regras de Versionamento Semântico

### MAJOR (X.0.0)
- Breaking changes no schema do banco
- Mudanças incompatíveis na API
- Refatorações massivas

### MINOR (x.Y.0)
- Novas funcionalidades
- Novos campos no banco (não-breaking)
- Novos blueprints/rotas

### PATCH (x.y.Z)
- Bug fixes
- Melhorias de performance
- Correções de typos
- Ajustes de UI

---

## � Regras de Templates e Componentes Compartilhados

### ⚠️ REGRA CRÍTICA: Nunca Duplicar Templates

**Princípio fundamental:** Um template deve existir em **UM ÚNICO LUGAR**

**Templates COMPARTILHADOS** (usados por múltiplos blueprints):
- ✅ DEVEM ficar em `/templates/` (root)
- ✅ Exemplos: `transacoes.html`, `base.html`, `confirmar_upload.html`
- ✅ Qualquer blueprint pode renderizar: `render_template('transacoes.html')`

**Templates ESPECÍFICOS** (usados por apenas um blueprint):
- ✅ DEVEM ficar em `/app/blueprints/<nome>/templates/`
- ✅ Exemplo: `dashboard.html` (só usado pelo blueprint dashboard)
- ✅ Renderizar: `render_template('dashboard.html')`

**🚫 NUNCA DUPLICAR:**
- ❌ NUNCA ter o mesmo template em `/templates/` E em `/app/blueprints/*/templates/`
- ❌ Flask serve `/templates/` PRIMEIRO, causando bugs silenciosos
- ❌ Mudanças "desaparecem" porque Flask ignora a versão do blueprint

**✅ ESTRUTURA CORRETA:**
```
templates/
  ├── base.html                      # Layout compartilhado
  ├── transacoes.html                # ✅ Compartilhado (usado por dashboard, admin)
  ├── confirmar_upload.html          # ✅ Compartilhado
  ├── _macros/                       # Componentes reutilizáveis
  │   ├── transacao_filters.html     
  │   ├── transacao_modal_edit.html  
  │   └── ...
  └── _partials/                     # Seções compartilhadas
      └── ...

app/blueprints/
  ├── admin/templates/               
  │   └── admin_transacoes.html      # ✅ Específico do Admin
  ├── dashboard/templates/           
  │   └── dashboard.html             # ✅ Específico do Dashboard
  └── upload/templates/              
      └── validar.html               # ✅ Específico do Upload
```

**Regra de Ouro:**
- Se o template é usado por 2+ blueprints → `/templates/` (root)
- Se o template é usado por 1 blueprint → `/app/blueprints/<nome>/templates/`
- **NUNCA duplicar - apenas uma versão deve existir**

### Obrigações ao Modificar Templates

**SEMPRE que modificar um componente compartilhado (`_macros/` ou `_partials/`):**
1. ✅ Verificar TODOS os blueprints que usam esse componente
2. ✅ Testar em todos os contextos de uso
3. ✅ Documentar mudanças no cabeçalho do componente
4. ✅ Reiniciar servidor após mudanças

**SEMPRE que criar funcionalidade repetida entre blueprints:**
1. ✅ Avaliar se deve virar componente compartilhado
2. ✅ Extrair para `_macros/` ou `_partials/`
3. ✅ Documentar variáveis esperadas no cabeçalho Jinja
4. ✅ Atualizar todos os templates que podem usar o componente

**Princípio DRY (Don't Repeat Yourself):**
- ❌ NUNCA duplicar código HTML entre templates
- ✅ SEMPRE usar `{% include %}` para reutilização
- ✅ SEMPRE usar `{% extends %}` para herança de layout
- ✅ Preferir componentes compartilhados a cópias

### Componentes Compartilhados Existentes

1. **`_macros/transacao_filters.html`**
   - Filtros de pesquisa (estabelecimento, categoria, tipo)
   - Soma de valores filtrados
   - Variáveis: `mes_atual`, `filtro_*`, `grupos_lista`, `soma_filtrada`

2. **`_macros/transacao_modal_edit.html`**
   - Modal de edição de transações
   - JavaScript incluído (abrirModalEditar, salvarEdicaoTransacao)
   - Variáveis: `grupos_lista`

---

## 🚀 Deploy e Validação Pré-Deploy

### ⚠️ REGRA CRÍTICA: Validação PRÉ-DEPLOY Obrigatória

**SEMPRE executar validação ANTES de qualquer deploy:**

```bash
./scripts/pre_deploy_validation.sh
```

**Exit codes:**
- ✅ `0` = Safe to deploy (≥95% de match)
- ❌ `1` = DO NOT deploy (corrigir erros)

📖 **Documentação:** [docs/PRE_DEPLOY_CHECKLIST.md](../docs/PRE_DEPLOY_CHECKLIST.md)

### O que é Validado

**Script testa fluxo BAU (Business As Usual) de produção:**

1. **4 arquivos históricos:**
   - 3x Fatura Itaú (CSV): Dez, Nov, Out 2025
   - 1x Extrato BTG (XLS)

2. **Processamento completo:**
   - Leitura (pandas: CSV ou Excel)
   - `detect_and_preprocess()` - detecção automática de banco
   - `processar_fatura_cartao()` ou `processar_extrato_conta()`
   - Geração de hash IdTransacao (FNV-1a 64-bit)

3. **Comparação com banco:**
   - Query por `archivo_origen`
   - Match por `IdTransacao` (hash)
   - Compara: Data, Estabelecimento, ValorPositivo, GRUPO, SUBGRUPO, TipoGasto
   - Critério: ≥95% idênticas = PASSOU

### 🔍 Interpretando Resultados: Por que não 100%?

**É NORMAL e ESPERADO ter 95-99% de match, não 100%.**

#### Diferenças Legítimas (3-5%):

**1. Códigos Genéricos de Estabelecimento** ✅ (Mais comum)
- **Exemplo**: "1 cartao 1RWMTA" (código interno do cartão)
- **IA classifica**: MeLi + Amazon (inferência genérica sem contexto)
- **Usuário corrige**: Carro/Estacionamento (classificação correta)
- **MarcacaoIA**: "Manual (Lote)" - prova de edição posterior
- **Valor típico**: R$ 6,67 (estacionamento)
- **Não é bug**: Sistema funcionou - permitiu override manual ✅

**2. Campos de Metadados que Evoluíram** ✅
- `tipodocumento`: "Cartão" (antigo) vs "Fatura Cartão de Crédito" (novo)
- `banco`: NULL em faturas antigas (só BTG/Mercado Pago preenchido)
- Campos renomeados/adicionados em atualizações de schema
- **Não afeta funcionalidade** - apenas formato

**3. Base de Padrões Evolui** ✅
- Classificações melhoram conforme sistema aprende
- Transações antigas podem ter classificações menos precisas
- Sistema está **melhorando**, não quebrando

**4. Edições Manuais Posteriores** ✅
- Usuário edita transações após upload
- Validação compara: classificação **automática atual** vs **manual posterior**
- Divergências são **esperadas e corretas**

#### ⚠️ Quando divergências SÃO problema:

❌ **Se campos CRÍTICOS diferem:**
- Data completamente diferente
- Valor com diferença >R$0.01
- TipoTransacao mudou (Crédito ↔ Débito)

❌ **Se TODAS as transações divergem:**
- Preprocessador quebrado
- Hash generation inconsistente
- Banco de dados corrompido

#### ✅ Critério de Aprovação:

**≥95% de match em campos críticos**
- Data, Estabelecimento, Valor, TipoTransacao (obrigatórios)
- GRUPO, SUBGRUPO, TipoGasto (podem variar 3-5%)
- Foco em faturas Itaú (mais estáveis que extratos)

### Workflow de Deploy Completo

**SEMPRE seguir esta ordem:**

```bash
# 1. Validação Estrutural (arquivos, diretórios)
./scripts/validate_pre_deploy.sh

# 2. ⭐ VALIDAÇÃO FUNCIONAL (OBRIGATÓRIO - não pule!)
./scripts/pre_deploy_validation.sh

# 3. Se ambos passaram:
#    - Local: deploy app_dev → app
#    - Servidor: deploy para VPS/Hostinger

# 4. Após deploy: Testar manualmente
#    - Login
#    - Upload de arquivo
#    - Listagem de transações
```

### Scripts de Deploy Disponíveis

1. **`pre_deploy_validation.sh`** ⭐ **CRÍTICO**
   - Valida sistema de upload funciona
   - Compara com dados históricos (≥95% match)
   - Exit code 0/1 para CI/CD

2. **`validate_pre_deploy.sh`**
   - Valida estrutura (arquivos, diretórios, banco)
   - Verifica que `app_dev/` não será deployado
   - Exit code 0/1

3. **`deploy_dev_to_prod.py`**
   - Deploy local: `app_dev/` → `app/`
   - Backup automático
   - Validações syntax, imports, security

4. **`rollback_deployment.py`**
   - Restaura backups anteriores
   - Lista backups disponíveis
   - Backup de segurança antes de restaurar

### Integração com Versionamento

**Workflow com arquivo crítico:**

```bash
# 1. Iniciar mudança
python scripts/version_manager.py start app/models.py

# 2. Modificar código
# ... fazer mudanças ...

# 3. Testar localmente
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py

# 4. Finalizar mudança
python scripts/version_manager.py finish app/models.py "Descrição"

# 5. ⭐ VALIDAR (OBRIGATÓRIO)
./scripts/pre_deploy_validation.sh

# 6. Se passou, deploy
# (conforme ambiente: local ou servidor)
```

### Situações de Emergência no Deploy

**Validação falhou (<95% match):**

1. **Ver log completo:**
   ```bash
   /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/validar_upload_completo.py
   ```

2. **Verificar mudanças recentes:**
   ```bash
   git log --oneline --since="1 week ago" -- app/utils/processors/
   ```

3. **Comparar hashes manualmente:**
   ```bash
   sqlite3 app/financas.db "
   SELECT IdTransacao, Data, Estabelecimento, ValorPositivo 
   FROM journal_entries 
   WHERE arquivo_origem = 'Fatura - fatura_itau-202512.csv' 
   LIMIT 10;
   "
   ```

4. **NÃO deploye até corrigir!**

**Rollback necessário:**

```bash
# Listar backups
python scripts/rollback_deployment.py --list

# Restaurar mais recente
python scripts/rollback_deployment.py

# Ou específico
python scripts/rollback_deployment.py --backup app_backup_20251228_143025.tar.gz
```

---

## �🔍 Comandos Úteis para o AI

```bash
# VERSIONAMENTO
python scripts/version_manager.py status
ls -la changes/
git tag -l "v*" --sort=-version:refname | head -10
git describe --tags --abbrev=0
grep -r "\-dev" app/ --include="*.py" | head -5

# DEPLOY E VALIDAÇÃO
./scripts/pre_deploy_validation.sh                           # ⭐ OBRIGATÓRIO antes de deploy
./scripts/validate_pre_deploy.sh                             # Validar estrutura
python scripts/rollback_deployment.py --list                 # Listar backups
python scripts/deploy_dev_to_prod.py --validate-only         # Validar sem deploye

# BANCO DE DADOS
sqlite3 app/financas.db "SELECT COUNT(*) FROM journal_entries;"
sqlite3 app/financas.db "SELECT DISTINCT archivo_origen FROM journal_entries LIMIT 10;"
python scripts/database_health_check.py                      # Health check completo

# SERVIDOR
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py
pkill -f "python.*run.py"                                   # Parar servidor
```

---

## ⚡ Atalhos Rápidos

**Mudança rápida (arquivo não-crítico):**
- Não requer `version_manager.py`
- Fazer mudança diretamente
- Commit normal

**Mudança em arquivo crítico:**
- `start` → modificar → testar → `finish`

**Bug fix urgente:**
- Usar branch hotfix
- Versionar mesmo assim
- Release patch imediato

---

## 🚨 Situações de Emergência

### Esqueci de rodar `start` antes de modificar

```bash
# Verificar diff
git diff app/models.py

# Se mudança é boa, criar documentação manualmente
cp changes/TEMPLATE.md changes/2025-12-27_models_<descricao>.md
# Editar arquivo com detalhes da mudança

# Atualizar versão manualmente no docstring
```

### Preciso desfazer mudança em -dev

```bash
# Descartar mudanças não commitadas
git checkout -- <arquivo>

# Ou reverter para versão estável anterior
python scripts/version_manager.py rollback <tag>
```

### Hook pre-commit está bloqueando commit válido

```bash
# Verificar o que está bloqueando
python scripts/version_manager.py status

# Se realmente precisa commitar (emergência), bypass (não recomendado)
git commit --no-verify -m "msg"
```

---

## � Automação Obrigatória de Restart do Servidor

### Comando Padrão de Restart

**Sempre usar este comando para religar o servidor:**

```bash
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py
```

### Quando Fazer Restart Automático

**🔄 OBRIGATÓRIO: Religar servidor automaticamente após:**
- Modificação em arquivos críticos (models.py, routes.py, processors)
- Finalização de mudanças com `version_manager.py finish`
- Instalação de novas dependências
- Mudanças em configurações (config.py)
- Atualizações no schema do banco

### Procedimento de Restart

1. **Parar servidor atual** (se rodando):
   ```bash
   pkill -f "python.*run.py"
   ```

2. **Iniciar novo servidor**:
   ```bash
   /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py
   ```

3. **Verificar se está funcionando**:
   - Acessar http://localhost:5000
   - Confirmar que não há erros no terminal

### Integração com Workflow de Versionamento

**No `version_manager.py finish`, sempre incluir:**
1. Finalizar mudança e commit
2. **RESTART AUTOMÁTICO do servidor**
3. Validar que servidor está operacional

---

## �📚 Referências Rápidas

- **Documentação completa:** `CONTRIBUTING.md`
- **Template de mudanças:** `changes/TEMPLATE.md`
- **Histórico de bugs:** `BUGS.md` (manter como referência histórica)
- **Status do projeto:** `STATUSPROJETO.md`
- **Arquitetura:** `ESTRUTURA_PROJETO.md`
- **Deploy e Validação:** `docs/PRE_DEPLOY_CHECKLIST.md` ⭐
- **Validação Técnica:** `docs/VALIDACAO_UPLOAD_TECNICO.md`
- **Scripts de Deploy:** `scripts/README.md`

---

## � Gestão de Servidores e Ambiente de Desenvolvimento

### ⚡ CAMINHOS CRÍTICOS DO PROJETO

**Diretórios Base:**
- **Projeto Root**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3`
- **Virtual Env**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv`
- **Backend**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend`
- **Frontend**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend`
- **Banco de Dados**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db`
- **Códigos de Apoio**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio`

### 🔧 Iniciar Ambiente Completo

**Automático (Recomendado):**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
./start_servers.sh
```

**Manual - Backend:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend

PYTHONPATH=/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend:/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio \
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Manual - Frontend:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend
npm run dev
```

### 🛑 Parar Servidores

```bash
# Parar tudo
pkill -f "uvicorn.*app.main"
pkill -f "next dev"

# Forçar porta 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Forçar porta 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

### 🌐 URLs do Sistema

| Serviço | URL | Porta |
|---------|-----|-------|
| **Frontend** | http://localhost:3000 | 3000 |
| **Backend API** | http://localhost:8000 | 8000 |
| **Docs API** | http://localhost:8000/docs | 8000 |

### 👤 Credenciais de Login

**⚠️ SEMPRE usar user_id = 1 para testes:**
- **Email**: `admin@example.com`
- **Senha**: `admin123`
- **User ID**: `1`

### 🎯 Comandos de Verificação Rápida

```bash
# Status dos servidores
ps aux | grep -E "(uvicorn.*app.main|next dev)" | grep -v grep

# Testar backend
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend OK" || echo "❌ Backend ERRO"

# Testar frontend
curl -s http://localhost:3000/ > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend ERRO"

# Verificar banco
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db ".tables"

# Verificar user_id 1
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db "SELECT id, nome, email FROM users WHERE id = 1;"
```

### 🚨 Troubleshooting Comum

**Backend não inicia:**
- Verificar PYTHONPATH inclui `app_dev/backend` e `codigos_apoio`
- Verificar porta 8000 livre: `lsof -i:8000`
- Verificar venv ativado

**Frontend não inicia:**
- Limpar cache: `rm -rf .next`
- Verificar porta 3000 livre: `lsof -i:3000`
- Reinstalar dependências se necessário: `npm install`

**Erro de Import no Frontend:**
- Verificar alias `@/lib/db-config` em tsconfig.json
- Limpar cache Next.js: `rm -rf .next`
- Path correto do banco em db-config.ts: `../backend/database/financas_dev.db`

---

## �💡 Lembrete Final

**Este sistema existe para:**
- ✅ Facilitar rollback de mudanças mal feitas
- ✅ Manter histórico detalhado de modificações
- ✅ Garantir rastreabilidade completa
- ✅ Proteger código em produção
- ✅ Permitir trabalho incremental seguro
- ✅ **PREVENIR REGRESSÕES COM VALIDAÇÃO PRÉ-DEPLOY** ⭐

**SEMPRE antes de deploy:**
1. ✅ Versionar mudanças críticas (`version_manager.py`)
2. ✅ **Validar upload funciona** (`pre_deploy_validation.sh`) ⭐
3. ✅ Validar estrutura (`validate_pre_deploy.sh`)
4. ✅ Fazer backup antes de deploy
5. ✅ Testar manualmente após deploy

**Sempre que começar a trabalhar no projeto, leia este arquivo primeiro!** 🎯
