# 8️⃣ Telas Admin Mobile

**Frente:** Telas Admin Mobile  
**Status:** 🔴 Não Iniciado  
**Prioridade:** 🟡 MÉDIA  
**Responsável:** A definir  
**Data Início:** A definir  
**Deadline:** A definir

---

## 🎯 Objetivo

Criar caminho/telas mobile para a área administrativa do sistema, permitindo que administradores acessem funcionalidades essenciais via smartphone.

---

## 📋 Escopo

### Incluído
- ✅ Mapeamento de funcionalidades admin necessárias
- ✅ Design mobile das telas admin
- ✅ Implementação das telas mobile
- ✅ Proteção por role (admin only)
- ✅ Navegação específica para admin
- ✅ Validação de funcionalidades

### Excluído
- ❌ Telas desktop admin (já existem)
- ❌ Funcionalidades não-essenciais em mobile
- ❌ Relatórios complexos (desktop only)

---

## 🔍 Fase 1: Mapeamento de Funcionalidades

### 1.1 Funcionalidades Admin Atuais (Desktop)

**Identificar o que já existe:**
```bash
# Buscar rotas admin no backend
grep -r "@router" app_dev/backend/app/domains/admin --include="*.py"

# Buscar telas admin no frontend
find app_dev/frontend/src/app/admin -name "*.tsx"
```

### 1.2 Funcionalidades Essenciais para Mobile

**Priorização (P0 = crítica, P3 = nice-to-have):**

| Funcionalidade | Prioridade | Mobile? | Justificativa |
|----------------|------------|---------|---------------|
| Visualizar usuários | P0 | ✅ Sim | Ver status/dados básicos |
| Ativar/desativar usuário | P0 | ✅ Sim | Ação rápida crítica |
| Ver transações de todos | P1 | ✅ Sim | Monitoramento |
| Dashboard global | P1 | ✅ Sim | Visão geral do sistema |
| Logs de sistema | P2 | ⚠️ Simplificado | Ver últimas ações |
| Configurações globais | P2 | ✅ Sim | Ajustes rápidos |
| Relatórios complexos | P3 | ❌ Não | Desktop only |
| Backup manual | P3 | ❌ Não | Desktop only |

### 1.3 Decisões de Features

**Features Mobile (implementar):**
1. ✅ Lista de usuários
2. ✅ Detalhes de usuário
3. ✅ Ativar/desativar usuário
4. ✅ Dashboard admin (métricas globais)
5. ✅ Logs recentes (últimas 50)
6. ✅ Configurações básicas

**Features Desktop Only (não implementar):**
1. ❌ Relatórios complexos com filtros avançados
2. ❌ Backup/restore manual
3. ❌ Edição de schema/migrações
4. ❌ Análise de performance detalhada

---

## 🎨 Fase 2: Design Mobile

### 2.1 Estrutura de Navegação

```
Admin Mobile
├── Dashboard Admin (home)
│   ├── Total de Usuários
│   ├── Usuários Ativos
│   ├── Transações Hoje
│   └── Últimas Ações
│
├── Usuários
│   ├── Lista de Usuários
│   │   ├── Filtro (ativo/inativo)
│   │   └── Busca por email
│   │
│   └── Detalhes do Usuário
│       ├── Informações básicas
│       ├── Status (ativo/inativo)
│       ├── Toggle ativar/desativar
│       └── Última atividade
│
├── Logs
│   └── Últimas 50 Ações
│       ├── Timestamp
│       ├── Usuário
│       └── Ação
│
└── Configurações
    └── Config globais (readonly)
```

### 2.2 Wireframes

#### Dashboard Admin
```
┌─────────────────────────┐
│ ⚙️ Admin Dashboard      │
├─────────────────────────┤
│                         │
│ 👥 Total Usuários       │
│    [  50  ]             │
│                         │
│ ✅ Usuários Ativos      │
│    [  47  ]             │
│                         │
│ 💰 Transações Hoje      │
│    [  1,234  ]          │
│                         │
│ 📊 Últimas Ações        │
│  • User X fez login     │
│  • User Y fez upload    │
│  • User Z criou meta    │
│                         │
└─────────────────────────┘
```

#### Lista de Usuários
```
┌─────────────────────────┐
│ 👥 Usuários             │
├─────────────────────────┤
│ 🔍 [Buscar...]          │
│ [ Todos ▼ ]             │
├─────────────────────────┤
│ user1@email.com     ✅  │
│ ID: 1  |  Ativo         │
├─────────────────────────┤
│ user2@email.com     ❌  │
│ ID: 2  |  Inativo       │
├─────────────────────────┤
│ user3@email.com     ✅  │
│ ID: 3  |  Ativo         │
└─────────────────────────┘
```

#### Detalhes do Usuário
```
┌─────────────────────────┐
│ ← Voltar                │
├─────────────────────────┤
│ 👤 user1@email.com      │
│                         │
│ ID: 1                   │
│ Role: user              │
│ Criado: 01/01/2026      │
│ Último login: 10/02/2026│
│                         │
│ Status: ✅ Ativo        │
│ [ Desativar Usuário ]   │
│                         │
│ 📊 Estatísticas:        │
│ • Transações: 1,234     │
│ • Uploads: 12           │
│ • Metas: 8              │
│                         │
└─────────────────────────┘
```

---

## 🛠️ Fase 3: Implementação

### 3.1 Backend - Proteção Admin

**Verificar que rotas admin estão protegidas:**
```python
# app/shared/dependencies.py
def require_admin(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """
    Verifica que usuário é admin
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user or user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Requer permissão de administrador."
        )
    return user

# app/domains/admin/router.py
@router.get("/users")
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os usuários (admin only)"""
    users = db.query(User).all()
    return users
```

### 3.2 Backend - APIs Necessárias

```python
# app/domains/admin/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def admin_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Dashboard com métricas globais"""
    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter_by(is_active=True).count(),
        "transactions_today": db.query(JournalEntry).filter(
            func.date(JournalEntry.created_at) == date.today()
        ).count(),
        "last_actions": get_last_actions(db, limit=10)
    }

@router.get("/users")
def list_users(
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lista usuários com filtros"""
    query = db.query(User)
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    if search:
        query = query.filter(User.email.ilike(f'%{search}%'))
    
    return query.all()

@router.get("/users/{user_id}")
def get_user_details(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Detalhes de um usuário específico"""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {
        "user": user,
        "stats": {
            "transactions": db.query(JournalEntry).filter_by(user_id=user_id).count(),
            "uploads": db.query(UploadHistory).filter_by(user_id=user_id).count(),
            "metas": db.query(BudgetGeral).filter_by(user_id=user_id).count()
        }
    }

@router.patch("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    status: bool,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Ativa/desativa usuário"""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.is_active = status
    db.commit()
    
    return {"message": f"Usuário {'ativado' if status else 'desativado'} com sucesso"}

@router.get("/logs")
def get_logs(
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Últimas ações do sistema"""
    return get_last_actions(db, limit=limit)
```

### 3.3 Frontend - Estrutura

```bash
# Criar estrutura de features admin
mkdir -p app_dev/frontend/src/features/admin
mkdir -p app_dev/frontend/src/features/admin/components
mkdir -p app_dev/frontend/src/features/admin/hooks
mkdir -p app_dev/frontend/src/features/admin/services
```

### 3.4 Frontend - Componentes Mobile

#### Dashboard Admin
```typescript
// src/features/admin/components/admin-dashboard-mobile.tsx
export function AdminDashboardMobile() {
  const { data, isLoading } = useAdminDashboard()
  
  if (isLoading) return <LoadingSkeleton />
  
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>👥 Total Usuários</CardHeader>
          <CardContent className="text-3xl font-bold">
            {data.total_users}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>✅ Ativos</CardHeader>
          <CardContent className="text-3xl font-bold text-green-600">
            {data.active_users}
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>💰 Transações Hoje</CardHeader>
        <CardContent className="text-3xl font-bold">
          {data.transactions_today}
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>📊 Últimas Ações</CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {data.last_actions.map(action => (
              <li key={action.id} className="text-sm">
                • {action.description}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
```

#### Lista de Usuários
```typescript
// src/features/admin/components/users-list-mobile.tsx
export function UsersListMobile() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<'all' | 'active' | 'inactive'>('all')
  const { data: users } = useAdminUsers({ search, status })
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Usuários</h1>
      
      <Input
        placeholder="Buscar por email..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-4"
      />
      
      <Select value={status} onValueChange={setStatus}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Todos</SelectItem>
          <SelectItem value="active">Ativos</SelectItem>
          <SelectItem value="inactive">Inativos</SelectItem>
        </SelectContent>
      </Select>
      
      <div className="mt-4 space-y-2">
        {users?.map(user => (
          <Card key={user.id} onClick={() => navigateToUser(user.id)}>
            <CardContent className="flex justify-between items-center p-4">
              <div>
                <div className="font-semibold">{user.email}</div>
                <div className="text-sm text-muted-foreground">
                  ID: {user.id} | {user.is_active ? 'Ativo' : 'Inativo'}
                </div>
              </div>
              <div>
                {user.is_active ? '✅' : '❌'}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

#### Detalhes do Usuário
```typescript
// src/features/admin/components/user-details-mobile.tsx
export function UserDetailsMobile({ userId }: { userId: number }) {
  const { data: user } = useAdminUserDetails(userId)
  const toggleStatus = useToggleUserStatus()
  
  const handleToggleStatus = async () => {
    await toggleStatus.mutateAsync({
      userId,
      status: !user.is_active
    })
  }
  
  return (
    <div className="p-4">
      <Button variant="ghost" onClick={goBack}>
        ← Voltar
      </Button>
      
      <div className="mt-4 space-y-4">
        <h1 className="text-2xl font-bold">{user.email}</h1>
        
        <Card>
          <CardContent className="p-4 space-y-2">
            <div><strong>ID:</strong> {user.id}</div>
            <div><strong>Role:</strong> {user.role}</div>
            <div><strong>Criado:</strong> {formatDate(user.created_at)}</div>
            <div><strong>Último login:</strong> {formatDate(user.last_login)}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>Status</CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span>{user.is_active ? '✅ Ativo' : '❌ Inativo'}</span>
              <Button
                variant="destructive"
                onClick={handleToggleStatus}
              >
                {user.is_active ? 'Desativar' : 'Ativar'}
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>Estatísticas</CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li>• Transações: {user.stats.transactions}</li>
              <li>• Uploads: {user.stats.uploads}</li>
              <li>• Metas: {user.stats.metas}</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

### 3.5 Navegação Admin

```typescript
// src/components/admin-nav.tsx
export function AdminNav() {
  const isAdmin = useIsAdmin()
  
  if (!isAdmin) return null
  
  return (
    <nav className="admin-nav">
      <NavLink href="/admin">Dashboard</NavLink>
      <NavLink href="/admin/users">Usuários</NavLink>
      <NavLink href="/admin/logs">Logs</NavLink>
      <NavLink href="/admin/settings">Configurações</NavLink>
    </nav>
  )
}
```

---

## ✅ Checklist de Implementação

### Backend
- [ ] Dependency `require_admin` implementada
- [ ] API `/admin/dashboard` funcionando
- [ ] API `/admin/users` com filtros funcionando
- [ ] API `/admin/users/{id}` com detalhes funcionando
- [ ] API `/admin/users/{id}/status` funcionando
- [ ] API `/admin/logs` funcionando
- [ ] Todas as rotas protegidas (admin only)

### Frontend
- [ ] Feature `/features/admin` criada
- [ ] Componente `AdminDashboardMobile` funcionando
- [ ] Componente `UsersListMobile` funcionando
- [ ] Componente `UserDetailsMobile` funcionando
- [ ] Hooks `useAdminDashboard`, `useAdminUsers` funcionando
- [ ] Navegação admin integrada
- [ ] Proteção de rotas (redirect se não admin)

### Validação
- [ ] Login como admin funciona
- [ ] Login como user comum não vê admin
- [ ] Dashboard carrega métricas corretas
- [ ] Lista de usuários funciona com filtros
- [ ] Detalhes de usuário carregam corretamente
- [ ] Toggle ativar/desativar funciona
- [ ] Logs carregam corretamente
- [ ] Navegação mobile funciona perfeitamente

---

## 📊 Métricas

### Progresso
```
Backend APIs:     ░░░░░░░░░░ 0%
Frontend Mobile:  ░░░░░░░░░░ 0%
Integração:       ░░░░░░░░░░ 0%
Validação:        ░░░░░░░░░░ 0%
TOTAL:            ░░░░░░░░░░ 0%
```

---

## 🚧 Riscos

1. **Alto:** Expor dados sensíveis de usuários
2. **Médio:** Permitir acesso admin para não-admin
3. **Baixo:** Mobile não ter todas as funcionalidades necessárias

### Mitigações
1. Não retornar senhas/secrets em APIs
2. Validação de role em todas as rotas
3. Priorizar funcionalidades essenciais

---

## 📝 Próximos Passos

1. [ ] Implementar APIs backend
2. [ ] Criar componentes mobile
3. [ ] Integrar navegação
4. [ ] Testar como admin
5. [ ] Testar como usuário comum (não deve ver)
6. [ ] Validar funcionalidades críticas

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [07_TELAS_NAO_MOBILE.md](./07_TELAS_NAO_MOBILE.md) (relacionado)

---

**Última Atualização:** 10/02/2026
