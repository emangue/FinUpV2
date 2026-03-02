# PLANO — Admin: Gestão Completa de Usuários + Grupos por Usuário

**Sub-projeto:** 01 | **Sprint:** 0 | **Estimativa:** ~14h (era ~6h; +8h para grupos por usuário)

---

## Contexto: Grupos por Usuário

**Problema:** `base_grupos_config` e `base_marcacoes` são globais. Quando um usuário cria um grupo, **vale para todos** — incorreto.

**Solução:** Adicionar `user_id` em ambas as tabelas. Cada usuário tem seus próprios grupos (padrão + customizados). Novo usuário recebe cópia da **base template** ao criar conta.

---

## Base template (fonte para novos usuários)

- **Tabelas template** (`base_grupos_template`, `base_marcacoes_template`) — globais, sem user_id
- **Fonte:** `generic_classification_rules` (grupos/subgrupos das regras) + complementos padrão (Salário, Transferência, Outros)
- **Raramente alterada** — admin pode editar em `/admin/grupos-base` (fase posterior)
- **Novo usuário:** copiar do template → `base_grupos_config` e `base_marcacoes` do usuário

Ver `BASE_TEMPLATE_GRUPOS.md` para detalhes.

---

## Tasks

### Fase 1 — Migrations e dados (~5h)

- [x] **A.00** Migration: criar tabelas template
  - `base_grupos_template` (id, nome_grupo, tipo_gasto_padrao, categoria_geral, cor) — UNIQUE(nome_grupo)
  - `base_marcacoes_template` (id, GRUPO, SUBGRUPO) — UNIQUE(GRUPO, SUBGRUPO)
  - Popular a partir de `generic_classification_rules` (DISTINCT grupo, subgrupo, tipo_gasto) + grupos faltantes de `base_grupos_config` atual (Salário, Transferência, Outros, Doações)

- [x] **A.01** Migration: `base_grupos_config` — add `user_id`, `is_padrao`; alterar UNIQUE
  - Add `user_id INTEGER NOT NULL` (FK users.id, default 1 para migração)
  - Add `is_padrao BOOLEAN DEFAULT false`
  - Drop `UNIQUE(nome_grupo)` → create `UNIQUE(user_id, nome_grupo)`

- [x] **A.02** Migration: `base_marcacoes` — add `user_id`
  - Add `user_id INTEGER NOT NULL` (FK users.id, default 1)
  - Create `UNIQUE(user_id, GRUPO, SUBGRUPO)`

- [x] **A.03** Script de migração de dados existentes (executar após A.00, A.01 e A.02)
  - Atribuir registros atuais de `base_grupos_config` e `base_marcacoes` a `user_id=1`
  - Para cada usuário existente (id 2, 3, 4...): **copiar do template** (não do user 1) → base_grupos_config e base_marcacoes do usuário

### Fase 2 — Backend Users (~2h)

- [x] **A.04** `UserService._inicializar_grupos_usuario(user_id)` — idempotente
  - **Copiar de `base_grupos_template`** → insert em `base_grupos_config` com `user_id=novo`, `is_padrao=true`
  - **Copiar de `base_marcacoes_template`** → insert em `base_marcacoes` com `user_id=novo`

- [x] **A.05** `UserService.create_user()` — chamar `_inicializar_grupos_usuario()` após flush

- [x] **A.06** `UserService.purge_user()` — adicionar delete de `base_grupos_config` e `base_marcacoes` WHERE user_id

- [x] **A.07** `GET /users/{id}/stats` — endpoint + `UserStatsResponse` schema

- [x] **A.08** `POST /users/{id}/reativar` — seta `ativo=True`

- [x] **A.09** `DELETE /users/{id}/purge` — body `PurgeConfirmacao`, user_id=1 protegido, log

- [x] **A.10** `GET /users/?apenas_ativos=false` — parâmetro na query existente

### Fase 3 — Backend: filtrar por user_id (~4h)

- [x] **A.11** `grupos/` — repository, service, router: filtrar `base_grupos_config` por user_id
  - `GrupoRepository.get_all(user_id)`, `get_by_nome(user_id, nome)`, etc.

- [x] **A.12** `marcacoes/` — repository, service, router: filtrar `base_marcacoes` por user_id
  - `MarcacaoRepository.get_all(user_id)`, `get_grupo_config(user_id, nome)`, etc.
  - `create_grupo_com_subgrupo` — passar user_id ao criar grupo e marcação

- [x] **A.13** `budget/` — service, router: filtrar grupos por user_id
  - `list_grupos_disponiveis`, `list_grupos_com_categoria`, `get_budget_planning`

- [x] **A.14** `upload/` — service, classifier, pattern_generator: buscar grupos/marcações do user_id
  - `_ensure_marcacao_exists(user_id, grupo, subgrupo)`
  - Queries em base_grupos_config e base_marcacoes com user_id

- [x] **A.15** `transactions/` — service: validar grupo existe para user_id; `_ensure_marcacao_exists(user_id, ...)`

- [x] **A.16** `dashboard/` — repository: JOIN com grupos do user_id

- [x] **A.17** `classification/` — service: `get_grupos_com_tipos(user_id)`

### Fase 4 — Frontend app_admin (~2h)

- [ ] **A.18** (opcional, fase posterior) Admin: tela `/admin/grupos-base` para editar template
  - Listar/editar `base_grupos_template` e `base_marcacoes_template`
  - Alterações raras — template é a base copiada para novos usuários

- [x] **F.01** `UserStatsCell` — useSWR lazy load + Tooltip completo

- [x] **F.02** Toggle "Ver inativos" + atualizar query + badge INATIVA + opacidade

- [x] **F.03** Botão "Reativar" em inativos; "Desativar" em ativos; ambos ausentes em user_id=1

- [x] **F.04** `PurgeUserModal` — 2 etapas (resumo de dados → digitar e-mail)

### Fase 5 — Testes (~2h)

- [x] **T.01** Criar usuário → confirmar `SELECT COUNT(*) FROM base_grupos_config WHERE user_id=X` = 14 (template)
- [x] **T.02** Trigger idempotente: chamar `_inicializar_grupos_usuario()` duas vezes → ainda 14 grupos
- [x] **T.03** User A cria grupo "MeuGrupo" → User B não vê "MeuGrupo" em GET /grupos/
- [x] **T.04** Purge → `SELECT COUNT(*) FROM journal_entries WHERE user_id=X` = 0 e base_grupos_config/base_marcacoes zerados
- [x] **T.05** user_id=1 → `DELETE /users/1/purge` retorna 403
- [x] **T.06** Reativar → usuário consegue logar normalmente

---

## Validação pelo usuário

Após subir o servidor (`./scripts/deploy/quick_start_all.sh`), testar em `http://localhost:3001`:

1. Criar uma nova conta via "+ Novo Usuário" → confirmar toast de grupos configurados
2. Logar como novo usuário no BAU (3000) → verificar que grupos existem (GET /grupos/)
3. Criar grupo "TesteCustom" como User A → logar como User B → User B não vê "TesteCustom"
4. Desativar a conta recém-criada → linha esmaece com badge INATIVA
5. Ativar toggle "Ver inativos" → conta aparece
6. Reativar → badge some, conta volta ao normal
7. Tentar purge em user_id=1 → deve falhar
8. Fazer purge de conta de teste → confirmar que não aparece mais em nenhuma listagem

---

## Ordem de execução

```
FASE 1 (migrations + dados)
  A.00 (criar template + popular) → A.01 → A.02 → A.03

FASE 2 (users)
  A.04 → A.05 → A.06   (A.07–A.10 já feitos)

FASE 3 (filtrar por user_id — ordem sugerida)
  A.11 (grupos) → A.12 (marcacoes)   (base para os demais)
  A.13 (budget) → A.14 (upload) → A.15 (transactions) → A.16 (dashboard) → A.17 (classification)

FASE 4 (frontend — já feita)
  F.01–F.04

FASE 5 (testes)
  T.01 → T.06
```

---

## Arquivos impactados (resumo)

| Domínio | Arquivos |
|---------|----------|
| migrations | Nova migration (template + base_grupos_config + base_marcacoes) |
| users | service.py (create_user, purge_user, _inicializar_grupos_usuario) |
| grupos | models.py, repository.py, service.py |
| categories | models.py (BaseMarcacao) |
| marcacoes | repository.py, service.py |
| budget | service.py, router.py |
| upload | service.py, pattern_generator.py |
| transactions | service.py |
| dashboard | repository.py |
| classification | service.py |

---

## Commit ao finalizar

```bash
git add app_dev/backend/app/domains/ \
        app_dev/backend/migrations/versions/ \
        app_admin/frontend/src/
git commit -m "feat(admin): gestão usuários + grupos por usuário — migration, init, purge, filtros"
```
