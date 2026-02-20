# 📝 Mapeamento Completo - Criação de Usuário

**Data:** 13/02/2026  
**Objetivo:** Mapear TUDO que acontece quando um novo usuário é criado no sistema

---

## 🎯 Visão Geral

Este documento mapeia o **processo completo de criação de usuário**, desde a criação da conta até todos os dados default gerados automaticamente. Essencial para a **Frente 5 (Teste Usuário Inicial)**.

---

## 📍 1. ENDPOINT DE CRIAÇÃO

### Backend: `POST /api/v1/users`

**Arquivo:** `app_dev/backend/app/domains/users/router.py`

```python
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Cria novo usuário
    """
    service = UserService(db)
    return service.create_user(user)
```

### Schema de Criação

**Arquivo:** `app_dev/backend/app/domains/users/schemas.py`

```python
class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")
```

**Campos obrigatórios:**
- ✅ `nome` (string, min 2 chars)
- ✅ `email` (EmailStr, validado)
- ✅ `password` (string, min 6 chars)

**Campos opcionais:**
- ⚙️ `role` (default: "user", pode ser "admin")

---

## 🔨 2. LÓGICA DE CRIAÇÃO

### Service Layer

**Arquivo:** `app_dev/backend/app/domains/users/service.py`

```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    """
    Lógica de negócio:
    1. Verifica se email já existe
    2. Hash da senha (bcrypt, 12 salt rounds)
    3. Define timestamps
    4. Salva no banco
    """
    
    # 1. Validação: Email duplicado?
    if self.repository.email_exists(user_data.email):
        raise HTTPException(
            status_code=400,
            detail=f"Email '{user_data.email}' já está cadastrado"
        )
    
    # 2. Criação do modelo
    now = datetime.now()
    user = User(
        email=user_data.email,
        nome=user_data.nome,
        password_hash=hash_password(user_data.password),  # bcrypt
        role=user_data.role,
        ativo=1,  # Ativo por padrão
        created_at=now,
        updated_at=now
    )
    
    # 3. Salvar no banco
    created = self.repository.create(user)
    return UserResponse.from_orm(created)
```

### Validações Aplicadas

1. **Email único** - Não pode duplicar
2. **Password mínimo** - 6 caracteres
3. **Bcrypt hash** - Senha nunca armazenada em texto plano
4. **Timestamps** - created_at e updated_at automáticos
5. **Ativo default** - Usuário já nasce ativo (ativo=1)

---

## 🗄️ 3. TABELA USERS - ESTRUTURA

**Tabela:** `users`

**Modelo:** `app_dev/backend/app/domains/users/models.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)
    ativo = Column(Integer, default=1)
    role = Column(String(20), default="user")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### Campos na Tabela

| Campo | Tipo | Nullable | Default | Descrição |
|-------|------|----------|---------|-----------|
| `id` | Integer | ❌ | AUTO | Primary key |
| `email` | String(255) | ❌ | - | Email único (indexed) |
| `password_hash` | String(255) | ❌ | - | Senha bcrypt |
| `nome` | String(200) | ❌ | - | Nome completo |
| `ativo` | Integer | ✅ | 1 | Status (1=ativo, 0=inativo) |
| `role` | String(20) | ✅ | "user" | Papel (user/admin) |
| `created_at` | DateTime | ✅ | - | Data de criação |
| `updated_at` | DateTime | ✅ | - | Última atualização |

---

## 📦 4. DADOS GERADOS AUTOMATICAMENTE

### 4.1. No Momento da Criação

**✅ O que É gerado:**
1. **ID único** - Auto-incrementado pelo SQLite/PostgreSQL
2. **Password hash** - bcrypt com 12 salt rounds
3. **Timestamps** - created_at e updated_at (mesmo valor inicial)
4. **Status ativo** - ativo=1 (pode fazer login imediatamente)
5. **Role default** - "user" (a menos que especificado "admin")

**❌ O que NÃO é gerado:**
- Nenhuma transação (journal_entries vazio)
- Nenhuma meta (budget_planning vazio)
- Nenhum cartão (cartoes vazio)
- Nenhuma marcação personalizada (base_padroes_usuario vazio)
- Nenhum grupo customizado

### 4.2. Bases Compartilhadas (Disponíveis para TODOS)

**Tabelas que TODOS os usuários compartilham:**

1. **`base_marcacoes`** - Grupos e subgrupos globais
   - ✅ 45+ grupos padrão (Alimentação, Transporte, Saúde, etc)
   - ✅ Disponíveis para todos desde o dia 1
   - ✅ Não precisa criar - já existem

2. **`base_grupos_config`** - Configurações de grupos
   - ✅ 60+ tipos de gasto mapeados
   - ✅ Define categoria_geral (Despesa/Receita)
   - ✅ Define se é Essencial/Não Essencial

3. **`base_tipos_gasto`** - Tipos de gasto genéricos
   - ✅ 100+ tipos mapeados
   - ✅ Usados na classificação automática

**⚠️ IMPORTANTE:** Estas bases NÃO têm `user_id` - são globais!

---

## 🎭 5. FLUXO COMPLETO DE ONBOARDING

### Cenário: Usuário "teste2@email.com" se registra

```
┌─────────────────────────────────────────────────┐
│ 1. Admin cria usuário via /settings/admin      │
│    Input: nome, email, senha, role             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 2. POST /api/v1/users                           │
│    - Valida email único                         │
│    - Hash da senha (bcrypt)                     │
│    - Salva em users table                       │
│    - Retorna user_id=5                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 3. Usuário faz login                            │
│    POST /api/v1/auth/login                      │
│    - Recebe JWT token (60min)                   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 4. Primeiro acesso ao dashboard                 │
│    GET /api/v1/dashboard                        │
│    - ⚠️  Nenhuma transação (vazio)              │
│    - ⚠️  Nenhuma meta criada (vazio)            │
│    - ⚠️  Grupos disponíveis (base_marcacoes)    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 5. Criar metas pela primeira vez                │
│    POST /api/v1/budget/planning                 │
│    - Cria 96 metas (8 grupos × 12 meses)        │
│    - Todas com valor 0.00 inicial              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 6. Primeiro upload de extrato                   │
│    POST /api/v1/upload                          │
│    - Classifica com base_generica (73.7%)       │
│    - Gera base_padroes_usuario específico       │
│    - Cria registros em journal_entries          │
└─────────────────────────────────────────────────┘
```

---

## 📊 6. ESTADO DO BANCO APÓS CRIAÇÃO

### Tabelas Afetadas

| Tabela | Registros | Observação |
|--------|-----------|------------|
| `users` | +1 | Novo usuário criado |
| `journal_entries` | 0 | Vazio até primeiro upload |
| `budget_planning` | 0 | Vazio até criar primeira meta |
| `cartoes` | 0 | Vazio até adicionar cartão |
| `base_padroes_usuario` | 0 | Vazio até primeiro upload |
| `base_marcacoes` | ~45 | **Global** - já existe |
| `base_grupos_config` | ~60 | **Global** - já existe |
| `base_tipos_gasto` | ~100 | **Global** - já existe |

### Query de Verificação

```sql
-- Verificar novo usuário
SELECT id, email, nome, role, ativo, created_at 
FROM users 
WHERE email = 'teste2@email.com';

-- Verificar estado vazio
SELECT COUNT(*) as total FROM journal_entries WHERE user_id = 5;  -- 0
SELECT COUNT(*) as total FROM budget_planning WHERE user_id = 5;  -- 0
SELECT COUNT(*) as total FROM cartoes WHERE user_id = 5;          -- 0
```

---

## 🔍 7. VALIDAÇÕES NECESSÁRIAS (FRENTE 5)

### Checklist de Testes

**Criação de Conta:**
- [ ] Email único validado (não permite duplicatas)
- [ ] Senha com min 6 caracteres
- [ ] Password hash gerado (bcrypt)
- [ ] Timestamps created_at e updated_at preenchidos
- [ ] Status ativo=1
- [ ] Role default="user"

**Login:**
- [ ] Consegue fazer login com email/senha
- [ ] Recebe JWT token válido
- [ ] Token expira após 60 minutos
- [ ] Token contém user_id, email, role

**Dashboard Vazio:**
- [ ] journal_entries vazio (0 transações)
- [ ] budget_planning vazio (0 metas)
- [ ] Grupos da base_marcacoes disponíveis
- [ ] Não quebra com dados vazios

**Criar Primeira Meta:**
- [ ] POST /budget/planning funciona
- [ ] Cria 96 registros (8 grupos × 12 meses) ou apenas metas individuais
- [ ] Valores default 0.00
- [ ] Filtrado por user_id corretamente

**Primeiro Upload:**
- [ ] Upload de extrato funciona
- [ ] Classificação genérica aplicada (73.7%)
- [ ] base_padroes_usuario populado automaticamente
- [ ] journal_entries criados com user_id correto
- [ ] Deduplica corretamente (mesmo arquivo não duplica)

---

## 🎯 8. PONTOS DE ATENÇÃO

### ⚠️  Isolamento de Dados

**CRÍTICO:** Sistema DEVE filtrar por `user_id` em TODAS as queries:

```python
# ❌ ERRADO - Vazamento de dados
journal_entries = db.query(JournalEntry).all()

# ✅ CORRETO - Isolado por usuário
journal_entries = db.query(JournalEntry).filter(
    JournalEntry.user_id == user_id
).all()
```

**Endpoints que DEVEM ter isolamento:**
- `GET /transactions/list` ✅ (já implementado)
- `GET /dashboard` ✅ (já implementado)
- `GET /budget/planning` ✅ (já implementado)
- `GET /cards` ✅ (já implementado)
- `GET /upload/history` ✅ (já implementado)

### 🔒 Segurança

**JWT Token:**
- ✅ Expira em 60 minutos
- ✅ Contém user_id (não pode ser adulterado)
- ✅ Validado em TODOS os endpoints protegidos

**Password:**
- ✅ Bcrypt com 12 salt rounds
- ✅ Nunca armazenada em texto plano
- ✅ Não retornada em nenhuma API

**Rate Limiting:**
- ✅ Login: 5 tentativas/minuto
- ✅ Previne brute force

---

## 📚 9. ARQUIVOS RELACIONADOS

### Backend

**Domínio Users:**
- `app/domains/users/models.py` - Modelo User
- `app/domains/users/schemas.py` - Schemas (Create, Update, Response)
- `app/domains/users/service.py` - Lógica de criação
- `app/domains/users/repository.py` - Queries SQL
- `app/domains/users/router.py` - Endpoints HTTP

**Domínio Auth:**
- `app/domains/auth/router.py` - Login/logout
- `app/domains/auth/service.py` - Validação de senha
- `app/domains/auth/jwt_utils.py` - Geração de token
- `app/domains/auth/password_utils.py` - Bcrypt hash

**Shared:**
- `app/shared/dependencies.py` - get_current_user_id()

### Frontend

**Admin:**
- `src/app/settings/admin/page.tsx` - Tela de criação de usuário

**Auth:**
- `src/contexts/AuthContext.tsx` - Context de autenticação
- `src/app/login/page.tsx` - Tela de login

---

## 🔄 10. PRÓXIMOS PASSOS (FRENTE 5)

### Implementar na Frente 5

1. **Criar script de teste automatizado:**
   - Criar usuário teste via API
   - Validar campos gerados
   - Fazer login e obter token
   - Testar dashboard vazio
   - Criar primeira meta
   - Fazer primeiro upload
   - Validar isolamento de dados

2. **Documentar gaps encontrados:**
   - Erros no fluxo de onboarding
   - UX ruins (usuário confuso com dashboard vazio)
   - Melhorias necessárias

3. **Propor melhorias:**
   - Tutorial de primeiro uso?
   - Dados de exemplo?
   - Wizard de onboarding?

---

## 📊 11. COMPARAÇÃO: USUÁRIO NOVO vs USUÁRIO COM DADOS

| Aspecto | Usuário Novo (teste2@email.com) | Usuário Existente (admin@financas.com) |
|---------|----------------------------------|----------------------------------------|
| **journal_entries** | 0 registros | ~2600 registros |
| **budget_planning** | 0 registros | ~96 metas (8×12) |
| **cartoes** | 0 registros | ~3 cartões |
| **base_padroes_usuario** | 0 registros | ~40 padrões aprendidos |
| **Dashboard** | Vazio | Dados ricos |
| **Upload** | Primeira vez (100% base_generica) | Mix (padrões + genérica) |

---

## ✅ RESUMO EXECUTIVO

### O que acontece quando crio um usuário?

**Criação básica:**
- ✅ 1 registro na tabela `users`
- ✅ Password hash bcrypt gerado
- ✅ Timestamps automáticos
- ✅ Status ativo=1
- ✅ Role="user" (ou "admin" se especificado)

**O que NÃO é criado:**
- ❌ Nenhuma transação
- ❌ Nenhuma meta
- ❌ Nenhum cartão
- ❌ Nenhuma marcação personalizada

**Disponível desde o dia 1:**
- ✅ Grupos da base_marcacoes (~45)
- ✅ Tipos de gasto da base_grupos_config (~60)
- ✅ Upload e classificação automática (73.7% cobertura)

**Fluxo ideal:**
1. Criar conta → Login → Dashboard vazio
2. (Opcional) Criar metas para o ano
3. Fazer primeiro upload → Transações classificadas
4. Sistema aprende padrões do usuário

---

**Documentação criada para:** Frente 5 (Teste Usuário Inicial)  
**Data:** 13/02/2026  
**Status:** 📝 Documentação completa pronta para implementação
