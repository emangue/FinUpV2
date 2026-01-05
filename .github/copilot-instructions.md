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

## �🔍 Comandos Úteis para o AI

```bash
# Ver status do versionamento
python scripts/version_manager.py status

# Listar mudanças pendentes
ls -la changes/

# Ver histórico de versões
git tag -l "v*" --sort=-version:refname | head -10

# Ver última versão commitada
git describe --tags --abbrev=0

# Verificar arquivos em modo -dev
grep -r "\-dev" app/ --include="*.py" | head -5
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

## 🚀 Iniciar/Parar Servidores (PROCESSO OTIMIZADO)

### ⚡ COMANDO ÚNICO - Quando usuário pedir "ligar servidores"

**SEMPRE usar este comando único:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_start.sh && ./quick_start.sh
```

**O que faz automaticamente:**
- ✅ Limpa portas 8000 e 3000
- ✅ Inicia Backend FastAPI (porta 8000) com venv
- ✅ Inicia Frontend Next.js (porta 3000)
- ✅ Roda em background com logs
- ✅ Salva PIDs para controle

**Parar servidores:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && chmod +x quick_stop.sh && ./quick_stop.sh
```

### URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

**Login padrão:** admin@email.com / admin123

### 🔄 Restart Automático Após Modificações

**OBRIGATÓRIO: Reiniciar servidores automaticamente após:**
- Modificação em arquivos críticos (models.py, routes.py, schemas)
- Finalização de mudanças com `version_manager.py finish`
- Instalação de novas dependências
- Mudanças em configurações (config.py)
- Atualizações no schema do banco

**Comando completo de restart:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4 && ./quick_stop.sh && ./quick_start.sh
```

### 📋 Monitoramento de Logs

```bash
# Backend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/backend.log

# Frontend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/frontend.log
```

### 🚨 Troubleshooting Rápido

**Portas ocupadas:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Banco não inicializado:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev
source venv/bin/activate
python init_db.py
```

### Integração com Workflow de Versionamento

**No `version_manager.py finish`, sempre incluir:**
1. Finalizar mudança e commit
2. **RESTART AUTOMÁTICO:** `./quick_stop.sh && ./quick_start.sh`
3. Validar que servidores estão operacionais (verificar logs)

---

## �📚 Referências Rápidas

- **Documentação completa:** `CONTRIBUTING.md`
- **Template de mudanças:** `changes/TEMPLATE.md`
- **Histórico de bugs:** `BUGS.md` (manter como referência histórica)
- **Status do projeto:** `STATUSPROJETO.md`
- **Arquitetura:** `ESTRUTURA_PROJETO.md`

---

## 💡 Lembrete Final

**Este sistema existe para:**
- ✅ Facilitar rollback de mudanças mal feitas
- ✅ Manter histórico detalhado de modificações
- ✅ Garantir rastreabilidade completa
- ✅ Proteger código em produção
- ✅ Permitir trabalho incremental seguro

**Sempre que começar a trabalhar no projeto, leia este arquivo primeiro!** 🎯
