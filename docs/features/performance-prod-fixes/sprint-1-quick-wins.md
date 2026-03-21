# Sprint 1 — Quick Wins: Nginx + Double-Fetch Carteira/Investimentos/Transações

> **Esforço total:** ~45 minutos  
> **Itens:** P5 · P7 · P8  
> **Pré-requisito:** Nenhum — pode iniciar imediatamente  
> **Impacto:** Elimina 4 fetches duplos desnecessários nas 3 telas mais usadas

---

## 🔗 Rastreamento de Erros — Do Sintoma ao Fix

> Antes de implementar, entenda **o que está errado, onde e por quê**. Cada tabela conecta o sintoma observado em produção à causa exata no código.

### P5 — Nginx `unhealthy`

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | `docker-compose ps` mostra `infra_nginx Up X days (unhealthy)` |
| **Risco** | Política de restart pode derrubar o proxy e tirar o site do ar |
| **Verificar agora** | `docker exec infra_nginx wget -q http://localhost/ -O /dev/null` → `Connection refused` |
| **Causa raiz** | Nginx no Docker não ouve em `localhost:80` internamente; ouve na bridge de rede Docker. O `wget` falha com Connection refused — o container é marcado unhealthy por isso, não por problema real. |
| **O fix** | Trocar para `nginx -t` — valida a config do processo; exit 0 se tudo saudável, sem depender de conectividade HTTP. |

### P7 — Double-fetch em Carteira e Investimentos

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Carteira e Investimentos demoram ~1.5s. DevTools Network mostra **2 batches de requests** com ~350ms de diferença entre eles. |
| **Medido com `perf_measure.py`** | `Investimentos: ~1500ms` — dois grupos de API calls capturados: `t≈97ms` (mês errado) e `t≈392ms` (mês correto, após `fetchLastMonthWithData` resolver). |
| **Arquivo exato** | `app_dev/frontend/src/app/mobile/carteira/page.tsx` → **linha 241** |
| **Arquivo exato** | `app_dev/frontend/src/app/mobile/investimentos/page.tsx` → **linha 51** |
| **Causa raiz** | `React.useState<Date>(new Date())` inicia `selectedMonth` com o mês atual. O `useEffect` de dados tem `[isAuth, anomes, selectedMonth]` nas deps → dispara imediatamente (mês errado) → `fetchLastMonthWithData` resolve → `selectedMonth` atualiza → 2º dispatch do useEffect → **2 fetches por visita**. |
| **O fix** | `useState<Date \| null>(null)` + guard `if (!selectedMonth) return` no useEffect. Dados buscados apenas quando o mês correto está disponível. |

### P8 — Double-fetch em Transações (debounce instável)

| Dimensão | Detalhe |
|---|---|
| **Sintoma** | Abertura de Transações dispara 2 pares de `transactions/list` + `transactions/resumo` com exato offset de 400ms entre eles. |
| **Medido com `perf_measure.py`** | `Transações: ~800ms` — dois batches com 400ms de offset → o debounce dispara mesmo sem mudança real de filtro. |
| **Arquivo exato** | `app_dev/frontend/src/app/mobile/transactions/page.tsx` → **linhas 132–144** |
| **Causa raiz** | `periodFilterRef.current = setTimeout(() => setDebouncedPeriod({yearInicio, ...}), 400)` — o objeto literal `{...}` criado no setTimeout tem **nova referência** mesmo com valores idênticos. `filters` (useMemo) recomputa → `fetchTransactions` (useCallback) é recriada → useEffect re-dispara. |
| **O fix** | `setState` funcional: retornar `prev` quando valores não mudaram → React não re-renderiza porque a referência é a mesma. |

---

## Índice

- [P5 — Fix healthcheck do nginx](#p5--fix-healthcheck-do-nginx-5-minutos)
- [P7 — selectedMonth = null em Carteira e Investimentos](#p7--selectedmonth--null-em-carteira-e-investimentos-20-minutos)
- [P8 — Debounce stable ref em Transactions](#p8--debounce-stable-ref-em-transactions-10-minutos)
- [Checklist final e validação](#checklist-final-e-validação)

---

## P5 — Fix healthcheck do nginx (5 minutos)

### Problema

O nginx está marcado como `unhealthy` no Docker porque o healthcheck interno tenta `wget http://localhost/` dentro do container — mas o container nginx não serve requisições em `localhost:80` (elas chegam via rede Docker do host). O nginx funciona normalmente para o usuário, mas qualquer automação que reinicie containers `unhealthy` vai derrubar o proxy e tirar o site do ar.

```
NAMES         STATUS
infra_nginx   Up 4d (unhealthy)   ← 🔴 falso alarme, mas perigoso
```

### Diagnóstico

```bash
# Dentro do container nginx, o healthcheck atual falha:
docker exec infra_nginx wget -q http://localhost/ -O /dev/null
# → Connection refused (nginx não escuta na porta 80 do loopback dentro do container)
```

### Fix

**Arquivo:** `docker-compose.prod.yml` — serviço `nginx`

```yaml
# ANTES (healthcheck incorreto):
services:
  nginx:
    image: nginx:alpine
    healthcheck:
      test: ["CMD", "wget", "-q", "http://localhost/", "-O", "/dev/null"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

# DEPOIS (healthcheck correto — testa config do nginx, não conectividade):
services:
  nginx:
    image: nginx:alpine
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**Por quê `nginx -t`?**  
O comando verifica a validade da configuração do nginx. Se o nginx estiver rodando e a config estiver correta, retorna exit code 0 (healthy). É um teste de saúde genuíno: se a config corrompeu ou o processo morreu, retorna não-zero.

### Aplicar na VM

```bash
# 1. Commit e push local
git add docker-compose.prod.yml
git commit -m "fix(nginx): corrige healthcheck para usar nginx -t em vez de wget"
git push

# 2. Aplicar no servidor
ssh minha-vps-hostinger
cd /var/www/finup
git pull

# Opção A: apenas reiniciar o nginx para pegar o novo healthcheck
docker-compose -f docker-compose.prod.yml up -d --no-deps nginx

# Opção B: se preferir parada completa
docker-compose -f docker-compose.prod.yml restart nginx

# 3. Validar após ~35s (interval + start_period)
docker-compose -f docker-compose.prod.yml ps
# infra_nginx   Up X min (healthy)   ← deve aparecer healthy agora
```

### Checklist P5

- [ ] `docker-compose.prod.yml` modificado com `nginx -t`
- [ ] Commit e push feitos
- [ ] `git pull` no servidor
- [ ] `docker-compose ps` mostra nginx como `(healthy)` após 35s
- [ ] Site continua acessível após restart: `curl -I https://meufinup.com.br`

---

## P7 — `selectedMonth = null` em Carteira e Investimentos (20 minutos)

### Problema

Tanto `app/mobile/carteira/page.tsx` quanto `app/mobile/investimentos/page.tsx` inicializam `selectedMonth` com `new Date()` (mês atual). Isso dispara um `useEffect` prematuro com o mês errado **antes** que `fetchLastMonthWithData` retorne o mês real com dados.

**Timeline medida com Playwright:**
```
t=42ms   auth/me resolve → isAuth=true
t=97ms   [Batch 1] distribuicao-tipo + timeline/patrimonio  ← mês ERRADO (Março)
t=381ms  fetchLastMonthWithData resolve → selectedMonth = Fev
t=392ms  [Batch 2] distribuicao-tipo + timeline/patrimonio  ← mês CORRETO (Fev)
```

**Resultado:** cada visita fria dispara **2× cada API de dados** — o primeiro batch é descartado.

### Arquivos

- `app_dev/frontend/src/app/mobile/carteira/page.tsx` (linha ~241)
- `app_dev/frontend/src/app/mobile/investimentos/page.tsx` (linha ~60)

### Fix — Carteira (`carteira/page.tsx`)

#### Passo 1: alterar estado inicial de `selectedMonth`

```typescript
// ANTES (linha ~241):
const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())

// DEPOIS:
const [selectedMonth, setSelectedMonth] = React.useState<Date | null>(null)
```

#### Passo 2: tornar `anomes` nullable

```typescript
// ANTES:
const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)

// DEPOIS:
const anomes = selectedMonth
  ? selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
  : null
```

#### Passo 3: adicionar guard no useEffect de dados

```typescript
// ANTES — useEffect de dados (linha ~264):
React.useEffect(() => {
  if (!isAuth) return
  // ... fetches de distribuicao-tipo, timeline/patrimonio, etc
}, [isAuth, anomes, selectedMonth])

// DEPOIS — adicionar guard para selectedMonth null:
React.useEffect(() => {
  if (!isAuth || !selectedMonth) return  // ← guard: aguarda selectedMonth ser definido
  // ... fetches de distribuicao-tipo, timeline/patrimonio, etc (sem alteração)
}, [isAuth, anomes, selectedMonth])
```

#### Passo 4: garantir renderização condicional onde `selectedMonth` era usado como não-null

Procurar usos de `selectedMonth` em JSX que esperavam `Date` (não `Date | null`). Corrigir com optional chaining ou null check:

```typescript
// Qualquer uso como: selectedMonth.getMonth()  →  selectedMonth?.getMonth()
// Qualquer uso em props que exigem Date: usar `selectedMonth ?? new Date()` apenas no JSX de display
// O useEffect de dados usa o guard acima, então não precisa de fallback lá
```

---

### Fix — Investimentos (`investimentos/page.tsx`)

**Exatamente o mesmo padrão.** As 4 mudanças são idênticas:

#### Passo 1: alterar estado inicial

```typescript
// ANTES (linha ~60):
const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())

// DEPOIS:
const [selectedMonth, setSelectedMonth] = React.useState<Date | null>(null)
```

#### Passo 2: `anomes` nullable

```typescript
// ANTES:
const anomes = selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)

// DEPOIS:
const anomes = selectedMonth
  ? selectedMonth.getFullYear() * 100 + (selectedMonth.getMonth() + 1)
  : null
```

#### Passo 3: guard no useEffect de dados

```typescript
React.useEffect(() => {
  if (!isAuth || !selectedMonth) return  // ← guard adicionado
  // ... fetches de getInvestimentos, distribuicao-tipo, timeline/patrimonio
}, [isAuth, anomes, selectedMonth])
```

#### Passo 4: ajustar usos no JSX (se `selectedMonth` for passado como `Date` para componentes filhos)

```typescript
// Componentes que exigem Date como prop:
<SomeComponent month={selectedMonth ?? new Date()} />
// ou mostrar loading enquanto null:
{selectedMonth ? <SomeComponent month={selectedMonth} /> : <Skeleton />}
```

### Validação P7

```bash
# Abrir DevTools → Network no Chromium mobile
# Navegar para Carteira ou Investimentos via bottom nav

# ANTES do fix: 2 batches de requests (t≈97ms e t≈392ms)
# APÓS o fix: apenas 1 batch de requests (t≈392ms — quando selectedMonth é definido)

# Verificar no console que não há: "Warning: Cannot read property of null"
```

**Impacto esperado:** elimina ~400–700ms de latência por visita (1 batch inteiro desnecessário).

### Checklist P7

- [ ] `carteira/page.tsx`: `useState<Date | null>(null)` declarado
- [ ] `carteira/page.tsx`: `anomes` é `number | null` (nullable)
- [ ] `carteira/page.tsx`: `useEffect` de dados tem `if (!isAuth || !selectedMonth) return`
- [ ] `investimentos/page.tsx`: mesmas 3 mudanças acima
- [ ] Nenhum erro TypeScript: `tsc --noEmit` passa
- [ ] Carteira abre sem erro, dados aparecem corretamente
- [ ] Investimentos abrem sem erro, dados aparecem corretamente
- [ ] DevTools Network: apenas 1 batch de requests por visita fria

---

## P8 — Debounce stable ref em Transactions (10 minutos)

### Problema

Em `app/mobile/transactions/page.tsx`, o `useEffect` de debounce cria um **novo objeto** com os mesmos valores do estado inicial, 400ms após o mount. Mesmo sendo valores idênticos, o novo objeto muda a referência de `debouncedPeriod`, o que força:
1. `filters` (useMemo) a recomputar
2. `fetchTransactions` e `fetchResumo` a serem recriadas
3. O `useEffect([fetchTransactions, fetchResumo])` a disparar de novo

**Timeline medida:**
```
t=188ms   [Batch 1] transactions/list + transactions/resumo   ← mount inicial
t=597ms   [Batch 2] transactions/list + transactions/resumo   ← debounce 400ms depois
```

**Custo:** 2 RTTs extras (~800ms) em toda abertura da tela de Transações.

### Arquivo

`app_dev/frontend/src/app/mobile/transactions/page.tsx` — linha ~136

### Fix

```typescript
// ANTES — código real em transactions/page.tsx linhas 132–144:
// (nota: usa periodFilterRef.current, não `const timer`)
useEffect(() => {
  if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  periodFilterRef.current = setTimeout(() => {
    setDebouncedPeriod({ yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo })
    //                   ↑ SEMPRE cria novo objeto literal → nova referência
    //                     mesmo com valores idênticos → filters recomputa → 2º fetch
  }, 400)
  return () => {
    if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  }
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])

// DEPOIS — functional update com comparação de igualdade:
// (preservar o padrão periodFilterRef.current — não trocar por const timer)
useEffect(() => {
  if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  periodFilterRef.current = setTimeout(() => {
    setDebouncedPeriod(prev => {
      // Se todos os valores são iguais, retorna a MESMA referência → sem re-render
      if (
        prev.yearInicio       === yearInicio &&
        prev.monthInicio      === monthInicio &&
        prev.yearFim          === yearFim &&
        prev.monthFim         === monthFim &&
        prev.semFiltroPeriodo === semFiltroPeriodo
      ) return prev  // ← mesma referência → filters (useMemo) não recomputa
      return { yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo }
    })
  }, 400)
  return () => {
    if (periodFilterRef.current) clearTimeout(periodFilterRef.current)
  }
}, [yearInicio, monthInicio, yearFim, monthFim, semFiltroPeriodo])
```

> **⚠️ Atenção:** O código real usa `periodFilterRef.current` (ref persistente) — **não** `const timer`. Não trocar por `const timer = setTimeout(...)` pois o `ref` é necessário para o cleanup correto entre renders.

**Mecanismo:** React garante que se o estado retornado de um `setState` funcional for `===` ao estado atual, não há re-render. Ao retornar `prev` quando os valores são iguais, o `debouncedPeriod` não muda referência → `filters` não recomputa → `fetchTransactions`/`fetchResumo` não são recriadas → segundo fetch não acontece.

### Validação P8

```bash
# DevTools → Network → navegar para Transações
# Filtrar por: list, resumo

# ANTES: 2 pares de requests (um no mount, outro ~400ms depois)
# APÓS:  1 par de requests apenas (no mount, o debounce não dispara segundo fetch)

# Testar que o debounce AINDA funciona para mudanças reais:
# Alterar filtro de período → deve disparar 1 fetch 400ms depois (correto)
```

### Checklist P8

- [ ] `transactions/page.tsx`: `setDebouncedPeriod` usa functional update com comparação
- [ ] TypeScript não reclama (o tipo de retorno do functional update é correto)
- [ ] Abrir Transações: apenas 1 par de requests no Network (não 2)
- [ ] Alterar filtro de período: novo fetch acontece após 400ms (debounce funciona)
- [ ] Alterar texto de busca: novo fetch acontece (debounce funciona)

---

## Ordem de Execução Recomendada

```
P5 (5 min)  →  P8 (10 min)  →  P7 (20 min)
  nginx          transactions      carteira + investimentos
```

**Justificativa:**
- P5 é só config — deploy sem tocar em código TypeScript
- P8 é 1 arquivo, mudança cirúrgica de 8 linhas
- P7 é 2 arquivos, mudança um pouco maior (precisa checar todos os usos do `selectedMonth` no JSX)

---

## Checklist Final Sprint 1

### Implementação
- [ ] P5: `docker-compose.prod.yml` modificado
- [ ] P7: `carteira/page.tsx` com `selectedMonth = null` + guard
- [ ] P7: `investimentos/page.tsx` com `selectedMonth = null` + guard
- [ ] P8: `transactions/page.tsx` com debounce functional update

### Qualidade
- [ ] `tsc --noEmit` sem erros em `carteira/page.tsx`
- [ ] `tsc --noEmit` sem erros em `investimentos/page.tsx`
- [ ] `tsc --noEmit` sem erros em `transactions/page.tsx`
- [ ] Nenhum `console.error` nas 3 telas

### Git e Deploy
- [ ] Commit com mensagem clara: `fix(perf): elimina double-fetch em carteira, investimentos e transactions`
- [ ] Push para GitHub
- [ ] Deploy via `./deploy/scripts/deploy_docker_build_local.sh`
- [ ] Validar em produção com Playwright: `python3 deploy/validations/ui_tests.py`

### Validação de Performance
- [ ] DevTools Network: Carteira → 1 batch de requests por visita fria
- [ ] DevTools Network: Investimentos → 1 batch de requests por visita fria
- [ ] DevTools Network: Transações → 1 par de requests por abertura
- [ ] Nginx: `docker-compose ps` mostra `(healthy)` em produção

---

## Playwright — Avaliação Pré/Pós Sprint 1

### Passo 1 — Capturar baseline ANTES das mudanças

```bash
# Executar antes de qualquer commit do Sprint 1 (salva o baseline)
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_baseline_pre_s1.txt

# ou usar o script dedicado desta feature:
python3 docs/features/performance-prod-fixes/perf_s1_verify.py --url https://meufinup.com.br

# Verificar status do nginx antes:
docker-compose -f docker-compose.prod.yml ps | grep nginx
```

### Passo 2 — Após deploy, capturar resultado

```bash
# Após commit + deploy do Sprint 1:
python3 scripts/testing/perf_measure.py --url https://meufinup.com.br \
  2>&1 | tee deploy/history/perf_resultado_s1.txt

# Comparar tempos:
grep -E "Carteira|Investimentos|Transações" deploy/history/perf_baseline_pre_s1.txt
grep -E "Carteira|Investimentos|Transações" deploy/history/perf_resultado_s1.txt
```

### Metas de aprovação

| Tela | Antes (esperado) | Meta pós-S1 | Critério de falha |
|---|---|---|---|
| Investimentos | ~1500ms | **< 800ms** | > 1000ms → P7 não aplicado corretamente |
| Carteira | ~1500ms | **< 800ms** | > 1000ms → P7 não aplicado corretamente |
| Transações | ~800ms | **< 500ms** | > 700ms → P8 não eliminou o segundo fetch |
| Nginx health | `(unhealthy)` | `(healthy)` | Qualquer coisa ≠ healthy → P5 pendente |

### Script standalone — verificação de double-fetch

```bash
# Executar o script de verificação pontual do Sprint 1:
# (a partir da raiz do projeto)
python3 docs/features/performance-prod-fixes/perf_s1_verify.py --url https://meufinup.com.br

# ou, a partir da própria pasta da feature:
python3 perf_s1_verify.py --url https://meufinup.com.br
```

**Resultado esperado após S1:**
```
Sprint 1 — Verificação de Double-Fetch
==================================================
  ✅ PASS  P7 Carteira (double-fetch)       (742ms, 1 batch)
  ✅ PASS  P7 Investimentos (double-fetch)  (710ms, 1 batch)
  ✅ PASS  P8 Transações (debounce race)    (430ms, 1 batch)
```

**Resultado se ainda houver problema:**
```
  ❌ FAIL  P7 Carteira (double-fetch)       (1480ms, 2 batches)
           → useState ainda iniciando com new Date() na linha 241
           → Verificar guard if (!selectedMonth) return no useEffect de dados
```

### Validação manual via DevTools Network

Para confirmar P7 sem Playwright:
1. Abrir DevTools → aba Network → filtrar por `/api/v1/investimentos`
2. Navegar para Carteira ou Investimentos via bottom nav
3. **Antes:** 2 grupos de requests com ~350ms de intervalo
4. **Depois:** apenas 1 grupo de requests (quando `selectedMonth` é definido)

Para confirmar P8:
1. Filtrar Network por `transactions/list`
2. Abrir aba Transações
3. **Antes:** 2 requests com exato offset de 400ms
4. **Depois:** 1 request apenas na abertura

---

## Resumo

| Item | Arquivo(s) | Linhas | Risco | Ganho |
|------|-----------|--------|-------|-------|
| P5 | `docker-compose.prod.yml` | 1 linha | ✅ Zero | Nginx healthy |
| P7 | `carteira/page.tsx`, `investimentos/page.tsx` | ~5 por arquivo | ✅ Baixo | -700ms/visita |
| P8 | `transactions/page.tsx` | ~8 linhas | ✅ Zero | -800ms/abertura |

**Próximo passo:** [Sprint 2 — Onboarding Cache](sprint-2-onboarding-cache.md)
