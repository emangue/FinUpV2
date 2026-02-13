# 9️⃣ Validação de Navegação

**Frente:** Validação de Navegação  
**Status:** 🔴 Não Iniciado  
**Prioridade:** 🟡 MÉDIA  
**Responsável:** A definir  
**Data Início:** A definir  
**Deadline:** A definir

---

## 🎯 Objetivo

Garantir que todos os botões de navegação (ir e voltar) funcionem corretamente em todas as telas, criando uma experiência fluida para o usuário.

---

## 📋 Escopo

### Incluído
- ✅ Mapeamento de todas as telas e fluxos
- ✅ Teste de navegação tela por tela
- ✅ Correção de botões quebrados
- ✅ Validação de fluxos completos
- ✅ Breadcrumbs (se aplicável)
- ✅ Back button behavior

### Excluído
- ❌ Criação de novas telas
- ❌ Redesign de navegação
- ❌ Mudanças em URLs/rotas (se não necessário)

---

## 🗺️ Fase 1: Mapeamento de Fluxos

### 1.1 Fluxos Principais

**Identificar jornadas do usuário:**

#### Fluxo 1: Login → Dashboard
```
Login (/login)
  ↓
Dashboard (/)
  ├→ Transações (/transactions)
  ├→ Upload (/upload)
  ├→ Metas (/budget)
  └→ Configurações (/settings)
```

#### Fluxo 2: Upload de Arquivo
```
Dashboard (/)
  ↓
Upload (/upload)
  ↓ [seleciona arquivo]
Preview (/upload/preview)
  ↓ [confirma]
Dashboard (/) [com toast de sucesso]
```

#### Fluxo 3: Gerenciar Transações
```
Dashboard (/)
  ↓
Transações (/transactions)
  ↓ [clica em transação]
Modal de Edição
  ↓ [salva]
Transações (/transactions) [atualizada]
```

#### Fluxo 4: Gerenciar Metas
```
Dashboard (/)
  ↓
Metas (/budget)
  ↓ [seleciona mês]
Form de Meta
  ↓ [salva]
Metas (/budget) [atualizada]
```

#### Fluxo 5: Admin (se aplicável)
```
Dashboard (/)
  ↓
Admin (/admin)
  ├→ Usuários (/admin/users)
  │   ↓ [clica em usuário]
  │   Detalhes (/admin/users/[id])
  │     ↓ [voltar]
  │   Usuários (/admin/users)
  └→ Logs (/admin/logs)
```

### 1.2 Mapa de Navegação Completo

```markdown
| De | Para | Botão/Link | Funciona? |
|----|------|------------|-----------|
| Login | Dashboard | Após login | ❓ |
| Dashboard | Transações | Card/Link | ❓ |
| Dashboard | Upload | Botão Upload | ❓ |
| Dashboard | Metas | Card/Link | ❓ |
| Dashboard | Config | Link sidebar | ❓ |
| Upload | Preview | Após processar | ❓ |
| Preview | Dashboard | Confirmar | ❓ |
| Preview | Upload | Cancelar | ❓ |
| Transações | Dashboard | Botão Voltar | ❓ |
| Metas | Dashboard | Botão Voltar | ❓ |
| Admin | Dashboard | Botão Voltar | ❓ |
| Users | User Detail | Clica usuário | ❓ |
| User Detail | Users | Botão Voltar | ❓ |
```

---

## 🧪 Fase 2: Teste de Navegação

### 2.1 Checklist por Tela

#### Dashboard (/)
- [ ] Link para Transações funciona
- [ ] Link para Upload funciona
- [ ] Link para Metas funciona
- [ ] Link para Configurações funciona
- [ ] Link para Admin funciona (se admin)
- [ ] Sidebar navega corretamente
- [ ] Logo volta para dashboard (se em outra tela)

#### Transações (/transactions)
- [ ] Botão Voltar leva para Dashboard
- [ ] Clicar em transação abre modal
- [ ] Fechar modal mantém na tela Transações
- [ ] Filtros não quebram navegação
- [ ] Paginação mantém estado

#### Upload (/upload)
- [ ] Botão Voltar leva para Dashboard
- [ ] Após upload, vai para Preview
- [ ] Preview > Cancelar volta para Upload
- [ ] Preview > Confirmar vai para Dashboard
- [ ] Toast de sucesso aparece no Dashboard

#### Metas (/budget)
- [ ] Botão Voltar leva para Dashboard
- [ ] Selecionar mês não quebra navegação
- [ ] Salvar meta mantém na mesma tela
- [ ] Editar meta funciona corretamente

#### Configurações (/settings)
- [ ] Botão Voltar leva para Dashboard
- [ ] Tabs de configuração navegam corretamente
- [ ] Salvar configuração mantém na tela

#### Admin (/admin)
- [ ] Botão Voltar leva para Dashboard
- [ ] Link para Usuários funciona
- [ ] Link para Logs funciona
- [ ] Detalhes de usuário abre corretamente
- [ ] Voltar de detalhes leva para lista

### 2.2 Script de Teste Automático (Playwright/Cypress)

```typescript
// e2e/navigation.spec.ts
describe('Navegação Completa', () => {
  beforeEach(() => {
    cy.login('user@test.com', 'password')
  })
  
  it('Dashboard → Transações → Dashboard', () => {
    cy.visit('/')
    cy.contains('Transações').click()
    cy.url().should('include', '/transactions')
    cy.contains('Voltar').click()
    cy.url().should('eq', Cypress.config().baseUrl + '/')
  })
  
  it('Dashboard → Upload → Preview → Dashboard', () => {
    cy.visit('/')
    cy.contains('Upload').click()
    cy.url().should('include', '/upload')
    
    // Fazer upload
    cy.get('input[type="file"]').attachFile('test-file.pdf')
    cy.contains('Processar').click()
    cy.url().should('include', '/upload/preview')
    
    // Confirmar
    cy.contains('Confirmar').click()
    cy.url().should('eq', Cypress.config().baseUrl + '/')
    cy.contains('Upload realizado com sucesso').should('be.visible')
  })
  
  it('Dashboard → Metas → Editar → Metas', () => {
    cy.visit('/')
    cy.contains('Metas').click()
    cy.url().should('include', '/budget')
    
    // Selecionar mês e grupo
    cy.get('[data-testid="month-select"]').select('Janeiro')
    cy.get('[data-testid="group-select"]').select('Alimentação')
    cy.get('[data-testid="value-input"]').type('1000')
    cy.contains('Salvar').click()
    
    // Deve permanecer em /budget
    cy.url().should('include', '/budget')
    cy.contains('Meta salva com sucesso').should('be.visible')
  })
  
  // ... mais testes
})
```

---

## 🔧 Fase 3: Correção de Problemas

### 3.1 Problemas Comuns

#### Problema 1: Botão Voltar Não Funciona
**Causa:** `onClick` não implementado ou `router.back()` não funciona

**Solução:**
```typescript
// ❌ ERRADO
<Button onClick={() => {}}>Voltar</Button>

// ✅ CORRETO
import { useRouter } from 'next/navigation'

function MyComponent() {
  const router = useRouter()
  
  return (
    <Button onClick={() => router.back()}>Voltar</Button>
  )
}

// ✅ OU rota específica
<Button onClick={() => router.push('/dashboard')}>Voltar</Button>
```

#### Problema 2: Link Quebrado (404)
**Causa:** Rota não existe ou path incorreto

**Solução:**
```typescript
// Verificar que rota existe
// src/app/transactions/page.tsx deve existir para /transactions

// ❌ ERRADO
<Link href="/transaction">Transações</Link>  // Falta 's'

// ✅ CORRETO
<Link href="/transactions">Transações</Link>
```

#### Problema 3: Estado Perdido Após Navegação
**Causa:** Não usar query params ou state management

**Solução:**
```typescript
// Preservar filtros na URL
const router = useRouter()
const searchParams = useSearchParams()

const handleFilter = (filter: string) => {
  const params = new URLSearchParams(searchParams)
  params.set('filter', filter)
  router.push(`/transactions?${params.toString()}`)
}
```

#### Problema 4: Modal Não Fecha Corretamente
**Causa:** State não atualizado ou navegação durante modal

**Solução:**
```typescript
// ✅ CORRETO - Fechar modal antes de navegar
const handleSave = async () => {
  await saveData()
  setModalOpen(false)  // Fechar modal primeiro
  router.refresh()     // Atualizar dados
}
```

### 3.2 Padrões de Correção

**Padrão 1: Botão Voltar Consistente**
```typescript
// src/components/back-button.tsx
export function BackButton({ 
  href, 
  fallback = '/' 
}: { 
  href?: string
  fallback?: string 
}) {
  const router = useRouter()
  
  const handleBack = () => {
    if (href) {
      router.push(href)
    } else if (window.history.length > 1) {
      router.back()
    } else {
      router.push(fallback)
    }
  }
  
  return (
    <Button variant="ghost" onClick={handleBack}>
      <ArrowLeft className="mr-2 h-4 w-4" />
      Voltar
    </Button>
  )
}
```

**Padrão 2: Navegação com Toast**
```typescript
// src/lib/utils/navigation.ts
export function navigateWithToast(
  router: Router,
  path: string,
  message: string
) {
  router.push(path)
  toast.success(message)
}

// Uso
navigateWithToast(router, '/dashboard', 'Upload concluído!')
```

---

## ✅ Fase 4: Validação Final

### 4.1 Teste Manual Completo

**Executar jornada completa do usuário:**
```markdown
1. [ ] Login
2. [ ] Dashboard carrega
3. [ ] Navegar para cada tela e voltar
4. [ ] Testar fluxos completos (upload, criar meta, etc)
5. [ ] Testar navegação via sidebar
6. [ ] Testar navegação via botões
7. [ ] Testar navegação via links
8. [ ] Testar browser back button
9. [ ] Testar browser forward button
10. [ ] Verificar que nenhuma navegação quebra
```

### 4.2 Matriz de Navegação

```markdown
| Origem | Destino | Método | Status |
|--------|---------|--------|--------|
| / | /transactions | Link | ✅ |
| / | /upload | Button | ✅ |
| / | /budget | Link | ✅ |
| /transactions | / | BackButton | ✅ |
| /upload | /upload/preview | Auto | ✅ |
| /upload/preview | / | Confirm | ✅ |
| /upload/preview | /upload | Cancel | ✅ |
| /budget | / | BackButton | ✅ |
| /admin | / | BackButton | ✅ |
| /admin/users | /admin/users/[id] | Click | ✅ |
| /admin/users/[id] | /admin/users | BackButton | ✅ |
```

### 4.3 Checklist Geral

- [ ] Todas as telas têm botão voltar (quando aplicável)
- [ ] Botão voltar sempre funciona
- [ ] Links não levam para 404
- [ ] Navegação preserva estado (quando necessário)
- [ ] Modais fecham corretamente
- [ ] Toasts aparecem após ações
- [ ] Browser back/forward funcionam
- [ ] Sidebar navega corretamente
- [ ] Logo volta para dashboard
- [ ] Logout funciona e limpa estado

---

## 📊 Métricas

### Progresso
```
Mapeamento:   ░░░░░░░░░░ 0%
Teste:        ░░░░░░░░░░ 0%
Correção:     ░░░░░░░░░░ 0%
Validação:    ░░░░░░░░░░ 0%
TOTAL:        ░░░░░░░░░░ 0%
```

### Navegações Testadas
```
Total de rotas:      X
Funcionando:         0
Quebradas:           0
Não testadas:        X
Taxa de sucesso:     0%
```

---

## 🚧 Riscos

1. **Médio:** Navegação quebra após correções
2. **Médio:** Estado perdido em navegações
3. **Baixo:** Usuário fica "preso" em alguma tela

### Mitigações
1. Testar após cada correção
2. Usar query params ou state management
3. Sempre ter botão voltar ou link para dashboard

---

## 📝 Próximos Passos

1. [ ] Mapear todas as telas e fluxos
2. [ ] Criar matriz de navegação
3. [ ] Testar cada navegação manualmente
4. [ ] Identificar navegações quebradas
5. [ ] Corrigir uma por uma
6. [ ] Re-testar navegações corrigidas
7. [ ] Executar validação final completa

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [07_TELAS_NAO_MOBILE.md](./07_TELAS_NAO_MOBILE.md) (relacionado)
- [08_TELAS_ADMIN_MOBILE.md](./08_TELAS_ADMIN_MOBILE.md) (relacionado)

---

**Última Atualização:** 10/02/2026
