# PLANO — Admin: Gestão Completa de Usuários

**Sub-projeto:** 01 | **Sprint:** 0 | **Estimativa:** ~6h

---

## Tasks

### Backend (~3h)

- [ ] **A.01** Migration: `base_grupos_config.is_padrao` + index
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_is_padrao_base_grupos_config"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **A.02** `UserService._inicializar_usuario()` — 11 grupos padrão + perfil vazio (idempotente)

- [ ] **A.03** `UserService.create_user()` — chamar `_inicializar_usuario()` após flush

- [ ] **A.04** `GET /users/{id}/stats` — endpoint + `UserStatsResponse` schema

- [ ] **A.05** `POST /users/{id}/reativar` — seta `ativo=True`

- [ ] **A.06** `DELETE /users/{id}/purge` — body `PurgeConfirmacao`, user_id=1 protegido, log

- [ ] **A.07** `GET /users/?apenas_ativos=false` — parâmetro na query existente

### Frontend — app_admin (~2h)

- [ ] **F.01** `UserStatsCell` — useSWR lazy load + Tooltip completo

- [ ] **F.02** Toggle "Ver inativos" + atualizar query + badge INATIVA + opacidade

- [ ] **F.03** Botão "Reativar" em inativos; "Desativar" em ativos; ambos ausentes em user_id=1

- [ ] **F.04** `PurgeUserModal` — 2 etapas (resumo de dados → digitar e-mail)

### Testes (~1h)

- [ ] **T.01** Criar usuário → confirmar `SELECT COUNT(*) FROM base_grupos_config WHERE user_id=X` = 11
- [ ] **T.02** Trigger idempotente: chamar `_inicializar_usuario()` duas vezes → ainda 11 grupos
- [ ] **T.03** Purge → `SELECT COUNT(*) FROM journal_entries WHERE user_id=X` = 0
- [ ] **T.04** user_id=1 → `DELETE /users/1/purge` retorna 403
- [ ] **T.05** Reativar → usuário consegue logar normalmente

---

## Validação pelo usuário

Após subir o servidor (`./scripts/deploy/quick_start_docker.sh`), testar em `http://localhost:3001`:

1. Criar uma nova conta via "+ Nova Conta" → confirmar toast de grupos configurados
2. Verificar na tela de transações do novo usuário que grupos existem (via API `GET /grupos/`)
3. Desativar a conta recém-criada → linha esmaece com badge INATIVA
4. Ativar toggle "Ver inativos" → conta aparece
5. Reativar → badge some, conta volta ao normal
6. Tentar purge em user_id=1 → deve falhar
7. Fazer purge de conta de teste → confirmar que não aparece mais em nenhuma listagem

---

## Ordem de execução

```
A.01 (migration) → A.02 → A.03   (trigger: precisa da migration)
A.04, A.05, A.06, A.07            (podem ser feitos em paralelo)
F.01, F.02, F.03, F.04            (frontend: após backend pronto)
T.01 → T.05                       (testes: ao final)
```

## Commit ao finalizar

```bash
git add app_dev/backend/app/domains/users/ \
        app_dev/backend/migrations/versions/ \
        app_admin/frontend/src/
git commit -m "feat(admin): gestão completa de usuários — purge, reativar, stats, trigger init"
```
