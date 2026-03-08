# Mapeamento Completo de APIs

> Data: Março/2026

---

## Infraestrutura

### API Client
- **Arquivo:** `src/core/utils/api-client.ts`
- **Funções:** `fetchWithAuth`, `fetchJsonWithAuth`, `apiGet`, `apiPost`, `apiPatch`, `apiPut`, `apiDelete`
- **Auth:** Cookie httpOnly (sem localStorage)
- **Timeout:** 30s | **Retries:** 3 | **Retry delay:** 1s

### API Config
- **Arquivo:** `src/core/config/api.config.ts`
- **Base URL:** `http://localhost:8000` (dev) ou `NEXT_PUBLIC_BACKEND_URL`
- **Prefix:** `/api/v1`

### Proxy Next.js
- **Arquivo:** `src/app/api/[...proxy]/route.ts`
- **Função:** Repassa todas as chamadas `/api/*` → FastAPI `localhost:8000/api/v1/*`

---

## Dashboard

**Serviço:** `src/features/dashboard/services/dashboard-api.ts`
**Tela:** `src/app/mobile/dashboard/page.tsx`
**Hook:** `src/features/dashboard/hooks/use-dashboard.ts`

| # | Endpoint | Cache | Observação |
|---|----------|-------|------------|
| 1 | `GET /dashboard/last-month-with-data?source=transactions` | 2 min | Detecta mês mais recente |
| 2 | `GET /dashboard/metrics?year=Y&month=M&ytd_month=M` | 2 min | Métricas principais + change_percentage |
| 3 | `GET /dashboard/chart-data?year=Y&month=M` | 5 min | Receitas vs Despesas |
| 4 | `GET /dashboard/chart-data-yearly?years=Y,Y,Y&ytd_month=M` | 5 min | Gráfico anual |
| 5 | `GET /dashboard/income-sources?year=Y&month=M` | 2 min | Receitas por grupo |
| 6 | `GET /dashboard/budget-vs-actual?year=Y&month=M` | sem cache | Budget vs realizado |
| 7 | `GET /dashboard/credit-cards?year=Y&month=M` | 2 min | Gastos cartão |
| 8 | `GET /dashboard/orcamento-investimentos?year=Y&month=M&ytd_month=M` | 2 min | Budget investimentos |
| 9 | `GET /investimentos/cenarios/principal/aporte-mes?ano=Y&mes=M` | 2 min | Aporte detalhado |
| 10 | `GET /plano/cashflow/mes?ano=Y&mes=M&modo_plano=true` | 5 min | Cashflow do mês |
| 11 | `GET /dashboard/last-month-with-data?source=patrimonio` | 2 min | Mês mais recente patrimônio |

**Padrão de loading:** Todos os 11 hooks disparam em paralelo no mount. Prefetch de meses adjacentes em background.

---

## Transações

**Tela:** `src/app/transactions/page.tsx`

| Endpoint | Observação |
|----------|------------|
| `GET /transactions/list?page=X&limit=10&filters` | Paginação offset, limit hardcoded |
| `GET /transactions/filtered-total?filters` | Total com filtros |
| `PUT /transactions/update/{id}` | Edição inline |

---

## Investimentos

**Serviço:** `src/features/investimentos/services/investimentos-api.ts`
**Tela:** `src/app/mobile/investimentos/page.tsx`
**Hook:** `src/features/investimentos/hooks/use-investimentos.ts`

| Endpoint | Observação |
|----------|------------|
| `GET /investimentos?tipo=T&ativo=1&anomes=YYYYMM&skip=0&limit=200` | limit=200 hardcoded |
| `GET /investimentos/resumo` | Total + yield do portfólio |
| `GET /investimentos/distribuicao-tipo?classe_ativo=X` | Distribuição por tipo |
| `GET /investimentos/{id}?anomes=YYYYMM` | Detalhe de um ativo |
| `GET /investimentos/{id}/historico?ano_inicio=Y&ano_fim=Y` | Histórico do ativo |
| `GET /investimentos/timeline/rendimentos?ano_inicio=Y&ano_fim=Y` | Timeline de rendimentos |
| `GET /investimentos/timeline/patrimonio?ano_inicio=Y&ano_fim=Y` | Timeline de patrimônio |
| `GET /investimentos/cenarios?ativo=false` | Lista de cenários |
| `GET /investimentos/cenarios/{id}/projecao?recalc=true` | Projeção do cenário |
| `GET /investimentos/cenarios/{id}/simular` | Simular cenário salvo |
| `POST/PATCH/DELETE /investimentos` | CRUD de ativos |
| `GET /investimentos/copiar-mes-anterior?anomes_destino=YYYYMM` | Copiar mês anterior |

**No mount:** `Promise.all([getInvestimentos(), getPortfolioResumo(), getDistribuicaoPorTipo()])` — 3 RTTs paralelos.

---

## Goals / Orçamento

**Serviço:** `src/features/goals/services/goals-api.ts`
**Hook:** `src/features/goals/hooks/use-goals.ts`

| Endpoint | Observação |
|----------|------------|
| `GET /budget/planning?mes_referencia=YYYY-MM` | Lista orçamento do mês (2 min cache) |
| `GET /budget/planning/{id}` | Detalhe de uma meta |
| `POST /budget/planning/bulk-upsert` | Criar/atualizar (mesmo para item único) |
| `PATCH /budget/planning/toggle/{id}` | Ativar/desativar |
| `DELETE /budget/{id}` | Excluir |
| `GET /budget/planning/grupos-com-categoria` | Grupos p/ dropdown cascata |
| `GET /budget/planning/grupos-disponiveis` | Grupos disponíveis |

---

## Plano (Cashflow & Projeções)

**Serviço:** `src/features/plano/api.ts`

| Endpoint | Observação |
|----------|------------|
| `GET /plano/renda` | Renda mensal |
| `POST /plano/renda` | Definir renda |
| `GET /plano/resumo?ano=Y&mes=M` | Resumo (renda, budget, disponível) |
| `GET /plano/orcamento?ano=Y&mes=M` | Itens de orçamento |
| `GET /plano/cashflow?ano=Y` | **Cashflow anual completo (12 meses)** |
| `GET /plano/cashflow/mes?ano=Y&mes=M&modo_plano=true` | Mês único (mas computa 12 internamente) |
| `GET /plano/cashflow/detalhe-mes?ano=Y&mes=M` | Diagnóstico detalhado do mês |
| `GET /plano/projecao?ano=Y&meses=N&reducao_pct=X` | Projeção futura |
| `GET /plano/projecao-longa?inflacao_pct=X` | Projeção longo prazo |
| `GET /plano/grupos-media-3-meses?ano=Y&mes=M` | Média 3 meses por grupo |
| `GET /plano/impacto-longo-prazo?ano=Y&mes=M` | Métricas de impacto |
| `PUT /plano/orcamento/bulk` | Salvar múltiplos orçamentos |
| `PUT /plano/orcamento/bulk-range` | Aplicar orçamentos para 13+ meses |

---

## Upload

**Serviço:** `src/features/upload/services/upload-api.ts`
**Hook:** `src/features/upload/hooks/use-upload.ts`

| Endpoint | Observação |
|----------|------------|
| `POST /upload/detect` | Detecta banco/tipo/período + duplicatas |
| `POST /upload/preview` | Upload + retorna sessionId |
| `GET /upload/preview/{sessionId}` | Preview das transações |
| `POST /upload/import-planilha` | Import CSV/XLSX genérico |
| `GET /compatibility/` | Matriz de compatibilidade de bancos |
| `GET /cards/` | Cartões de crédito do usuário |
| `POST /cards/` | Criar cartão |

---

## Bancos & Categorias

**Serviços:** `src/features/banks/services/bank-api.ts` | `src/features/categories/services/category-api.ts`

| Endpoint | Observação |
|----------|------------|
| `GET /compatibility/` | Lista bancos |
| `POST /compatibility/` | Criar banco |
| `PUT /compatibility/{id}` | Atualizar banco |
| `DELETE /compatibility/{id}` | Excluir banco |
| `GET /categories` | Lista categorias |
| `POST/PUT/DELETE /categories/{id}` | CRUD de categorias |

---

## Autenticação

**Contexto:** `src/contexts/AuthContext.tsx`

| Endpoint | Observação |
|----------|------------|
| `POST /auth/login` | Login → access_token + user |
| `POST /auth/logout` | Logout |
| `GET /auth/me` | Usuário atual (chamado no mount do app) |

---

## Mapa de Caching Atual

| Módulo | Cache | TTL | Dedup | Invalidação |
|--------|-------|-----|-------|-------------|
| Dashboard | In-memory | 2-5 min | ✅ | Manual (`invalidateDashboardCache`) |
| Goals | In-memory | 2 min | ✅ | Manual (`invalidateGoalsCache`) |
| Investimentos | ❌ Nenhum | — | ❌ | Todo fetch |
| Plano/Cashflow | ❌ Nenhum | — | ❌ | Todo fetch |
| Upload | ❌ Nenhum | — | ❌ | Todo fetch |
| Banks | ❌ Nenhum | — | ❌ | Full refetch após mutação |
| Categorias | ❌ Nenhum | — | ❌ | Full refetch após mutação |
| Transações | ❌ Nenhum | — | ❌ | Todo fetch |
