# 📱 Plano de Integração Mobile - Protótipos → Produção

**Data de Criação:** 05/02/2026  
**Versão:** 1.1  
**Última Atualização:** 05/02/2026  
**Status:** 📋 Planejamento  
**Projeto:** ProjetoFinancasV5 - Mobile Integration

---

## ⚠️ ESCLARECIMENTO IMPORTANTE

### Dashboard NÃO é Funcionalidade Nova

O protótipo `export-to-main-project/dashboard/` é um **REDESIGN** do dashboard existente:

- ✅ **Desktop Dashboard JÁ EXISTE:** 6 componentes funcionais em produção
- ✅ **Mobile Dashboard JÁ EXISTE:** Versão mobile básica funcional  
- ✅ **Backend 100% PRONTO:** 6 APIs totalmente funcionais
- 🎨 **Protótipo:** Nova UI/UX para substituir design mobile atual

**Trabalho necessário:**
- 🔄 Substituir frontend mobile atual pelo design do protótipo (8-10h)
- ➕ Criar 2 APIs novas para features extras (donut chart, changePercentage) (3-4h)
- ✅ Reutilizar 100% do backend existente

**NÃO vamos:**
- ❌ Criar funcionalidade do zero
- ❌ Reescrever backend (já existe e funciona)
- ❌ Criar nova tela (apenas redesign da existente)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Preparação do Ambiente](#preparação-do-ambiente)
3. [Inventário de Protótipos](#inventário-de-protótipos)
4. [Roadmap de Implementação](#roadmap-de-implementação)
5. [Mapeamento de Dependências](#mapeamento-de-dependências)
6. [Mapeamento de Dados](#mapeamento-de-dados)
7. [Estratégia de Componentes](#estratégia-de-componentes)
8. [Análise de Riscos](#análise-de-riscos)
9. [Passo a Passo Detalhado](#passo-a-passo-detalhado)
10. [Critérios de Aprovação](#critérios-de-aprovação)

---

## 🎯 Visão Geral

### Objetivo

Integrar **4 protótipos Next.js standalone** desenvolvidos em `export-to-main-project/` no aplicativo mobile principal (`app_dev/frontend/`), seguindo a estratégia:

**🎨 FRONTEND:** Copiar 100% do design dos protótipos (UI/UX novo)  
**🔌 BACKEND:** Reutilizar 90% das APIs existentes + criar 3 novos endpoints  
**📊 DADOS:** Conectar diretamente nas tabelas do banco (journal_entries, base_marcacoes, budget_geral)

### Metodologia de Implementação

1. **Setup:** Copiar componentes do protótipo para estrutura do projeto
2. **Mock Data:** Testar frontend com dados fake do protótipo
3. **Backend:** Criar endpoints faltantes (apenas 3)
4. **Integração:** Conectar frontend nas APIs reais
5. **Validação:** Testar end-to-end e aprovar

### 📊 Grafo de Dependências

```
┌─────────────────────────────────────────────────────────────┐
│                    INÍCIO DO PROJETO                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────┐                ┌──────────────┐
│   UPLOAD     │                │    METAS     │
│   (6-8h)     │                │  (12-14h)    │
│              │                │              │
│ Backend: ✅  │                │ Backend: ✅  │
│ 0 novos APIs │                │ 0 novos APIs │
└──────┬───────┘                └──────┬───────┘
       │                               │
       │ Depende                       │ Independente
       ▼                               ▼
┌──────────────┐                ┌──────────────┐
│  PREVIEW     │                │  CONCLUÍDO   │
│  (16-18h)    │                │              │
│              │                └──────────────┘
│ Backend: ⚠️  │
│ 1 novo API   │
│ (opcional)   │
└──────┬───────┘
       │
       │ Independente
       ▼
┌──────────────┐
│  DASHBOARD   │
│  (10-14h)    │
│              │
│ Backend: ⚠️  │
│ 2 novos APIs │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  CONCLUÍDO   │
│              │
└──────────────┘

Legenda:
✅ Backend 100% pronto
⚠️ Backend requer novos endpoints
```

### 🎯 Ordem Recomendada de Implementação

**Semana 1 (Paralelo):**
- 👤 Dev 1: Upload (6-8h) → Preview (16-18h)
- 👤 Dev 2: Metas (12-14h) → Dashboard backend (3-4h)

**Semana 2:**
- 👥 Ambos: Dashboard frontend (8-10h)
- 👥 Ambos: Testes finais e ajustes

**Bloqueadores:**
- ⚠️ Preview depende de Upload (usa sessionId do upload)
- ✅ Dashboard e Metas são independentes
- ✅ Podem ser implementados em paralelo

---

## 🛠️ Preparação do Ambiente

### 1️⃣ Verificar Status do Projeto

**⏱️ Tempo:** 5 minutos

```bash
# Navegar para raiz do projeto
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Verificar branch atual
git branch --show-current

# Verificar mudanças não commitadas
git status

# Se houver mudanças, commitar antes de prosseguir
git add .
git commit -m "chore: save work before mobile integration"
```

**✅ Checklist:**
- [ ] Branch atual identificada
- [ ] Nenhuma mudança sem commit (ou commitadas)
- [ ] Repositório sincronizado com GitHub

---

### 2️⃣ Criar Branch de Feature

**⏱️ Tempo:** 2 minutos

```bash
# Criar e mudar para nova branch
git checkout -b feature/mobile-prototypes-integration

# Push para remoto (criar branch no GitHub)
git push -u origin feature/mobile-prototypes-integration

# Confirmar está na branch correta
git branch --show-current
# Output esperado: feature/mobile-prototypes-integration
```

**✅ Checklist:**
- [ ] Branch `feature/mobile-prototypes-integration` criada
- [ ] Branch enviada para GitHub
- [ ] Git mostra branch correta

---

### 3️⃣ Validar Acesso aos Protótipos

**⏱️ Tempo:** 3 minutos

```bash
# Verificar se pasta existe e tem conteúdo
ls -la export-to-main-project/
# Deve listar: dashboard, metas, preview-upload, upload

# Verificar estrutura de cada protótipo
for proto in dashboard metas preview-upload upload; do
  echo "\n=== $proto ==="
  ls -la export-to-main-project/$proto/app/
done

# Contar componentes de cada protótipo
find export-to-main-project/ -name "*.tsx" -o -name "*.ts" | wc -l
# Deve ter ~50-100 arquivos TypeScript
```

**✅ Checklist:**
- [ ] 4 pastas de protótipos existem
- [ ] Cada protótipo tem pasta `app/` com página principal
- [ ] ~50-100 arquivos TypeScript encontrados

---

### 4️⃣ Verificar Backend e Database

**⏱️ Tempo:** 5 minutos

```bash
# Verificar servidores rodando
curl http://localhost:8000/api/health
# Esperado: {"status": "ok"}

curl http://localhost:3000/
# Esperado: HTML do Next.js

# Verificar banco de dados
sqlite3 app_dev/backend/database/financas_dev.db ".tables"
# Deve listar: journal_entries, base_marcacoes, budget_geral, etc

# Verificar usuário admin existe
sqlite3 app_dev/backend/database/financas_dev.db \
  "SELECT id, email, is_active FROM users WHERE email='admin@financas.com';"
# Esperado: 1|admin@financas.com|1
```

**✅ Checklist:**
- [ ] Backend rodando (porta 8000)
- [ ] Frontend rodando (porta 3000)
- [ ] Banco de dados acessível
- [ ] Usuário admin existe e está ativo

---

### 5️⃣ Instalar Dependências Faltantes

**⏱️ Tempo:** 3 minutos

```bash
# Frontend - instalar bibliotecas para virtual scrolling
cd app_dev/frontend
npm install react-window @types/react-window
npm install react-virtuoso

# Backend - verificar se todas dependências estão OK
cd ../backend
source ../../.venv/bin/activate
pip install -r requirements.txt

cd ../..
```

**✅ Checklist:**
- [ ] `react-window` instalado (para Preview performance)
- [ ] `react-virtuoso` instalado (alternativa)
- [ ] Backend dependencies atualizadas

---

### 6️⃣ Criar Estrutura Base de Pastas

**⏱️ Tempo:** 2 minutos

```bash
# Criar rotas mobile que ainda não existem
mkdir -p app_dev/frontend/src/app/mobile/upload
mkdir -p app_dev/frontend/src/app/mobile/preview
mkdir -p app_dev/frontend/src/app/mobile/insights
mkdir -p app_dev/frontend/src/app/mobile/goals

# Criar estrutura de features
mkdir -p app_dev/frontend/src/features/upload/components
mkdir -p app_dev/frontend/src/features/upload/hooks
mkdir -p app_dev/frontend/src/features/upload/types
mkdir -p app_dev/frontend/src/features/upload/utils

# Verificar criação
ls -la app_dev/frontend/src/app/mobile/
ls -la app_dev/frontend/src/features/upload/
```

**✅ Checklist:**
- [ ] 4 rotas mobile criadas (upload, preview, insights, goals)
- [ ] Estrutura de features/upload/ criada
- [ ] Pastas vazias, prontas para receber código

---

### 7️⃣ Backup Antes de Começar

**⏱️ Tempo:** 2 minutos

```bash
# Criar backup do banco de dados
./scripts/deploy/backup_daily.sh

# Verificar backup criado
ls -lh app_dev/backend/database/backups_daily/
# Deve mostrar arquivo mais recente com data de hoje

# Criar tag git (checkpoint)
git tag -a v-mobile-integration-start -m "Checkpoint: início integração mobile"
git push origin v-mobile-integration-start
```

**✅ Checklist:**
- [ ] Backup do banco criado
- [ ] Tag git criada como checkpoint
- [ ] Tag enviada para GitHub

---

**🎉 AMBIENTE PREPARADO!**

Tempo total de preparação: ~20 minutos

Agora pode começar a implementação dos protótipos seguindo a ordem recomendada:
1. Upload (6-8h)
2. Preview (16-18h)
3. Dashboard backend (3-4h)
4. Metas (12-14h)
5. Dashboard frontend (8-10h)

---

### Protótipos a Integrar

| # | Protótipo | Localização | Status Atual | Prioridade |
|---|-----------|-------------|--------------|------------|
| 1 | **Upload Mobile** | `export-to-main-project/upload/` | Existe no desktop, precisa mobile | 🔴 Alta |
| 2 | **Preview Mobile** | `export-to-main-project/preview-upload/` | Existe no desktop, precisa mobile | 🔴 Alta |
| 3 | **Dashboard Mobile** | `export-to-main-project/dashboard/` | **REDESIGN** - Desktop e mobile existem, protótipo é UI/UX nova | 🟡 Média |
| 4 | **Metas (Goals)** | `export-to-main-project/metas/` | ✅ Backend pronto (estender budget_geral) | 🟢 Baixa |

### Estatísticas Gerais

- **Total de Telas:** 7 (2 novas mobile + 1 redesign + 4 novas goals)
- **Total de Componentes:** 51 (21 atoms + 15 molecules + 10 organisms + 5 templates)
- **Endpoints EXISTENTES:** 18 (90% do backend pronto)
- **Endpoints NOVOS:** 4 (apenas 5-7h de trabalho)
- **Estimativa Total:** 38-47 horas (~1 semana com 2 devs, ~2 semanas com 1 dev)

---

## 📦 Inventário de Protótipos

### 1️⃣ Upload Mobile

**Localização:** `export-to-main-project/upload/`  
**Porta:** 3001  
**Status:** ✅ Funcionalidade existe no desktop, precisa versão mobile

#### Telas

| Tela | Rota | Complexidade | Estimativa |
|------|------|--------------|------------|
| Upload Form | `/` | Baixa | 4-6h |

#### Componentes (8 total)

**Atoms:**
- Button
- IconButton
- Badge

**Molecules:**
- FileInput (drag & drop)
- BankSelector
- CardSelector
- MonthYearPicker
- FormatSelector

**Organisms:**
- UploadForm

#### Dados Mock

```typescript
interface MockData {
  banks: Array<{id: string, name: string}>
  creditCards: Array<{id: string, bankId: string, lastDigits: string, name: string}>
  months: string[] // ["Janeiro", "Fevereiro", ...]
  years: number[] // [2024, 2025, 2026]
  fileFormats: Array<{value: string, label: string}> // CSV, Excel, PDF, OFX
}
```

#### Backend API

**✅ TODOS OS ENDPOINTS JÁ EXISTEM** - Localização: `app_dev/backend/app/domains/upload/router.py`

**1. POST /api/v1/upload/preview** (Principal)
- **Request:** FormData com file, banco, cartao, tipoDocumento, mesFatura
- **Response:** `{sessionId, totalRegistros, success}`
- **Tabelas:** Cria registros em `preview_transacoes`
- **Lógica:** 
  1. Salva arquivo em `uploads_temp/`
  2. Detecta banco via `bank_format_compatibility`
  3. Parseia arquivo (CSV/Excel/PDF/OFX)
  4. Classifica automaticamente (4 estratégias)
  5. Retorna sessionId para preview

**2. GET /api/v1/upload/session/{sessionId}** (Validar sessão)
- **Response:** `{exists: boolean, totalTransactions: number}`
- **Uso:** Verificar se sessão ainda válida

**3. GET /api/v1/banks** (Listar bancos)
- **Response:** `[{id, name, logoUrl, formatsSupported}]`
- **Tabela:** `bank_format_compatibility`
- **Uso:** Povoar dropdown de bancos

**4. GET /api/v1/cards** (Listar cartões do usuário)
- **Response:** `[{id, bankId, lastDigits, name, brand}]`
- **Tabela:** `credit_cards` (se existir) ou hardcoded
- **Uso:** Povoar dropdown de cartões

**📊 Tabelas do Banco Usadas:**
- `preview_transacoes` - Armazena transações temporárias
- `bank_format_compatibility` - Configuração dos bancos
- `uploads_temp/` - Arquivos enviados (filesystem)

**🔍 Estratégias de Classificação Automática:**
1. Base Parcelas (`base_parcelas`) - Compras parceladas conhecidas
2. Base Padrões (`base_marcacoes`) - Estabelecimentos com regex
3. Journal Entries (`journal_entries`) - Transações idênticas anteriores
4. Regras Genéricas - Palavras-chave (PIX, TED, etc)

#### Status Desktop

- ✅ Implementado em `app_dev/frontend/src/app/upload/page.tsx`
- ✅ Usa componente `UploadDialog`
- ⚠️ Não otimizado para mobile (needs adaptation)

#### 📊 Mapeamento Componente → Dados → Backend

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| FileInput (drag&drop) | - | - | - | ✅ Copiar |
| BankSelector | Lista de bancos | `GET /api/v1/banks` | bank_format_compatibility | ✅ Pronto |
| CardSelector | Lista de cartões | `GET /api/v1/cards` | credit_cards | ✅ Pronto |
| MonthYearPicker | - | - | - | ✅ Copiar |
| FormatSelector | Formatos aceitos | Hardcoded | - | ✅ Copiar |
| TabBar (Extrato/Fatura) | - | - | - | ✅ Copiar |
| UploadButton | - | `POST /api/v1/upload/preview` | preview_transacoes | ✅ Pronto |
| ProgressBar | Upload progress | - | - | ✅ Copiar |

**📂 Estrutura de Arquivos:**
```
app_dev/frontend/src/
├── app/mobile/upload/
│   └── page.tsx                    # Copiar de export-to-main-project/upload/app/page.tsx
├── features/upload/components/
│   ├── file-input.tsx              # Drag & drop component
│   ├── bank-selector.tsx           # Dropdown com busca
│   ├── card-selector.tsx           # Filtrado por banco
│   ├── month-year-picker.tsx       # Date picker
│   ├── upload-form.tsx             # Form container
│   └── index.ts                    # Exports
└── features/upload/
    ├── types.ts                    # TypeScript interfaces
    └── hooks/
        └── use-upload.ts           # Upload logic + progress
```

#### Plano de Implementação

**FASE 1 - Frontend Mock (4-6h):**
1. Criar `app_dev/frontend/src/app/mobile/upload/page.tsx`
2. Copiar componentes de `export-to-main-project/upload/src/components/`
3. Adaptar layout para mobile (tela cheia, bottom buttons)
4. Usar dados mock hardcoded

**FASE 2 - Backend Real (2-3h):**
1. Conectar ao endpoint `POST /api/v1/upload/preview`
2. Implementar upload de arquivo com progress
3. Redirecionar para preview após sucesso
4. Tratamento de erros

**APROVAÇÃO NECESSÁRIA:**
- [ ] Layout mobile aprovado
- [ ] Drag & drop funciona em touch
- [ ] Seleção de banco/cartão fluida
- [ ] Upload com progress funciona
- [ ] Redirecionamento para preview OK

---

### 2️⃣ Preview Mobile

**Localização:** `export-to-main-project/preview-upload/`  
**Porta:** 3003  
**Status:** ✅ Funcionalidade existe no desktop, precisa versão mobile

#### Telas

| Tela | Rota | Complexidade | Estimativa |
|------|------|--------------|------------|
| Preview & Classification | `/` | Alta | 16-20h |

#### Componentes (13 total)

**Atoms:**
- Button
- IconButton  
- Badge
- TabButton
- Alert

**Molecules:**
- FileInfoCard (banco, cartão, arquivo, mês, total)
- PreviewHeader
- TabBar (filtros: Todas, Classificadas, Não Classificadas, etc)
- ClassificationModal (dropdown grupo/subgrupo)

**Organisms:**
- TransactionCard (agrupável, expansível)
- TransactionList (virtualized)
- BottomActionBar (confirmar/cancelar)

**Templates:**
- PreviewLayout

#### Dados Mock

```typescript
interface MockTransaction {
  id: string
  date: string // "DD/MM/YYYY"
  description: string // "UBER 01/12"
  value: number // -50.00
  grupo?: string
  subgrupo?: string
  source: 'base_parcelas' | 'base_padroes' | 'journal_entries' | 'regras_genericas' | 'manual' | 'unclassified'
  occurrences?: number // Para agrupamento
  items?: MockTransaction[] // Itens do grupo
  isDuplicate?: boolean
  isExcluded?: boolean
}

interface MockFileInfo {
  banco: string // "Itaú"
  cartao: string // "9266"
  arquivo: string // "fatura-202601.csv"
  mesFatura: string // "fevereiro de 2026"
  totalLancamentos: number // 58
  somaTotal: number // -17064.96
}

interface MockClassification {
  grupos: string[] // ["Casa", "Alimentação", "Transporte", ...]
  subgrupos: Record<string, string[]> // {"Casa": ["Aluguel", "Celular", ...]}
}
```

#### Backend API

**✅ 3 ENDPOINTS EXISTEM | ⚠️ 1 OPCIONAL (batch classification)**

**Localização:** `app_dev/backend/app/domains/upload/router.py`

**1. GET /api/v1/upload/preview/{sessionId}** (Carregar preview)
- **Response:** 
  ```typescript
  {
    fileInfo: {banco, cartao, arquivo, mesFatura, totalLancamentos, somaTotal},
    transactions: [{id, data, lancamento, valor, grupo?, subgrupo?, origem, isDuplicata}],
    grupos: string[],
    subgrupos: Record<string, string[]>
  }
  ```
- **Tabelas:** 
  - `preview_transacoes` WHERE session_id
  - `base_marcacoes` (para grupos/subgrupos)
  - `journal_entries` (detecção duplicatas)
- **Lógica:**
  1. Busca transações da sessão
  2. Calcula contadores (classificadas, não classificadas, por origem)
  3. Agrupa transações idênticas (mesmo nome/valor)
  4. Retorna grupos e subgrupos disponíveis

**2. PATCH /api/v1/upload/preview/{sessionId}/classify** (Classificar transação)
- **Request:** `{transactionId: string, grupo: string, subgrupo: string}`
- **Response:** `{success: boolean, updated: number}`
- **Tabelas:** UPDATE `preview_transacoes` SET grupo, subgrupo
- **Lógica:** Atualiza classificação + salva em `base_marcacoes` para aprendizado

**3. POST /api/v1/upload/preview/{sessionId}/confirm** (Confirmar importação)
- **Request:** Nenhum body
- **Response:** `{success: boolean, totalImportados: number, duplicatasIgnoradas: number}`
- **Tabelas:** 
  - SELECT * FROM `preview_transacoes` WHERE session_id
  - INSERT INTO `journal_entries` (transações classificadas)
  - INSERT INTO `base_marcacoes` (novos padrões aprendidos)
  - DELETE FROM `preview_transacoes` WHERE session_id
- **Validações:**
  1. Todas transações classificadas?
  2. Detectar duplicatas (IdTransacao hash)
  3. Validar grupo/subgrupo existem
- **Lógica:**
  1. Verifica se todas classificadas (se não, retorna erro 400)
  2. Para cada transação não duplicada:
     - Gera IdTransacao (hash de data+estabelecimento+valor)
     - Insere em journal_entries
     - Atualiza base_marcacoes se novo padrão
  3. Limpa preview_transacoes
  4. Retorna estatísticas

**4. DELETE /api/v1/upload/preview/{sessionId}** (Cancelar importação)
- **Response:** `{success: boolean}`
- **Tabelas:** DELETE FROM `preview_transacoes` WHERE session_id
- **Lógica:** Remove transações temporárias e arquivo de upload

**⚠️ 5. PATCH /api/v1/upload/preview/{sessionId}/batch** (OPCIONAL - não existe)
- **Request:** `{transactionIds: string[], grupo: string, subgrupo: string}`
- **Response:** `{success: boolean, updated: number}`
- **Uso:** Classificar múltiplas transações de uma vez
- **Prioridade:** Baixa (frontend pode chamar /classify múltiplas vezes)
- **Esforço:** 1-2h se necessário

**📊 Tabelas do Banco Usadas:**
- `preview_transacoes` - Transações temporárias (session-based)
- `journal_entries` - Transações confirmadas (permanentes)
- `base_marcacoes` - Padrões de classificação (aprendizado)
- `base_parcelas` - Parcelas de compras (detecção automática)

**🔍 Campos Críticos:**
- `IdTransacao` - Hash único (data + estabelecimento_base + valor + sequencia)
- `origem` - Como foi classificada (base_parcelas, base_padroes, journal_entries, regras_genericas, manual, unclassified)
- `isDuplicata` - Se IdTransacao já existe em journal_entries

#### Status Desktop

- ✅ Implementado em `app_dev/frontend/src/app/upload/preview/page.tsx`
- ✅ Sistema completo de classificação
- ✅ Detecção de duplicatas
- ✅ Agrupamento de transações
- ⚠️ Layout desktop (tabela) - precisa virar cards mobile

#### Plano de Implementação

**FASE 1 - Frontend Mock (16-20h):**

1. **Criar estrutura base (2h)**
   - `app_dev/frontend/src/app/mobile/preview/page.tsx`
   - State management (useState para transactions, filters, selectedTab)

2. **Implementar FileInfoCard (1h)**
   - Card com informações do arquivo
   - Layout vertical para mobile
   - Ícones representativos

3. **Implementar TabBar de filtros (2h)**
   - Tabs: Todas (58), Classificadas (39), Não Classificadas (19), Base Parcelas (15), Base Padrões (6), Journal Entries (9), Regras Genéricas (9), Manual (0)
   - Scroll horizontal
   - Badge com contadores

4. **Implementar TransactionCard (4h)**
   - Layout card (não tabela)
   - Mostra: data, descrição, valor, grupo/subgrupo, origem
   - Suporte a agrupamento (4× IOF COMPRA INTERNACIONAL)
   - Expansível (seta ▶️)
   - Estados visuais: classificada (branco), não classificada (amarelo), duplicada (vermelho)

5. **Implementar TransactionList com Virtual Scroll (3h)**
   - Usar react-window ou react-virtuoso
   - Renderizar apenas itens visíveis (performance)
   - Lazy loading de grupos expandidos

6. **Implementar ClassificationModal como BottomSheet (4h)**
   - Bottom sheet (não modal desktop)
   - Dropdown de Grupo com busca
   - Dropdown de Subgrupo (filtrado por Grupo)
   - Validação: ambos obrigatórios
   - Aplicar a todas ocorrências do grupo

7. **Implementar Alert de validação (1h)**
   - "⚠️ 19 transações sem classificação"
   - Progresso: "39 de 58 classificadas"
   - Bloquear botão "Confirmar" se houver não classificadas

8. **Implementar BottomActionBar (1h)**
   - Botões fixos no bottom: "Cancelar" e "Confirmar Importação"
   - Confirmar desabilitado até todas classificadas

9. **Usar mock data (2h)**
   - Criar `mockPreviewData.ts` com 58 transações
   - Incluir exemplos de cada tipo de origem
   - Incluir duplicatas e não classificadas

**FASE 2 - Backend Real (4-6h):**

1. **Conectar GET preview (1h)**
   - Buscar sessionId da URL
   - Fetch de `GET /api/v1/upload/preview/{sessionId}`
   - Loading state

2. **Implementar atualização de classificação (2h)**
   - `PATCH /api/v1/upload/preview/{sessionId}/classify`
   - Atualizar estado local após sucesso
   - Recalcular contadores

3. **Implementar confirmação (1h)**
   - `POST /api/v1/upload/preview/{sessionId}/confirm`
   - Validar todas classificadas
   - Redirecionar para `/mobile/transactions` após sucesso

4. **Implementar cancelamento (1h)**
   - `DELETE /api/v1/upload/preview/{sessionId}`
   - Confirmar ação (dialog)
   - Voltar para upload

**APROVAÇÃO NECESSÁRIA:**

- [ ] **Layout Mobile Aprovado**
  - [ ] Cards legíveis em telas pequenas (iPhone SE)
  - [ ] Scroll suave (60fps)
  - [ ] Bottom sheet abre/fecha sem lag

- [ ] **Funcionalidades Core**
  - [ ] Filtros (tabs) funcionam
  - [ ] Agrupamento funciona (expandir/colapsar)
  - [ ] Classificação atualiza todas ocorrências do grupo
  - [ ] Alert de validação correto

- [ ] **Integração Backend**
  - [ ] Preview carrega dados reais
  - [ ] Classificação salva no backend
  - [ ] Confirmação salva transações em journal_entries
  - [ ] Cancelamento deleta sessão

- [ ] **Performance**
  - [ ] Lista de 100+ transações renderiza em <3s
  - [ ] Scroll sem travamentos
  - [ ] Bottom sheet abre instantaneamente

---

### 3️⃣ Dashboard Mobile (Redesign)

**Localização:** `export-to-main-project/dashboard/`  
**Porta:** 3000  
**Status:** 🎨 **REDESIGN** - Dashboard já existe, protótipo é nova UI/UX

> **⚠️ IMPORTANTE:** Dashboard NÃO é funcionalidade nova!  
> ✅ Desktop dashboard já existe e funciona  
> ✅ Mobile dashboard já existe (design básico)  
> ✅ Backend 100% pronto (6 APIs funcionais)  
> 🎨 Protótipo = Redesign visual para substituir mobile atual

#### Telas

| Tela | Rota | O Que Fazer | Estimativa |
|------|------|-------------|------------|
| Dashboard Overview | `/mobile/dashboard` | **Substituir** mobile atual pelo design do protótipo | 8-10h |

#### Componentes (Inline - 1 página)

**Componentes Principais:**
- Month Selector (scroll horizontal)
- Wallet Balance Card (saldo, variação %)
- Bar Chart (receitas/despesas por mês)
- Donut Chart (breakdown de receitas por fonte)
- Tab Bar (Income/Expenses/Budget)
- Bottom Navigation

#### Dados Mock

```typescript
interface MockDashboardData {
  walletBalance: number // 45230.00
  changePercentage: number // 2.5 (%)
  monthlyData: Array<{
    month: string // "Jan", "Feb", ...
    income: number // 15000
    expenses: number // 12000
  }>
  incomeSources: Array<{
    name: string // "Salary", "Freelance", "Investments"
    amount: number // 12000
    percentage: number // 80
    color: string // "#10B981"
  }>
  currentMonth: string // "February 2026"
}
```

#### Backend API

**Endpoints Existentes:** ✅ Maioria já existe em `app_dev/backend/app/domains/dashboard/`  
**Endpoints Novos:** ⚠️ Apenas 2 precisam ser criados:
- `GET /api/v1/dashboard/income-sources` (breakdown de receitas)
- Enhancement em `/api/v1/dashboard/metrics` (adicionar changePercentage)

**Query Params:**
```typescript
{
  userId: number // Vem do JWT
  year?: number // 2026
  month?: number // 2 (Feb)
}
```

**Response:**
```typescript
{
  walletBalance: number
  changePercentage: number
  monthlyData: Array<{month: string, income: number, expenses: number}>
  incomeSources: Array<{name: string, amount: number, percentage: number, color: string}>
  currentMonth: string
}
```

**Lógica Backend:**
```python
# Aggregar de journal_entries
# WHERE user_id = X AND Ano = 2026
# GROUP BY Mes, Grupo (onde CategoriaGeral = 'Receita')
# Calcular percentuais
# Wallet balance = último saldo conhecido ou soma de todas receitas - despesas
```

#### Status Atual

- ✅ **Backend:** Dashboard domain completo existe (`app_dev/backend/app/domains/dashboard/`)
  - 6 endpoints funcionais (metrics, chart, budget, categories, cards, transactions)
  - Apenas 2 novos endpoints necessários
- ❌ **Frontend:** Ignorar versão atual, usar 100% design do protótipo
  - Copiar todos componentes de `export-to-main-project/dashboard/`
  - Conectar nas APIs existentes do backend
  - Design moderno com charts interativos

#### Plano de Implementação

#### 📊 Mapeamento Componente → Dados → Backend

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| MonthSelector | Lista de meses | Frontend (hardcoded) | - | ✅ Reuso |
| YTDToggle | - | Frontend (state) | - | ✅ Copiar |
| WalletBalanceCard | saldo, variação % | `GET /dashboard/metrics` | journal_entries | ⚠️ Enhancement |
| BarChart | receitas/despesas por mês | `GET /dashboard/chart` | journal_entries | ✅ Pronto |
| DonutChart (receitas) | receitas por fonte | ❌ `GET /dashboard/income-sources` | journal_entries | ❌ Criar |
| TabBar (Income/Expenses) | - | Frontend (state) | - | ✅ Copiar |
| MetricCards | totais mês atual | `GET /dashboard/metrics` | journal_entries | ✅ Pronto |
| BottomNavigation | - | - | - | ✅ Reuso |

**⚠️ Endpoints Faltantes (Criar):**

**1. GET /api/v1/dashboard/income-sources** (NOVO - 2-3h)
```python
# app_dev/backend/app/domains/dashboard/router.py
@router.get("/income-sources")
def get_income_sources(
    user_id: int = Depends(get_current_user_id),
    year: int = Query(default=current_year),
    month: Optional[int] = None
):
    # Query:
    # SELECT Grupo, SUM(Valor) as total
    # FROM journal_entries
    # WHERE user_id = X
    #   AND Ano = Y
    #   AND (Mes = M OR month IS NULL)
    #   AND CategoriaGeral = 'Receita'
    # GROUP BY Grupo
    # ORDER BY total DESC
    
    # Calcular percentuais
    # Atribuir cores (hardcoded ou de base_marcacoes)
    
    return {
        "incomeSources": [
            {"name": "Salário", "amount": 12000, "percentage": 80, "color": "#10B981"},
            {"name": "Freelance", "amount": 2000, "percentage": 13, "color": "#3B82F6"},
            {"name": "Investimentos", "amount": 1000, "percentage": 7, "color": "#8B5CF6"}
        ],
        "totalIncome": 15000
    }
```

**2. Enhancement: PATCH /api/v1/dashboard/metrics** (1h)
```python
# Adicionar campo changePercentage
# Comparar soma do mês atual vs mês anterior

# Query adicional:
# last_month_total = SUM(Valor) WHERE Mes = current_month - 1
# current_month_total = SUM(Valor) WHERE Mes = current_month
# changePercentage = ((current - last) / last) * 100

return {
    "walletBalance": 45230.00,
    "changePercentage": 2.5,  # ← NOVO
    "totalIncome": 15000,
    "totalExpenses": 12000,
    # ...
}
```

**📂 Estrutura de Arquivos:**
```
app_dev/frontend/src/
├── app/mobile/insights/
│   └── page.tsx                    # Copiar de export-to-main-project/dashboard/app/page.tsx
├── components/mobile/
│   ├── bar-chart.tsx               # Extrair SVG do protótipo
│   ├── donut-chart.tsx             # Extrair SVG do protótipo
│   ├── month-scroll-picker.tsx     # ✅ JÁ EXISTE - reutilizar
│   ├── ytd-toggle.tsx              # Copiar do protótipo
│   └── metric-card.tsx             # Copiar do protótipo
└── features/dashboard/
    ├── types.ts
    ├── hooks/
    │   ├── use-dashboard-metrics.ts
    │   ├── use-income-sources.ts    # ← NOVO endpoint
    │   └── use-chart-data.ts
    └── utils/
        └── format-currency.ts
```

**FASE 1 - Frontend Novo do Protótipo (6-8h):**

**ESTRATÉGIA:** Copiar 100% do frontend do protótipo, manter dados mock inicialmente

1. **Copiar página principal (1h)**
   ```bash
   # Copiar página do protótipo
   cp export-to-main-project/dashboard/app/page.tsx \
      app_dev/frontend/src/app/mobile/insights/page.tsx
   
   # Ajustar imports para estrutura do projeto principal
   ```

2. **Copiar todos os componentes inline (2h)**
   - Month Selector (scroll horizontal)
   - Wallet Balance Card (saldo + variação %)
   - Bar Chart (receitas/despesas por mês)
   - Donut Chart (breakdown de receitas)
   - Tab Bar (Income/Expenses/Budget)
   - Todos os estilos CSS/Tailwind

3. **Adaptar imports e paths (1h)**
   - Ajustar imports de `@/components` para estrutura do projeto
   - Ajustar imports de tipos/interfaces
   - Garantir que tailwind classes funcionam

4. **Testar com mock data (1h)**
   - Usar mock data do protótipo (já existe no arquivo)
   - Testar todos os componentes renderizam
   - Testar interações (month selector, tooltips)

5. **Ajustes de layout mobile (1-2h)**
   - Garantir responsividade
   - Testar em iPhone SE, 14 Pro, 14 Pro Max
   - Ajustar safe areas, bottom nav

**IMPORTANTE:** NÃO criar componentes do zero, COPIAR do protótipo!

**FASE 2 - Conectar Backend Existente (4-6h):**

**ESTRATÉGIA:** Reutilizar 90% das APIs existentes, criar apenas 2 novas

1. **Mapear APIs existentes (1h)**
   - ✅ `GET /api/v1/dashboard/metrics` → wallet balance, totals
   - ✅ `GET /api/v1/dashboard/chart` → monthly data (income/expenses)
   - ✅ `GET /api/v1/dashboard/budget` → budget comparison
   - ✅ `GET /api/v1/dashboard/categories` → despesas por categoria
   - ✅ `GET /api/v1/dashboard/cards` → despesas por cartão
   - ✅ `GET /api/v1/dashboard/transactions` → transações recentes

2. **Criar 2 novos endpoints (3-4h)**
   
   **A. Income Sources Breakdown:**
   ```python
   # app_dev/backend/app/domains/dashboard/router.py
   @router.get("/income-sources")
   def get_income_sources(
       user_id: int = Depends(get_current_user_id),
       year: int = Query(default=current_year),
       month: Optional[int] = None
   ):
       # Agregar journal_entries WHERE CategoriaGeral='Receita'
       # GROUP BY Grupo
       # Retornar: [{name, amount, percentage, color}]
   ```
   
   **B. Enhancement em /metrics:**
   ```python
   # Adicionar campo changePercentage
   # Comparar mês atual com mês anterior
   # Retornar: {walletBalance, changePercentage, ...}
   ```

3. **Conectar frontend nas APIs (1-2h)**
   ```typescript
   // Substituir mock data por fetch real
   const [data, setData] = useState(null)
   
   useEffect(() => {
     Promise.all([
       fetch('/api/v1/dashboard/metrics'),
       fetch('/api/v1/dashboard/chart'),
       fetch('/api/v1/dashboard/income-sources') // NOVO
     ]).then(([metrics, chart, sources]) => {
       setData({
         walletBalance: metrics.walletBalance,
         changePercentage: metrics.changePercentage, // NOVO
         monthlyData: chart.data,
         incomeSources: sources.data // NOVO
       })
     })
   }, [])
   ```

4. **Testar integração (1h)**
   - Validar dados batem com banco
   - Testar performance (<2s)
   - Error handling

**APROVAÇÃO NECESSÁRIA:**

- [ ] **Layout Mobile Aprovado**
  - [ ] Charts legíveis em telas pequenas
  - [ ] Cores contrastantes e acessíveis
  - [ ] Month selector fluido

- [ ] **Funcionalidades Core**
  - [ ] Bar chart mostra últimos 6-12 meses
  - [ ] Donut chart soma 100%
  - [ ] Seleção de mês atualiza dados

- [ ] **Backend Correto**
  - [ ] Wallet balance correto (conferir manualmente)
  - [ ] Variação % calculada corretamente
  - [ ] Income sources somam total de receitas
  - [ ] Performance <2s para carregar

- [ ] **Performance**
  - [ ] Dashboard carrega em <2s
  - [ ] Charts renderizam suavemente
  - [ ] Troca de mês instantânea

---

### 4️⃣ Metas (Goals/Budget)

**Localização:** `export-to-main-project/metas/`  
**Porta:** 3004  
**Status:** ✅ **Backend pronto** - Estender budget_geral (NÃO criar tabela nova)

> **✅ DECISÃO DE SCHEMA TOMADA:**  
> Estender tabela `budget_geral` com colunas: tipo_meta, ativo, icone, cor, ordem  
> NÃO criar tabela `goals` separada  
> Benefício: Reutilizar 100% das APIs de budget (GET, POST, PUT, DELETE)

#### Telas

| Tela | Rota | Complexidade | Estimativa |
|------|------|--------------|------------|
| Goals List | `/` | Alta | 12-14h |
| Goal Details | `/detalhes-meta` | Alta | 12-16h |
| Edit Goal | `/editar-meta` | Média | 10-12h |
| Manage Goals | `/gerenciar-metas` | Média | 10-12h |

#### Componentes (16 atoms + 5 molecules + 4 organisms + 4 templates = 29 total)

**Atoms:**
- GoalIcon (ícone da categoria)
- Badge (ativo/inativo)
- MonthButton
- ProgressBar
- TabButton
- IconButton
- Button
- Input
- Select
- Switch (toggle)

**Molecules:**
- GoalCard (meta individual com progresso)
- MonthSelector (horizontal scroll)
- StatsCard (estatística resumida)
- TabBar (Gastos/Investimentos)
- FilterButtons

**Organisms:**
- GoalsList (lista de metas com filtros)
- DonutChart (overview de metas)
- Header
- BottomNav

**Templates:**
- MetasLayout (tela principal)
- DetalhesMetaLayout (detalhes)
- EditarMetaLayout (formulário)
- GerenciarMetasLayout (gerenciar)

#### Dados Mock

```typescript
interface MockGoal {
  id: string
  name: string // "Casa"
  type: 'gasto' | 'investimento'
  budget: number // 2000.00
  spent: number // 1500.00
  percentage: number // 75
  icon: string // "home"
  color: string // "#10B981"
  category: string // "Fixo" ou "Variável"
  alertAt80: boolean // Alertar em 80%
  alertAt100: boolean // Alertar em 100%
  active: boolean
  description?: string
  deadline?: string // "2026-12-31"
  createdAt: string
  updatedAt: string
}

interface MockGoalsData {
  goals: MockGoal[]
  totalBudget: number // Soma de todos budgets
  totalSpent: number // Soma de todos spent
  overallPercentage: number // Total spent / total budget
  transactions: Array<{
    id: string
    date: string
    description: string
    value: number
    goalId: string
  }>
}
```

#### 📊 Mapeamento Componente → Dados → Backend

**Tela 1: Lista de Metas (Goals List)**

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| MonthSelector | Lista de meses | Frontend (hardcoded) | - | ✅ Reuso |
| DonutChart (metas) | metas com budget/spent | `GET /budget/` ou `/goals/` | budget_geral | ✅ Adaptar |
| GoalCard | id, name, budget, spent, % | `GET /budget/` ou `/goals/` | budget_geral | ✅ Adaptar |
| TabBar (Gastos/Investimentos) | - | Frontend (filter) | - | ✅ Copiar |
| FAB (Criar meta) | - | - | - | ✅ Copiar |

**Tela 2: Detalhes da Meta (Goal Details)**

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| ProgressCard | meta com progresso | `GET /budget/{id}` ou `/goals/{id}` | budget_geral | ✅ Adaptar |
| MonthlyBreakdownChart | gastos por mês | `GET /transactions/` filtrado | journal_entries | ✅ Pronto |
| TransactionList | transações da meta | `GET /transactions/?grupo=X` | journal_entries | ✅ Pronto |

**Tela 3: Editar Meta (Edit Goal)**

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| FormFields | meta atual | `GET /budget/{id}` ou `/goals/{id}` | budget_geral | ✅ Adaptar |
| IconPicker | lista de ícones | Frontend (hardcoded) | - | ✅ Copiar |
| ColorPicker | paleta de cores | Frontend (hardcoded) | - | ✅ Copiar |
| SaveButton | - | `PUT /budget/{id}` ou `/goals/{id}` | budget_geral | ✅ Adaptar |

**Tela 4: Gerenciar Metas (Manage Goals)**

| Componente Protótipo | Dados Necessários | Backend Endpoint | DB Table | Status |
|---------------------|-------------------|------------------|----------|--------|
| GoalsList (ativas) | todas metas ativas | `GET /budget/?active=true` | budget_geral | ✅ Adaptar |
| ArchivedList | metas arquivadas | `GET /budget/?active=false` | budget_geral | ✅ Adaptar |
| ToggleButton | - | `PATCH /budget/{id}/toggle` | budget_geral | ⚠️ Criar |
| DeleteButton | - | `DELETE /budget/{id}` | budget_geral | ⚠️ Criar |

**✅ Backend Preparado - Endpoints Existentes:**

**Existem em:** `app_dev/backend/app/domains/budget/`

1. `GET /api/v1/budget/` - Lista todos orçamentos do usuário
2. `GET /api/v1/budget/{id}` - Busca orçamento específico
3. `POST /api/v1/budget/` - Criar novo orçamento
4. `PUT /api/v1/budget/{id}` - Atualizar orçamento

**✅ DECISÃO TOMADA: Estender budget_geral (NÃO criar tabela nova)**

**Migration Necessária:** (1h)
```sql
-- Migration Alembic
ALTER TABLE budget_geral ADD COLUMN tipo_meta TEXT CHECK(tipo_meta IN ('gasto', 'investimento'));
ALTER TABLE budget_geral ADD COLUMN alerta_80 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN alerta_100 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
ALTER TABLE budget_geral ADD COLUMN descricao TEXT;
ALTER TABLE budget_geral ADD COLUMN prazo DATE;
ALTER TABLE budget_geral ADD COLUMN icone TEXT DEFAULT 'home';
ALTER TABLE budget_geral ADD COLUMN cor TEXT DEFAULT '#10B981';
ALTER TABLE budget_geral ADD COLUMN ordem INTEGER DEFAULT 0;
```

**Endpoints Novos Necessários (2-3h):**

1. `PATCH /api/v1/budget/{id}/toggle` - Ativar/desativar meta
2. `DELETE /api/v1/budget/{id}` - Deletar meta (soft delete)
3. `PUT /api/v1/budget/reorder` - Reordenar metas (batch)

**📂 Estrutura de Arquivos:**
```
app_dev/frontend/src/
├── app/mobile/goals/
│   ├── page.tsx                        # Lista - copiar de export-to-main-project/metas/
│   ├── [id]/
│   │   └── page.tsx                    # Detalhes
│   ├── edit/[id]/
│   │   └── page.tsx                    # Editar
│   └── manage/
│       └── page.tsx                    # Gerenciar
├── features/budget/components/goals/
│   ├── goal-card.tsx
│   ├── goals-list.tsx
│   ├── goal-details.tsx
│   ├── goal-edit-form.tsx
│   ├── icon-picker.tsx
│   ├── color-picker.tsx
│   └── index.ts
└── features/budget/
    ├── types.ts                         # Goal interface
    ├── hooks/
    │   ├── use-goals.ts                 # CRUD operations
    │   └── use-goal-transactions.ts     # Filtered transactions
    └── utils/
        └── calculate-progress.ts        # Budget vs spent
```

#### Backend API

> **✅ DECISÃO DE SCHEMA:** Estender `budget_geral`, NÃO criar tabela `goals` nova.  
> Benefícios: Reusa 100% das APIs de budget, apenas adiciona colunas.

**Endpoints:** ✅ 90% EXISTEM (budget), apenas 2-3 novos

1. **Goals CRUD = Budget APIs (reutilizar):**
   - `GET /api/v1/budget/goals` - Listar todas metas do usuário
   - `POST /api/v1/budget/goals` - Criar meta
   - `GET /api/v1/budget/goals/{goalId}` - Buscar meta específica
   - `PUT /api/v1/budget/goals/{goalId}` - Atualizar meta
   - `DELETE /api/v1/budget/goals/{goalId}` - Deletar meta

2. **Goals Details:**
   - `GET /api/v1/budget/goals/{goalId}/details` - Detalhes + transações + breakdown mensal

3. **Goals Management:**
   - `PATCH /api/v1/budget/goals/{goalId}/toggle` - Ativar/desativar
   - `PUT /api/v1/budget/goals/reorder` - Reordenar (bulk update)

**Database Schema:**

**Opção 1 - Estender tabela existente:**
```sql
ALTER TABLE budget_geral ADD COLUMN tipo_meta TEXT CHECK(tipo_meta IN ('gasto', 'investimento'));
ALTER TABLE budget_geral ADD COLUMN alerta_80 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN alerta_100 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
ALTER TABLE budget_geral ADD COLUMN descricao TEXT;
ALTER TABLE budget_geral ADD COLUMN prazo DATE;
ALTER TABLE budget_geral ADD COLUMN icone TEXT;
ALTER TABLE budget_geral ADD COLUMN cor TEXT;
ALTER TABLE budget_geral ADD COLUMN ordem INTEGER DEFAULT 0;
```

**Opção 2 - Criar nova tabela:**
```sql
CREATE TABLE goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  nome TEXT NOT NULL,
  tipo TEXT CHECK(tipo IN ('gasto', 'investimento')),
  orcamento REAL NOT NULL,
  categoria TEXT, -- Fixo, Variável, etc
  icone TEXT,
  cor TEXT,
  alerta_80 BOOLEAN DEFAULT FALSE,
  alerta_100 BOOLEAN DEFAULT FALSE,
  ativo BOOLEAN DEFAULT TRUE,
  descricao TEXT,
  prazo DATE,
  ordem INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_ativo ON goals(ativo);
```

#### Status Atual

- ✅ Budget existe em `app_dev/backend/app/domains/budget/`
- ✅ Endpoint `GET /api/v1/budget/` retorna orçamentos por grupo
- ❌ Não existe sistema de "metas" com alertas, prazos, tipos
- ❌ Não existe UI de goals no mobile

#### Plano de Implementação

**FASE 1 - Goals List (Frontend Mock) (12-14h):**

1. **Criar estrutura base (1h)**
   - `app_dev/frontend/src/app/mobile/goals/page.tsx`
   - Layout com header, tabs, lista, bottom nav

2. **Implementar MonthSelector (1h)** (reuso do component existente)
   - Scroll horizontal de meses
   - Highlight mês atual

3. **Criar DonutChart component (2h)**
   - Chart circular com breakdown de metas
   - Centro com percentual overall
   - Legenda com cores

4. **Implementar TabBar (1h)**
   - Tabs: Gastos | Investimentos
   - Filter goals por tipo

5. **Criar GoalCard component (3h)**
   - Card com ícone, nome, progresso
   - ProgressBar com percentual
   - Badge "Ativo" ou "Inativo"
   - Cor customizada por meta
   - Tap para abrir detalhes

6. **Implementar GoalsList (2h)**
   - Lista de GoalCards
   - Filtrado por tab ativa
   - Ordenável (drag to reorder - opcional)

7. **Implementar FloatingActionButton (1h)**
   - FAB "+" para criar nova meta
   - Abre tela de edição

8. **Usar mock data (1h)**
   - Criar `mockGoalsData.ts`
   - 6 metas (4 gastos + 2 investimentos)
   - Mix de ativas/inativas, abaixo/acima budget

**FASE 2 - Goals List (Backend Real) (10-14h):**

1. **✅ Schema decidido: Estender `budget_geral`** 
   - Decisão tomada: NÃO criar tabela nova
   - Reutilizar 100% das APIs de budget existentes
   - Apenas adicionar colunas: tipo_meta, ativo, icone, cor, ordem

2. **Criar migration Alembic (1h)**
   - Adicionar colunas necessárias à budget_geral
   - Script SQL pronto (ver seção Migration)

3. **✅ Goals Model JÁ EXISTE (budget_geral)**
   - `app_dev/backend/app/domains/budget/models.py`
   - Apenas adicionar campos novos ao modelo existente

4. **✅ Goals Repository JÁ EXISTE (budget)**
   - `app_dev/backend/app/domains/budget/repository.py`
   - Reutilizar métodos CRUD existentes
   - Adicionar filtro por tipo_meta e ativo

5. **Goals Service - Estender (2h)**
   - `app_dev/backend/app/domains/budget/service.py`
   - Adicionar métodos: toggle_ativo, calcular_progresso
   - Lógica de spent já existe

6. **Goals Router - Estender (2h)**
   - `app_dev/backend/app/domains/budget/router.py`
   - Adicionar apenas 2 endpoints: toggle, soft delete
   - CRUD já existe (GET, POST, PUT)

7. **Registrar router (0.5h)**
   - `app_dev/backend/app/main.py`
   - Include router

8. **Conectar frontend (2h)**
   - Fetch de `GET /api/v1/budget/goals`
   - Loading, error states
   - Atualizar UI com dados reais

9. **Testar (1-2h)**
   - Validar cálculos
   - Testar filtros
   - Performance

**FASE 3 - Goal Details (12-16h):**

1. **Frontend Mock (6-8h)**
   - Criar `app_dev/frontend/src/app/mobile/goals/[id]/page.tsx`
   - Header com nome da meta
   - Progress card (budget, spent, remaining)
   - Monthly breakdown chart
   - Transaction list (filtered by goal)
   - Action buttons (edit, delete)

2. **Backend (4-6h)**
   - Endpoint `GET /api/v1/budget/goals/{goalId}/details`
   - Agregar transações por mês
   - Retornar histórico de 6-12 meses
   - Calcular projeção de conclusão (se deadline existe)

3. **Conectar (2h)**
   - Fetch e renderizar dados reais

**FASE 4 - Edit/Create Goal (10-12h):**

1. **Frontend Mock (5-6h)**
   - Criar `app_dev/frontend/src/app/mobile/goals/edit/[id]/page.tsx`
   - Form fields: nome, budget, tipo, categoria, ícone, cor
   - Icon picker component
   - Color picker component
   - Toggles para alertas (80%, 100%)
   - Date picker para deadline
   - Save/Cancel buttons

2. **Backend (3-4h)**
   - Endpoints `POST /api/v1/budget/goals` e `PUT /api/v1/budget/goals/{id}`
   - Validações: nome obrigatório, budget > 0, etc
   - Criar/atualizar goal

3. **Conectar (2h)**
   - Submit form
   - Validação frontend
   - Redirect após sucesso

**FASE 5 - Manage Goals (10-12h):**

1. **Frontend Mock (5-6h)**
   - Criar `app_dev/frontend/src/app/mobile/goals/manage/page.tsx`
   - Lista de metas (todas, incluindo inativas)
   - Toggle ativo/inativo
   - Delete com confirmação
   - Reorder (drag & drop - opcional)

2. **Backend (3-4h)**
   - Endpoint `PATCH /api/v1/budget/goals/{id}/toggle`
   - Endpoint `DELETE /api/v1/budget/goals/{id}` (soft delete recomendado)
   - Endpoint `PUT /api/v1/budget/goals/reorder` (batch update)

3. **Conectar (2h)**
   - Actions funcionais
   - Atualizar lista após mudanças

**APROVAÇÃO NECESSÁRIA:**

**Goals List:**
- [ ] **Schema de Banco Aprovado** (decisão: estender budget_geral vs nova tabela)
- [ ] Layout mobile aprovado
- [ ] DonutChart correto
- [ ] Filtros funcionam
- [ ] FAB abre tela de criação

**Goal Details:**
- [ ] Layout aprovado
- [ ] Monthly breakdown correto
- [ ] Transaction filtering correto
- [ ] Performance <2s

**Edit/Create:**
- [ ] Form validações corretas
- [ ] Icon picker funcional
- [ ] Color picker funcional
- [ ] Salvamento funcional

**Manage:**
- [ ] Toggle ativo/inativo funciona
- [ ] Delete pede confirmação e funciona
- [ ] Reorder funciona (se implementado)

---

## � Mapeamento de Dependências

### Relação Entre Protótipos

```
graph TD
    A[Upload Mobile] -->|sessionId| B[Preview Mobile]
    C[Metas] -.->|independente| D[Qualquer ordem]
    E[Dashboard Backend] -->|APIs prontas| F[Dashboard Frontend]
    
    style A fill:#10B981
    style B fill:#F59E0B
    style C fill:#10B981
    style E fill:#F59E0B
    style F fill:#10B981
```

**Legenda:**
- 🟢 Verde: Backend 100% pronto (pode começar imediatamente)
- 🟠 Laranja: Backend precisa de novos endpoints
- ➡️ Seta sólida: Dependência BLOQUEANTE
- ➡️ Seta tracejada: Independente (pode fazer em paralelo)

---

### Dependências Detalhadas

#### 1️⃣ Upload → Preview (BLOQUEANTE)

**Por quê Preview depende de Upload:**
```typescript
// Preview precisa do sessionId gerado pelo Upload

// 1. Upload executa (usuário faz upload)
POST /api/v1/upload/preview
Response: { sessionId: "abc123", ... }

// 2. Upload redireciona para Preview
router.push(`/mobile/preview?sessionId=abc123`)

// 3. Preview carrega dados usando sessionId
GET /api/v1/upload/preview/abc123
Response: { transactions: [...], ... }
```

**⚠️ Bloqueio:**
- Preview NÃO funciona sem Upload completo
- Upload DEVE gerar sessionId válido
- sessionId DEVE persistir no banco (preview_transacoes)

**🎯 Ordem de Implementação:**
1. Upload (6-8h) ✅
2. Preview (16-18h) ✅

---

#### 2️⃣ Dashboard Backend → Dashboard Frontend

**Por quê Frontend depende de Backend:**
```typescript
// Dashboard frontend precisa de 2 APIs que NÃO existem

// Já existem (6 APIs):
GET /api/v1/dashboard/metrics   // ✅ Existe
GET /api/v1/dashboard/chart     // ✅ Existe
GET /api/v1/dashboard/budget    // ✅ Existe
GET /api/v1/dashboard/categories // ✅ Existe
GET /api/v1/dashboard/cards     // ✅ Existe
GET /api/v1/dashboard/transactions // ✅ Existe

// Precisam ser criadas (2 APIs):
GET /api/v1/dashboard/income-sources // ❌ Não existe (donut chart)
PATCH /api/v1/dashboard/metrics      // ❌ Enhancement (changePercentage)
```

**⚠️ Bloqueio Parcial:**
- Frontend pode ser copiado COM mock data
- Backend tem 6/8 APIs prontas (75%)
- Apenas 2 APIs precisam ser criadas (3-4h)

**🎯 Ordem de Implementação:**
- Opção A (Paralela): Frontend com mock (8h) || Backend criar 2 APIs (4h)
- Opção B (Sequencial): Backend criar APIs (4h) → Frontend conectar (8h)

**Recomendação:** Opção A (mais rápido)

---

#### 3️⃣ Metas (INDEPENDENTE)

**Por quê Metas NÃO depende de outros:**
```python
# ✅ DECISÃO: Metas = Budget estendido (mesma tabela budget_geral)

# Endpoints existentes:
GET /api/v1/budget/        # ✅ Lista budgets (= goals)
GET /api/v1/budget/{id}    # ✅ Busca budget específico
POST /api/v1/budget/       # ✅ Criar budget
PUT /api/v1/budget/{id}    # ✅ Atualizar budget

# ✅ Tabela: budget_geral (já existe - ESTENDER, não criar nova)
# Migration: ADD COLUMN tipo_meta, ativo, icone, cor, ordem
# NÃO criar tabela goals separada (decisão tomada)
```

**✅ Pode começar a qualquer momento:**
- Não usa dados de Upload/Preview
- Não usa dados de Dashboard
- Backend 100% pronto (apenas extend schema)
- Pode ser feito em paralelo com qualquer outro

**🎯 Ordem Recomendada:**
- Fazer em paralelo com Dashboard backend (enquanto aguarda frontend)

---

### Ordem Ótima de Implementação

#### Semana 1 (Paralelo - 2 devs)

**👤 Dev 1: Upload → Preview**
```bash
Dia 1-2: Upload Frontend (6h)
Dia 2-3: Upload Backend conectar (2h)
Dia 3-7: Preview Frontend (16h)
Dia 8: Preview Backend conectar (4h)
```

**👤 Dev 2: Metas + Dashboard Backend**
```bash
Dia 1-4: Metas Frontend (12h)
Dia 5-6: Dashboard Backend criar 2 APIs (3h)
Dia 7-8: Metas Backend conectar (4h)
```

#### Semana 2 (Juntos - 2 devs)

**👥 Ambos: Dashboard Frontend + Ajustes Finais**
```bash
Dia 1-3: Dashboard Frontend copiar (8h)
Dia 4: Dashboard conectar APIs (2h)
Dia 5: Testes integração completa (8h)
```

**Total:** 38-47h (1 semana com 2 devs)

---

### Dependências de Biblioteca/Pacotes

#### Frontend (npm install)

```json
{
  "react-window": "^1.8.10",          // Virtual scrolling (Preview)
  "@types/react-window": "^1.8.8",
  "react-virtuoso": "^4.7.0",         // Alternativa virtual scroll
  "recharts": "^2.10.0"                // Charts (se não tiver)
}
```

**Instalação:**
```bash
cd app_dev/frontend
npm install react-window @types/react-window react-virtuoso recharts
```

#### Backend (pip install)

**✅ Todas dependências JÁ estão no requirements.txt**
```
fastapi
sqlalchemy
alembic
pydantic
pandas       # Upload parsing
openpyxl     # Excel files
PyPDF2       # PDF parsing
```

Nenhuma instalação adicional necessária! ✅

---

### Dependências de Banco de Dados

#### Tabelas Necessárias (TODAS já existem)

```sql
-- Upload/Preview
preview_transacoes          ✅ Existe
bank_format_compatibility   ✅ Existe
journal_entries             ✅ Existe
base_marcacoes              ✅ Existe
base_parcelas               ✅ Existe

-- Dashboard
journal_entries             ✅ Existe (reutiliza)

-- Metas
budget_geral                ✅ Existe (extend colunas)
```

#### Migrations Necessárias (Apenas 1)

**1. Extend budget_geral para Metas** (1h)
```sql
-- Migration: add_meta_fields_to_budget.py
ALTER TABLE budget_geral ADD COLUMN tipo_meta TEXT CHECK(tipo_meta IN ('gasto', 'investimento'));
ALTER TABLE budget_geral ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
ALTER TABLE budget_geral ADD COLUMN icone TEXT DEFAULT 'home';
ALTER TABLE budget_geral ADD COLUMN cor TEXT DEFAULT '#10B981';
ALTER TABLE budget_geral ADD COLUMN ordem INTEGER DEFAULT 0;
```

**Comando:**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic revision --autogenerate -m "add meta fields to budget_geral"
alembic upgrade head
```

**Sem outras migrations necessárias!** Todas as tabelas já existem.

---

### Resumo de Dependências

| Protótipo | Depende De | Bloqueante? | Backend APIs | Migrations |
|-----------|------------|-------------|--------------|------------|
| **Upload** | Nada | ❌ Não | 4 existem | 0 |
| **Preview** | Upload sessionId | ✅ Sim | 3 existem + 1 opcional | 0 |
| **Dashboard** | Backend 2 APIs | ⚠️ Parcial | 6 existem + 2 criar | 0 |
| **Metas** | Nada | ❌ Não | 4 existem (budget) | 1 extend budget_geral ✅ |

**Bloqueios Reais:**
1. Preview DEVE ser feito DEPOIS de Upload (sessionId)
2. Dashboard frontend funciona com mock, mas precisa APIs para produção
3. Metas precisa migration antes de produção

**Total de Trabalho Bloqueante:** ~1h (apenas migration de Metas)

---

## �🗺️ Roadmap de Implementação

### Timeline Geral

**Com 1 dev:** 2 semanas (38-47h)  
**Com 2 devs:** 1 semana (paralelo)

```
Semana 1 (Dev 1): Upload (6h) + Preview (16h)
Semana 1 (Dev 2): Metas (12h) + Dashboard backend (3h)
Semana 2 (Ambos): Dashboard frontend (8h) + Testes (4h)
```

### Fase 1: Upload + Preview Mobile (ALTA PRIORIDADE) 🔴

**Duração:** 2 semanas (20-26h)  
**Objetivo:** Mobile users podem importar arquivos e classificar transações

| Sprint | Tarefa | Duração | Deps |
|--------|--------|---------|------|
| **Sprint 1.1** | Upload Form - Frontend Mock | 4-6h | - |
| **Sprint 1.2** | Upload Form - Backend Real | 2-3h | 1.1 |
| **Sprint 1.3** | Preview - Frontend Mock | 16-20h | 1.2 |
| **Sprint 1.4** | Preview - Backend Real | 4-6h | 1.3 |

**Deliverables:**
- ✅ Upload mobile funcional
- ✅ Preview mobile com classificação
- ✅ Confirmação salva em journal_entries
- ✅ Fluxo completo testado

**Critérios de Sucesso:**
- [ ] Upload de arquivo funciona em iOS/Android
- [ ] Preview renderiza 100+ transações sem lag
- [ ] Classificação atualiza backend
- [ ] Confirmação redireciona para transactions

---

### Fase 2: Dashboard Mobile - Redesign (MÉDIA PRIORIDADE) 🟡

**Duração:** 1.5 semanas (10-14h)  
**Objetivo:** Substituir dashboard mobile atual pelo design novo do protótipo

**✅ O QUE JÁ EXISTE:**
- Desktop dashboard funcional (6 componentes)
- Mobile dashboard básico (design antigo)
- Backend 100% funcional (6 APIs prontas)

**🎨 O QUE VAMOS FAZER:**
- Copiar UI/UX nova do protótipo
- Manter backend existente (90%)
- Criar apenas 2 APIs novas (donut chart + changePercentage)

**⚠️ ESTRATÉGIA CRÍTICA:**
- ✅ **Frontend:** Copiar 100% do protótipo (design novo)
- ✅ **Backend:** Reutilizar 90% das APIs existentes
- ✅ **Trabalho:** Apenas adaptar e conectar (não criar do zero)

| Sprint | Tarefa | Duração | Deps |
|--------|--------|---------|------|
| **Sprint 2.1** | Copiar Frontend do Protótipo | 6-8h | - |
| **Sprint 2.2** | Criar 2 Novos Endpoints Backend | 3-4h | - |
| **Sprint 2.3** | Conectar Frontend nas APIs | 1-2h | 2.1, 2.2 |
| **Sprint 2.4** | Testes e Ajustes | 1h | 2.3 |

**Deliverables:**
- ✅ Dashboard mobile redesenhado (novo UI/UX)
- ✅ Bar chart de receitas/despesas
- ✅ Donut chart de income sources
- ✅ Seletor de mês funcional

**Critérios de Sucesso:**
- [ ] Charts legíveis em telas pequenas
- [ ] Dados agregados corretamente
- [ ] Performance <2s para carregar
- [ ] Month selector atualiza dados

---

### Fase 3: Sistema de Metas (BAIXA PRIORIDADE) 🟢

**Duração:** 4 semanas (44-52h)  
**Objetivo:** Mobile users gerenciam metas de gastos e investimentos

| Sprint | Tarefa | Duração | Deps |
|--------|--------|---------|------|
| **Sprint 3.1** | ✅ Schema Decidido: Estender budget_geral + Migration | 1h | - |
| **Sprint 3.2** | Goals List - Frontend Mock | 12-14h | 3.1 |
| **Sprint 3.3** | Goals List - Backend Real | 12-16h | 3.1, 3.2 |
| **Sprint 3.4** | Goal Details - Full Stack | 12-16h | 3.3 |
| **Sprint 3.5** | Edit/Create Goal - Full Stack | 10-12h | 3.3 |
| **Sprint 3.6** | Manage Goals - Full Stack | 10-12h | 3.3 |

**Deliverables:**
- ✅ Lista de metas funcional
- ✅ Detalhes de meta com breakdown
- ✅ Criar/editar metas
- ✅ Gerenciar metas (ativar/desativar/deletar)

**Critérios de Sucesso:**
- [ ] CRUD completo funciona
- [ ] Metas calculam spent corretamente
- [ ] Alertas (80%, 100%) funcionam
- [ ] UI fluida e responsiva

---

## 📊 Mapeamento de Dados

### Tabela de Transformações Mock → Real

| Tela | Campo Mock | Fonte Backend | Transformação Necessária |
|------|-----------|---------------|--------------------------|
| **Upload** | `banks` | Hardcoded frontend | Nenhuma (pode mover para config backend) |
| | `creditCards` | Hardcoded ou API | Considerar endpoint `GET /api/v1/cards` |
| **Preview** | `transactions` | `GET /api/v1/upload/preview/{sessionId}` | Mapear `origem` → `source` |
| | `grupos/subgrupos` | `base_marcacoes` table | Join e agrupar |
| **Insights** | `monthlyData` | Aggregar `journal_entries` WHERE Ano=X | GROUP BY Mes, somar Valor |
| | `incomeSources` | Aggregar `journal_entries` WHERE CategoriaGeral='Receita' | GROUP BY Grupo, calcular % |
| | `walletBalance` | Calcular: Σ(Receitas) - Σ(Despesas) | All time ou YTD |
| **Goals** | `goals` | `goals` table (nova) ou `budget_geral` (extend) | Adicionar campos extras |
| | `spent` | Aggregar `journal_entries` WHERE Grupo=goal.name | SUM(Valor) WHERE Grupo matches |
| | `transactions` | `journal_entries` WHERE Grupo=goal.name | Filter by Grupo/Subgrupo |

### Gaps de Dados Identificados

| Gap | Impacto | Solução |
|-----|---------|---------|
| **Wallet Balance** | Dashboard insights não tem fonte de saldo real | Calcular agregando todas transações OU adicionar campo `saldo_atual` em users |
| **Income Source Colors** | Backend não retorna cores para cada fonte | Hardcoded frontend OU adicionar coluna `cor` em base_marcacoes |
| **Goal Icons** | Backend não tem campo ícone | Adicionar coluna `icone` em budget_geral (estender) |
| **Alert Thresholds** | Budget não tem alertas 80%/100% | Adicionar colunas `alerta_80`, `alerta_100` |
| **Goal Deadlines** | Budget não tem prazos | Adicionar coluna `prazo` (DATE) |
| **Transaction Grouping** | Preview agrupa no frontend, pode ser pesado | Considerar agregar no backend (opcional) |

### Mapeamento Completo: Componente → API → Tabela

#### 📤 Upload Mobile

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| FileInput | arquivo binário | - | - | - | ✅ Frontend only |
| BankSelector | lista de bancos | `GET /api/v1/banks` | bank_format_compatibility | `SELECT id, name, logoUrl FROM bank_format_compatibility` | ✅ Pronto |
| CardSelector | lista de cartões | `GET /api/v1/cards` | credit_cards | `SELECT id, lastDigits, name FROM credit_cards WHERE user_id=X` | ✅ Pronto |
| MonthYearPicker | - | - | - | - | ✅ Frontend only |
| FormatSelector | - | - | - | - | ✅ Frontend only |
| UploadButton | response sessionId | `POST /api/v1/upload/preview` | preview_transacoes | `INSERT INTO preview_transacoes ...` | ✅ Pronto |

**📋 Fluxo de Dados Upload:**
```
1. User seleciona arquivo → FileInput (state)
2. User seleciona banco → BankSelector → GET /banks
3. User seleciona cartão → CardSelector → GET /cards
4. User escolhe mês → MonthYearPicker (state)
5. User clica Upload → POST /preview → sessionId retornado
6. Redirect → /mobile/preview?sessionId=abc123
```

**🔌 APIs Necessárias:** 3 (TODAS existem)
**📊 Tabelas Usadas:** bank_format_compatibility, credit_cards, preview_transacoes

---

#### 🔍 Preview Mobile

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| FileInfoCard | banco, cartão, arquivo, mês, total | `GET /preview/{id}` | preview_transacoes | `SELECT session_id, banco, cartao, arquivo FROM preview_transacoes WHERE session_id=X LIMIT 1` | ✅ Pronto |
| TabBar (8 filtros) | contadores por origem | Frontend calc | - | - | ✅ Calcular no frontend |
| TransactionCard | data, nome, valor, grupo, subgrupo | `GET /preview/{id}` | preview_transacoes | `SELECT * FROM preview_transacoes WHERE session_id=X` | ✅ Pronto |
| TransactionList | todas transações | `GET /preview/{id}` | preview_transacoes | `SELECT * FROM preview_transacoes WHERE session_id=X ORDER BY data DESC` | ✅ Pronto |
| ClassificationModal | grupos, subgrupos | `GET /marcacoes/grupos` | base_marcacoes | `SELECT DISTINCT grupo, subgrupo FROM base_marcacoes` | ✅ Pronto |
| BottomActionBar | - | `POST /preview/{id}/confirm` | journal_entries | `INSERT INTO journal_entries ... DELETE FROM preview_transacoes` | ✅ Pronto |

**📋 Fluxo de Dados Preview:**
```
1. Page load → GET /preview/{sessionId}
2. Calcular contadores (all: 58, classified: 39, ...) → Frontend
3. Agrupar transações idênticas → Frontend
4. User clica transação → Abrir ClassificationModal
5. User escolhe grupo/subgrupo → PATCH /preview/{id}/classify
6. Atualizar estado local (optimistic update)
7. User clica Confirmar → Validar todas classificadas
8. POST /preview/{id}/confirm → Importa para journal_entries
9. Redirect → /mobile/transactions
```

**🔌 APIs Necessárias:** 4 (3 existem + 1 opcional batch)
**📊 Tabelas Usadas:** preview_transacoes, base_marcacoes, journal_entries, base_parcelas

**⚠️ API Opcional (não bloqueante):**
- `PATCH /preview/{id}/batch` - Classificar múltiplas transações de uma vez
- Benefício: Performance (1 request vs N requests)
- Workaround: Chamar PATCH /classify em loop (funciona, mas mais lento)
- Esforço: 1-2h se necessário

---

#### 📊 Dashboard Mobile (Redesign)

**⚠️ CONTEXTO:** Dashboard desktop e mobile JÁ EXISTEM. Este é um REDESIGN da interface mobile.

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| MonthSelector | lista de meses | Frontend hardcoded | - | - | ✅ Reuso componente |
| YTDToggle | - | Frontend state | - | - | ✅ Copiar do protótipo |
| WalletBalanceCard | saldo, variação % | `GET /dashboard/metrics` | journal_entries | `SELECT SUM(Valor) FROM journal_entries WHERE user_id=X AND CategoriaGeral='Receita' MINUS despesas` | ⚠️ Enhancement |
| BarChart | receitas/despesas por mês | `GET /dashboard/chart` | journal_entries | `SELECT Mes, CategoriaGeral, SUM(Valor) FROM journal_entries WHERE Ano=X GROUP BY Mes, CategoriaGeral` | ✅ Pronto |
| DonutChart (receitas) | receitas por fonte | ❌ `GET /dashboard/income-sources` | journal_entries | `SELECT Grupo, SUM(Valor) FROM journal_entries WHERE CategoriaGeral='Receita' GROUP BY Grupo` | ❌ Criar |
| TabBar (Income/Expenses) | - | Frontend state | - | - | ✅ Copiar |
| MetricCards | totais mês | `GET /dashboard/metrics` | journal_entries | `SELECT SUM(Valor) FROM journal_entries WHERE user_id=X AND Mes=Y` | ✅ Pronto |

**📋 Fluxo de Dados Dashboard:**
```
1. Page load → Carregar mês atual
2. GET /dashboard/metrics?year=2026&month=2 → Saldo, totais
3. GET /dashboard/chart?year=2026 → Dados do bar chart
4. GET /dashboard/income-sources?year=2026&month=2 → Donut chart
5. User alterna mês → Recarregar todos endpoints com novo mês
6. User alterna YTD → Recarregar sem filtro de mês
```

**🔌 APIs Necessárias:** 8 total
- ✅ 6 existem (metrics, chart, budget, categories, cards, transactions)
- ❌ 2 precisam ser criadas:
  1. `GET /dashboard/income-sources` (2-3h) - Donut chart de receitas
  2. Enhancement `GET /dashboard/metrics` (1h) - Adicionar changePercentage

**📊 Tabelas Usadas:** journal_entries (100% reutilização)

**🆕 API a Criar (income-sources):**
```python
# app_dev/backend/app/domains/dashboard/router.py
@router.get("/income-sources")
def get_income_sources(
    user_id: int = Depends(get_current_user_id),
    year: int = Query(...),
    month: Optional[int] = None
):
    query = """
    SELECT 
        Grupo,
        SUM(Valor) as total,
        COUNT(*) as count
    FROM journal_entries
    WHERE user_id = :user_id
      AND Ano = :year
      AND (:month IS NULL OR Mes = :month)
      AND CategoriaGeral = 'Receita'
      AND IgnorarDashboard = 0
    GROUP BY Grupo
    ORDER BY total DESC
    """
    
    results = db.execute(query, {"user_id": user_id, "year": year, "month": month})
    total_income = sum(r.total for r in results)
    
    return {
        "incomeSources": [
            {
                "name": r.Grupo,
                "amount": float(r.total),
                "percentage": round((r.total / total_income) * 100, 1),
                "color": get_color_for_group(r.Grupo),  # Helper function
                "count": r.count
            }
            for r in results
        ],
        "totalIncome": float(total_income)
    }
```

---

#### 🎯 Metas (Goals) Mobile

##### Tela 1: Goals List

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| MonthSelector | lista de meses | Frontend hardcoded | - | - | ✅ Reuso |
| DonutChart (metas) | metas com budget/spent | `GET /budget/?active=true` | budget_geral, journal_entries | `SELECT * FROM budget_geral WHERE user_id=X AND ativo=1` + JOIN para spent | ✅ Adaptar |
| GoalCard | id, name, budget, spent, % | `GET /budget/` | budget_geral | Same as above | ✅ Adaptar |
| TabBar (Gastos/Invest) | - | Frontend filter | - | - | ✅ Copiar |
| FAB (Criar meta) | - | - | - | - | ✅ Copiar |

##### Tela 2: Goal Details

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| ProgressCard | meta com progresso | `GET /budget/{id}` | budget_geral | `SELECT * FROM budget_geral WHERE id=X` | ✅ Pronto |
| MonthlyBreakdownChart | gastos por mês | `GET /transactions/?grupo=X` | journal_entries | `SELECT Mes, SUM(Valor) FROM journal_entries WHERE Grupo=X GROUP BY Mes` | ✅ Pronto |
| TransactionList | transações da meta | `GET /transactions/?grupo=X` | journal_entries | `SELECT * FROM journal_entries WHERE Grupo=X ORDER BY Data DESC` | ✅ Pronto |

##### Tela 3: Edit Goal

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| FormFields | meta atual | `GET /budget/{id}` | budget_geral | `SELECT * FROM budget_geral WHERE id=X` | ✅ Pronto |
| IconPicker | lista de ícones | Frontend hardcoded | - | - | ✅ Copiar |
| ColorPicker | paleta | Frontend hardcoded | - | - | ✅ Copiar |
| SaveButton | - | `PUT /budget/{id}` | budget_geral | `UPDATE budget_geral SET ... WHERE id=X` | ✅ Pronto |

##### Tela 4: Manage Goals

| Componente UI | Dados Necessários | Backend API | DB Table | Método SQL | Status |
|---------------|-------------------|-------------|----------|------------|--------|
| GoalsList (ativas) | metas ativas | `GET /budget/?active=true` | budget_geral | `SELECT * FROM budget_geral WHERE ativo=1` | ✅ Adaptar |
| ArchivedList | metas arquivadas | `GET /budget/?active=false` | budget_geral | `SELECT * FROM budget_geral WHERE ativo=0` | ✅ Adaptar |
| ToggleButton | - | ❌ `PATCH /budget/{id}/toggle` | budget_geral | `UPDATE budget_geral SET ativo = NOT ativo WHERE id=X` | ❌ Criar (30min) |
| DeleteButton | - | ❌ `DELETE /budget/{id}` | budget_geral | `UPDATE budget_geral SET deleted_at = NOW() WHERE id=X` | ❌ Criar (30min) |

**📋 Fluxo de Dados Goals:**
```
1. Page load → GET /budget/?active=true
2. Calcular spent: Para cada goal, GET /transactions/?grupo={goal.name}&year=Y&month=M
3. Calcular progresso: (spent / budget) * 100
4. Colorir: red (>100%), yellow (80-100%), green (<80%)
5. User clica goal → Navigate to /mobile/goals/{id}
6. Details page → GET /budget/{id} + GET /transactions/?grupo=X
7. User edita → PUT /budget/{id}
8. User deleta → DELETE /budget/{id} (soft delete)
```

**🔌 APIs Necessárias:** 7 total
- ✅ 5 existem (GET /budget, GET /budget/{id}, POST /budget, PUT /budget/{id}, GET /transactions)
- ❌ 2 precisam ser criadas:
  1. `PATCH /budget/{id}/toggle` (30min) - Ativar/desativar
  2. `DELETE /budget/{id}` (30min) - Soft delete

**📊 Tabelas Usadas:** 
- budget_geral (precisa extend com colunas: tipo_meta, ativo, icone, cor, ordem)
- journal_entries (para calcular spent)

**🛠️ Migration Necessária (DECISÃO: ESTENDER budget_geral):**
```sql
-- ✅ Migration: add_meta_fields_to_budget
-- Decisão: NÃO criar tabela goals, estender budget_geral existente
ALTER TABLE budget_geral ADD COLUMN tipo_meta TEXT CHECK(tipo_meta IN ('gasto', 'investimento'));
ALTER TABLE budget_geral ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
ALTER TABLE budget_geral ADD COLUMN icone TEXT DEFAULT 'home';
ALTER TABLE budget_geral ADD COLUMN cor TEXT DEFAULT '#10B981';
ALTER TABLE budget_geral ADD COLUMN ordem INTEGER DEFAULT 0;
ALTER TABLE budget_geral ADD COLUMN alerta_80 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN alerta_100 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN descricao TEXT;
ALTER TABLE budget_geral ADD COLUMN prazo DATE;
```

---

### Resumo do Mapeamento

#### Estatísticas de APIs

| Protótipo | APIs Existentes | APIs Novas | APIs Opcionais | Total | % Pronto |
|-----------|----------------|------------|----------------|-------|----------|
| Upload | 4 | 0 | 0 | 4 | 100% ✅ |
| Preview | 3 | 0 | 1 | 4 | 95% ✅ |
| Dashboard | 6 | 2 | 0 | 8 | 75% ⚠️ |
| Metas | 5 | 2 | 0 | 7 | 71% ⚠️ |
| **TOTAL** | **18** | **4** | **1** | **23** | **90%** |

#### Estatísticas de Tabelas

| Tabela DB | Usada Por | Opera\u00e7\u00f5es | Status |
|-----------|-----------|---------|--------|
| preview_transacoes | Upload, Preview | INSERT, SELECT, UPDATE, DELETE | ✅ Existe |
| journal_entries | Preview, Dashboard, Metas | INSERT, SELECT | ✅ Existe |
| base_marcacoes | Preview, Upload | SELECT | ✅ Existe |
| base_parcelas | Preview (detecção) | SELECT | ✅ Existe |
| bank_format_compatibility | Upload | SELECT | ✅ Existe |
| credit_cards | Upload | SELECT | ✅ Existe |
| budget_geral | Metas | SELECT, INSERT, UPDATE, DELETE | ⚠️ Precisa extend |

**Todas as 7 tabelas JÁ existem!** Apenas budget_geral precisa de colunas adicionais.

#### Esforço Total de Backend

| Tarefa | Esforço | Bloqueante? |
|--------|---------|-------------|
| Criar GET /dashboard/income-sources | 2-3h | ⚠️ Sim (para Dashboard) |
| Enhancement GET /dashboard/metrics | 1h | ⚠️ Sim (para Dashboard) |
| Criar PATCH /budget/{id}/toggle | 30min | ⚠️ Sim (para Metas Manage) |
| Criar DELETE /budget/{id} | 30min | ⚠️ Sim (para Metas Manage) |
| Migration budget_geral | 30min | ⚠️ Sim (para Metas) |
| Criar PATCH /preview/{id}/batch | 1-2h | ✅ Não (opcional) |
| **TOTAL** | **5-7h** | **4-5h bloqueantes** |

**Conclusão:** 90% do backend está pronto. Apenas 5-7h de trabalho para 100% funcional!

---

## 🧩 Estratégia de Componentes

### Componentes Compartilhados (Criar uma vez, usar em todos)

**Localização:** `app_dev/frontend/src/components/mobile/`

| Componente | Status | Onde Usar | Prioridade |
|------------|--------|-----------|------------|
| `tab-button.tsx` | 🆕 Criar | Preview, Goals, Insights | Alta |
| `tab-bar.tsx` | 🆕 Criar | Preview, Goals, Insights | Alta |
| `stats-card.tsx` | 🆕 Criar | Insights, Goals | Média |
| `donut-chart.tsx` | 🆕 Criar | Insights, Goals | Alta |
| `bar-chart.tsx` | 🆕 Criar | Insights, Goals Details | Alta |
| `month-scroll-picker.tsx` | ✅ Existe | Goals, Insights | - |
| `progress-bar.tsx` | ✅ Existe | Goals | - |
| `icon-button.tsx` | ✅ Existe | Todos | - |
| `bottom-navigation.tsx` | ✅ Existe | Todos | - |
| `mobile-header.tsx` | ✅ Existe | Todos | - |
| `transaction-card.tsx` | ✅ Existe | Preview, Goals Details | - |
| `category-icon.tsx` | 🔄 Rename de GoalIcon | Goals, Preview | Baixa |

**Ações Imediatas:**

1. **Criar componentes novos:**
```bash
touch app_dev/frontend/src/components/mobile/tab-button.tsx
touch app_dev/frontend/src/components/mobile/tab-bar.tsx
touch app_dev/frontend/src/components/mobile/stats-card.tsx
touch app_dev/frontend/src/components/mobile/donut-chart.tsx
touch app_dev/frontend/src/components/mobile/bar-chart.tsx
```

2. **Extrair de protótipos:**
   - Copiar implementação de `export-to-main-project/*/src/components/atoms/` e `molecules/`
   - Adaptar para shadcn/ui style
   - Remover dependências específicas do protótipo

3. **Documentar props:**
   - Cada componente deve ter TypeScript interfaces claras
   - Incluir exemplo de uso no comentário

### Componentes Feature-Specific

**Localização:** `app_dev/frontend/src/features/<feature>/components/`

| Feature | Componentes Específicos | Prioridade |
|---------|------------------------|------------|
| **Upload** | `file-input.tsx`, `upload-form.tsx` | Alta |
| **Preview** | `file-info-card.tsx`, `classification-bottom-sheet.tsx`, `transaction-list.tsx` | Alta |
| **Insights** | `insights-chart.tsx`, `income-sources-breakdown.tsx` | Média |
| **Goals** | `goal-card.tsx`, `goals-list.tsx`, `goal-details.tsx`, `goal-edit-form.tsx`, `manage-goals.tsx` | Baixa |

**Estratégia:**
- Componentes específicos NÃO devem ser reutilizados fora da feature
- Se perceber reutilização em 2+ features, refatorar para compartilhado
- Manter features isoladas para facilitar manutenção

---

## ⚠️ Análise de Riscos

### 🔴 Riscos Críticos

#### Risco 1: Performance do Preview Mobile
**Impacto:** Alto | **Probabilidade:** Alta

**Problema:** Preview com 100+ transações pode travar em telas mobile

**Mitigação:**
1. ✅ Implementar lista virtualizada (react-window)
2. ✅ Paginar transações (carregar 20 por vez)
3. ✅ Agrupar por padrão (reduz itens visíveis)
4. ✅ React.memo em TransactionCard
5. ✅ Debounce em busca/filtros
6. ✅ Testar em dispositivos reais (não só simulador)

**Responsável:** Dev Frontend  
**Prazo Validação:** Sprint 1.3 (Preview Mock)

---

#### Risco 2: Classificação Modal em Mobile
**Impacto:** Médio | **Probabilidade:** Média

**Problema:** Dropdowns com 100+ grupos/subgrupos não são mobile-friendly

**Mitigação:**
1. ✅ Usar bottom sheet em vez de modal
2. ✅ Implementar busca/filtro nos dropdowns
3. ✅ Seção "Recentes" (últimos 5 usados)
4. ✅ Seção "Favoritos" (top 10 mais usados)
5. ⚠️ Considerar sugestões de IA (futuro)

**Responsável:** Dev Frontend  
**Prazo Validação:** Sprint 1.3 (Preview Mock)

---

#### Risco 3: Schema de Banco para Goals
**Impacto:** Alto | **Probabilidade:** Baixa

**✅ DECISÃO TOMADA: Estender `budget_geral`**

**Motivo:** Reutilizar APIs existentes, menos código, budget e goals são conceitos relacionados

**Mitigação:**
1. ✅ **DECISÃO TOMADA** - Estender budget_geral
2. ✅ Migration SQL pronta (ver Sprint 3.1)
3. ✅ 4 APIs CRUD já existem (GET, POST, PUT, DELETE)
4. ✅ Apenas 2 endpoints novos (toggle, reorder)

**Responsável:** Tech Lead (decisão aprovada)  
**Status:** ✅ Resolvido - Estender budget_geral

---

#### Risco 4: Chart Rendering em Telas Pequenas
**Impacto:** Médio | **Probabilidade:** Baixa

**Problema:** Charts podem ficar ilegíveis em iPhone SE (375px)

**Mitigação:**
1. ✅ Usar SVG responsivo (viewBox)
2. ✅ Simplificar dados em mobile (mostrar 6 meses em vez de 12)
3. ✅ Fontes maiores em labels
4. ✅ Testar em múltiplos tamanhos (SE, 14 Pro, 14 Pro Max)
5. ⚠️ Considerar gestos de zoom/pan (futuro)

**Responsável:** Dev Frontend  
**Prazo Validação:** Sprint 2.1 (Insights Mock)

---

### 🟡 Riscos Médios

#### Risco 5: Sincronização Mock → Real Data
**Impacto:** Médio | **Probabilidade:** Baixa

**Problema:** Estrutura de mock data pode não bater com backend response

**Mitigação:**
1. ✅ Definir TypeScript interfaces ANTES de implementar
2. ✅ Usar adapter pattern para transformações
3. ✅ Testar mock e real lado a lado
4. ✅ Documentar diferenças no código

**Responsável:** Dev Full Stack  
**Prazo:** Cada transição Mock → Real

---

#### Risco 6: Upload File Size Limits
**Impacto:** Médio | **Probabilidade:** Média

**Problema:** Mobile uploads grandes podem dar timeout

**Mitigação:**
1. ✅ Limite de 5MB no frontend (validação)
2. ✅ Progress indicator durante upload
3. ✅ Retry logic para falhas
4. ⚠️ Considerar chunked upload (futuro)

**Responsável:** Dev Backend + Frontend  
**Prazo Validação:** Sprint 1.2 (Upload Backend)

---

### ✅ Riscos Baixos

#### Risco 7: Browser Compatibility
**Impacto:** Baixo | **Probabilidade:** Baixa

**Problema:** Charts/SVG podem não renderizar em browsers antigos

**Mitigação:** Target iOS 14+, Android 10+ apenas

---

### 🛡️ Desafios Técnicos

#### Touch Interactions
- **Desktop:** Click, hover
- **Mobile:** Tap, long press, swipe
- **Solução:** Implementar event handlers mobile-specific, evitar hover-dependent UX

#### Navigation Patterns
- **Desktop:** Sidebar + top nav
- **Mobile:** Bottom tabs + header
- **Solução:** Usar componentes existentes (`bottom-navigation.tsx`)

#### Form Inputs
- **Desktop:** Dropdown select
- **Mobile:** Native select (iOS/Android optimized)
- **Solução:** shadcn/ui Select com mobile styling OU native `<select>`

#### Viewport Height
- **Desktop:** `vh` funciona bem
- **Mobile:** Keyboard reduz viewport → UI quebra
- **Solução:** Usar `dvh` (dynamic viewport height) OU CSS `env(safe-area-inset-bottom)`

---

## 📝 Passo a Passo Detalhado

### 🚀 Setup Inicial (Antes de começar)

**⏱️ Tempo estimado:** 30 minutos

#### Checklist de Preparação

- [ ] **1. Verificar Status do Projeto:**
  ```bash
  cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
  
  # Verificar branch atual
  git branch --show-current
  
  # Verificar mudanças não commitadas
  git status
  
  # Se houver mudanças, commitar antes de prosseguir
  git add .
  git commit -m "chore: save current work before mobile integration"
  ```

- [ ] **2. Criar Branch de Feature:**
  ```bash
  # Criar e mudar para nova branch
  git checkout -b feature/mobile-prototypes-integration
  
  # Push para remoto (criar branch no GitHub)
  git push -u origin feature/mobile-prototypes-integration
  
  # Confirmar está na branch correta
  git branch --show-current
  # Output esperado: feature/mobile-prototypes-integration
  ```

- [ ] **3. Validar Acesso aos Protótipos:**
  ```bash
  # Verificar se pasta existe e tem conteúdo
  ls -la export-to-main-project/
  # Deve listar: dashboard, metas, preview-upload, upload
  
  # Verificar estrutura de cada protótipo
  for proto in dashboard metas preview-upload upload; do
    echo "\n=== $proto ==="
    ls -la export-to-main-project/$proto/app/
  done
  
  # Contar componentes de cada protótipo
  find export-to-main-project/ -name "*.tsx" -o -name "*.ts" | wc -l
  # Deve ter ~50-100 arquivos TypeScript
  ```

- [ ] **Backup:**
  ```bash
  ./scripts/deploy/backup_daily.sh
  ```

- [ ] **Documentação:**
  - [ ] Ler este documento completamente
  - [ ] Stakeholder aprovou prioridades
  - [ ] Tech lead revisou arquitetura

- [ ] **Ambiente:**
  - [ ] Servidores rodando (backend + frontend)
  - [ ] Banco de dados atualizado
  - [ ] Dependências instaladas

- [ ] **Ferramentas:**
  - [ ] VS Code + extensões
  - [ ] iOS Simulator OU Android Emulator
  - [ ] Postman/Insomnia (testar APIs)

---

### 📱 FASE 1: Upload + Preview Mobile

#### Sprint 1.1: Upload Form - Frontend Mock (4-6h)

**Objetivo:** Tela de upload funciona com dados fake

**Passo 1: Criar estrutura (0.5h)**

```bash
# Criar diretórios
mkdir -p app_dev/frontend/src/app/mobile/upload
mkdir -p app_dev/frontend/src/features/upload/components

# Criar arquivos
touch app_dev/frontend/src/app/mobile/upload/page.tsx
touch app_dev/frontend/src/features/upload/components/upload-form.tsx
touch app_dev/frontend/src/features/upload/components/index.ts
```

**Passo 2: Copiar componentes do protótipo (1h)**

```bash
# Copiar componentes úteis
cp export-to-main-project/upload/src/components/atoms/Button.tsx app_dev/frontend/src/components/mobile/
cp export-to-main-project/upload/src/components/molecules/FileInput.tsx app_dev/frontend/src/features/upload/components/
# ... etc
```

**Passo 3: Criar mock data (0.5h)**

```typescript
// app_dev/frontend/src/features/upload/mockData.ts
export const mockBanks = [
  { id: '1', name: 'Itaú' },
  { id: '2', name: 'Nubank' },
  { id: '3', name: 'Bradesco' },
  // ...
]

export const mockCreditCards = [
  { id: '1', bankId: '1', lastDigits: '9266', name: 'Itaú Mastercard' },
  // ...
]

export const mockMonths = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

export const mockYears = [2024, 2025, 2026]

export const mockFileFormats = [
  { value: 'csv', label: 'CSV' },
  { value: 'xlsx', label: 'Excel' },
  { value: 'pdf', label: 'PDF' },
  { value: 'ofx', label: 'OFX' }
]
```

**Passo 4: Implementar UploadForm component (2h)**

```typescript
// app_dev/frontend/src/features/upload/components/upload-form.tsx
'use client'

import { useState } from 'react'
import { mockBanks, mockCreditCards, mockMonths, mockYears, mockFileFormats } from '../mockData'

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [bank, setBank] = useState('')
  const [card, setCard] = useState('')
  const [tipoDocumento, setTipoDocumento] = useState<'extrato' | 'fatura'>('fatura')
  const [month, setMonth] = useState('')
  const [year, setYear] = useState(2026)
  const [format, setFormat] = useState('csv')

  const handleSubmit = () => {
    // Mock submit - apenas log por enquanto
    console.log('Mock upload:', { file, bank, card, tipoDocumento, month, year, format })
    alert('Mock upload - conectar backend no próximo sprint')
  }

  return (
    <div className="p-4 space-y-4">
      {/* File input drag & drop */}
      <div className="border-2 border-dashed rounded-lg p-8 text-center">
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      </div>

      {/* Tabs: Extrato | Fatura */}
      <div className="flex gap-2">
        <button onClick={() => setTipoDocumento('extrato')}>Extrato</button>
        <button onClick={() => setTipoDocumento('fatura')}>Fatura</button>
      </div>

      {/* Selects */}
      <select value={bank} onChange={(e) => setBank(e.target.value)}>
        <option value="">Selecione o banco</option>
        {mockBanks.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
      </select>

      {tipoDocumento === 'fatura' && (
        <select value={card} onChange={(e) => setCard(e.target.value)}>
          <option value="">Selecione o cartão</option>
          {mockCreditCards.filter(c => c.bankId === bank).map(c => (
            <option key={c.id} value={c.id}>{c.name} •••• {c.lastDigits}</option>
          ))}
        </select>
      )}

      <select value={month} onChange={(e) => setMonth(e.target.value)}>
        <option value="">Mês</option>
        {mockMonths.map((m, i) => <option key={i} value={String(i+1)}>{m}</option>)}
      </select>

      <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
        {mockYears.map(y => <option key={y} value={y}>{y}</option>)}
      </select>

      <button onClick={handleSubmit} disabled={!file || !bank}>
        Processar Arquivo
      </button>
    </div>
  )
}
```

**Passo 5: Criar página mobile (0.5h)**

```typescript
// app_dev/frontend/src/app/mobile/upload/page.tsx
import { UploadForm } from '@/features/upload/components/upload-form'
import { MobileHeader } from '@/components/mobile/mobile-header'

export default function MobileUploadPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <MobileHeader title="Importar Arquivo" />
      <UploadForm />
    </div>
  )
}
```

**Passo 6: Testar no browser mobile (0.5h)**

```bash
# Iniciar dev server
npm run dev

# Abrir: http://localhost:3000/mobile/upload
# Testar em Chrome DevTools (iPhone SE, iPhone 14)
```

**✅ Checklist Sprint 1.1:**
- [ ] Tela carrega sem erros
- [ ] File input funciona (selecionar arquivo)
- [ ] Tabs Extrato/Fatura alternam
- [ ] Bank selector funciona
- [ ] Card selector filtra por banco
- [ ] Month/Year selecionáveis
- [ ] Botão "Processar" mostra alert com mock data
- [ ] Layout responsivo (testa em iPhone SE)

**🚫 Bloqueadores para próximo sprint:**
- Upload form frontend não funcional

**📸 Screenshot para aprovação:**
- Tirar screenshot e enviar para stakeholder

---

#### Sprint 1.2: Upload Form - Backend Real (2-3h)

**Objetivo:** Upload envia arquivo real para backend e redireciona para preview

**Passo 1: Implementar upload com FormData (1h)**

```typescript
// app_dev/frontend/src/features/upload/components/upload-form.tsx
import { useRouter } from 'next/navigation'

export function UploadForm() {
  const router = useRouter()
  const [isUploading, setIsUploading] = useState(false)
  
  const handleSubmit = async () => {
    if (!file || !bank) return

    setIsUploading(true)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('banco', bank)
    formData.append('tipoDocumento', tipoDocumento)
    if (card) formData.append('cartao', card)
    if (month) formData.append('mesFatura', `${year}-${month.padStart(2, '0')}`)

    try {
      const response = await fetch('/api/v1/upload/preview', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${getToken()}` // JWT do localStorage
        }
      })

      if (!response.ok) throw new Error('Upload failed')

      const data = await response.json()
      
      // Redirecionar para preview
      router.push(`/mobile/preview?sessionId=${data.sessionId}`)
    } catch (error) {
      console.error('Upload error:', error)
      alert('Erro ao fazer upload. Tente novamente.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    // ... mesmo JSX, mas button agora:
    <button onClick={handleSubmit} disabled={!file || !bank || isUploading}>
      {isUploading ? 'Processando...' : 'Processar Arquivo'}
    </button>
  )
}
```

**Passo 2: Adicionar progress indicator (0.5h)**

```typescript
// Usar XMLHttpRequest para tracking de upload progress
const xhr = new XMLHttpRequest()
xhr.upload.addEventListener('progress', (e) => {
  if (e.lengthComputable) {
    const percentComplete = (e.loaded / e.total) * 100
    setUploadProgress(percentComplete)
  }
})
```

**Passo 3: Testar com backend real (0.5h)**

```bash
# Garantir backend rodando
./scripts/deploy/quick_start.sh

# Testar upload de arquivo CSV real
# Verificar logs do backend
tail -f temp/logs/backend.log

# Verificar se sessionId é retornado
# Verificar se redirecionamento funciona
```

**✅ Checklist Sprint 1.2:**
- [ ] Upload envia arquivo para backend
- [ ] Progress bar mostra percentual
- [ ] Backend retorna sessionId
- [ ] Redirecionamento para `/mobile/preview?sessionId=...`
- [ ] Erros são tratados e mostrados ao usuário
- [ ] Loading state durante upload

**🚫 Bloqueadores para próximo sprint:**
- Upload não retorna sessionId válido
- Backend não aceita arquivo

---

#### Sprint 1.3: Preview - Frontend Mock (16-20h)

**Objetivo:** Tela de preview funciona com dados fake, agrupamento, classificação

**Passo 1: Criar estrutura (0.5h)**

```bash
mkdir -p app_dev/frontend/src/app/mobile/preview
mkdir -p app_dev/frontend/src/features/upload/components/preview

touch app_dev/frontend/src/app/mobile/preview/page.tsx
touch app_dev/frontend/src/features/upload/components/preview/file-info-card.tsx
touch app_dev/frontend/src/features/upload/components/preview/transaction-card.tsx
touch app_dev/frontend/src/features/upload/components/preview/transaction-list.tsx
touch app_dev/frontend/src/features/upload/components/preview/classification-bottom-sheet.tsx
touch app_dev/frontend/src/features/upload/components/preview/index.ts
```

**Passo 2: Criar mock data realista (1h)**

```typescript
// app_dev/frontend/src/features/upload/mockPreviewData.ts
export const mockFileInfo = {
  banco: 'Itaú',
  cartao: '9266',
  arquivo: 'fatura-202601.csv',
  mesFatura: 'fevereiro de 2026',
  totalLancamentos: 58,
  somaTotal: -17064.96
}

export const mockTransactions: Transaction[] = [
  {
    id: '1',
    date: '15/01/2026',
    description: 'IOF COMPRA INTERNACIONAL',
    value: -31.94,
    grupo: 'Serviços',
    subgrupo: 'IOF',
    source: 'journal_entries',
    occurrences: 4,
    items: [
      { id: '1-1', date: '15/01/2026', description: 'IOF COMPRA INTERNACIONAL', value: -31.94 },
      { id: '1-2', date: '16/01/2026', description: 'IOF COMPRA INTERNACIONAL', value: -31.94 },
      { id: '1-3', date: '17/01/2026', description: 'IOF COMPRA INTERNACIONAL', value: -31.94 },
      { id: '1-4', date: '18/01/2026', description: 'IOF COMPRA INTERNACIONAL', value: -31.94 },
    ]
  },
  {
    id: '2',
    date: '05/01/2026',
    description: 'CONTA VIVO',
    value: -96.50,
    grupo: 'Casa',
    subgrupo: 'Celular',
    source: 'base_padroes',
    occurrences: 2,
    items: [
      { id: '2-1', date: '05/01/2026', description: 'CONTA VIVO', value: -96.50 },
      { id: '2-2', date: '06/01/2026', description: 'CONTA VIVO', value: -96.50 },
    ]
  },
  {
    id: '3',
    date: '10/01/2026',
    description: 'MERCADO LIDER 03/12',
    value: -150.00,
    grupo: '',
    subgrupo: '',
    source: 'unclassified',
    occurrences: 1
  },
  // ... mais 55 transações (incluir classificadas, não classificadas, duplicatas)
]

export const mockGrupos = ['Casa', 'Alimentação', 'Transporte', 'Saúde', 'Educação', 'Lazer', 'Serviços']

export const mockSubgrupos: Record<string, string[]> = {
  'Casa': ['Aluguel', 'Celular', 'Internet', 'Energia', 'Água'],
  'Alimentação': ['Supermercado', 'Restaurante', 'Delivery', 'Padaria'],
  'Transporte': ['Uber', 'Combustível', 'Manutenção', 'Estacionamento'],
  // ... etc
}
```

**Passo 3: Implementar FileInfoCard (1h)**

```typescript
// file-info-card.tsx
export function FileInfoCard({ fileInfo }: { fileInfo: FileInfo }) {
  return (
    <div className="bg-white rounded-lg p-4 space-y-2">
      <div className="flex justify-between">
        <span className="text-gray-600">Banco:</span>
        <span className="font-medium">{fileInfo.banco}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-600">Cartão:</span>
        <span className="font-medium">•••• {fileInfo.cartao}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-600">Arquivo:</span>
        <span className="font-medium">{fileInfo.arquivo}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-600">Mês Fatura:</span>
        <span className="font-medium">{fileInfo.mesFatura}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-600">Total de Lançamentos:</span>
        <span className="font-medium">{fileInfo.totalLancamentos}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-600">Soma Total:</span>
        <span className={`font-bold ${fileInfo.somaTotal < 0 ? 'text-red-600' : 'text-green-600'}`}>
          R$ {Math.abs(fileInfo.somaTotal).toFixed(2)}
        </span>
      </div>
    </div>
  )
}
```

**Passo 4: Implementar TabBar de filtros (2h)**

```typescript
// app_dev/frontend/src/components/mobile/tab-bar.tsx
interface Tab {
  key: string
  label: string
  count: number
}

export function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    <div className="flex overflow-x-auto gap-2 px-4 py-2 bg-white border-b">
      {tabs.map(tab => (
        <button
          key={tab.key}
          onClick={() => onTabChange(tab.key)}
          className={`
            flex-shrink-0 px-4 py-2 rounded-full 
            ${activeTab === tab.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'}
          `}
        >
          {tab.label} ({tab.count})
        </button>
      ))}
    </div>
  )
}
```

**Passo 5: Implementar TransactionCard (4h)**

```typescript
// transaction-card.tsx
export function TransactionCard({ transaction, onClassify, onExpand }: TransactionCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getBackgroundColor = () => {
    if (transaction.isDuplicate) return 'bg-red-50'
    if (!transaction.grupo) return 'bg-yellow-50'
    return 'bg-white'
  }

  return (
    <div className={`${getBackgroundColor()} rounded-lg p-4 mb-2`}>
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex-1">
          {transaction.occurrences && transaction.occurrences > 1 && (
            <button onClick={() => setIsExpanded(!isExpanded)} className="flex items-center gap-2">
              <span>{isExpanded ? '▼' : '▶️'}</span>
              <span className="font-semibold">{transaction.occurrences}× {transaction.description}</span>
            </button>
          )}
          {(!transaction.occurrences || transaction.occurrences === 1) && (
            <span className="font-semibold">{transaction.description}</span>
          )}
          <div className="text-sm text-gray-600 mt-1">
            {transaction.date} • {transaction.source}
          </div>
        </div>
        <div className="text-right">
          <div className={`font-bold ${transaction.value < 0 ? 'text-red-600' : 'text-green-600'}`}>
            R$ {Math.abs(transaction.value).toFixed(2)}
          </div>
        </div>
      </div>

      {/* Classification */}
      <div className="mt-3 flex justify-between items-center">
        {transaction.grupo ? (
          <div className="text-sm">
            <span className="font-medium">{transaction.grupo}</span> › {transaction.subgrupo}
          </div>
        ) : (
          <div className="text-sm text-yellow-600">Não classificado</div>
        )}
        <button onClick={() => onClassify(transaction)} className="text-blue-500 text-sm">
          {transaction.grupo ? 'Editar' : 'Classificar'}
        </button>
      </div>

      {/* Expanded items */}
      {isExpanded && transaction.items && (
        <div className="mt-3 pl-4 border-l-2 border-gray-300 space-y-2">
          {transaction.items.map(item => (
            <div key={item.id} className="text-sm flex justify-between">
              <span>{item.date} - {item.description}</span>
              <span className="font-medium">R$ {Math.abs(item.value).toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

**Passo 6: Implementar TransactionList com Virtual Scroll (3h)**

```typescript
// transaction-list.tsx
import { FixedSizeList as List } from 'react-window'

export function TransactionList({ transactions, onClassify }: TransactionListProps) {
  const Row = ({ index, style }: { index: number, style: React.CSSProperties }) => (
    <div style={style}>
      <TransactionCard 
        transaction={transactions[index]} 
        onClassify={onClassify}
      />
    </div>
  )

  return (
    <List
      height={600}
      itemCount={transactions.length}
      itemSize={120} // Altura estimada de cada card
      width="100%"
    >
      {Row}
    </List>
  )
}
```

**Passo 7: Implementar ClassificationBottomSheet (4h)**

```typescript
// classification-bottom-sheet.tsx
import { useState } from 'react'
import { Sheet } from '@/components/ui/sheet' // shadcn/ui

export function ClassificationBottomSheet({ 
  transaction, 
  grupos, 
  subgrupos, 
  isOpen, 
  onClose, 
  onSave 
}: ClassificationBottomSheetProps) {
  const [selectedGrupo, setSelectedGrupo] = useState(transaction.grupo || '')
  const [selectedSubgrupo, setSelectedSubgrupo] = useState(transaction.subgrupo || '')

  const availableSubgrupos = selectedGrupo ? subgrupos[selectedGrupo] || [] : []

  const handleSave = () => {
    if (!selectedGrupo || !selectedSubgrupo) {
      alert('Grupo e Subgrupo são obrigatórios')
      return
    }
    onSave(transaction.id, selectedGrupo, selectedSubgrupo)
    onClose()
  }

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <div className="p-6 space-y-4">
        <h2 className="text-xl font-bold">Classificar Transação</h2>
        
        <div>
          <label className="block text-sm font-medium mb-2">Transação:</label>
          <div className="text-gray-700">{transaction.description}</div>
          <div className="text-gray-500 text-sm">R$ {Math.abs(transaction.value).toFixed(2)}</div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Grupo:</label>
          <select 
            value={selectedGrupo} 
            onChange={(e) => {
              setSelectedGrupo(e.target.value)
              setSelectedSubgrupo('') // Reset subgrupo
            }}
            className="w-full border rounded p-2"
          >
            <option value="">Selecione um grupo</option>
            {grupos.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Subgrupo:</label>
          <select 
            value={selectedSubgrupo} 
            onChange={(e) => setSelectedSubgrupo(e.target.value)}
            className="w-full border rounded p-2"
            disabled={!selectedGrupo}
          >
            <option value="">Selecione um subgrupo</option>
            {availableSubgrupos.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {transaction.occurrences && transaction.occurrences > 1 && (
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-sm text-blue-700">
              Esta classificação será aplicada a <strong>{transaction.occurrences} ocorrências</strong> desta transação.
            </p>
          </div>
        )}

        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 border rounded p-2">Cancelar</button>
          <button onClick={handleSave} className="flex-1 bg-blue-500 text-white rounded p-2">Salvar</button>
        </div>
      </div>
    </Sheet>
  )
}
```

**Passo 8: Implementar página preview com lógica (4h)**

```typescript
// app_dev/frontend/src/app/mobile/preview/page.tsx
'use client'

import { useState, useMemo } from 'react'
import { mockFileInfo, mockTransactions, mockGrupos, mockSubgrupos } from '@/features/upload/mockPreviewData'
import { FileInfoCard } from '@/features/upload/components/preview/file-info-card'
import { TabBar } from '@/components/mobile/tab-bar'
import { TransactionList } from '@/features/upload/components/preview/transaction-list'
import { ClassificationBottomSheet } from '@/features/upload/components/preview/classification-bottom-sheet'

type TabKey = 'all' | 'classified' | 'unclassified' | 'base_parcelas' | 'base_padroes' | 'journal_entries' | 'regras_genericas' | 'manual'

export default function MobilePreviewPage() {
  const [transactions, setTransactions] = useState(mockTransactions)
  const [activeTab, setActiveTab] = useState<TabKey>('all')
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)

  // Calcular contadores
  const counts = useMemo(() => {
    const classified = transactions.filter(t => t.grupo && t.subgrupo).length
    const unclassified = transactions.filter(t => !t.grupo || !t.subgrupo).length
    const bySource = (source: string) => transactions.filter(t => t.source === source).length

    return {
      all: transactions.length,
      classified,
      unclassified,
      base_parcelas: bySource('base_parcelas'),
      base_padroes: bySource('base_padroes'),
      journal_entries: bySource('journal_entries'),
      regras_genericas: bySource('regras_genericas'),
      manual: bySource('manual')
    }
  }, [transactions])

  // Filtrar transações por tab
  const filteredTransactions = useMemo(() => {
    if (activeTab === 'all') return transactions
    if (activeTab === 'classified') return transactions.filter(t => t.grupo && t.subgrupo)
    if (activeTab === 'unclassified') return transactions.filter(t => !t.grupo || !t.subgrupo)
    return transactions.filter(t => t.source === activeTab)
  }, [transactions, activeTab])

  const tabs = [
    { key: 'all', label: 'Todas', count: counts.all },
    { key: 'classified', label: 'Classificadas', count: counts.classified },
    { key: 'unclassified', label: 'Não Classificadas', count: counts.unclassified },
    { key: 'base_parcelas', label: 'Base Parcelas', count: counts.base_parcelas },
    { key: 'base_padroes', label: 'Base Padrões', count: counts.base_padroes },
    { key: 'journal_entries', label: 'Journal Entries', count: counts.journal_entries },
    { key: 'regras_genericas', label: 'Regras Genéricas', count: counts.regras_genericas },
    { key: 'manual', label: 'Manual', count: counts.manual },
  ]

  const handleClassify = (transactionId: string, grupo: string, subgrupo: string) => {
    setTransactions(prev => prev.map(t => {
      // Se for agrupada, atualizar todas do grupo
      if (t.id === transactionId) {
        if (t.items) {
          return {
            ...t,
            grupo,
            subgrupo,
            items: t.items.map(item => ({ ...item, grupo, subgrupo }))
          }
        }
        return { ...t, grupo, subgrupo }
      }
      return t
    }))
  }

  const handleConfirm = () => {
    if (counts.unclassified > 0) {
      alert(`Ainda há ${counts.unclassified} transações não classificadas. Classifique todas antes de confirmar.`)
      return
    }
    alert('Mock confirm - conectar backend no próximo sprint')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white p-4 border-b">
        <h1 className="text-xl font-bold">Preview de Importação</h1>
        <p className="text-sm text-gray-600">Revise os dados antes de confirmar</p>
      </div>

      {/* Alert se houver não classificadas */}
      {counts.unclassified > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 m-4">
          <div className="flex">
            <div>
              <p className="font-bold text-yellow-700">⚠️ {counts.unclassified} transações sem classificação</p>
              <p className="text-sm text-yellow-600">
                Complete a classificação antes de confirmar a importação. {counts.classified} de {counts.all} transações já classificadas.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* File Info */}
      <div className="p-4">
        <FileInfoCard fileInfo={mockFileInfo} />
      </div>

      {/* Counter */}
      <div className="px-4 py-2">
        <h2 className="font-bold">{filteredTransactions.length} de {counts.all} lançamentos</h2>
      </div>

      {/* Tabs */}
      <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Transactions List */}
      <div className="p-4">
        <TransactionList 
          transactions={filteredTransactions}
          onClassify={setSelectedTransaction}
        />
      </div>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 flex gap-2">
        <button className="flex-1 border rounded p-3">Cancelar</button>
        <button 
          className={`flex-1 rounded p-3 ${counts.unclassified === 0 ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-500'}`}
          onClick={handleConfirm}
          disabled={counts.unclassified > 0}
        >
          Confirmar Importação
        </button>
      </div>

      {/* Classification Bottom Sheet */}
      {selectedTransaction && (
        <ClassificationBottomSheet
          transaction={selectedTransaction}
          grupos={mockGrupos}
          subgrupos={mockSubgrupos}
          isOpen={!!selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
          onSave={handleClassify}
        />
      )}
    </div>
  )
}
```

**Passo 9: Testar exaustivamente (2h)**

```bash
# Testar em múltiplos tamanhos de tela
# - iPhone SE (375px)
# - iPhone 14 Pro (393px)
# - iPhone 14 Pro Max (430px)

# Testar funcionalidades:
# - Tabs filtram corretamente
# - Agrupamento expande/colapsa
# - Bottom sheet abre e fecha
# - Classificação atualiza todas ocorrências
# - Alert desaparece quando todas classificadas
# - Botão confirmar habilita/desabilita corretamente
# - Scroll suave sem lag
```

**✅ Checklist Sprint 1.3:**
- [ ] Tela carrega com mock data
- [ ] FileInfoCard mostra informações corretas
- [ ] Tabs filtram transações
- [ ] Contadores batem (classificadas, não classificadas, etc)
- [ ] TransactionCard mostra dados corretamente
- [ ] Agrupamento funciona (4× IOF)
- [ ] Expandir grupo mostra itens individuais
- [ ] Bottom sheet abre ao clicar "Classificar"
- [ ] Dropdown grupo/subgrupo funcionam
- [ ] Classificação atualiza todas ocorrências
- [ ] Alert de validação correto
- [ ] Botão confirmar desabilitado se houver não classificadas
- [ ] Performance OK (lista de 58 transações sem lag)

**🚫 Bloqueadores para próximo sprint:**
- Preview não renderiza
- Bottom sheet não abre
- Classificação não atualiza
- Performance ruim (lag ao scrollar)

**📸 Screenshots para aprovação:**
- Tela completa
- Bottom sheet aberto
- Alert de validação
- Lista filtrada por tabs

---

#### Sprint 1.4: Preview - Backend Real (4-6h)

**Objetivo:** Preview carrega dados reais do backend, classificação salva, confirmação funciona

**Passo 1: Conectar GET preview (1h)**

```typescript
// page.tsx
'use client'

import { useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function MobilePreviewPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('sessionId')

  const [isLoading, setIsLoading] = useState(true)
  const [fileInfo, setFileInfo] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [grupos, setGrupos] = useState([])
  const [subgrupos, setSubgrupos] = useState({})

  useEffect(() => {
    if (!sessionId) {
      alert('Session ID não encontrado')
      return
    }

    const fetchPreview = async () => {
      try {
        const response = await fetch(`/api/v1/upload/preview/${sessionId}`, {
          headers: {
            'Authorization': `Bearer ${getToken()}`
          }
        })

        if (!response.ok) throw new Error('Failed to fetch preview')

        const data = await response.json()
        
        setFileInfo(data.fileInfo)
        setTransactions(data.transactions)
        setGrupos(data.grupos)
        setSubgrupos(data.subgrupos)
      } catch (error) {
        console.error('Error fetching preview:', error)
        alert('Erro ao carregar preview. Tente novamente.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchPreview()
  }, [sessionId])

  if (isLoading) return <div>Carregando preview...</div>

  // ... resto do componente igual
}
```

**Passo 2: Implementar PATCH classificação (2h)**

```typescript
const handleClassify = async (transactionId: string, grupo: string, subgrupo: string) => {
  try {
    const response = await fetch(`/api/v1/upload/preview/${sessionId}/classify`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        transactionId,
        grupo,
        subgrupo
      })
    })

    if (!response.ok) throw new Error('Failed to classify')

    // Atualizar estado local
    setTransactions(prev => prev.map(t => 
      t.id === transactionId ? { ...t, grupo, subgrupo } : t
    ))
  } catch (error) {
    console.error('Error classifying:', error)
    alert('Erro ao classificar. Tente novamente.')
  }
}
```

**Passo 3: Implementar POST confirmação (1h)**

```typescript
import { useRouter } from 'next/navigation'

const router = useRouter()

const handleConfirm = async () => {
  if (counts.unclassified > 0) {
    alert(`Ainda há ${counts.unclassified} transações não classificadas.`)
    return
  }

  try {
    const response = await fetch(`/api/v1/upload/preview/${sessionId}/confirm`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })

    if (!response.ok) throw new Error('Failed to confirm')

    const data = await response.json()
    
    alert(`Importação confirmada! ${data.totalImportados} transações importadas.`)
    router.push('/mobile/transactions') // Redirecionar para lista de transações
  } catch (error) {
    console.error('Error confirming:', error)
    alert('Erro ao confirmar importação. Tente novamente.')
  }
}
```

**Passo 4: Implementar DELETE cancelamento (0.5h)**

```typescript
const handleCancel = async () => {
  if (!confirm('Deseja realmente cancelar esta importação?')) return

  try {
    const response = await fetch(`/api/v1/upload/preview/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })

    if (!response.ok) throw new Error('Failed to cancel')

    alert('Importação cancelada.')
    router.push('/mobile/upload')
  } catch (error) {
    console.error('Error canceling:', error)
    alert('Erro ao cancelar.')
  }
}
```

**Passo 5: Testar fluxo completo (1-2h)**

```bash
# Teste end-to-end:
# 1. Upload arquivo CSV
# 2. Preview carrega dados reais
# 3. Classificar transações não classificadas
# 4. Verificar backend salvou classificação (curl ou Postman)
# 5. Confirmar importação
# 6. Verificar journal_entries tem novas transações
# 7. Redirecionar para /mobile/transactions
```

**✅ Checklist Sprint 1.4:**
- [ ] Preview carrega dados do backend
- [ ] Grupos/subgrupos vêm de base_marcacoes
- [ ] Classificação salva no backend via PATCH
- [ ] Confirmação cria transações em journal_entries
- [ ] Cancelamento deleta sessão
- [ ] Redirecionamento funciona após confirmação
- [ ] Erros são tratados e exibidos
- [ ] Loading states durante requisições

**🚫 Bloqueadores:**
- Backend não retorna dados
- Classificação não persiste
- Confirmação não salva transações

**🎉 FASE 1 COMPLETA!**
- [ ] Upload mobile funcional
- [ ] Preview mobile funcional
- [ ] Fluxo completo testado
- [ ] Stakeholder aprovou

---

### 📊 FASE 2: Dashboard Mobile - Redesign

#### Sprint 2.1: Insights Dashboard - Frontend Mock (8-10h)

_[Similar ao Sprint 1.3, mas focado em dashboard com charts]_

...

---

### 🎯 FASE 3: Sistema de Metas

#### Sprint 3.1: ✅ Schema Decidido - Migration (1h)

**✅ DECISÃO TOMADA: Estender `budget_geral`**

**Motivo:** Reutilizar 100% das APIs existentes, apenas adicionar colunas

**Por quê esta decisão:**
- ✅ Budget e goals são conceitos relacionados
- ✅ Reutiliza estrutura existente (menos código)
- ✅ 4 APIs CRUD já existem (GET, POST, PUT, DELETE)
- ✅ Apenas 2 endpoints novos necessários (toggle, reorder)
- ✅ Migration simples (9 colunas adicionais)

**SQL Migration:**
```sql
-- Migration: add_meta_fields_to_budget_geral
-- Decisão: Estender budget_geral (NÃO criar tabela goals nova)
ALTER TABLE budget_geral ADD COLUMN tipo_meta TEXT CHECK(tipo_meta IN ('gasto', 'investimento'));
ALTER TABLE budget_geral ADD COLUMN alerta_80 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN alerta_100 BOOLEAN DEFAULT FALSE;
ALTER TABLE budget_geral ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
ALTER TABLE budget_geral ADD COLUMN descricao TEXT;
ALTER TABLE budget_geral ADD COLUMN prazo DATE;
ALTER TABLE budget_geral ADD COLUMN icone TEXT DEFAULT 'home';
ALTER TABLE budget_geral ADD COLUMN cor TEXT DEFAULT '#10B981';
ALTER TABLE budget_geral ADD COLUMN ordem INTEGER DEFAULT 0;
```

**Comando para executar:**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic revision -m "add meta fields to budget_geral"
# Copiar SQL acima para o arquivo de migration gerado
alembic upgrade head
```

---

**✅ Decisão Validada:**
- [x] Decisão tomada: Estender budget_geral
- [x] Motivo: Reutilizar APIs existentes + menos código
- [x] SQL migration validado
- [x] Não criar tabela goals nova

---

_[Continuar com Sprints 3.2-3.6]_

---

## ✅ Critérios de Aprovação

### Aprovação de Cada Tela (Checklist Obrigatório)

Antes de marcar uma tela como "completa", ela deve passar por TODOS os critérios:

#### 1. **Layout Mobile**
- [ ] Legível em iPhone SE (375px width)
- [ ] Legível em iPhone 14 Pro (393px width)
- [ ] Legível em iPhone 14 Pro Max (430px width)
- [ ] Scroll suave sem lag (60fps)
- [ ] Botões grandes o suficiente para touch (min 44x44px)
- [ ] Safe area respeitada (notch/home indicator)

#### 2. **Funcionalidades Core**
- [ ] Todas funcionalidades principais funcionam
- [ ] Validações de formulário corretas
- [ ] Estados visuais claros (loading, error, success)
- [ ] Navegação funciona (voltar, avançar)

#### 3. **Integração Backend**
- [ ] Dados carregam do backend
- [ ] Mutações salvam no backend
- [ ] Erros do backend são tratados
- [ ] Autenticação JWT funciona

#### 4. **Performance**
- [ ] Tela carrega em <3s
- [ ] Interações respondem em <100ms
- [ ] Scroll sem travamentos
- [ ] Sem memory leaks (verificar DevTools)

#### 5. **Testes Manuais**
- [ ] Happy path funciona (fluxo normal)
- [ ] Edge cases tratados (campos vazios, valores extremos)
- [ ] Erros de rede tratados (simular offline)
- [ ] Múltiplos devices testados (real ou simulador)

#### 6. **Documentação**
- [ ] Código comentado onde necessário
- [ ] TypeScript interfaces documentadas
- [ ] README atualizado (se necessário)

### Aprovação Final do Projeto

Projeto só é marcado como "completo" quando:

- [ ] **TODAS as 7 telas** passaram pelos critérios acima
- [ ] **Fluxos completos** testados end-to-end:
  - [ ] Upload → Preview → Confirm → Transactions
  - [ ] Dashboard mobile redesenhado com dados reais
  - [ ] Goals CRUD completo (criar, editar, deletar, ativar/desativar)
- [ ] **Performance global:**
  - [ ] App carrega em <3s
  - [ ] Navegação fluida entre telas
  - [ ] Sem crashes ou bugs críticos
- [ ] **Backend estável:**
  - [ ] Todos endpoints funcionando
  - [ ] Database migrations aplicadas
  - [ ] Logs sem erros
- [ ] **Code review:**
  - [ ] Tech lead revisou código
  - [ ] Arquitetura aprovada (segue DDD)
  - [ ] Sem código duplicado
  - [ ] Componentes reutilizáveis identificados
- [ ] **Deploy:**
  - [ ] Feature branch mergeada na main
  - [ ] Deploy em staging/production
  - [ ] Smoke tests passando
  - [ ] Rollback plan documentado

---

## 📚 Apêndices

### A. Referências Técnicas

- [React Window Documentation](https://react-window.vercel.app/)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

### B. Comandos Úteis

```bash
# Iniciar servidores
./scripts/deploy/quick_start.sh

# Parar servidores
./scripts/deploy/quick_stop.sh

# Backup diário
./scripts/deploy/backup_daily.sh

# Validar sincronização git
./scripts/deploy/validate_server_access.sh

# Logs backend
tail -f temp/logs/backend.log

# Logs frontend
tail -f temp/logs/frontend.log

# Migrations
cd app_dev/backend
alembic upgrade head
alembic history
alembic current

# Testar API
curl -X GET http://localhost:8000/api/v1/upload/preview/SESSION_ID \
  -H "Authorization: Bearer YOUR_JWT"
```

### C. Troubleshooting

**Problema:** Preview não carrega dados

```bash
# Verificar sessionId válido
# Verificar backend está rodando
# Verificar JWT não expirado
# Verificar logs do backend
```

**Problema:** Performance ruim (lag ao scrollar)

```bash
# Verificar se virtual scroll está habilitado
# Verificar quantidade de itens sendo renderizados
# Usar React DevTools Profiler
# Adicionar React.memo nos componentes
```

**Problema:** Bottom sheet não abre

```bash
# Verificar z-index do sheet
# Verificar overflow hidden no parent
# Verificar JavaScript errors no console
```

---

## 📞 Contatos e Suporte

**Dev Lead:** [Nome]  
**Stakeholder:** [Nome]  
**Tech Lead:** [Nome]

**Reuniões:**
- Daily standup: [horário]
- Sprint review: [horário]
- Retrospective: [horário]

---

**FIM DO DOCUMENTO**

---

**Última atualização:** 05/02/2026  
**Próxima revisão:** Após Sprint 1.4 (fim da Fase 1)
