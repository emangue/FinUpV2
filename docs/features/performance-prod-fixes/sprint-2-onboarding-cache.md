# Sprint 2 — Onboarding Cache: Eliminar Fetches Desnecessários em Toda Navegação

> **Esforço total:** ~30 minutos  
> **Item:** P1  
> **Pré-requisito:** Nenhum (independente do Sprint 1)  
> **Impacto:** Dashboard: 7s → ~2s | Bottom nav: 6–8s → ~1.5s

---

## 🔗 Rastreamento de Erros — Do Sintoma ao Fix

> P1 é o maior ganho de performance isolado do projeto: **3–4 fetches completamente desnecessários** em toda navegação para 99% dos usuários ativos.

### P1 — Fetches Redundantes de `/onboarding/progress`

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Dashboard demora ~7s. Aba Network mostra 3–4 chamadas para `/api/v1/onboarding/progress` em cada página carregada. |
| **Medido com `perf_measure.py`** | Capturado em produção: |

```
t=459ms  OnboardingGuard  → 696ms   (layout — dispara em toda troca de rota)
t=597ms  NudgeBanners     → 1575ms  (página dashboard — no mount)
t=597ms  DemoModeBanner   → 3561ms  (página dashboard — no mount)
t=597ms  OnboardingGuard  → 4165ms  (4ª call — Next.js re-monta o layout)
Delay acumulado:           ~5.8–6.5s apenas para onboarding checks
```

| Dimensão | Detalhe |
|---|---|
| **Arquivos exatos** | `OnboardingGuard.tsx` linhas **18–35** · `NudgeBanners.tsx` linhas **24–30** · `DemoModeBanner.tsx` linhas **8–14** |
| **Causa raiz — OnboardingGuard** | Não persiste quando `onboarding_completo = true`. Na próxima rota, repete o fetch do zero. |
| **Causa raiz — NudgeBanners** | Não verifica `nudge_dismissed_*` no localStorage **antes** de fazer o fetch. Busca a API mesmo quando todos os nudges já foram dispensados. |
| **Causa raiz — DemoModeBanner** | Usa `fetch()` simples (sem guard, sem cache). Busca mesmo quando usuário confirmadamente não tem dados demo. |
| **Para 99% dos usuários ativos** | `onboarding_completo = true` · todos nudges dispensados · `tem_demo = false`. **O resultado seria idêntico sem qualquer fetch.** |
| **O fix** | 3 camadas de cache independentes: `localStorage` para onboarding completo (permanente), `localStorage` para nudges dispensados, `sessionStorage` para ausência de demo (por segurança entre contas). |

---

## Contexto — Por Que 3 Componentes Chamam a Mesma API

```
Layout (/mobile/layout.tsx)
  └── OnboardingGuard        → fetch /api/v1/onboarding/progress  (a cada rota)

Dashboard (/mobile/dashboard/page.tsx)
  ├── NudgeBanners           → fetch /api/v1/onboarding/progress  (no mount)
  └── DemoModeBanner         → fetch /api/v1/onboarding/progress  (no mount)
```

**Medido em produção (Playwright):**
```
t=459ms  OnboardingGuard   → 696ms  (layout, monta em toda rota)
t=597ms  NudgeBanners      → 1575ms (página dashboard)
t=597ms  DemoModeBanner    → 3561ms (página dashboard)
t=597ms  OnboardingGuard   → 4165ms (4ª chamada — Next.js re-monta o layout)
```

**Para um usuário com onboarding completo** (99% dos usuários ativos), os 3 componentes recebem a resposta, constatam que não há nada para mostrar, e renderizam vazio. **O fetch inteiro é desperdiçado.**

---

## Estratégia: 3 Camadas de Cache Independentes

Cada componente recebe um cache diferente porque cada um tem uma lógica específica:

| Componente | Cache | Tipo | Quando invalida |
|------------|-------|------|-----------------|
| `OnboardingGuard` | `onboarding_completo = true` | `localStorage` | Nunca (onboarding completo é permanente) |
| `NudgeBanners` | `nudge_dismissed_{tipo}` | `localStorage` | Usuário dispensa manualmente |
| `DemoModeBanner` | `sem_demo = true` | `sessionStorage` | Ao sair da sessão (segurança) |

**Resultado para usuário com tudo completo:** 0 fetches de onboarding em toda navegação (era 3–4×/tela).

---

## Índice

- [Camada 1 — OnboardingGuard](#camada-1--onboardingguard-10-minutos)
- [Camada 2 — NudgeBanners](#camada-2--nudgebanners-10-minutos)
- [Camada 3 — DemoModeBanner](#camada-3--demodemodebanner-10-minutos)
- [Checklist e Validação](#checklist-final-sprint-2)

---

## Camada 1 — `OnboardingGuard` (10 minutos)

**Arquivo:** `app_dev/frontend/src/features/onboarding/OnboardingGuard.tsx`

### Contexto do componente

O `OnboardingGuard` roda no layout (toda troca de rota). Ele já tem lógica para `onboarding_pulado`:

```typescript
// Código existente (resumido):
const pulado = localStorage.getItem('onboarding_pulado') === 'true';
if (pulado) { setChecking(false); return; }  // ← pula fetch quando pulado

// Se não pulado: faz fetch e redireciona para onboarding se não completo
fetchWithAuth(`/api/v1/onboarding/progress`)
  .then((data) => {
    if (data?.onboarding_completo) {
      setChecking(false);  // ← mostra conteúdo
    } else {
      router.replace('/mobile/onboarding/welcome');
    }
  })
```

**Problema:** quando `onboarding_completo` é `true`, o resultado **não é persistido**. Na próxima rota, repete o fetch do zero.

### Microação 1 — Adicionar constante de chave

```typescript
// No topo do componente, junto com ONBOARDING_PULADO_KEY:
const ONBOARDING_PULADO_KEY = 'onboarding_pulado'
const ONBOARDING_COMPLETO_KEY = 'onboarding_completo'  // ← ADICIONAR
```

### Microação 2 — Checar cache antes do fetch

```typescript
// ANTES (verificação existente):
const pulado = localStorage.getItem(ONBOARDING_PULADO_KEY) === 'true'
if (pulado) { setChecking(false); return; }
// → faz fetch

// DEPOIS — checar também se onboarding_completo já foi cacheado:
const pulado = localStorage.getItem(ONBOARDING_PULADO_KEY) === 'true'
const completo = localStorage.getItem(ONBOARDING_COMPLETO_KEY) === 'true'  // ← ADICIONAR
if (pulado || completo) { setChecking(false); return; }  // ← sem fetch
// → faz fetch (apenas para usuários que ainda não completaram)
```

### Microação 3 — Persistir resultado quando completo

```typescript
// ANTES — quando API retorna onboarding_completo:
.then((data) => {
  if (data?.onboarding_completo) {
    setChecking(false);
    return;
  }
  router.replace('/mobile/onboarding/welcome');
})

// DEPOIS — persistir antes de setar checking:
.then((data) => {
  if (data?.onboarding_completo) {
    localStorage.setItem(ONBOARDING_COMPLETO_KEY, 'true');  // ← ADICIONAR
    setChecking(false);
    return;
  }
  router.replace('/mobile/onboarding/welcome');
})
```

### Código completo após fix (diff)

```typescript
// features/onboarding/OnboardingGuard.tsx

// +const ONBOARDING_COMPLETO_KEY = 'onboarding_completo'

useEffect(() => {
  const pulado = localStorage.getItem(ONBOARDING_PULADO_KEY) === 'true'
+ const completo = localStorage.getItem(ONBOARDING_COMPLETO_KEY) === 'true'
+ if (pulado || completo) { setChecking(false); return; }
- if (pulado) { setChecking(false); return; }

  fetchWithAuth(`${apiUrl}/api/v1/onboarding/progress`)
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (data?.onboarding_completo) {
+       localStorage.setItem(ONBOARDING_COMPLETO_KEY, 'true')
        setChecking(false)
        return
      }
      router.replace('/mobile/onboarding/welcome')
    })
    .catch(() => setChecking(false))
}, [router])
```

**Linhas modificadas:** +3 linhas, -1 linha. Total: ~4 linhas.

---

## Camada 2 — `NudgeBanners` (10 minutos)

**Arquivo:** `app_dev/frontend/src/features/onboarding/NudgeBanners.tsx`

### Contexto do componente

`NudgeBanners` chama `/onboarding/progress` para decidir quais banners exibir (ex: "você ainda não tem um plano", "faz 30 dias sem upload"). Cada nudge pode ser dispensado pelo usuário com um botão "×".

Quando todos os nudges foram dispensados (ou nunca foram necessários), o componente faz fetch mas renderiza nada.

### Microação 1 — Definir tipos de nudge

```typescript
// Já devem existir como const no componente, ou adicionar:
const NUDGE_TYPES = ['sem_upload', 'sem_plano', 'sem_investimento', 'upload_30_dias'] as const
type NudgeType = typeof NUDGE_TYPES[number]
```

### Microação 2 — Checar se todos os nudges foram dispensados antes do fetch

```typescript
// ANTES (useEffect atual):
useEffect(() => {
  fetchWithAuth(`${apiUrl}/api/v1/onboarding/progress`)
    .then((r) => (r.ok ? r.json() : null))
    .then(setProgress)
    .catch(() => setProgress(null))
}, [])

// DEPOIS — skip fetch se todos foram dispensados:
useEffect(() => {
  // Se todos os tipos de nudge foram dispensados pelo usuário, não buscar
  const todosDispensados = NUDGE_TYPES.every(
    (tipo) => localStorage.getItem(`nudge_dismissed_${tipo}`) === 'true'
  )
  if (todosDispensados) return  // ← zero fetch, zero render

  fetchWithAuth(`${apiUrl}/api/v1/onboarding/progress`)
    .then((r) => (r.ok ? r.json() : null))
    .then(setProgress)
    .catch(() => setProgress(null))
}, [])
```

### Microação 3 — Persistir dispensa no handler existente

> **✅ Já implementado!** Ao ler o código real de `NudgeBanners.tsx`, o handler `handleClose` **já salva** no localStorage:

```typescript
// Código já existente em NudgeBanners.tsx (handler já implementado corretamente):
const NUDGE_PREFIX = 'nudge_dismissed_'

const handleClose = (tipo: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(`${NUDGE_PREFIX}${tipo}`, 'true')  // ← JÁ EXISTE
  }
  setVisible(null)
}
```

**Apenas a Microação 2 (guard antes do fetch) é necessária para `NudgeBanners`.** O dismiss já é persistido corretamente.

### Microação 4 — Limpar cache de nudges após upload bem-sucedido

Quando um arquivo é enviado com sucesso, o nudge `sem_upload` deve aparecer novamente na sessão seguinte (o usuário pode ter ficado dias sem fazer upload novamente). Adicionar invalidação na função de upload:

```typescript
// Em qualquer handler de sucesso de upload (features/upload/ ou similar):
// Após upload bem-sucedido:
localStorage.removeItem('nudge_dismissed_sem_upload')
localStorage.removeItem('nudge_dismissed_upload_30_dias')
```

> **Localização:** Buscar por `toast.success` ou `onUploadSuccess` em `features/upload/`.

### Checklist Camada 2

- [ ] Constante `NUDGE_TYPES` definida com todos os tipos
- [ ] `useEffect` verifica `todosDispensados` antes do fetch
- [ ] Handler de dismiss persiste no localStorage
- [ ] Após upload bem-sucedido, nudges de upload são invalidados

---

## Camada 3 — `DemoModeBanner` (10 minutos)

**Arquivo:** `app_dev/frontend/src/features/onboarding/DemoModeBanner.tsx`

### Contexto do componente

`DemoModeBanner` chama `/onboarding/progress` para verificar se o usuário está em modo demo (`tem_demo: true`). Se não estiver em modo demo, renderiza nada — mas faz o fetch de qualquer forma.

Diferente do `localStorage` (persistente entre sessões), usa-se `sessionStorage` aqui: se o usuário sair e entrar novamente com outra conta que tenha dados demo, queremos verificar de novo.

### Microação 1 — Checar sessionStorage antes do fetch

```typescript
// ANTES (useEffect atual):
useEffect(() => {
  fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
    .then((r) => (r.ok ? r.json() : null))
    .then(setData)
    .catch(() => setData(null))
}, [])

// DEPOIS — skip fetch se confirmado que não há demo nesta sessão:
useEffect(() => {
  // Se já confirmamos nesta sessão que o usuário não tem dados demo, pular o fetch
  if (sessionStorage.getItem('sem_demo') === 'true') return  // ← zero fetch

  fetch(`${apiUrl}/api/v1/onboarding/progress`, { credentials: 'include' })
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => {
      if (d && !d.tem_demo) {
        sessionStorage.setItem('sem_demo', 'true')  // ← cachear ausência de demo
      }
      setData(d)
    })
    .catch(() => setData(null))
}, [])
```

### Por que `sessionStorage` e não `localStorage`?

| Critério | `localStorage` | `sessionStorage` |
|----------|----------------|------------------|
| Persiste após fechar aba | ✅ Sim | ❌ Não |
| Persiste entre sessões | ✅ Sim | ❌ Não |
| Isolado por aba | ❌ Não | ✅ Sim |

**Motivo de usar `sessionStorage` aqui:** se o usuário fizer logout e login com outra conta que tenha dados demo na mesma sessão do browser, queremos mostrar o banner. Com `localStorage`, o `sem_demo = true` da primeira conta infectaria a segunda conta. O `sessionStorage` é limpo quando a aba fecha — nova sessão, nova verificação.

### Microação 2 — Limpar `sem_demo` ao fazer logout

```typescript
// Em qualquer handler de logout (features/auth/ ou similar):
// Após logout:
sessionStorage.removeItem('sem_demo')
// (ou: sessionStorage.clear() se for o único item crítico)
```

> **Localização:** Buscar por `router.push('/login')` ou `logout()` no código de autenticação.

### Checklist Camada 3

- [ ] `useEffect` verifica `sessionStorage.getItem('sem_demo')` antes do fetch
- [ ] Quando `!d.tem_demo`, persiste `sem_demo = true` no `sessionStorage`
- [ ] Handler de logout limpa `sem_demo` do `sessionStorage`
- [ ] Trocar de conta na mesma sessão ainda mostra o banner se nova conta tiver demo

---

## Análise de Edge Cases

### E1 — Usuário completa o onboarding durante a sessão

**Cenário:** usuário entrou sem dados, completou o setup wizard, agora tem dados reais.  
**Impacto:** `OnboardingGuard` não verifica de novo (cache diz `completo = true`).  
**Resultado esperado:** nenhum problema — o usuário JÁ está na tela correta.  
**Ação necessária:** nenhuma.

### E2 — Usuário precisa ver um novo nudge após voltar a usar o app

**Cenário:** usuário não faz upload há 30 dias. O nudge `upload_30_dias` deveria aparecer, mas o dismiss antigo está no localStorage.  
**Solução:** O dismiss de nudge não deve ser permanente para nudges baseados em tempo. Adicionar TTL:

```typescript
// Em vez de: localStorage.setItem(`nudge_dismissed_${tipo}`, 'true')
// Usar:
const NUDGE_DISMISS_TTL_DAYS = 7  // mostrar de novo em 7 dias
localStorage.setItem(
  `nudge_dismissed_${tipo}`,
  JSON.stringify({ dismissed: true, at: Date.now() })
)

// Na verificação:
const raw = localStorage.getItem(`nudge_dismissed_${tipo}`)
if (raw) {
  const { dismissed, at } = JSON.parse(raw)
  const expirado = Date.now() - at > NUDGE_DISMISS_TTL_DAYS * 24 * 60 * 60 * 1000
  if (dismissed && !expirado) return true  // ainda dispensado
  localStorage.removeItem(`nudge_dismissed_${tipo}`)  // limpeza automática
}
return false
```

> **Prioridade:** esta melhoria é opcional para o Sprint 2. Implementar se o nudge de `upload_30_dias` for crítico para o produto.

### E3 — Dados corrompidos no localStorage

**Cenário:** localStorage corrompido por extensão de browser ou erro.  
**Solução:** já coberto pelo `.catch(() => setChecking(false))` — se o fetch falhar, o guard libera a passagem.

---

## Checklist Final Sprint 2

### Implementação
- [ ] `OnboardingGuard.tsx`: `ONBOARDING_COMPLETO_KEY` definida
- [ ] `OnboardingGuard.tsx`: guard antes do fetch com `completo` check
- [ ] `OnboardingGuard.tsx`: `localStorage.setItem` após API retornar completo
- [ ] `NudgeBanners.tsx`: `NUDGE_TYPES` definida
- [ ] `NudgeBanners.tsx`: check `todosDispensados` antes do fetch
- [ ] `NudgeBanners.tsx`: handler de dismiss persiste no localStorage
- [ ] `NudgeBanners.tsx`: upload de arquivo invalida nudges de upload
- [ ] `DemoModeBanner.tsx`: guard `sessionStorage.getItem('sem_demo')`
- [ ] `DemoModeBanner.tsx`: persiste `sem_demo` quando `!tem_demo`
- [ ] `DemoModeBanner.tsx`: logout limpa `sem_demo`

### Qualidade
- [ ] `tsc --noEmit` sem erros nos 3 arquivos
- [ ] Nenhum `console.error` ao navegar entre telas
- [ ] OnboardingGuard não bloqueia telas após cache definido

### Validação de Performance
- [ ] DevTools Network ao abrir Dashboard: `/onboarding/progress` chamado **0×** (usuário com dados)
- [ ] DevTools Network ao trocar de tela via bottom nav: `/onboarding/progress` chamado **0×**
- [ ] Na primeira visita após login: `/onboarding/progress` chamado **1×** (OnboardingGuard)
- [ ] Limpar localStorage e recarregar: fetch acontece normalmente

### Git e Deploy
- [ ] Commit: `fix(perf): cache localStorage/sessionStorage para onboarding (P1)`
- [ ] Push e deploy via script padrão
- [ ] Playwright: `python3 deploy/validations/ui_tests.py` passa

---

## Playwright — Avaliação Pré/Pós Sprint 2

### Passo 1 — Capturar baseline ANTES das mudanças

```bash
# Se já executou pós-S1, usar aquele como base. Caso contrário:
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_baseline_pre_s2.txt

# Contar chamadas de onboarding na baseline:
grep -i "onboarding" deploy/history/perf_baseline_pre_s2.txt
```

### Passo 2 — Após deploy, capturar resultado

```bash
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_resultado_s2.txt

# Comparar Dashboard:
grep -E "Dashboard|Budget|Bottom" deploy/history/perf_baseline_pre_s2.txt
grep -E "Dashboard|Budget|Bottom" deploy/history/perf_resultado_s2.txt
```

### Metas de aprovação

| Cenário | Antes | Meta pós-S2 | Critério de falha |
|---|---|---|---|
| Dashboard (1ª visita pós-login) | ~7s | **< 3s** | > 5s → OnboardingGuard ainda sem cache |
| Dashboard (2ª+ visita) | ~7s | **< 1s** | > 2s → cache localStorage não persiste |
| Troca de tela via bottom nav | 6–8s | **< 0.5s** | > 2s → OnboardingGuard ainda fazendo fetch |
| Network: chamadas `/onboarding/progress` | 3–4x/página | **0x** (usuários com dados) | > 0x na 2ª visita → cache não funciona |

### Validação manual via DevTools

```bash
# Passos para validar manualmente (sem Playwright):
# 1. Logar na conta admin@financas.com em modo incógnito
# 2. Abrir DevTools > Network > filtrar por "onboarding"
# 3. Navegar para /mobile/dashboard
#    Esperado: 1 chamada (OnboardingGuard na primeira visita)
# 4. Clicar em outra tela (Transações) e voltar para Dashboard
#    Esperado: 0 chamadas (cache localStorage ativo)
# 5. Verificar localStorage no Console:
#    localStorage.getItem('onboarding_completo')  → deve retornar 'true'
#    localStorage.getItem('nudge_dismissed_sem_upload')  → 'true' (se já dispensou)
#    sessionStorage.getItem('sem_demo')  → 'true'
```

### Script de verificação

```bash
# Executar verificação automática do Sprint 2:
# (a partir da raiz do projeto)
python3 docs/features/performance-prod-fixes/perf_s2_verify.py --url https://meufinup.com.br

# ou, a partir da própria pasta da feature:
python3 perf_s2_verify.py --url https://meufinup.com.br
```

**Resultado esperado pós-S2:**
```
Sprint 2 — Verificação de Onboarding Cache
==================================================
  ✅ PASS  Dashboard 1ª visita               (2100ms, 1 chamada onboarding)
  ✅ PASS  Dashboard 2ª visita (cache hit)    (420ms, 0 chamadas onboarding)
  ✅ PASS  Navegação bottom nav             (380ms, 0 chamadas onboarding)
```

**Se o cache não estiver funcionando:**
```
  ❌ FAIL  Dashboard 2ª visita (cache hit)    (6800ms, 3 chamadas onboarding)
           → Verificar: localStorage.setItem após API retornar completo?
           → Verificar: guard 'const completo = ...' antes do fetch?
```

---

## Impacto Esperado

| Cenário | Antes | Depois |
|---------|-------|--------|
| Dashboard (1ª visita pós-login) | 3–4 fetches /onboarding (~13s total) | 1 fetch /onboarding (~4–5s) |
| Dashboard (2ª+ visita) | 3–4 fetches /onboarding (~13s total) | **0 fetches** (~2–3s) |
| Troca de tela via bottom nav | 1 fetch /onboarding (~6.7s) por tela | **0 fetches** (~1.5s) |
| Usuário em onboarding | 1 fetch /onboarding (correto) | 1 fetch /onboarding (correto) |

**Próximo passo:** [Sprint 3 — Backend Cache Cashflow](sprint-3-backend-cache-cashflow.md)
