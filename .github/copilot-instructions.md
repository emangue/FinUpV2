# 🤖 Instruções GitHub Copilot - Sistema Modular de Finanças v5

## ⚠️ REGRAS CRÍTICAS - SEMPRE SEGUIR

### � ESTRUTURA DE PASTAS - REGRA OBRIGATÓRIA (NOVA ORGANIZAÇÃO 22/01/2026)

**REGRA CRÍTICA:** SEMPRE respeitar a estrutura organizada do projeto ao criar novos arquivos.

**✅ ESTRUTURA OFICIAL:**
```
ProjetoFinancasV5/
├── 📚 docs/                    # TODA documentação
│   ├── architecture/           # Arquitetura, modularidade, performance
│   ├── deploy/                # Deploy, servidores, VPS
│   ├── features/              # Features, autenticação, marcações
│   └── planning/              # Sprints, TODOs, relatórios
│
├── 🔧 scripts/                 # TODOS os scripts
│   ├── database/              # Migrations, fixes, populações
│   ├── deploy/                # quick_start, quick_stop, backup_daily, audit
│   ├── maintenance/           # Limpeza, reorganização, pausas
│   ├── migration/             # Migrações de dados, copiar usuários
│   └── testing/               # Testes standalone, validações
│
├── 🗂️ temp/                    # Arquivos TEMPORÁRIOS (ignorados no git)
│   ├── logs/                  # backend.log, frontend.log
│   └── pids/                  # backend.pid, frontend.pid
│
├── 📱 app_dev/                 # Aplicação (backend + frontend)
├── 📂 _arquivos_historicos/    # Histórico e backups
└── 📖 README.md               # Documentação principal
```

**🎯 REGRAS OBRIGATÓRIAS AO CRIAR ARQUIVOS:**

1. **Documentação (.md):**
   - ✅ SEMPRE em `docs/`
   - Deploy/VPS → `docs/deploy/`
   - Arquitetura/DB → `docs/architecture/`
   - Features/Planos → `docs/features/`
   - Sprints/TODOs → `docs/planning/`
   - ❌ NUNCA criar `.md` na raiz

2. **Scripts (.py, .sh):**
   - ✅ SEMPRE em `scripts/`
   - Migrations/fixes DB → `scripts/database/`
   - Start/stop/backup → `scripts/deploy/`
   - Limpeza/manutenção → `scripts/maintenance/`
   - Testes → `scripts/testing/`
   - ❌ NUNCA criar scripts na raiz

3. **Arquivos Temporários:**
   - ✅ SEMPRE em `temp/`
   - Logs → `temp/logs/` (backend.log, frontend.log)
   - PIDs → `temp/pids/` (backend.pid, frontend.pid)
   - ❌ NUNCA criar `.log` ou `.pid` na raiz
   - ⚠️ `temp/` está no `.gitignore`

4. **Aplicação:**
   - ✅ Backend → `app_dev/backend/`
   - ✅ Frontend → `app_dev/frontend/`
   - ❌ NUNCA misturar com docs/scripts

**🚫 PROIBIÇÕES ABSOLUTAS:**

```bash
# ❌ NUNCA FAZER ISSO:
touch STATUS_DEPLOY.md              # Criar .md na raiz
touch fix_something.py              # Criar script na raiz
echo "log" > backend.log            # Criar log na raiz
echo "123" > backend.pid            # Criar PID na raiz

# ✅ SEMPRE FAZER ASSIM:
touch docs/deploy/STATUS_DEPLOY.md
touch scripts/database/fix_something.py
echo "log" > temp/logs/backend.log
echo "123" > temp/pids/backend.pid
```

**📋 Checklist Antes de Criar Arquivo:**

- [ ] ✅ É documentação? → Vai em `docs/`
- [ ] ✅ É script? → Vai em `scripts/`
- [ ] ✅ É log/PID? → Vai em `temp/`
- [ ] ✅ É código de aplicação? → Vai em `app_dev/`
- [ ] ✅ Path está correto e categorizado?

**🔍 VALIDAÇÃO:**

Se o usuário reportar "arquivos na raiz", SEMPRE:
1. Verificar: `ls -1 | grep -E "\.(md|py|sh|log|pid)$"`
2. Mover para local correto: `mv arquivo.md docs/categoria/`
3. Atualizar referências em scripts
4. Confirmar: `ls -1 | wc -l` (deve ter ~12 itens na raiz)

---

### �🔄 GESTÃO AUTOMÁTICA DE VERSÃO DA PASTA (REGRA OBRIGATÓRIA)

**Quando o usuário renomear a pasta do projeto (ex: V5 → V6), você DEVE atualizar todas as referências automaticamente.**

#### Scripts Disponíveis:

1. **`check_version.py`** - Valida se todas as referências estão corretas
2. **`fix_version.py`** - Corrige automaticamente todas as referências

#### Arquivos que São Atualizados:

- ✅ `quick_start.sh` - Script de inicialização
- ✅ `quick_stop.sh` - Script de parada  
- ✅ `backup_daily.sh` - Script de backup
- ✅ `app_dev/backend/.env` - Variáveis de ambiente
- ✅ `app_dev/backend/app/core/config.py` - Configuração backend
- ✅ `app_dev/frontend/src/lib/db-config.ts` - Configuração frontend

#### Workflow Obrigatório ao Detectar Mudança de Versão:

```bash
# 1. Usuário renomeou: ProjetoFinancasV5 → ProjetoFinancasV6

# 2. VOCÊ DEVE executar:
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV6
python check_version.py              # Valida inconsistências

# 3. Se houver inconsistências:
python fix_version.py --dry-run      # Simula correções (mostrar ao usuário)
python fix_version.py --backup       # Aplica com backup

# 4. Reiniciar servidores:
./quick_stop.sh && sleep 2 && ./quick_start.sh

# 5. Validar novamente:
python check_version.py
```

#### Detecção Automática:

Os scripts detectam a versão automaticamente baseado no nome da pasta:
- `ProjetoFinancasV5` → detecta **V4**
- `ProjetoFinancasV5` → detecta **V5**  
- `ProjetoFinancasV6` → detecta **V6**

#### Quando Executar:

- 🔄 **SEMPRE** que detectar que o path atual contém versão diferente dos arquivos
- 🔄 Quando o usuário mencionar que renomeou a pasta
- 🔄 Se encontrar erros de "arquivo não encontrado" com paths de versão antiga
- 🔄 Antes de qualquer modificação em arquivos de config

#### Output Esperado do check_version.py:

```
🔍 RELATÓRIO DE VALIDAÇÃO DE VERSÃO
======================================================================

📁 Versão atual detectada: V6

❌ Arquivos com versão incorreta (3):
   app_dev/backend/.env
      Linha 11: Encontrado V5 (deveria ser V6)
   
📊 Resumo: 3 corretos, 3 incorretos

💡 Para corrigir: python fix_version.py
```

#### 🚫 NUNCA:

- Modificar manualmente os paths em cada arquivo (use os scripts!)
- Ignorar inconsistências de versão
- Rodar servidores sem corrigir versões
- Esquecer de reiniciar servidores após correção

---

### � FILTROS DE DATA - REGRA INVIOLÁVEL (NUNCA USAR CAMPO DATA)

**REGRA CRÍTICA:** JAMAIS usar o campo `Data` (string DD/MM/YYYY) para filtros SQL.

**✅ SEMPRE usar:**
- `JournalEntry.Ano == year` (campo integer)
- `JournalEntry.Mes == month` (campo integer, 1-12)
- `JournalEntry.MesFatura == "YYYYMM"` (campo string formatado, apenas se necessário)

**❌ NUNCA usar:**
```python
# ❌ PROIBIDO - Campo Data é string DD/MM/YYYY
JournalEntry.Data.like(f'%/{year}')
JournalEntry.Data.like(f'%/{month:02d}/{year}')
date_filter baseado em JournalEntry.Data
_build_date_filter() que usa campo Data
```

**✅ CORRETO:**
```python
# ✅ Filtros eficientes e confiáveis
filters = [
    JournalEntry.user_id == user_id,
    JournalEntry.Ano == year,           # Ano como integer
    JournalEntry.Mes == month,          # Mês como integer (se específico)
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0
]

# Para ano inteiro (YTD)
filters = [
    JournalEntry.user_id == user_id,
    JournalEntry.Ano == year,           # Só ano, sem filtro de mês
    JournalEntry.CategoriaGeral == 'Despesa',
    JournalEntry.IgnorarDashboard == 0
]
```

**Por quê essa regra existe:**
- ❌ Campo `Data` é string "DD/MM/YYYY" → filtros lentos e propensos a erros
- ✅ Campos `Ano` e `Mes` são integers → filtros rápidos e precisos
- ❌ LIKE patterns em strings são ineficientes 
- ✅ Comparações de integers são otimizadas pelo banco

**Checklist obrigatório antes de qualquer query:**
- [ ] ✅ Usa `JournalEntry.Ano == year`?
- [ ] ✅ Se mês específico, usa `JournalEntry.Mes == month`?
- [ ] ❌ NÃO usa campo `Data`?
- [ ] ❌ NÃO usa `_build_date_filter()`?
- [ ] ❌ NÃO usa `.like()` em datas?

---

### �💾 BACKUP DIÁRIO AUTOMÁTICO (REGRA OBRIGATÓRIA)

**SEMPRE executar backup diário no início de cada sessão de trabalho:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && chmod +x backup_daily.sh && ./backup_daily.sh
```

**O que faz:**
- ✅ Cria backup diário do banco de dados (um por dia)
- ✅ Mantém últimos 7 dias automaticamente
- ✅ Armazena em `app_dev/backend/database/backups_daily/`
- ✅ Verifica se já existe backup de hoje (não duplica)

**Quando executar:**
- 🔄 No início de cada sessão de trabalho (antes de qualquer modificação)
- 🔄 Antes de executar migrations/regenerações
- 🔄 Antes de modificar schema do banco
- 🔄 Antes de executar scripts que modificam dados

**Procedimento Obrigatório:**
1. Verificar se backup de hoje existe: `ls -lh app_dev/backend/database/backups_daily/`
2. Se não existir: Executar `./backup_daily.sh`
3. Confirmar sucesso antes de prosseguir com modificações

**🚫 NUNCA:**
- Pular backup antes de modificações críticas
- Deletar pasta `backups_daily/` manualmente
- Modificar banco sem backup do dia atual

### � TIPOS DE DOCUMENTO - ESTRATÉGIAS DIFERENTES (REGRA INVIOLÁVEL)

**NUNCA usar a mesma lógica de hash/deduplicação para extrato e fatura!**

Os dois tipos de documento têm requisitos **fundamentalmente opostos** para detecção de duplicatas:

#### 🏦 EXTRATOS (Extrato Bancário, Conta Corrente)

**Característica:** Transações únicas com detalhes específicos no nome

**SEMPRE usar:** `lancamento` COMPLETO (texto integral)

**Por quê:** Nomes similares com datas/detalhes diferentes são transações DIFERENTES

**Exemplo CRÍTICO:**
```python
# ❌ ERRADO - Vai gerar o mesmo hash para transações diferentes!
estabelecimento_base = "PIX TRANSF EMANUEL"  # Remove data
hash1 = hash("15/10/2025|PIX TRANSF EMANUEL|1000.00")
hash2 = hash("30/10/2025|PIX TRANSF EMANUEL|1000.00")
# hash1 == hash2 → FALSO POSITIVO (são PIX diferentes!)

# ✅ CORRETO - Preserva texto completo
lancamento1 = "PIX TRANSF EMANUEL15/10"  # Data no nome
lancamento2 = "PIX TRANSF EMANUEL30/10"  # Data diferente
hash1 = hash("15/10/2025|PIX TRANSF EMANUEL15/10|1000.00")
hash2 = hash("30/10/2025|PIX TRANSF EMANUEL30/10|1000.00")
# hash1 != hash2 → CORRETO (são transações diferentes)
```

**Casos Reais:**
- `PIX TRANSF EMANUEL15/10` vs `PIX TRANSF EMANUEL30/10` → Diferentes
- `TED BANCO XP 15/10` vs `TED BANCO XP 30/10` → Diferentes
- `Transferência Azul 01/12` vs `Transferência Azul 15/12` → Diferentes

#### 💳 FATURAS (Cartão de Crédito)

**Característica:** Parcelas do mesmo estabelecimento com formatos variados

**SEMPRE usar:** `estabelecimento_base` (SEM parcela)

**Por quê:** Formatos de parcela diferentes representam a MESMA transação base

**Exemplo CRÍTICO:**
```python
# ✅ CORRETO - Normaliza formatos de parcela
estabelecimento1 = "LOJA (1/12)"  # Formato antigo (parênteses)
estabelecimento2 = "LOJA 01/12"   # Formato novo (espaço)
estabelecimento_base1 = extrair_base("LOJA (1/12)")  # → "LOJA"
estabelecimento_base2 = extrair_base("LOJA 01/12")   # → "LOJA"
hash1 = hash("15/10/2025|LOJA|100.00")
hash2 = hash("15/10/2025|LOJA|100.00")
# hash1 == hash2 → CORRETO (mesma compra, formato diferente)

# ❌ ERRADO - Vai ver como transações diferentes!
lancamento1 = "LOJA (1/12)"
lancamento2 = "LOJA 01/12"
hash1 = hash("15/10/2025|LOJA (1/12)|100.00")
hash2 = hash("15/10/2025|LOJA 01/12|100.00")
# hash1 != hash2 → FALSO NEGATIVO (mesma transação não detectada!)
```

**Casos Reais:**
- `NETFLIX (1/1)` vs `NETFLIX 01/01` → Mesma transação
- `MERCADO (3/12)` vs `MERCADO 03/12` → Mesma transação
- `UBER (2/5)` vs `UBER 02/05` → Mesma transação

#### 🚨 IMPLEMENTAÇÃO OBRIGATÓRIA - Lógica Condicional

**Em QUALQUER código que gere/valide IdTransacao, SEMPRE usar:**

```python
# ✅ CORRETO - Estratégia condicional
if tipo_documento == 'extrato':
    # Extrato: preserva TUDO
    estabelecimento_para_hash = lancamento  # Completo
else:
    # Fatura: remove parcela
    estabelecimento_para_hash = extrair_estabelecimento_base(lancamento)

id_transacao = generate_id_transacao(
    data=data,
    estabelecimento=estabelecimento_para_hash,
    valor=valor,
    sequencia=sequencia
)
```

**Arquivos que DEVEM ter lógica condicional:**
- ✅ `app/domains/upload/processors/marker.py` - Upload de novos arquivos
- ✅ `regenerate_sql.py` - Regeneração do banco
- ✅ `app/domains/transactions/service.py` - Qualquer validação de duplicatas
- ✅ Scripts de migração/regeneração de hashes

**🚫 PROIBIÇÕES ABSOLUTAS:**

```python
# ❌ NUNCA fazer isso:
estabelecimento_base = extrair_base(lancamento)  # Para TODOS os tipos
hash_all = hash(f"{data}|{estabelecimento_base}|{valor}")

# ❌ NUNCA usar lancamento completo para faturas:
if tipo_documento == 'fatura':
    hash_fatura = hash(f"{data}|{lancamento}|{valor}")  # Vai quebrar parcelas!

# ❌ NUNCA usar estabelecimento_base para extratos:
if tipo_documento == 'extrato':
    estab_base = extrair_base(lancamento)
    hash_extrato = hash(f"{data}|{estab_base}|{valor}")  # Vai gerar falsos positivos!
```

**📋 Checklist Antes de Modificar Hash/Deduplicação:**

- [ ] ✅ Código usa lógica condicional baseada em `tipo_documento`?
- [ ] ✅ Extrato usa `lancamento` completo?
- [ ] ✅ Fatura usa `estabelecimento_base` (sem parcela)?
- [ ] ✅ Testei com ambos os tipos de documento?
- [ ] ✅ Validei que extratos não geram falsos positivos?
- [ ] ✅ Validei que faturas normalizam parcelas diferentes?

**🎯 Lembre-se:** Esta separação existe porque:
- **Extratos** têm transações únicas com informações temporais no nome
- **Faturas** têm parcelas da mesma compra com formatações variadas

**Misturar as estratégias causa:**
- ❌ Falsos positivos em extratos (transações diferentes vistas como duplicatas)
- ❌ Falsos negativos em faturas (parcelas da mesma compra não detectadas)

---

### �🗄️ BANCO DE DADOS ÚNICO - REGRA INVIOLÁVEL

**Path absoluto único para TODO o sistema:**
```
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db
```

**Arquivos de configuração:**
1. **Backend:** `app_dev/backend/app/core/config.py` → `DATABASE_PATH`
2. **Frontend:** `app_dev/frontend/src/lib/db-config.ts` → `DB_ABSOLUTE_PATH`

**🚫 NUNCA:**
- Criar outro banco de dados em QUALQUER local:
  * ❌ `app_dev/financas.db`
  * ❌ `app_dev/financas_dev.db`
  * ❌ `app_dev/backend/financas.db`
  * ❌ Qualquer variação de path
- Usar paths relativos diferentes
- Modificar apenas um dos arquivos
- Criar cópias do banco
- Fazer backup manual (usar scripts de backup)

**✅ SEMPRE:**
- Usar path absoluto completo: `app_dev/backend/database/financas_dev.db`
- Se mudar, mudar nos 2 arquivos simultaneamente
- Testar backend E frontend após mudanças
- Ver `DATABASE_CONFIG.md` para detalhes
- Verificar `.gitignore` para ignorar duplicados

**🔍 VERIFICAÇÃO PERIÓDICA:**
```bash
# DEVE retornar APENAS 1 arquivo
find app_dev -name "*.db" -type f | grep -v node_modules
# Resultado esperado: app_dev/backend/database/financas_dev.db
```

---

### 🔍 EXPLORAÇÃO ANTES DE IMPLEMENTAÇÃO - REGRA OBRIGATÓRIA

**REGRA CRÍTICA:** SEMPRE explorar domínios existentes antes de criar novas funcionalidades.

**⚠️ PROBLEMA COMUM:** Criar APIs/funcionalidades duplicadas quando já existem domínios implementados.

#### ✅ PROCESSO OBRIGATÓRIO ANTES DE IMPLEMENTAR:

**1. 🕵️ INVESTIGAR ARQUITETURA EXISTENTE:**
```bash
# Verificar domínios disponíveis
ls app_dev/backend/app/domains/

# Verificar modelos existentes  
find app_dev -name "models.py" | head -10

# Verificar APIs registradas
grep "router" app_dev/backend/app/main.py

# Testar APIs existentes
curl http://localhost:8000/api/v1/grupos/
curl http://localhost:8000/api/v1/categories/
```

**2. 📋 CHECKLIST ANTES DE CRIAR NOVO DOMÍNIO:**
- [ ] ✅ Verifiquei se já existe domínio relacionado?
- [ ] ✅ Li os modelos existentes (`**/models.py`)?
- [ ] ✅ Testei APIs existentes (`curl /api/v1/...`)?  
- [ ] ✅ Procurei por tabelas relacionadas no banco?
- [ ] ✅ Verifiquei se posso ESTENDER em vez de DUPLICAR?

#### 🎯 EXEMPLO REAL - LIÇÃO APRENDIDA:

**❌ ERRO COMETIDO:**
- Criado `/api/v1/classification/groups-with-types` 
- Buscou dados em `journal_entries` (dados inconsistentes)
- Ignorou domínio `grupos` existente com `base_grupos_config`

**✅ SOLUÇÃO CORRETA:**
- Usar `/api/v1/grupos/` (domínio existente)
- Buscar tipos em `base_grupos_config` (fonte oficial)  
- Estender funcionalidade em vez de duplicar

#### 🚫 SINAIS DE VIOLAÇÃO DESTA REGRA:

**APIs duplicadas:**
- Criar `/api/categories/new` quando `/api/categories/` já existe
- Fazer `/api/usuarios/` quando `/api/users/` já funciona
- Buscar dados em `journal_entries` quando existem tabelas específicas

**Tabelas/modelos duplicados:**
- Criar `NewModel` quando `ExistingModel` já resolve
- Duplicar campos entre modelos
- Criar tabelas temporárias quando existem oficiais

**Lógica duplicada:**
- Reescrever validações que já existem
- Criar helpers quando já existem em `/core/` ou `/shared/`

#### ⚡ COMMANDS ÚTEIS PARA EXPLORAÇÃO:

```bash
# Backend - Explorar domínios
find app_dev/backend/app/domains -name "*.py" | head -20

# Backend - Ver todas as APIs
curl http://localhost:8000/docs | grep "/api/"

# Banco - Ver todas as tabelas  
sqlite3 app_dev/backend/database/financas_dev.db ".tables"

# Banco - Ver schema de tabela específica
sqlite3 app_dev/backend/database/financas_dev.db ".schema base_grupos_config"

# Frontend - Ver componentes existentes
find app_dev/frontend/src -name "*.tsx" | grep -v node_modules | head -20
```

#### 🎯 MANTRA OBRIGATÓRIO:

> **"EXPLORE ANTES DE IMPLEMENTAR"**  
> 1. Existe domínio relacionado?  
> 2. Existe API similar?  
> 3. Existe tabela oficial?  
> 4. Posso estender em vez de duplicar?

#### 🏆 BENEFÍCIOS DE SEGUIR ESTA REGRA:

- ✅ **Evita duplicação** de código e APIs
- ✅ **Mantém arquitetura limpa** e consistente
- ✅ **Reutiliza** validações e lógicas existentes
- ✅ **Economiza tempo** de desenvolvimento
- ✅ **Reduz bugs** por usar código já testado

---

## 🧹 LIMPEZA E ORGANIZAÇÃO - LIÇÕES APRENDIDAS

### ⚠️ ARQUIVOS QUE NÃO DEVEM EXISTIR

**Após refatoração modular, estes arquivos/pastas foram REMOVIDOS e NÃO devem ser recriados:**

#### Backend - Rotas Antigas (REMOVIDAS):
```
❌ app_dev/backend/app/routers/          # Substituído por domains/*/router.py
   ├── auth.py
   ├── cartoes.py
   ├── compatibility.py
   ├── dashboard.py
   ├── exclusoes.py
   ├── marcacoes.py
   ├── transactions.py
   ├── upload.py
   ├── upload_classifier.py
   └── users.py

❌ app_dev/backend/app/models/           # Substituído por domains/*/models.py
❌ app_dev/backend/app/schemas/          # Substituído por domains/*/schemas.py
```

#### Backend - Configurações Duplicadas (REMOVIDAS):
```
❌ app_dev/backend/app/config.py         # Usar app/core/config.py
❌ app_dev/backend/app/database.py       # Usar app/core/database.py
❌ app_dev/backend/app/dependencies.py   # Usar app/shared/dependencies.py
```

#### Frontend - Rotas API Antigas (REMOVIDAS):
```
❌ app_dev/frontend/src/app/api/cartoes/
❌ app_dev/frontend/src/app/api/categories/
❌ app_dev/frontend/src/app/api/compatibility/
❌ app_dev/frontend/src/app/api/dashboard/
❌ app_dev/frontend/src/app/api/exclusoes/
❌ app_dev/frontend/src/app/api/grupos/
❌ app_dev/frontend/src/app/api/health/
❌ app_dev/frontend/src/app/api/marcacoes/
❌ app_dev/frontend/src/app/api/transactions/
❌ app_dev/frontend/src/app/api/upload/
❌ app_dev/frontend/src/app/api/users/

✅ ÚNICO permitido: app_dev/frontend/src/app/api/[...proxy]/
```

#### Databases Duplicados (REMOVIDOS):
```
❌ app_dev/financas.db
❌ app_dev/financas_dev.db
❌ app_dev/backend/financas.db
❌ *.db.backup_* (backups manuais na pasta database/)

✅ ÚNICO oficial: app_dev/backend/database/financas_dev.db
```

### 🚨 SE VOCÊ CRIAR ALGUM DESSES ARQUIVOS:

**PARE IMEDIATAMENTE e pergunte:**
1. Por que estou criando isso?
2. Já existe equivalente na nova arquitetura?
3. Devo usar domínio isolado ou proxy genérico?
4. Estou duplicando funcionalidade?

**LEMBRE-SE:**
- Backend: Use `domains/*/router.py` (NUNCA `app/routers/`)
- Frontend: Use proxy `[...proxy]` (NUNCA rotas individuais)
- Config: Use `app/core/` e `app/shared/` (NUNCA duplicar na raiz)
- Database: Use APENAS o path oficial (NUNCA criar outros)

---

## 🏗️ ARQUITETURA MODULAR - BACKEND

### Estrutura de Domínios (DDD - Domain-Driven Design)

```
app_dev/backend/app/
├── core/                      # ✅ Configurações globais (NUNCA lógica de negócio)
│   ├── config.py              # Settings (DATABASE_PATH aqui)
│   ├── database.py            # SQLAlchemy setup
│   └── __init__.py
│
├── domains/                   # ✅ Domínios de negócio ISOLADOS
│   ├── transactions/          # Domínio de transações
│   │   ├── models.py          # JournalEntry model
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── repository.py      # TODAS as queries SQL
│   │   ├── service.py         # TODA lógica de negócio
│   │   ├── router.py          # Endpoints FastAPI
│   │   └── __init__.py
│   │
│   ├── users/                 # Domínio de usuários
│   ├── categories/            # Domínio de categorias
│   ├── cards/                 # Domínio de cartões
│   └── upload/                # Domínio de upload
│
├── shared/                    # ✅ Compartilhado entre domínios
│   ├── dependencies.py        # get_current_user_id, etc
│   └── __init__.py
│
└── main.py                    # FastAPI app setup
```

### Princípios de Isolamento de Domínios

**1. CADA DOMÍNIO É AUTOCONTIDO:**
```python
# ✅ CORRETO - Domínio transactions isolado
from app.domains.transactions.models import JournalEntry
from app.domains.transactions.service import TransactionService

# ❌ ERRADO - Não importar de outros domínios
from app.domains.users.models import User  # NÃO fazer isso em transactions
```

**2. CAMADAS OBRIGATÓRIAS (Repository → Service → Router):**

**Repository (Queries SQL isoladas):**
```python
# domains/transactions/repository.py
class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: str, user_id: int):
        return self.db.query(JournalEntry).filter(...).first()
    
    # TODAS as queries SQL aqui
```

**Service (Lógica de negócio isolada):**
```python
# domains/transactions/service.py
class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def update_transaction(self, id: str, user_id: int, data):
        # Validações de negócio
        # Cálculos
        # Chamadas ao repository
```

**Router (Apenas validação HTTP):**
```python
# domains/transactions/router.py
@router.patch("/{id}")
def update(id: str, data: UpdateSchema, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.update_transaction(id, 1, data)
```

**3. REGRAS DE IMPORTAÇÃO:**

```python
# ✅ CORRETO
from app.core.database import Base, get_db
from app.shared.dependencies import get_current_user_id
from .models import JournalEntry  # Mesmo domínio
from .repository import TransactionRepository  # Mesmo domínio

# ❌ ERRADO
from app.models import JournalEntry  # Modelo monolítico antigo
from ..users.models import User  # Import cruzado entre domínios
from app.domains.categories import *  # Import * é proibido
```

### Quando Modificar um Domínio

**Cenário:** Adicionar campo `categoria` em transações

**✅ Passos corretos:**
1. Modificar `domains/transactions/models.py` (adicionar coluna)
2. Atualizar `domains/transactions/schemas.py` (adicionar campo nos schemas)
3. Modificar `domains/transactions/repository.py` (queries se necessário)
4. Atualizar `domains/transactions/service.py` (validações/cálculos)
5. Testar `domains/transactions/router.py`
6. **PARAR:** Não precisa tocar em users, categories, cards, upload!

**Arquivos afetados:** ~5 arquivos (todos no mesmo domínio)
**Antes da modularização:** ~15 arquivos espalhados

---

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
- Refatorações massivas de domínios

### MINOR (x.Y.0)
- Novas funcionalidades em domínios
- Novos campos no banco (não-breaking)
- Novos domínios/módulos

### PATCH (x.y.Z)
- Bug fixes em domínios específicos
- Melhorias de performance
- Correções de typos

---

## 🚫 PROIBIÇÕES ABSOLUTAS

### 1. Imports Cruzados entre Domínios
```python
# ❌ PROIBIDO
# Em domains/transactions/service.py
from app.domains.users.models import User  # NÃO!

# ✅ CORRETO
# Use shared/ para funcionalidades compartilhadas
from app.shared.dependencies import get_current_user_id
```

### 2. Lógica de Negócio no Router
```python
# ❌ PROIBIDO
@router.post("/")
def create(data: Schema, db: Session = Depends(get_db)):
    # Cálculos complexos aqui
    valor_positivo = abs(data.valor)  # NÃO!
    # Validações aqui
    if not data.grupo:  # NÃO!
        raise HTTPException(...)
    
    transaction = Model(**data.dict())
    db.add(transaction)
    db.commit()
    return transaction

# ✅ CORRETO
@router.post("/")
def create(data: Schema, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.create(data)  # Lógica no service
```

### 3. Queries SQL no Service
```python
# ❌ PROIBIDO
class TransactionService:
    def get_transaction(self, id: str):
        # Query SQL aqui
        return self.db.query(Model).filter(...).first()  # NÃO!

# ✅ CORRETO
class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
    
    def get_transaction(self, id: str):
        return self.repository.get_by_id(id)  # Query no repository
```

### 4. Modificar Modelos de Outros Domínios
```python
# ❌ PROIBIDO
# Em domains/transactions/models.py
from app.domains.categories.models import BaseMarcacao  # NÃO!

class JournalEntry(Base):
    categoria = relationship(BaseMarcacao)  # NÃO criar relationships cruzadas!
```

### 5. Usar Paths Relativos para Database
```python
# ❌ PROIBIDO
DATABASE_PATH = "../database/financas.db"
DATABASE_PATH = "./financas.db"
DB_PATH = Path(__file__).parent / "database" / "financas.db"

# ✅ CORRETO - Path absoluto único
DATABASE_PATH = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db")
```

---

## ✅ PADRÕES OBRIGATÓRIOS

### 1. Criar Novo Domínio

```bash
mkdir -p app_dev/backend/app/domains/novo_dominio
```

**Arquivos obrigatórios:**
1. `models.py` - Modelo SQLAlchemy
2. `schemas.py` - Pydantic schemas (Create, Update, Response)
3. `repository.py` - Queries SQL isoladas
4. `service.py` - Lógica de negócio
5. `router.py` - Endpoints FastAPI
6. `__init__.py` - Exports

**Template de `__init__.py`:**
```python
from .models import NovoModel
from .schemas import NovoCreate, NovoUpdate, NovoResponse
from .service import NovoService
from .repository import NovoRepository
from .router import router

__all__ = [
    "NovoModel",
    "NovoCreate",
    "NovoUpdate",
    "NovoResponse",
    "NovoService",
    "NovoRepository",
    "router",
]
```

**Registrar em `main.py`:**
```python
from app.domains.novo_dominio.router import router as novo_router
app.include_router(novo_router, prefix="/api/v1")
```

### 2. Adicionar Nova Funcionalidade a Domínio Existente

**Exemplo:** Adicionar endpoint de estatísticas em transactions

1. **Repository** - Adicionar query:
```python
# domains/transactions/repository.py
def get_statistics(self, user_id: int, filters):
    return self.db.query(
        func.count(JournalEntry.id),
        func.sum(JournalEntry.Valor)
    ).filter(JournalEntry.user_id == user_id).first()
```

2. **Service** - Adicionar lógica:
```python
# domains/transactions/service.py
def get_statistics(self, user_id: int, filters):
    count, total = self.repository.get_statistics(user_id, filters)
    return {
        "count": count or 0,
        "total": float(total or 0),
        "average": total / count if count else 0
    }
```

3. **Router** - Adicionar endpoint:
```python
# domains/transactions/router.py
@router.get("/statistics")
def get_stats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_statistics(user_id, {})
```

**Arquivos modificados:** 3 (todos no mesmo domínio)
**Impacto:** Zero em outros domínios

---

## 🔍 Checklist de Modificação

Antes de fazer qualquer mudança, perguntar:

- [ ] ✅ Estou modificando apenas um domínio?
- [ ] ✅ Queries SQL estão no repository?
- [ ] ✅ Lógica de negócio está no service?
- [ ] ✅ Router só valida e chama service?
- [ ] ✅ Não estou importando de outros domínios?
- [ ] ✅ Database path é o absoluto único?
- [ ] ✅ Testei o domínio isoladamente?

---

## 🔧 FRONTEND - Configuração Centralizada

### URLs de API (api.config.ts)

**Path:** `app_dev/frontend/src/core/config/api.config.ts`

```typescript
// ✅ ÚNICO lugar onde URLs são definidas
export const API_CONFIG = {
  BACKEND_URL: 'http://localhost:8000',
  API_PREFIX: '/api/v1',
}

export const API_ENDPOINTS = {
  TRANSACTIONS: {
    LIST: `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/list`,
    // ...
  }
}
```

**🚫 NUNCA:**
- Hardcoded URLs em componentes
- `fetch('http://localhost:8000/...')` direto
- URLs diferentes em arquivos diferentes

**✅ SEMPRE:**
- Importar de `@/core/config/api.config`
- Usar `API_ENDPOINTS.TRANSACTIONS.LIST`
- Mudar URL = 1 arquivo apenas

### Proxy Genérico

**Path:** `app_dev/frontend/src/app/api/[...proxy]/route.ts`

**Benefício:** Substitui 20+ rotas individuais por 1 arquivo

```typescript
// ✅ ANTES: 1 arquivo
// app/api/[...proxy]/route.ts

// ❌ DEPOIS: 20+ arquivos (não fazer)
// app/api/transactions/route.ts
// app/api/dashboard/route.ts
// app/api/upload/route.ts
// ...
```

---

## � FRONTEND - Arquitetura Feature-Based

### Estrutura de Features (Isolamento por Domínio)

```
app_dev/frontend/src/
├── core/                          # ✅ Configurações e utilitários globais
│   ├── config/
│   │   └── api.config.ts          # URLs centralizadas
│   └── types/
│       └── shared.types.ts        # Types compartilhados
│
├── features/                      # ✅ Domínios de negócio ISOLADOS
│   ├── transactions/              # Feature de transações
│   │   ├── components/            # Componentes específicos
│   │   │   ├── edit-transaction-modal.tsx
│   │   │   ├── transaction-filters.tsx
│   │   │   ├── add-group-modal.tsx
│   │   │   └── index.ts           # Export barrel
│   │   ├── hooks/                 # Hooks customizados
│   │   ├── services/              # Lógica de API
│   │   ├── types/                 # Types específicos
│   │   └── index.ts               # Export principal
│   │
│   ├── dashboard/                 # Feature de dashboard
│   │   ├── components/
│   │   │   ├── budget-vs-actual.tsx
│   │   │   ├── category-expenses.tsx
│   │   │   ├── chart-area-interactive.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   ├── upload/                    # Feature de upload
│   │   ├── components/
│   │   │   ├── upload-dialog.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   │
│   └── settings/                  # Feature de configurações
│       └── components/
│           └── index.ts
│
└── components/                    # ✅ Componentes COMPARTILHADOS apenas
    ├── dashboard-layout.tsx       # Layout global
    ├── app-sidebar.tsx            # Sidebar global
    ├── nav-main.tsx               # Navegação global
    └── ui/                        # Componentes UI base
        ├── button.tsx
        ├── card.tsx
        └── ...
```

### Princípios de Isolamento de Features

**1. CADA FEATURE É AUTOCONTIDA:**
```typescript
// ✅ CORRETO - Feature transactions isolada
import { EditTransactionModal, TransactionFilters } from '@/features/transactions'

// ❌ ERRADO - Não importar de outras features
import { UploadDialog } from '@/features/upload'  // NÃO fazer em transactions
```

**2. ESTRUTURA OBRIGATÓRIA (components → hooks → services):**

**Components (UI isolada):**
```typescript
// features/transactions/components/edit-transaction-modal.tsx
export function EditTransactionModal({ id, onClose }: Props) {
  const { updateTransaction } = useTransactionService()  // Hook local
  // ...
}
```

**Hooks (Estado e lógica):**
```typescript
// features/transactions/hooks/use-transaction-service.ts
export function useTransactionService() {
  const updateTransaction = async (id: string, data) => {
    // Chama service
  }
  return { updateTransaction }
}
```

**Services (API calls):**
```typescript
// features/transactions/services/transaction-api.ts
import { API_ENDPOINTS } from '@/core/config/api.config'

export async function updateTransaction(id: string, data) {
  const response = await fetch(API_ENDPOINTS.TRANSACTIONS.UPDATE(id), {
    method: 'PATCH',
    body: JSON.stringify(data)
  })
  return response.json()
}
```

**3. REGRAS DE IMPORTAÇÃO:**

```typescript
// ✅ CORRETO
import { API_CONFIG } from '@/core/config/api.config'
import { Button } from '@/components/ui/button'  // UI compartilhado
import { EditTransactionModal } from '@/features/transactions'  // Mesma feature

// ❌ ERRADO
import { EditTransactionModal } from '@/features/transactions/components/edit-transaction-modal'  // Path direto, usar index
import { UploadDialog } from '@/features/upload'  // Import cruzado entre features
```

### Quando Modificar uma Feature

**Cenário:** Adicionar filtro de "Categoria" em transações

**✅ Passos corretos:**
1. Modificar `features/transactions/components/transaction-filters.tsx` (adicionar campo)
2. Atualizar `features/transactions/types/` (adicionar tipo se necessário)
3. Modificar `features/transactions/services/` (adicionar parâmetro na API)
4. Testar `features/transactions/` isoladamente
5. **PARAR:** Não precisa tocar em dashboard, upload, settings!

**Arquivos afetados:** ~3 arquivos (todos na mesma feature)
**Antes da modularização:** ~10 arquivos espalhados

---

## 🚫 PROIBIÇÕES FRONTEND

### 1. Imports Cruzados entre Features
```typescript
// ❌ PROIBIDO
// Em features/transactions/components/list.tsx
import { UploadDialog } from '@/features/upload/components/upload-dialog'  // NÃO!

// ✅ CORRETO
// Criar componente compartilhado se usado por múltiplas features
import { SharedDialog } from '@/components/shared-dialog'
```

### 2. Componentes Compartilhados em Features
```typescript
// ❌ PROIBIDO
// features/transactions/components/button-primary.tsx
// Se usado por 2+ features, NÃO deve estar em nenhuma feature específica

// ✅ CORRETO
// components/ui/button-primary.tsx (compartilhado)
```

### 3. Lógica de API nos Componentes
```typescript
// ❌ PROIBIDO
export function TransactionsList() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/transactions/list')  // NÃO!
      .then(res => res.json())
      .then(setData)
  }, [])
}

// ✅ CORRETO
export function TransactionsList() {
  const { transactions, loading } = useTransactions()  // Hook com service
}
```

### 4. URLs Hardcoded
```typescript
// ❌ PROIBIDO
const response = await fetch('http://localhost:8000/api/v1/transactions')

// ✅ CORRETO
import { API_ENDPOINTS } from '@/core/config/api.config'
const response = await fetch(API_ENDPOINTS.TRANSACTIONS.LIST)
```

---

## ✅ PADRÕES FRONTEND OBRIGATÓRIOS

### 1. Criar Nova Feature

```bash
mkdir -p src/features/nova_feature/{components,hooks,services,types}
```

**Arquivos obrigatórios:**
1. `components/index.ts` - Export barrel de componentes
2. `index.ts` - Export principal da feature

**Template de `components/index.ts`:**
```typescript
export { NovoComponente } from './novo-componente'
export { OutroComponente } from './outro-componente'
export type { NovoComponenteProps } from './novo-componente'
```

**Template de `index.ts` (raiz da feature):**
```typescript
// Components
export * from './components'

// Hooks (quando houver)
// export * from './hooks'

// Services (quando houver)
// export * from './services'

// Types (quando houver)
// export * from './types'
```

### 2. Adicionar Componente a Feature Existente

**Exemplo:** Adicionar modal de exclusão em transactions

1. **Criar componente:**
```typescript
// features/transactions/components/delete-transaction-modal.tsx
export function DeleteTransactionModal({ id, onClose }: Props) {
  // ...
}
```

2. **Adicionar ao index:**
```typescript
// features/transactions/components/index.ts
export { DeleteTransactionModal } from './delete-transaction-modal'
```

3. **Usar na página:**
```typescript
// app/transactions/page.tsx
import { DeleteTransactionModal } from '@/features/transactions'
```

**Arquivos modificados:** 2-3 (todos na mesma feature)
**Impacto:** Zero em outras features

---

## 🔍 Checklist de Modificação Frontend

Antes de fazer qualquer mudança, perguntar:

- [ ] ✅ Estou modificando apenas uma feature?
- [ ] ✅ Componente é específico desta feature (não compartilhado)?
- [ ] ✅ Calls de API estão em services/?
- [ ] ✅ Lógica de estado está em hooks/?
- [ ] ✅ Componentes só fazem UI?
- [ ] ✅ Não estou importando de outras features?
- [ ] ✅ URLs vêm de api.config.ts?
- [ ] ✅ Testei a feature isoladamente?

---

## �🎯 Regras de Versionamento Semântico

### MAJOR (X.0.0)
- Breaking changes no schema do banco
- Mudanças incompatíveis na API
- Refatorações massivas

### MINOR (x.Y.0)
- Novas funcionalidades
- Novos campos no banco (não-breaking)
- Novos blueprints/rotas

### PATCH (x.y.Z)
- Bug fixes em domínios específicos
- Melhorias de performance
- Correções de typos

---

## � CORREÇÕES OBRIGATÓRIAS APÓS REMOVER ARQUIVOS ANTIGOS

### Se você remover arquivos da arquitetura antiga, SEMPRE verificar:

**1. Imports em `app/main.py`:**
```python
# ❌ ERRADO (routers antigos)
from .routers import auth, dashboard, compatibility

# ✅ CORRETO (apenas domínios)
from .domains.transactions.router import router as transactions_router
from .domains.users.router import router as users_router
# ...
```

**2. Imports em `run.py`:**
```python
# ❌ ERRADO
from app.config import settings

# ✅ CORRETO
from app.core.config import settings
```

**3. Imports em scripts (`backend/scripts/*.py`):**
```python
# ❌ ERRADO
from app.database import engine, Base

# ✅ CORRETO
from app.core.database import engine, Base
```

**4. Verificar ausência de rotas antigas em `main.py`:**
```python
# ❌ REMOVER estas linhas se existirem:
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(compatibility.router)
# ...

# ✅ MANTER apenas domínios:
app.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
# ...
```

**5. Testar após qualquer remoção:**
```bash
# Reiniciar servidores
./quick_stop.sh && ./quick_start.sh

# Verificar backend
curl http://localhost:8000/api/health

# Verificar logs
tail -30 backend.log | grep -i error
```

---

## �🚀 Iniciar/Parar Servidores (PROCESSO OTIMIZADO)

### ⚡ COMANDO ÚNICO - Quando usuário pedir "ligar servidores"

**SEMPRE usar este comando único:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && chmod +x quick_start.sh && ./quick_start.sh
```

**O que faz automaticamente:**
- ✅ Limpa portas 8000 e 3000
- ✅ Inicia Backend FastAPI (porta 8000) com venv
- ✅ Inicia Frontend Next.js (porta 3000)
- ✅ Roda em background com logs
- ✅ Salva PIDs para controle

**Parar servidores:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && chmod +x quick_stop.sh && ./quick_stop.sh
```

### URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/api/health

**Login padrão:** admin@email.com / admin123

### 🔄 Restart Automático Após Modificações

**OBRIGATÓRIO: Reiniciar servidores automaticamente após:**
- Modificação em domínios (models.py, routes.py, schemas)
- Finalização de mudanças com `version_manager.py finish`
- Instalação de novas dependências
- Mudanças em configurações (config.py)
- Atualizações no schema do banco

**Comando completo de restart:**

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && ./quick_stop.sh && ./quick_start.sh
```

### 📋 Monitoramento de Logs

```bash
# Backend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/backend.log

# Frontend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/frontend.log
```

### 🚨 Troubleshooting Rápido

**Portas ocupadas:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Banco não inicializado:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev
source venv/bin/activate
python init_db.py
```

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

### ⚡ SEMPRE USAR OS SCRIPTS QUICK

**REGRA OBRIGATÓRIA:** NUNCA rodar servidores manualmente. SEMPRE usar os scripts:

```bash
# Iniciar tudo
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && ./quick_start.sh

# Parar tudo
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && ./quick_stop.sh

# Restart completo
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && ./quick_stop.sh && ./quick_start.sh
```

**O que faz automaticamente:**
- ✅ Limpa portas 8000 e 3000
- ✅ Ativa venv do Python automaticamente
- ✅ Navega para diretórios corretos (backend/ e frontend/)
- ✅ Inicia Backend FastAPI (porta 8000)
- ✅ Inicia Frontend Next.js (porta 3000)
- ✅ Roda em background com logs
- ✅ Salva PIDs para controle

**🚫 NUNCA fazer:**
```bash
# ❌ ERRADO - Vai dar erro "ModuleNotFoundError: No module named 'app'"
cd app_dev && python run.py

# ❌ ERRADO - Vai tentar rodar Flask em vez de FastAPI
cd app_dev && source venv/bin/activate && python run.py

# ✅ CORRETO - Sempre usar os scripts quick
./quick_start.sh
```

**Por quê?**
- Existem 2 arquivos `run.py`:
  - `/app_dev/run.py` (Flask - ANTIGO, não usar)
  - `/app_dev/backend/run.py` (FastAPI - CORRETO)
- Os scripts quick garantem o caminho certo
- Evita erros de módulo não encontrado

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
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5 && ./quick_stop.sh && ./quick_start.sh
```

### 📋 Monitoramento de Logs

```bash
# Backend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/backend.log

# Frontend
tail -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/frontend.log
```

### 🚨 Troubleshooting Rápido

**Portas ocupadas:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Banco não inicializado:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev
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

---

## 🗄️ MIGRATIONS E ALEMBIC - REGRA OBRIGATÓRIA (IMPLEMENTADO 22/01/2026)

### ✅ Alembic Configurado e Operacional

**Path:** `app_dev/backend/migrations/`

**Alembic está configurado para:**
- ✅ Auto-detectar todos os modelos SQLAlchemy
- ✅ Suportar SQLite (dev) e PostgreSQL (prod)
- ✅ Gerar migrations com `--autogenerate`
- ✅ Sincronizar schema entre ambientes

### 🔄 Workflow de Migrations - SEMPRE SEGUIR

**1. Modificar Modelo:**
```python
# app_dev/backend/app/domains/transactions/models.py
class JournalEntry(Base):
    # Adicionar novo campo
    nova_coluna: str = Column(String, nullable=True)
```

**2. Gerar Migration:**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic revision --autogenerate -m "adiciona_nova_coluna_journal"
```

**3. Revisar Migration Gerada:**
```bash
# Verificar arquivo criado em migrations/versions/
ls -lrt migrations/versions/

# Editar se necessário (adicionar defaults, validações, etc)
```

**4. Aplicar Migration:**
```bash
# Local (dev)
alembic upgrade head

# Produção (via SSH)
ssh user@servidor "cd /var/www/finup/app_dev/backend && alembic upgrade head"
```

**5. Validar:**
```bash
# Verificar migration aplicada
alembic current

# Ver histórico
alembic history
```

### 🚫 NUNCA Modificar Schema Manualmente

**❌ PROIBIDO:**
```sql
-- NUNCA fazer isso diretamente no banco!
ALTER TABLE journal_entries ADD COLUMN nova_coluna TEXT;
```

**✅ SEMPRE:**
1. Modificar modelo Python
2. Gerar migration com Alembic
3. Aplicar migration
4. Commitar código + migration file

### 📋 Comandos Alembic Úteis

```bash
# Ver migration atual
alembic current

# Ver histórico de migrations
alembic history --verbose

# Downgrade (reverter)
alembic downgrade -1  # Volta 1 migration
alembic downgrade <revision>  # Volta para revision específica

# Upgrade para versão específica
alembic upgrade <revision>

# Ver SQL da migration (sem executar)
alembic upgrade head --sql

# Criar migration vazia (para dados)
alembic revision -m "popular_dados_iniciais"
```

### 🔧 Migrations de Dados (Data Migrations)

**Para popular/modificar dados (não schema):**

```python
# migrations/versions/XXXX_popular_dados.py
def upgrade():
    op.execute("""
        INSERT INTO base_marcacoes (nome, categoria) 
        VALUES ('Novo Grupo', 'Despesa')
    """)

def downgrade():
    op.execute("""
        DELETE FROM base_marcacoes WHERE nome = 'Novo Grupo'
    """)
```

---

## 🔄 AMBIENTE ESPELHO - POSTGRESQL LOCAL (IMPLEMENTADO 22/01/2026)

### 🎯 Por Que Usar PostgreSQL Local?

**Vantagens de ambiente espelho:**
- ✅ **100% paridade** com produção
- ✅ **Detecta bugs** antes do deploy
- ✅ **Testa migrations** com segurança
- ✅ **Valida tipos** PostgreSQL vs SQLite
- ✅ **Performance real** de queries

**Desvantagens (menores):**
- ⚠️ Setup inicial (instalar PostgreSQL)
- ⚠️ Consumo de recursos (vs SQLite)
- ⚠️ Complexidade de troubleshooting

**Conclusão:** SEMPRE use PostgreSQL local para desenvolvimento sério.

### 📦 Setup PostgreSQL Local

**Opção 1: Postgres.app (macOS - recomendado):**
```bash
# Download de https://postgresapp.com
# Arraste para /Applications
# Inicie o app → crie server → pronto!
```

**Opção 2: Docker (multiplataforma):**
```bash
# docker-compose.yml na raiz do projeto
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: finup_user
      POSTGRES_PASSWORD: sua_senha_dev
      POSTGRES_DB: finup_db_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

# Iniciar
docker-compose up -d postgres

# Parar
docker-compose down
```

**Opção 3: Homebrew (macOS):**
```bash
brew install postgresql@16
brew services start postgresql@16

# Criar database
createdb finup_db_dev
psql finup_db_dev -c "CREATE USER finup_user WITH PASSWORD 'sua_senha_dev';"
psql finup_db_dev -c "GRANT ALL PRIVILEGES ON DATABASE finup_db_dev TO finup_user;"
```

### 🔧 Configurar Aplicação para PostgreSQL

**1. Criar `.env` no backend:**
```bash
# app_dev/backend/.env
DATABASE_URL=postgresql://finup_user:sua_senha_dev@localhost:5432/finup_db_dev
```

**2. Aplicar migrations:**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic upgrade head
```

**3. Migrar dados do SQLite:**
```bash
python scripts/migration/sqlite_to_postgres.py \
  --source sqlite:///path/to/financas_dev.db \
  --target postgresql://finup_user:senha@localhost/finup_db_dev
```

**4. Validar:**
```bash
# Backend deve iniciar normalmente
./scripts/deploy/quick_start.sh

# Verificar logs
tail -f temp/logs/backend.log
```

### 🔄 Alternar Entre SQLite e PostgreSQL

**SQLite (rápido para testes):**
```bash
# Remover/renomear .env
mv app_dev/backend/.env app_dev/backend/.env.postgres
# Reiniciar
./scripts/deploy/quick_stop.sh && ./scripts/deploy/quick_start.sh
```

**PostgreSQL (paridade prod):**
```bash
# Restaurar .env
mv app_dev/backend/.env.postgres app_dev/backend/.env
# Reiniciar
./scripts/deploy/quick_stop.sh && ./scripts/deploy/quick_start.sh
```

---

## 🛡️ SAFE DEPLOY PROCESS - OBRIGATÓRIO ANTES DE PROD (IMPLEMENTADO 22/01/2026)

### 🎯 Comando Único de Validação

**SEMPRE executar antes de fazer deploy:**

```bash
./scripts/deploy/safe_deploy.sh
```

**O script valida automaticamente:**
1. ✅ **Git** - Sem mudanças uncommitted, branch correta
2. ✅ **Migrations** - Pendentes são detectadas e podem ser aplicadas
3. ✅ **Backend** - Dependências, .env, startup test
4. ✅ **Frontend** - node_modules, build test
5. ✅ **Backup** - Backup automático do banco
6. ✅ **Paridade** - Schemas dev vs prod (se PostgreSQL)
7. ✅ **Changelog** - Atualização automática
8. ✅ **Confirmação** - Push automático opcional

### 🚨 Se Alguma Validação Falhar

O script **para imediatamente** e mostra o erro:

```bash
❌ Backend não inicia corretamente!
   Erro: ModuleNotFoundError: No module named 'psycopg2'
   Execute: pip install -r requirements.txt
```

**NUNCA pule validações** - elas existem para evitar deploy quebrado.

### 🚀 Workflow Completo de Deploy

```bash
# 1. Fazer mudanças no código
# 2. Commitar
git add .
git commit -m "feat: adiciona nova funcionalidade X"

# 3. Validar TUDO
./scripts/deploy/safe_deploy.sh

# 4. Se tudo OK, push automático
# (ou manual: git push origin main)

# 5. No servidor (SSH)
ssh user@servidor
cd /var/www/finup
git pull origin main

# 6. Aplicar migrations
cd app_dev/backend
source venv/bin/activate
alembic upgrade head

# 7. Restart serviços
systemctl restart finup-backend finup-frontend

# 8. Verificar logs
journalctl -u finup-backend -f
journalctl -u finup-frontend -f

# 9. Testar endpoints
curl https://meufinup.com.br/api/health
```

### 📋 Checklist Manual (se script não disponível)

- [ ] ✅ Git: mudanças commitadas
- [ ] ✅ Migrations: `alembic current` mostra última
- [ ] ✅ Backend: `python -c "from app.main import app"`
- [ ] ✅ Frontend: `npm run build` sem erros
- [ ] ✅ Backup: `./scripts/deploy/backup_daily.sh`
- [ ] ✅ Tests: rodar testes (se existirem)
- [ ] ✅ Changelog: atualizado
- [ ] ✅ Push: `git push origin main`

---

## 📝 CHANGELOG AUTOMÁTICO - HISTÓRIA DO APP (IMPLEMENTADO 22/01/2026)

### 🎯 Geração Automática de CHANGELOG.md

**Script:** `scripts/deploy/generate_changelog.sh`

**Gera automaticamente baseado em commits git:**
- ✨ Features (palavras: feat, add, novo)
- 🐛 Fixes (palavras: fix, corrige, resolve)
- 🔧 Refatoração (palavras: refactor, melhora, otimiza)
- 📚 Documentação (palavras: docs, doc, readme)

### 🔄 Uso

**Manual:**
```bash
# Gerar para próxima versão (auto-incrementa patch)
./scripts/deploy/generate_changelog.sh

# Gerar para versão específica
./scripts/deploy/generate_changelog.sh --version 2.1.0
```

**Automático (via safe_deploy.sh):**
```bash
# Changelog é gerado automaticamente no deploy
./scripts/deploy/safe_deploy.sh
```

### 📋 Formato do CHANGELOG.md

```markdown
# 📝 Changelog - Sistema FinUp

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

## [v1.2.0] - 2026-01-22

### ✨ Novas Funcionalidades
- feat: adiciona suporte a PostgreSQL (abc123)
- add: implementa Alembic para migrations (def456)

### 🐛 Correções
- fix: corrige erro de autenticação no middleware (ghi789)

### 🔧 Melhorias e Refatoração
- refactor: otimiza queries do dashboard (jkl012)

### 📚 Documentação
- docs: atualiza copilot-instructions com migrations (mno345)

---

## [v1.1.0] - 2026-01-15
...
```

### 🏷️ Criar Tag Git Após Changelog

```bash
# Após gerar changelog
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# Próximo changelog será gerado a partir desta tag
```

### 🎯 Padrões de Commit Recomendados

Use prefixos para categorização automática:

```bash
git commit -m "feat: nova funcionalidade X"       # Features
git commit -m "fix: corrige bug Y"                # Fixes
git commit -m "refactor: melhora performance Z"   # Refatoração
git commit -m "docs: atualiza README"             # Documentação
git commit -m "chore: atualiza dependências"      # Outros
```

---

## 🔍 VALIDAÇÃO DE PARIDADE DEV-PROD (IMPLEMENTADO 22/01/2026)

### 🎯 Script de Validação

**Path:** `scripts/testing/validate_parity.py`

**Compara:**
- ✅ Schemas de tabelas (colunas, tipos, constraints)
- ✅ Contagens de registros
- ✅ Índices e foreign keys
- ✅ Tipos de dados PostgreSQL

### 🔄 Uso

**Configurar produção:**
```bash
# Adicionar ao .env
PROD_DATABASE_URL=postgresql://finup_user:senha@servidor/finup_db
```

**Executar validação:**
```bash
python scripts/testing/validate_parity.py
```

**Output esperado:**
```
═══════════════════════════════════════════════════════════
✅ VALIDAÇÃO DE PARIDADE DEV-PROD
═══════════════════════════════════════════════════════════

🔍 Comparando schemas das tabelas...
  Tabelas apenas em LOCAL: 0
  Tabelas apenas em PROD:  0
  Tabelas comuns:          21

📊 Comparando contagens de registros...
Tabela                                    Local       Prod     Status
─────────────────────────────────────────────────────────────────
journal_entries                            2631       2631     ✅ OK
users                                         4          4     ✅ OK
base_marcacoes                               45         45     ✅ OK
...

✅ PARIDADE 100% - Ambientes idênticos!
```

### 🚨 Se Divergências Forem Detectadas

```bash
⚠️  Tabelas APENAS em PROD: ['nova_tabela']
⚠️  Diferenças de colunas:
  journal_entries:
    Apenas em PROD: {'nova_coluna'}
```

**Ações:**
1. Gerar migration para adicionar tabela/coluna em LOCAL
2. Aplicar migration: `alembic upgrade head`
3. Validar novamente: `python scripts/testing/validate_parity.py`

### 📋 Integração com Safe Deploy

O `safe_deploy.sh` **automaticamente** executa validação de paridade:
- Se ambientes divergem → aviso + opção de continuar
- Se paridade OK → deploy prossegue

---

## 🎯 REGRAS FINAIS DE DEPLOY - NUNCA PULAR

### ✅ Antes de Qualquer Deploy em Produção

1. **Commitar tudo:**
   ```bash
   git status  # Deve estar limpo
   ```

2. **Rodar safe deploy:**
   ```bash
   ./scripts/deploy/safe_deploy.sh
   ```

3. **Verificar changelog:**
   ```bash
   cat CHANGELOG.md | head -30
   ```

4. **Fazer backup:**
   ```bash
   ./scripts/deploy/backup_daily.sh
   ```

5. **Push e deploy:**
   ```bash
   git push origin main
   # SSH no servidor e fazer pull + migrations + restart
   ```

### 🚫 NUNCA Fazer em Produção

- ❌ Modificar banco direto (sempre usar Alembic)
- ❌ Deploy sem testar localmente
- ❌ Deploy sem backup
- ❌ Deploy com mudanças uncommitted
- ❌ Deploy sem validar paridade
- ❌ Deploy sem atualizar changelog

### ✅ SEMPRE Fazer

- ✅ Usar PostgreSQL local para dev sério
- ✅ Gerar migrations para mudanças de schema
- ✅ Rodar `safe_deploy.sh` antes de push
- ✅ Validar paridade dev-prod
- ✅ Criar tags git para releases
- ✅ Manter changelog atualizado
- ✅ Testar migrations em dev antes de prod

---

**Sempre que começar a trabalhar no projeto, leia este arquivo primeiro!** 🎯
