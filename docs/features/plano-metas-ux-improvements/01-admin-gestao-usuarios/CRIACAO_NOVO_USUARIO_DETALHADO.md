# Detalhamento: O que é criado para um novo usuário

**Data:** 28/02/2026  
**Objetivo:** Documentar exatamente o que acontece ao criar um usuário via Admin → Contas → Novo Usuário

---

## 1. Fluxo de criação (atual)

### Frontend (app_admin)
- **Página:** `/admin/contas`
- **Ação:** Clica em "Novo Usuário" → preenche Nome, Email, Senha, Perfil (user/admin)
- **Request:** `POST /api/v1/users/` com body:
  ```json
  {
    "nome": "Nome Completo",
    "email": "novo@email.com",
    "password": "senha123",
    "role": "user"
  }
  ```

### Backend (UserService.create_user)
1. Valida se email já existe
2. Cria **apenas 1 registro** na tabela `users`:
   - `email`, `nome`, `password_hash` (bcrypt), `role`, `ativo=1`, `created_at`, `updated_at`
3. Retorna `UserResponse` com id, email, nome, role, ativo, created_at, updated_at

---

## 2. O que É criado (hoje)

| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| **users** | 1 | Único registro criado: conta de acesso (login, perfil, status) |

**Campos do novo usuário:**
- `id` — auto-increment
- `email` — único
- `nome` — nome completo
- `password_hash` — bcrypt da senha
- `role` — "user" ou "admin"
- `ativo` — 1 (ativo)
- `created_at`, `updated_at` — timestamp

---

## 3. O que NÃO é criado (usuário começa zerado)

| Tabela | user_id? | O que o novo usuário tem |
|--------|----------|---------------------------|
| journal_entries | ✅ | 0 transações |
| upload_history | ✅ | 0 uploads |
| budget_planning | ✅ | 0 planos/metas |
| cartoes | ✅ | 0 cartões |
| base_padroes | ✅ | 0 padrões de estabelecimentos |
| base_parcelas | ✅ | 0 parcelas |
| preview_transacoes | ✅ | 0 (temporário) |
| transacoes_exclusao | ✅ | 0 exclusões |
| investimentos_portfolio | ✅ | 0 carteiras |
| investimentos_historico | ✅ | 0 transações |
| investimentos_planejamento | ✅ | 0 planejamentos |
| investimentos_cenarios | ✅ | 0 cenários |

---

## 4. Dados globais (disponíveis para todos)

Estas tabelas **não têm user_id** — são compartilhadas:

| Tabela | Descrição |
|--------|-----------|
| **base_grupos_config** | Grupos padrão (Alimentação, Transporte, etc.) — ~21 registros |
| **base_marcacoes** | Subgrupos/marcações globais |
| **generic_classification_rules** | Regras de classificação automática |
| **bank_format_compatibility** | Formatos de extrato bancário |
| **screen_visibility** | Configuração de telas visíveis |

O novo usuário **já tem acesso** a esses dados desde o primeiro login.

---

## 5. Resumo visual

```
┌─────────────────────────────────────────────────────────────┐
│  CRIAR USUÁRIO (Admin → Contas → Novo Usuário)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  CRIADO: 1 registro em users                                │
│  • id, email, nome, password_hash, role, ativo, timestamps  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ DADOS GLOBAIS │   │ DADOS POR     │   │ PRÓXIMOS       │
│ (já existem)  │   │ USUÁRIO       │   │ PASSOS        │
│               │   │ (zerados)     │   │               │
│ • grupos      │   │ • 0 transações│   │ 1. Fazer      │
│ • marcações   │   │ • 0 uploads   │   │    upload     │
│ • regras      │   │ • 0 planos    │   │ 2. Criar      │
│ • telas       │   │ • 0 cartões   │   │    metas      │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## 6. Pendências (PLANO 01-admin — atualizado 28/02/2026)

O plano foi **expandido** para incluir grupos por usuário. Ver `PLANO.md` e `TECH_SPEC.md`:

- [ ] **A.01–A.03** Migrations: `base_grupos_config` (user_id, is_padrao) + `base_marcacoes` (user_id) + script de dados
- [ ] **A.04–A.06** `_inicializar_grupos_usuario()`, `create_user()` chama init, `purge_user()` deleta grupos/marcações
- [ ] **A.11–A.17** Filtrar todos os domínios (grupos, marcações, budget, upload, transactions, dashboard, classification) por user_id

**Nota:** Após implementação, novo usuário receberá cópia dos grupos padrão do admin (user_id=1). Grupos criados por um usuário não aparecerão para outros.

---

## 7. Como testar

1. Acesse `http://localhost:3001/admin/contas`
2. Faça login como admin
3. Clique em "Novo Usuário"
4. Preencha: Nome, Email, Senha, Perfil (Usuário)
5. Salve
6. Verifique no banco:
   ```sql
   SELECT * FROM users ORDER BY id DESC LIMIT 1;
   -- Deve mostrar o novo usuário
   SELECT COUNT(*) FROM journal_entries WHERE user_id = <novo_id>;
   -- Deve ser 0
   ```
