# Plano de Restauração Completo – Sprints A a H

**Data:** 20/02/2026  
**Contexto:** Implantação falhou; todas as sprints (A–H) foram implementadas em conversas anteriores. Este documento mapeia o que existe, o que pode ter sido perdido e como restaurar o app ao estado ajustado.

---

## ⚠️ Limitação Importante

**Não é possível acessar o histórico completo de conversas.** Este plano foi montado com base em:

- Resumo da conversa (YTD/Ano toggle, commit 0f3ba79a)
- Documentos do projeto (VALIDACAO_GIT, SPRINT_TRACKER)
- Busca no código atual
- Histórico de commits do Git

---

## 1. Estado Atual do Repositório

| Item | Valor |
|------|--------|
| Branch atual | `main` |
| Main local vs origin | **25 commits atrás** de `origin/main` |
| Branch `feature/plano-aposentadoria-ajustes` | **Não existe** (local nem remoto) |
| Último commit relevante | `0f3ba79a` – "restaura router/service transactions e dashboard + Sprint A/B" |
| Alterações não commitadas | Dashboard YTD, orcamento-tab, bar-chart, gastos-por-cartao, etc. |

### Alterações locais (não commitadas)

```
M app_dev/backend/app/domains/dashboard/repository.py
M app_dev/backend/app/domains/dashboard/router.py
M app_dev/backend/app/domains/dashboard/service.py
M app_dev/frontend/src/app/mobile/dashboard/page.tsx
M app_dev/frontend/src/components/mobile/ytd-toggle.tsx
M app_dev/frontend/src/features/dashboard/components/bar-chart.tsx
M app_dev/frontend/src/features/dashboard/components/gastos-por-cartao-box.tsx
M app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx
M app_dev/frontend/src/features/dashboard/hooks/use-dashboard.ts
M app_dev/frontend/src/features/dashboard/services/dashboard-api.ts
```

Essas alterações correspondem ao **toggle Mês/YTD/Ano** (Sprint G – Reorganização Dashboard).

---

## 2. Mapeamento Sprints A–H vs Código

### Sprint A: Ajustes UX (Feito ✅)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Remover mensagem "Ver Todas" (se existir) | VALIDACAO_GIT: "Sprint A – remove mensagem Ver Todas" | Verificar em `mobile/dashboard` e `transactions` |
| Ajustes gerais de UX | Difícil rastrear sem histórico | ⚠️ Verificar manualmente |

**Ação:** Procurar por "Ver Todas" e avaliar se deve ser removida ou mantida.

---

### Sprint B: Despesas vs Plano — Highlight (Feito ✅)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Highlight em Despesas vs Plano (acima/abaixo do plano) | `orcamento-tab.tsx` linhas 243–260: `highlightText`, `highlightClass`, cores vermelho/verde | ✅ Presente |

**Arquivo:** `app_dev/frontend/src/features/dashboard/components/orcamento-tab.tsx`

---

### Sprint C: Paleta + Central de Grupos (Feito ✅)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Paleta de cores | `features/goals/lib/colors.ts`, `components/mobile/category-icon.tsx` | ✅ Presente |
| Central de Grupos | Verificar se existe tela/rota dedicada | ⚠️ Buscar "central grupos" ou "grupos" em settings |

**Ação:** Confirmar se há tela "Central de Grupos" em `/settings/grupos` ou similar.

---

### Sprint D: Preview Upload — Deletar (Feito ✅)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Deletar preview antes de confirmar | Backend: `delete_preview` em `upload/router.py`, `upload/service.py` | ✅ Presente |
| UI para deletar no preview | `upload/preview/[sessionId]/page.tsx` | ✅ Presente |

**Endpoints:** `DELETE /upload/preview/{session_id}`

---

### Sprint E: Remover Investimentos + Metas lista (Feito ✅)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Remover item "Investimentos" do menu/sidebar | Verificar `nav-main`, `app-sidebar`, `BottomNavigation` | ⚠️ Verificar |
| Remover "Metas lista" (ou simplificar) | `mobile/budget` ainda tem filtro investimentos | ⚠️ Pode ser "remover da lista principal" |

**Ação:** Conferir se o menu mobile tem 5 tabs (Dashboard, Transações, Metas, Upload, Profile) e se Investimentos foi removido da navegação principal.

---

### Sprint F: Tela Transações Redesign (Em progresso ⏳)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Redesign da tela de transações | `mobile/transactions/page.tsx` | ✅ Existe |
| Filtros (all, receita, despesa, transferência, investimentos) | Linhas 25, 112, 256 | ✅ Presente |

**Ação:** Validar visual e fluxo conforme protótipo/PRD.

---

### Sprint G: Reorganização Dashboard (Em progresso ⏳)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Toggle Mês / YTD / Ano | `ytd-toggle.tsx` (3 opções) | ✅ Presente (alterações locais) |
| YearScrollPicker | `year-scroll-picker.tsx` | ✅ Presente |
| Backend chart-data-ytd, years-with-data, through_month | `dashboard/router.py`, `service.py`, `repository.py` | ✅ Presente (alterações locais) |
| OrcamentoTab com period/throughMonth | `orcamento-tab.tsx` | ✅ Presente |
| BarChart com legendas YTD/Ano | `bar-chart.tsx` | ✅ Presente |
| GastosPorCartaoBox com throughMonth | `gastos-por-cartao-box.tsx` | ✅ Presente |

**Importante:** As alterações do Sprint G estão **não commitadas**. É essencial preservá-las.

---

### Sprint H: Plano Aposentadoria (cenários, gráfico) (Em progresso ⏳)

| O que fazer | Evidência no código | Status |
|-------------|--------------------|--------|
| Tab Plano Aposentadoria no dashboard mobile | `mobile/dashboard/page.tsx` – `PlanoAposentadoriaTab` | ✅ Presente |
| Tela Personalizar Plano | `mobile/personalizar-plano/page.tsx` | ✅ Presente |
| Componentes | `plano-aposentadoria-tab.tsx`, `PersonalizarPlanoLayout.tsx` | ✅ Presente |
| Simulador de cenários | `simulador-cenarios.tsx` (investimentos) | ✅ Presente |

**Rotas:** `/mobile/personalizar-plano`, tab "Plano" no dashboard.

---

## 3. Plano de Execução – Restauração

### Fase 0: Preservar trabalho atual (antes de qualquer pull/reset)

```bash
# 1. Criar branch com TODO o estado atual (incluindo não commitado)
git checkout -b wip/restauracao-sprints-20fev2026
git add app_dev/backend/app/domains/dashboard/
git add app_dev/frontend/src/app/mobile/dashboard/
git add app_dev/frontend/src/components/mobile/
git add app_dev/frontend/src/features/dashboard/
git status   # conferir
git commit -m "wip: estado atual com YTD/Ano toggle e alterações dashboard (Sprint G)"
```

### Fase 1: Sincronizar com remoto (sem perder trabalho)

```bash
# 2. Voltar para main e puxar
git checkout main
git pull origin main

# 3. Reaplicar suas alterações em cima da main atualizada
git checkout wip/restauracao-sprints-20fev2026 -- app_dev/backend/app/domains/dashboard/
git checkout wip/restauracao-sprints-20fev2026 -- app_dev/frontend/src/app/mobile/dashboard/
git checkout wip/restauracao-sprints-20fev2026 -- app_dev/frontend/src/components/mobile/
git checkout wip/restauracao-sprints-20fev2026 -- app_dev/frontend/src/features/dashboard/

# 4. Resolver conflitos se houver (git status, editar arquivos)
# 5. Testar localmente
```

### Fase 2: Verificação por Sprint

| Sprint | Ação |
|--------|------|
| A | Buscar "Ver Todas" e ajustar conforme UX desejada |
| B | ✅ Já presente em orcamento-tab |
| C | Verificar paleta e Central de Grupos |
| D | ✅ Backend e frontend presentes |
| E | Verificar menu/sidebar – Investimentos removido ou não |
| F | Validar tela de transações |
| G | ✅ Código presente (commit na Fase 0) |
| H | ✅ Plano Aposentadoria presente |

### Fase 3: Commit e deploy

```bash
# 1. Criar branch de feature para merge
git checkout -b feature/restauracao-sprints-completa
git add .
git status
git commit -m "feat: restauração completa Sprints A-H (YTD/Ano, highlight, plano aposentadoria)"

# 2. Push da branch
git push -u origin feature/restauracao-sprints-completa

# 3. No servidor: fazer pull da branch, testar, depois merge na main
```

---

## 4. Checklist de Validação Pós-Restauração

- [ ] Backend sobe sem erro (`uvicorn` ou `python -m uvicorn`)
- [ ] Frontend builda (`npm run build`)
- [ ] Dashboard mobile: toggle Mês/YTD/Ano funciona
- [ ] OrcamentoTab: Despesas vs Plano com highlight (vermelho/verde)
- [ ] Tab Plano Aposentadoria visível e funcional
- [ ] Preview upload: botão/opção de deletar funciona
- [ ] Transações mobile: tela carrega e filtros funcionam
- [ ] Navegação (Bottom Nav) com 5 tabs corretas

---

## 5. Arquivos Críticos – Referência Rápida

| Sprint | Arquivos principais |
|--------|---------------------|
| A | `mobile/dashboard/page.tsx`, `mobile/transactions/page.tsx` |
| B | `features/dashboard/components/orcamento-tab.tsx` |
| C | `features/goals/lib/colors.ts`, `settings/grupos/` |
| D | `upload/preview/[sessionId]/page.tsx`, `upload/router.py` |
| E | `components/*/nav-*.tsx`, `BottomNavigation` |
| F | `mobile/transactions/page.tsx` |
| G | `ytd-toggle.tsx`, `year-scroll-picker.tsx`, `dashboard/*`, `orcamento-tab.tsx`, `bar-chart.tsx`, `gastos-por-cartao-box.tsx` |
| H | `plano-aposentadoria/*`, `mobile/personalizar-plano/` |

---

## 6. Documentos Relacionados

- [PLANO_REVERSAO_DASHBOARD_YTD.md](../features/PLANO_REVERSAO_DASHBOARD_YTD.md) – Detalhes do toggle Mês/YTD/Ano
- [VALIDACAO_GIT_20FEV2026.md](VALIDACAO_GIT_20FEV2026.md) – Estratégia Git e branches
- [PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md](PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md) – Plano geral de implantação

---

**Última atualização:** 20/02/2026
