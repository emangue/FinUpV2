# 🗺️ ROADMAP — Sistema FinUp: UX + Plano + Patrimônio

> **Este arquivo é o orquestrador master.** Ele não detalha implementações — cada sub-projeto tem seu próprio PRD, TECH_SPEC e Plano. Aqui vivem: sequência de execução, dependências entre sub-projetos e status geral.

---

## 📦 Sub-projetos

| # | Pasta | Foco | Sprint(s) | Estimativa | Dep. de |
|---|-------|------|-----------|-----------|---------|
| 01 | `01-admin-gestao-usuarios/` | Ciclo de vida de contas + grupos por usuário | 0 | ~14h | — |
| 02 | `02-ux-fundacao/` | Bugs críticos + Nav redesign + Empty states | 1 | ~10h | — |
| 03 | `03-onboarding-grupos/` | Primeiro login, grupos padrão, checklist, notificações | 2 | ~8h | 01 (trigger) |
| 04 | `04-upload-completo/` | Smart detection, rollback, multi-file, import, demo | 3, 3.5, 4, 5 | ~32h | 03 (grupos) |
| 05 | `05-plano-financeiro/` | Renda, meta anual, desvio, aposentadoria, déficit | 6, 7 | ~28h | 03 (perfil financeiro) |
| 06 | `06-patrimonio-investimentos/` | Vínculos, cotações, CDI, IR, posição, venda | 8, 9 | ~26h | 04 (uploads) + 05 (plano) |

**Total estimado: ~110h**

---

## 🔗 Mapa de dependências

```
01-admin          ──────────────────────────────────────┐
                                                        ↓
02-ux-fundacao    ──────────────────────────────────────┐
                                                        ↓
03-onboarding ←── depende de 01 (trigger de init)       │
      │                                                 ↓
      ├──────────────────────────────────→ 04-upload
      │                                        │
      └──────────────────────────────────→ 05-plano-financeiro
                                               │
                                    04 + 05 ──→ 06-patrimonio
```

**Regras:**
- 01 e 02 são **totalmente independentes** — podem ser feitos em paralelo
- 03 deve ser feito **após 01** (para o trigger de inicialização funcionar)
- 04 pode começar após 03 estar **pelo menos parcialmente done** (grupos padrão criados)
- 05 pode ser feito em paralelo com 04
- 06 só faz sentido completo após 04 e 05

---

## 📅 Sequência recomendada de execução

```
FASE 1 — Fundação (pode ser feita em qualquer ordem entre si)
  ├── Sprint 0: 01-admin-gestao-usuarios     (~6h)
  └── Sprint 1: 02-ux-fundacao               (~10h)

FASE 2 — Ativação de usuário
  └── Sprint 2: 03-onboarding-grupos         (~8h)

FASE 3 — Inteligência de dados (podem ser feitos em paralelo)
  ├── Sprints 3+3.5+4+5: 04-upload-completo  (~32h)
  └── Sprints 6+7:       05-plano-financeiro (~28h)

FASE 4 — Patrimônio (depende de FASE 3 completa)
  └── Sprints 8+9: 06-patrimonio-investimentos (~26h)
```

---

## ✅ Status dos sub-projetos

| Sub-projeto | PRD | TECH_SPEC | PLANO | Implementado | Observações |
|-------------|-----|-----------|-------|--------------|-------------|
| 01-admin | ✅ | ✅ | ✅ | ✅ | A.00–A.17 + T.01–T.06 concluídos; A.18 opcional |
| 02-ux-fundacao | ✅ | ✅ | ✅ | ✅ | Bugs + Nav + Empty states + FAB Upload + detecção por conteúdo |
| 03-onboarding | ✅ | ✅ | ✅ | ✅ | Welcome, choose-path, demo mode, checklist, nudges |
| 04-upload | ✅ | ✅ | ✅ | 🔄 | Sprint 3–5 ✅ (planilha genérica, import-planilha, FAB, batch, BatchClassifyModal) |
| 05-plano | ✅ | ✅ | ✅ | ❌ | Aguarda 03 |
| 06-patrimonio | ✅ | ✅ | ✅ | ❌ | Aguarda 04+05 |

---

## 🚀 Próximos passos (ordem sugerida)

1. **05-plano** — Pode iniciar (03 concluído): renda, meta anual, desvio, aposentadoria
2. **05-plano — Volta ao legado** — Ver `05-plano-financeiro/PLANO_VOLTA_LEGADO.md`: remover `plano_compromissos`, alinhar ao modelo de 3 camadas (budget_planning + base_expectativas futura)
3. **05-plano — Plano de ajuste** — Ver `05-plano-financeiro/PLANO_DE_AJUSTE.md`: **Fase 0 primeiro** (shell do wizard em `/mobile/construir-plano`), depois hub, projeção, etc. Regra: toda edição do plano passa pelo wizard.

---

## 📋 Protocolo de testes (Definition of Done por sub-projeto)

A cada item de qualquer sub-projeto:

```
1. Implementar (código + migration se necessário)
2. Testes automatizados: docker exec finup_backend_dev pytest -v
3. Build check: docker exec finup_frontend_app_dev npm run build
4. Subir servidor: ./scripts/deploy/quick_start_docker.sh
5. Informar ao usuário: "Pronto para testar. Acesse [URL] e valide: [lista de ações]"
6. Aguardar feedback
7. Só então: git commit + próximo item
```

---

## 📁 Estrutura de cada sub-projeto

```
XX-nome-do-subprojeto/
├── PRD.md              ← O quê e por quê (user stories + acceptance criteria)
├── TECH_SPEC.md        ← Como (código, migrations, componentes)
└── PLANO.md            ← Quando e em que ordem (tasks + estimativas)
```

---

## 📚 Arquivos legados (referência)

Os arquivos originais (PRD monolítico, TECH_SPEC monolítico, UX doc, PLANO original) estão em `_legado/` para consulta. Eles cobrem o mesmo conteúdo mas de forma não estruturada.
