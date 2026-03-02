# Proposta: Grupos por Usuário (base_grupos_config + base_marcacoes)

**Data:** 28/02/2026  
**Status:** ✅ Incorporada ao PLANO.md e TECH_SPEC.md do sub-projeto 01-admin

**Problema:** Hoje `base_grupos_config` e `base_marcacoes` são globais. Quando um usuário cria um grupo, **vale para todos** — isso não está correto.

---

## 1. Situação atual (problemática)

| Tabela | user_id? | Comportamento |
|--------|----------|---------------|
| base_grupos_config | ❌ Não | Grupo criado por User A aparece para User B, C, D... |
| base_marcacoes | ❌ Não | Subgrupo criado por User A aparece para todos |

**Fluxo atual:** `POST /marcacoes/grupos` → insere em base_grupos_config (global) → todos veem.

---

## 2. Objetivo

- Cada usuário tem **seus próprios grupos** (padrão + customizados)
- Grupo criado por User A **não** aparece para User B
- Novo usuário recebe **cópia dos grupos padrão** ao criar conta

---

## 3. Estratégia proposta

### 3.1. Adicionar `user_id` às tabelas

**base_grupos_config:**
- Adicionar `user_id INTEGER NOT NULL` (FK users.id)
- Adicionar `is_padrao BOOLEAN DEFAULT false` (marca grupos copiados do template)
- Remover `UNIQUE(nome_grupo)` → trocar por `UNIQUE(user_id, nome_grupo)` (mesmo nome pode existir para usuários diferentes)

**base_marcacoes:**
- Adicionar `user_id INTEGER NOT NULL` (FK users.id)
- Trocar `UNIQUE(GRUPO, SUBGRUPO)` → `UNIQUE(user_id, GRUPO, SUBGRUPO)`

### 3.2. Migração dos dados existentes

1. **base_grupos_config:** Atribuir todos os 14 registros atuais a `user_id=1` (admin), `is_padrao=true`
2. **base_marcacoes:** Atribuir todos os registros atuais a `user_id=1`
3. Para cada outro usuário existente (2, 3, 4...): copiar grupos e marcações do user_id=1

### 3.3. Criação de novo usuário

Ao chamar `UserService.create_user()`:
1. Criar registro em `users`
2. Chamar `_inicializar_grupos_usuario(user_id)`:
   - Copiar de `base_grupos_config WHERE user_id=1 AND is_padrao=true` → insert com `user_id=novo`, `is_padrao=true`
   - Copiar de `base_marcacoes WHERE user_id=1` cujos grupos existem no template → insert com `user_id=novo`

### 3.4. Quando usuário cria grupo

`MarcacaoService.create_grupo_com_subgrupo()`:
- Receber `user_id` do token
- Inserir em `base_grupos_config` com `user_id=user_id`, `is_padrao=false`
- Inserir em `base_marcacoes` com `user_id=user_id`

### 3.5. Queries — filtrar por user_id

**Todos os pontos que leem base_grupos_config ou base_marcacoes** devem filtrar por `user_id` do usuário logado:

- `GET /grupos/` → `WHERE user_id = :current_user_id`
- `GET /marcacoes/` → `WHERE user_id = :current_user_id`
- Classificação no upload → buscar grupos do user_id
- Budget/dashboard → JOIN com grupos do user_id
- etc.

---

## 4. Impacto (arquivos a alterar)

| Área | Arquivos |
|------|----------|
| **Migration** | Nova migration: add user_id, is_padrao em base_grupos_config; add user_id em base_marcacoes |
| **Models** | `grupos/models.py`, `categories/models.py` (BaseMarcacao) |
| **Users** | `users/service.py` — create_user + _inicializar_grupos_usuario |
| **Marcações** | `marcacoes/service.py`, `marcacoes/repository.py` — passar user_id em create |
| **Grupos** | `grupos/repository.py`, `grupos/router.py` — filtrar por user_id |
| **Upload** | `upload/service.py`, classifier — buscar grupos do user_id |
| **Budget** | `budget/service.py` — filtrar grupos do user_id |
| **Dashboard** | `dashboard/repository.py` — JOIN com grupos do user_id |
| **Transactions** | `transactions/service.py` — validar grupo existe para user_id |
| **Frontend** | APIs de grupos/marcações já passam token → backend filtra |

---

## 5. Ordem de execução sugerida

1. **Migration** — add colunas (user_id nullable inicialmente para migrar dados)
2. **Migrar dados** — script que atribui user_id=1 e copia para outros usuários
3. **Alterar constraint** — user_id NOT NULL, UNIQUE(user_id, nome_grupo)
4. **Backend** — models, repositories, services (filtrar por user_id)
5. **Trigger** — _inicializar_grupos_usuario no create_user
6. **Testes** — criar user → verificar grupos; criar grupo → só o dono vê

---

## 6. Alternativa mais simples (curto prazo)

Se a migração completa for pesada, uma alternativa **temporária**:

- **Bloquear** criação de grupos por usuários comuns (apenas admin pode criar)
- Manter base global
- Documentar que "grupos customizados" será implementado em sprint futura

Isso evita o bug (ninguém cria grupo que afeta outros) mas não entrega a funcionalidade completa.

---

## 7. Decisão

Recomendação: **implementar a solução completa** (seção 3), pois:
- O design atual é incorreto e pode causar conflitos entre usuários
- O TECH_SPEC do plano 01-admin já previa user_id
- A migração é factível com script de dados
