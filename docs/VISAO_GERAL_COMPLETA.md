# FinUp — Visão Geral Completa do Projeto

> Documento de referência para validação de ideias e discussão fora do ambiente de desenvolvimento.
> Atualizado em: Março 2026

**Documentos relacionados:**
- [`TELAS_DETALHADAS.md`](./TELAS_DETALHADAS.md) — Detalhamento completo de cada tela, botão, gráfico e interação
- [`UPLOAD_FLUXO_COMPLETO.md`](./UPLOAD_FLUXO_COMPLETO.md) — Todos os arquivos do upload + fluxo passo a passo com variantes e erros

---

## O que é o FinUp?

O **FinUp** é um sistema de gestão financeira pessoal. A ideia central é: o usuário importa os extratos do banco/cartão, o sistema classifica automaticamente as transações, e a partir disso o usuário consegue ver para onde vai o dinheiro, criar um plano financeiro e acompanhar metas de aposentadoria.

**URL pública:** `https://meufinup.com.br`

---

## Estrutura Macro

O projeto tem **3 aplicações** rodando em conjunto:

```
ProjetoFinancasV5/
├── app_dev/
│   ├── backend/     → API (Python + FastAPI)
│   └── frontend/    → App do usuário (Next.js, mobile-first)
├── app_admin/
│   └── frontend/    → Painel administrativo (Next.js)
├── docs/            → Documentação e planejamento
└── scripts/         → Deploy, migrações, utilitários
```

### Como sobe tudo:
```bash
./scripts/deploy/quick_start.sh
```
Isso sobe: PostgreSQL (5432), Redis (6379), Backend (8000), App usuário (3000), Admin (3001).

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python + FastAPI 0.115 |
| Banco de dados | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 + Alembic (migrações) |
| Cache | Redis 7 (uso mínimo por enquanto) |
| Auth | JWT (HS256, 60 min) + cookies httpOnly |
| Frontend (app) | Next.js 16 + React 19 + Tailwind CSS 4 |
| Frontend (admin) | Next.js 16 + React 19 + SWR |
| Componentes UI | Radix UI + Lucide React |
| Gráficos | Recharts 2 |
| Processamento | Pandas, NumPy, openpyxl, pdfplumber, OCR |
| Infra | Docker + Docker Compose |

---

## Jornada do Usuário (fluxo completo)

```
1. Cadastro (feito pelo admin)
   → Grupos/subgrupos copiados do template global automaticamente

2. Login
   → Dashboard com checklist de onboarding

3. Primeiro Upload
   → Detecta banco, extrai transações
   → Preview: classifica automaticamente (GRUPO/SUBGRUPO)
   → Usuário revisa e confirma

4. Plano Financeiro
   → Define renda mensal líquida
   → Define meta de gasto por grupo (orçamento)
   → Acompanha: realizado vs. planejado

5. Monitoramento
   → Dashboard: receita, despesa, investimentos, saldo
   → Cashflow anual (tabela 12 meses)
   → "Anos perdidos" (impacto de gastar além do planejado)

6. Investimentos
   → Registra portfólio
   → Acompanha histórico mensal
   → Cenários de aposentadoria
```

---

## Backend — Domínios

O backend segue **Domain-Driven Design (DDD)**: cada domínio tem seus próprios `models.py`, `service.py`, `router.py` e `schemas.py`.

### Mapa de Domínios

| Domínio | Pasta | O que faz |
|---------|-------|-----------|
| **auth** | `/domains/auth` | Login, logout, JWT, cookies |
| **users** | `/domains/users` | CRUD de usuários, estatísticas |
| **transactions** | `/domains/transactions` | Transações financeiras (a tabela central) |
| **categories** | `/domains/categories` | Marcações (GRUPO/SUBGRUPO por usuário) |
| **grupos** | `/domains/grupos` | Configuração de grupos por usuário |
| **marcacoes** | `/domains/marcacoes` | Subgrupos dentro de cada grupo |
| **budget** | `/domains/budget` | Orçamento mensal por grupo |
| **dashboard** | `/domains/dashboard` | Métricas, gráficos, resumos |
| **upload** | `/domains/upload` | Pipeline de importação de extratos |
| **plano** | `/domains/plano` | Plano financeiro, cashflow, projeções |
| **investimentos** | `/domains/investimentos` | Portfólio, histórico, aposentadoria |
| **onboarding** | `/domains/onboarding` | Checklist e estado de onboarding |
| **classification** | `/domains/classification` | Engine de classificação automática |
| **exclusoes** | `/domains/exclusoes` | Marcar transações para ignorar |
| **cards** | `/domains/cards` | Cartões de crédito |
| **screen_visibility** | `/domains/screen_visibility` | Quais telas ficam visíveis por usuário |

---

## Modelo de Dados — Tabelas Principais

### `journal_entries` — A tabela central
Toda transação importada vai aqui.

```
id
user_id                 → dono da transação
Data                    → data da transação
Estabelecimento         → nome do local (ex: "MERCADO PINHEIROS")
Valor                   → valor negativo = despesa, positivo = receita
TipoTransacao           → CREDITO (receita) | DEBITO (despesa)
GRUPO                   → ex: "Alimentação"
SUBGRUPO                → ex: "Supermercado"
CategoriaGeral          → Receita | Despesa | Investimentos
IdTransacao             → hash único (evita duplicatas)
IdParcela               → hash para rastrear parcelamentos
parcela_atual / TotalParcelas → "2/12" = segunda de 12 parcelas
fonte                   → upload | demo
is_demo                 → true quando é dado de demonstração
arquivo_origem          → nome do arquivo importado
upload_history_id       → qual upload gerou essa transação
IgnorarDashboard        → excluída dos cálculos
MesFatura / Ano / Mes   → para filtragem temporal
```

### `base_grupos_config` — Grupos por usuário
Cada usuário tem sua própria configuração de grupos (copiada do template ao criar conta).

```
id
user_id
nome_grupo              → ex: "Alimentação"
tipo_gasto_padrao       → Fixo | Variável
categoria_geral         → Receita | Despesa | Investimentos
cor                     → hex color
is_padrao               → foi copiado do template ou criado manualmente
```

### `base_marcacoes` — Subgrupos por usuário
```
id
user_id
GRUPO                   → ex: "Alimentação"
SUBGRUPO                → ex: "Supermercado", "Restaurante", "Delivery"
```

### `budget_planning` — Orçamento mensal
```
id
user_id
grupo                   → qual grupo (ex: "Alimentação")
mes_referencia          → "2026-01" (YYYY-MM)
valor_planejado         → meta de gasto naquele grupo naquele mês
valor_medio_3_meses     → calculado a partir do histórico
cor                     → visual no app
ativo                   → true/false
```

### `user_financial_profile` — Perfil financeiro
```
id
user_id (único por usuário)
renda_mensal_liquida    → salário líquido
aporte_planejado        → quanto quer guardar por mês
idade_atual
idade_aposentadoria     → default: 65
patrimonio_atual        → quanto tem hoje
taxa_retorno_anual      → default: 8% a.a.
```

### `base_expectativas` — Expectativas futuras
Lançamentos futuros que o usuário sabe que vão acontecer (parcelamentos, extras sazonais, etc.)

```
id
user_id
descricao               → ex: "IPVA 2026"
valor
grupo                   → qual grupo afeta
tipo_lancamento         → Despesa | Receita
mes_referencia          → "2026-03"
tipo_expectativa        → sazonal_plano | renda_plano | parcela_futura
status                  → pendente | realizado | divergente | cancelado
journal_entry_id        → vinculado à transação real quando acontecer
```

### `investimentos_portfolio` — Portfólio
```
id
user_id
nome_produto            → ex: "Tesouro IPCA+ 2035"
corretora               → ex: "XP Investimentos"
tipo_investimento       → Renda Fixa | Ações | FII | etc.
classe_ativo            → Prefixado | Pós-fixado | etc.
data_aplicacao
valor_total_inicial
ativo
```

### `upload_history` — Histórico de uploads
```
id
user_id
banco                   → ex: "nubank", "itau"
tipo_documento          → fatura_cartao | extrato_conta
mes_fatura              → "2026-01"
status                  → pending | success | error
transacoes_importadas   → quantas foram confirmadas
data_upload, data_confirmacao
```

---

## Upload — Pipeline de Importação

Quando o usuário sobe um extrato, passa por 4 fases antes de confirmar:

```
Fase 1 — Extração Bruta
  Lê CSV, XLSX ou PDF (com OCR se necessário)
  Detecta: banco, período, colunas

Fase 2 — Normalização (IDs)
  Gera IdTransacao (FNV-1a hash)
  Gera IdParcela se detectar "2/12" etc.
  Detecta parcelamentos

Fase 3 — Classificação
  Busca GRUPO/SUBGRUPO via padrões aprendidos
  Marca origem_classificacao = "pattern_match" | "manual" | "ia"

Fase 4 — Deduplicação
  Verifica se IdTransacao já existe na base
  Marca is_duplicate = true se for repetido
```

Apenas após o usuário revisar o preview e clicar em "Confirmar" as transações são salvas em `journal_entries`.

**Bancos suportados:** Nubank, Itaú, BTG, MercadoPago, genérico (CSV/XLSX).
**Formatos:** CSV, XLSX, PDF.

---

## Dashboard — O que calcula

O dashboard lê de `journal_entries` com filtros de `user_id`, `Ano`, `Mes` e `IgnorarDashboard = false`.

**Métricas principais:**
- **Receita total** — soma de CREDITO no período
- **Despesa total** — soma de DEBITO (excluindo Investimentos)
- **Investimentos** — DEBITO com CategoriaGeral = Investimentos
- **Saldo** — Receita − Despesa − Investimentos

**Filtros de período:**
- Mês específico
- YTD (ano até mês atual)
- Ano completo

**Gráficos:**
- Tendência mensal (últimos 12 meses)
- Breakdown por grupo
- Orçado vs. realizado

---

## Plano Financeiro — Como funciona

O "Plano" é a seção mais elaborada. Ela conecta:

```
Renda (user_financial_profile.renda_mensal_liquida)
  ↓
− Orçamentos por grupo (budget_planning por mês)
  ↓
= Disponível para aporte

Aporte planejado (user_financial_profile.aporte_planejado)
  ↓
Projeção de patrimônio (juros compostos)
  ↓
Simulação de aposentadoria
```

**Endpoints-chave do plano:**

| Endpoint | O que retorna |
|----------|--------------|
| `GET /plano/resumo` | Renda, total orçado, disponível |
| `GET /plano/orcamento` | Budget vs realizado por grupo |
| `GET /plano/cashflow` | Tabela 12 meses (renda, gastos, aporte, saldo) |
| `GET /plano/projecao` | Projeção de patrimônio com cenário de redução |
| `GET /plano/impacto-longo-prazo` | "Anos perdidos" se gastar além do planejado |
| `GET /plano/expectativas` | Lançamentos futuros planejados |
| `GET /plano/perfil` | Perfil completo (renda, idade, patrimônio, taxa) |

---

## Frontend — Páginas do App

O app é **mobile-first**. Todas as páginas principais estão em `/mobile/`:

| Página | Rota | O que o usuário faz |
|--------|------|---------------------|
| **Dashboard** | `/mobile/dashboard` | Vê métricas, gráficos, saldo do mês |
| **Plano** | `/mobile/plano` | Hub do plano financeiro |
| **Construir Plano** | `/mobile/construir-plano` | Wizard para criar plano do zero |
| **Budget** | `/mobile/budget` | Visão geral dos orçamentos |
| **Budget (detalhe)** | `/mobile/budget/[goalId]` | Editar uma meta específica |
| **Upload** | `/mobile/upload` | Importar extrato bancário |
| **Transações** | `/mobile/transactions` | Listar e filtrar transações |
| **Investimentos** | `/mobile/investimentos` | Portfólio e histórico |
| **Perfil** | `/mobile/profile` | Dados do usuário e configurações |
| **Grupos** | `/mobile/grupos` | Gerenciar grupos e subgrupos |
| **Exclusões** | `/mobile/exclusions` | Transações excluídas do dashboard |
| **Onboarding** | `/mobile/onboarding/*` | Fluxo de boas-vindas |

**Navegação inferior:**
Home → Upload → Plano → Carteira → Perfil

---

## Admin — Painel Administrativo

Acessível em `localhost:3001`. Só para usuários com `role = admin`.

**O que o admin faz:**
- Criar, editar e desativar usuários
- Deletar usuário completamente (purge em 2 etapas com confirmação por email)
- Ver estatísticas: quantas transações, uploads, grupos cada usuário tem
- Configurar bancos e categorias genéricas
- Controlar visibilidade de telas por usuário

---

## Sistema de Grupos e Classificação

Este é o coração da classificação automática:

### Hierarquia de Classificação:
```
CategoriaGeral  →  GRUPO        →  SUBGRUPO
Despesa            Alimentação     Supermercado
Despesa            Alimentação     Restaurante
Despesa            Transporte      Combustível
Despesa            Transporte      Uber/99
Receita            Salário         CLT
Investimentos      Renda Fixa      Tesouro Direto
```

### Como funciona a classificação automática:
1. O sistema tem uma tabela `generic_classification_rules` com padrões aprendidos
2. Ao importar, compara `Estabelecimento` com padrões (ex: "MERCADAO" → Supermercado)
3. Se não encontra padrão, marca como `origem_classificacao = null` (usuário classifica manualmente)
4. Toda classificação manual vira aprendizado para futuras importações

### Template global vs. grupos por usuário:
- `base_grupos_template` → template global mantido pelo admin
- `base_grupos_config` → cópia do template para cada usuário (podem customizar)
- Ao criar usuário, o template é copiado automaticamente

---

## Investimentos — Como rastreia

```
investimentos_portfolio     → produtos (Tesouro, CDB, Ações...)
    ↓
investimentos_historico     → saldo mensal de cada produto
    ↓
investimentos_transacoes    → liga depósitos do extrato ao produto
    ↓
investimentos_cenario_projecao → simulações de aposentadoria
```

O sistema detecta transações com `CategoriaGeral = Investimentos` e pode vinculá-las a produtos específicos do portfólio.

---

## Branch Atual: `feature/plano-metas-ux-improvements`

Esta branch é a maior entrega ativa. Tem 6 sub-projetos:

| # | Nome | Status |
|---|------|--------|
| 01 | Admin — Gestão de Usuários | ✅ Entregue |
| 02 | UX Fundação (navegação, estados vazios) | ✅ Entregue |
| 03 | Onboarding e Grupos | ✅ Entregue |
| 04 | Upload Completo (multi-arquivo, rollback) | ✅ Entregue |
| 05 | Plano Financeiro (cashflow, projeções) | 🚧 Em andamento |
| 06 | Patrimônio e Investimentos | 🔜 Próximo |

### O que ainda falta no `05-plano-financeiro`:
- Fases 3–5 do wizard (aporte, expectativas sazonais, parcelas futuras)
- Tab de aposentadoria no plano
- Expectativas automáticas (detectar parcelas futuras a partir de parcelamentos em andamento)

### Migrations pendentes:
- `k6l7m8n9o0p1` — adiciona `aporte_planejado` no `user_financial_profile`
- `l7m8n9o0p1q2` — cria tabela `base_expectativas`

---

## Segurança

- Senhas: bcrypt
- Tokens: JWT HS256, 60 minutos, cookie httpOnly
- CORS: só aceita `localhost:3000` e `localhost:3001` (e domínio de produção)
- Rate limit: 5 tentativas/minuto no login
- Todas as queries filtram por `user_id` (usuário nunca vê dado de outro)
- Purge de usuário: 2 etapas (resumo → confirmação por email + texto "DELETE PERMANENTLY")
- Em produção: `/docs` (Swagger) desabilitado, debug off

---

## Convenções do Projeto

### Backend:
- Cada domínio em `app/domains/{nome}/` com `models.py`, `router.py`, `service.py`, `schemas.py`
- Prefixos de rota: `/api/v1/{dominio}/`
- Autenticação via `Depends(get_current_user_id)` em todos os endpoints protegidos
- Transações de banco: `db.commit()` apenas no service, nunca no router

### Frontend:
- Páginas em `src/app/mobile/{pagina}/page.tsx`
- Features em `src/features/{feature}/` com `api.ts`, hooks, components
- Componentes UI reutilizáveis em `src/components/ui/`
- Chamadas de API: `fetch` com `Authorization: Bearer {token}`

### Documentação:
- Cada feature tem pasta em `docs/features/{feature}/` com `PLANO.md`, `TECH_SPEC.md`, `PRD.md`
- `PLANO.md` = o quê e por quê
- `TECH_SPEC.md` = como implementar (modelos, endpoints, componentes)
- `PRD.md` = requisitos de produto

---

## Referência Rápida de Arquivos

### Backend:
```
app_dev/backend/app/main.py                         → FastAPI app init
app_dev/backend/app/core/config.py                  → Settings (JWT, DB, CORS)
app_dev/backend/app/core/database.py                → SQLAlchemy setup
app_dev/backend/app/domains/{dominio}/models.py     → Tabelas
app_dev/backend/app/domains/{dominio}/router.py     → Endpoints
app_dev/backend/app/domains/{dominio}/service.py    → Lógica de negócio
app_dev/backend/migrations/versions/                → Migrações Alembic
```

### Frontend (app):
```
app_dev/frontend/src/app/mobile/dashboard/page.tsx  → Dashboard principal
app_dev/frontend/src/app/mobile/plano/page.tsx      → Hub do plano
app_dev/frontend/src/app/mobile/upload/page.tsx     → Upload de extrato
app_dev/frontend/src/features/plano/api.ts          → API do plano
app_dev/frontend/src/features/dashboard/            → Feature de dashboard
app_dev/frontend/src/components/ui/                 → Componentes UI base
```

### Admin:
```
app_admin/frontend/src/app/admin/contas/page.tsx    → Gestão de usuários
app_admin/frontend/src/components/PurgeUserModal.tsx → Modal de purge
app_admin/frontend/src/components/UserStatsCell.tsx  → Stats do usuário
```

### Documentação:
```
docs/features/plano-metas-ux-improvements/          → Feature principal ativa
docs/features/plano-metas-ux-improvements/VISAO_FLUXO_DADOS.md → Fluxo de dados
docs/VISAO_GERAL_COMPLETA.md                        → Este arquivo
```

---

## Perguntas Frequentes para Validação de Ideias

**"Posso adicionar um novo tipo de transação?"**
→ Sim. Adicionar em `TipoTransacao` (enum no model), ajustar cálculos em `dashboard/repository.py` e `plano/service.py`.

**"Posso criar um novo grupo/categoria?"**
→ Sim. Adicionar em `base_grupos_template` via admin, usuários existentes precisam atualizar manualmente (ou via migration).

**"Posso criar uma nova tela no app?"**
→ Sim. Criar `src/app/mobile/{nova-tela}/page.tsx`, adicionar `use client`, e opcionalmente uma feature em `src/features/`.

**"Posso adicionar um campo novo numa tabela?"**
→ Sim, mas exige: (1) alterar `models.py`, (2) criar migration Alembic, (3) atualizar `schemas.py`, (4) ajustar `service.py` se necessário.

**"Posso criar um novo domínio no backend?"**
→ Sim. Criar pasta `app/domains/{novo}/` com os 4 arquivos (models, router, service, schemas), registrar o router em `main.py`.

**"Posso adicionar um novo banco suportado no upload?"**
→ Sim. Criar processor em `app/domains/upload/processors/`, registrar em `detect.py`.

---

*Este documento é mantido manualmente. Atualize quando houver mudanças arquiteturais significativas.*
