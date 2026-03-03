# PLANO — Onboarding + Grupos Padrão

**Sub-projeto:** 03 | **Sprint:** 2 | **Estimativa:** ~8h  
**Pré-requisito:** Sub-projeto 01 commitado (trigger de init cria grupos automaticamente)

---

## Tasks

### Backend (~3h)

- [ ] **A.01** Migration: `journal_entries.fonte` (string) + `is_demo` (boolean)
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_fonte_is_demo_journal_entries"
  docker exec finup_backend_dev alembic upgrade head
  ```
- [ ] **A.02** `GET /onboarding/progress` — 4 flags de completude
- [ ] **A.03** Definir e implementar dataset demo (~90 transações em `DEMO_SEED`)
- [ ] **A.04** `POST /onboarding/modo-demo` — inserir seed com `fonte='demo'`
- [ ] **A.05** `DELETE /onboarding/modo-demo` — limpar `WHERE fonte='demo'`

### Frontend (~5h)

- [ ] **F.01** Middleware: detectar primeiro acesso → redirect para `/mobile/onboarding/welcome`
- [ ] **F.02** Layout `/mobile/onboarding/` (sem bottom nav)
- [ ] **F.03** Tela `welcome/page.tsx` — headline + 3 bullets + 2 CTAs + "Pular"
- [ ] **F.04** Tela `choose-path/page.tsx` — "Meus dados" (upload) vs. "Explorar" (demo)
- [ ] **F.05** `OnboardingChecklist` no `/mobile/inicio` com useSWR + desaparece quando completo
- [ ] **F.06** `DemoModeBanner` — detectar dados demo + CTA "Usar meus dados →"
- [ ] **F.07** 4 banners S29 (nudges contextuais) com localStorage para "não mostrar de novo"

---

## Validação pelo usuário

Após `./scripts/deploy/quick_start_docker.sh`:

1. Criar usuário novo via admin → logar no app → redireciona para `/mobile/onboarding/welcome` ✅
2. Clicar "Explorar primeiro" → app carrega com dados fictícios + banner "Modo Exploração" ✅
3. "Usar meus dados →" no banner → dados demo somem + vai para upload ✅
4. Logar com usuário novo "Começar com meus dados" → vai para upload ✅
5. Após primeiro upload: checklist aparece no Início com 2/4 marcados ✅
6. Criar plano → 3/4 ✅
7. Adicionar investimento → 4/4 → checklist some ✅
8. Verificar: banner S29 de "Hora de subir extrato" após 30 dias (simular via data falsa ou testar manualmente) ✅

---

## Ordem de execução

```
A.01 (migration) → A.02, A.03 em paralelo → A.04, A.05 (depende de A.03)
F.01 → F.02 → F.03 → F.04   (onboarding: sequencial)
F.05 (checklist: após A.02)
F.06, F.07 (independentes do resto)
```

## Commit ao finalizar

```bash
git add app_dev/backend/app/domains/onboarding/ \
        app_dev/backend/migrations/versions/ \
        app_dev/frontend/src/app/mobile/onboarding/ \
        app_dev/frontend/src/features/onboarding/
git commit -m "feat(onboarding): welcome, choose path, demo mode, checklist, nudges"
```
