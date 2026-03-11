# Performance Prod Fixes — Plano de Implementação

> **Criado em:** 10/03/2026  
> **Versão da análise:** `docs/ANALISE_PERFORMANCE_VM.md` (10–11/03/2026)  
> **Status:** 🟡 Aguardando Implementação  
> **Prioridade:** 🔴 Crítica (impacto direto no UX de produção)

---

## TL;DR

Correções cirúrgicas identificadas após diagnóstico completo da VM de produção via SSH + Playwright + EXPLAIN ANALYZE. **A VM é saudável — o problema é 100% do app**. Foram mapeados **8 problemas** e priorizados em **4 sprints**, do mais simples ao mais arquitetural.

---

## Contexto — O Que Foi Medido

| Tela | Tempo medido | Meta |
|------|-------------|------|
| Dashboard (1ª visita) | **~7s** ❌ | < 2s |
| Transações (via bottom nav) | **~8s** ❌ | < 2s |
| Budget/Plano | **5.8s** ❌ | < 1s |
| Investimentos (visita fria) | **~1.5s dupla** ⚠️ | < 1s |
| Carteira (visita fria) | **~1.5s dupla** ⚠️ | < 1s |
| Chips mês Jan/Fev/Mar | **330ms** ✅ | — |
| Troca Mês/YTD/Ano | **~350ms** ✅ | — |

**VM:** 15.6 GB RAM, 4 vCPUs, load avg 0.44 — completamente ociosa.  
**Banco:** queries individuais em <1ms com EXPLAIN ANALYZE. Índices corretos.  
**Redis:** 3.3 MB RAM — confirma zero caching ativo.

---

## Causa Raiz por Tela

| Sintoma | Causa | Fix |
|---------|-------|-----|
| Dashboard trava 7s | `/onboarding/progress` chamado 3–4× simultâneo | Sprint 2 — P1 |
| Bottom nav lento 6–8s | `OnboardingGuard` refaz fetch a cada rota | Sprint 2 — P1 |
| Budget/Plano 5.8s | `/cashflow?ano=` recomputa 50 queries (ignora cache) | Sprint 3 — P2 |
| Carteira/Investimentos dupla | `selectedMonth = new Date()` dispara fetch prematuro | Sprint 1 — P7 |
| Transações dupla | debounce cria objeto novo com mesmos valores → re-render | Sprint 1 — P8 |
| Nginx unhealthy | healthcheck incorreto (não operacional ainda) | Sprint 1 — P5 |

---

## Mapa de Prioridades

| ID | Descrição | Esforço | Ganho | Sprint |
|----|-----------|---------|-------|--------|
| **P5** | Fix nginx healthcheck | 5 min | Operacional | 1 |
| **P7** | `selectedMonth = null` — Carteira + Investimentos | 20 min | Elimina 2 fetches duplos | 1 |
| **P8** | Debounce stable ref — Transactions | 10 min | Elimina 2 fetches duplos | 1 |
| **P1** | Cache localStorage onboarding (3 componentes) | 30 min | Dashboard -5s, bottom nav -6s | 2 |
| **P2** | Cache DB cashflow anual | 15 min | Budget: 5.8s → 0.3s | 3 |
| **P3** | React Query para cashflow (dedup frontend) | 3-4h | UX fluída | 4 |
| **P6** | Redis para `/onboarding/progress` | 2h | Backend: <5ms/req | 4 |
| **P9** | Migrar Investimentos para endpoint `/overview` (B2) | 1h | Visita fria via API unificada | 4 |

---

## Sprints

| Sprint | Itens | Esforço | Redução de latência |
|--------|-------|---------|---------------------|
| [Sprint 1 — Quick Wins](sprint-1-quick-wins.md) | P5 · P7 · P8 | **~45 min** | Elimina 4 fetches duplos nas 3 telas |
| [Sprint 2 — Onboarding Cache](sprint-2-onboarding-cache.md) | P1 | **~30 min** | Dashboard: 7s → ~2s; bottom nav: 8s → ~1.5s |
| [Sprint 3 — Backend Cache Cashflow](sprint-3-backend-cache-cashflow.md) | P2 | **~15 min** | Budget: 5.8s → ~0.3s |
| [Sprint 4 — React Query + Redis](sprint-4-react-query-redis.md) | P3 · P6 · P9 | **~6–7h** | UX fluída, sem duplicatas residuais |

**Total sprints 1–3:** ~90 minutos de código. **Ganho imediato: ~70% de redução de latência.**

---

## Impacto Esperado Após Todos os Sprints

| Cenário | Hoje | Após S1+S2 | Após S1+S2+S3 | Após S4 |
|---------|------|-----------|----------------|---------|
| Dashboard 1ª visita | ~7s | ~4–5s | ~4–5s | ~1–2s |
| Dashboard 2ª+ visita | ~7s | **~1–2s** | ~1–2s | ~0.5s |
| Bottom nav (qualquer tela) | 6–8s | **~1.5s** | ~1.5s | ~0.5s |
| Budget/Plano | 5.8s | 5.8s | **~0.3s** | ~0.3s |
| Transações abertura | ~3s | **~1.5s** | ~1.5s | ~0.8s |
| Carteira (visita fria) | ~1.5s (dupla) | **~0.8s** | ~0.8s | ~0.5s |
| Investimentos (visita fria) | ~1.5s (dupla) | **~0.8s** | ~0.8s | ~0.5s |

---

## Arquivos Modificados (Todos os Sprints)

| Arquivo | Sprint | Item |
|---------|--------|------|
| `docker-compose.prod.yml` | 1 | P5 |
| `app/mobile/carteira/page.tsx` | 1 | P7 |
| `app/mobile/investimentos/page.tsx` | 1 | P7 |
| `app/mobile/transactions/page.tsx` | 1 | P8 |
| `features/onboarding/OnboardingGuard.tsx` | 2 | P1 |
| `features/onboarding/NudgeBanners.tsx` | 2 | P1 |
| `features/onboarding/DemoModeBanner.tsx` | 2 | P1 |
| `backend/app/domains/plano/router.py` | 3 | P2 |
| Múltiplos hooks de features | 4 | P3 |
| `backend/app/domains/onboarding/service.py` | 4 | P6 |
| `app/mobile/investimentos/page.tsx` | 4 | P9 |

**Total de arquivos:** 11 arquivos em 4 sprints.

---

## Referências

- **Análise completa:** [`ANALISE_PERFORMANCE_VM.md`](ANALISE_PERFORMANCE_VM.md)
- **Feature api-performance:** [`docs/features/api-performance/`](../api-performance/)
- **Plano de ação original:** [`ANALISE_PERFORMANCE_VM.md — Seção 4`](ANALISE_PERFORMANCE_VM.md)
- **Scripts de verificação:** [`perf_s1_verify.py`](perf_s1_verify.py) · [`perf_s2_verify.py`](perf_s2_verify.py)
