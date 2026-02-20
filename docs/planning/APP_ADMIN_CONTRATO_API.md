# Contrato de API – app_admin

**Objetivo:** Documentar os endpoints que o app_admin usa. Ao alterar auth ou users no backend, verificar impacto aqui.

---

## Endpoints utilizados

| Método | Endpoint | Uso |
|--------|----------|-----|
| POST | `/api/v1/auth/login` | Login (email, password) |
| GET | `/api/v1/auth/me` | Verificar usuário autenticado |
| POST | `/api/v1/auth/logout` | Logout |
| GET | `/api/v1/users/` | Listar usuários (admin) |
| POST | `/api/v1/users/` | Criar usuário (admin) |
| PUT | `/api/v1/users/{id}` | Atualizar usuário (admin) |
| DELETE | `/api/v1/users/{id}` | Desativar usuário (admin) |
| GET | `/api/v1/screens/admin/all` | Listar todas as telas (admin) |
| PATCH | `/api/v1/screens/{id}` | Atualizar status da tela (admin) |
| GET | `/api/v1/compatibility/` | Listar bancos e formatos |
| PUT | `/api/v1/compatibility/{id}` | Atualizar banco (admin) |
| GET | `/api/v1/classification/rules` | Listar regras de classificação |
| POST | `/api/v1/classification/rules` | Criar regra (admin) |
| PATCH | `/api/v1/classification/rules/{id}` | Atualizar regra (admin) |
| DELETE | `/api/v1/classification/rules/{id}` | Deletar regra (admin) |
| GET | `/api/v1/classification/stats` | Estatísticas das regras |
| GET | `/api/v1/classification/groups-with-types` | Grupos/subgrupos disponíveis |
| POST | `/api/v1/classification/rules/test` | Testar texto contra regras |
| POST | `/api/v1/classification/rules/import` | Importar regras hardcoded (admin) |

---

## Respostas esperadas

**auth/login:** `{ access_token, token_type, user: { id, email, nome, role } }`  
**auth/me:** `{ id, email, nome, role }`  
**users (list):** `{ users: [...], total: number }`  
**users (create/update):** `{ id, email, nome, role, ativo, created_at, updated_at }`

---

## Checklist ao alterar backend

Ao modificar `app_dev/backend/app/domains/auth/` ou `app_dev/backend/app/domains/users/`:

- [ ] Verificar se app_admin ainda funciona (login, contas)
- [ ] Atualizar este documento se houver mudança de contrato
