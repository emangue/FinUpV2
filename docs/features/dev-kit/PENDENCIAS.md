# Pendências de Código

Todas as alterações identificadas mas ainda não implementadas.
Cada item tem arquivo exato, o que fazer e referência de onde a análise foi feita.

---

## 🔴 Segurança — Crítico

### SEC-01 — Upload sem validação chamada nos endpoints
**Arquivo:** `app_dev/backend/app/domains/upload/router.py`
**Status:** Função `_validar_arquivo()` e constantes já existem no arquivo. Falta apenas chamar.

**O que fazer:**

**Endpoint `/detect` (linha ~58):**
```python
# Adicionar antes de `file_bytes = await file.read()`:
_validar_arquivo(file)
file_bytes = await file.read()
if len(file_bytes) > MAX_UPLOAD_BYTES:
    raise HTTPException(400, f"Arquivo muito grande. Máximo: {MAX_UPLOAD_BYTES // 1024 // 1024}MB")
```

**Endpoint `/preview` (linha ~131):**
```python
# Adicionar no início do endpoint, antes de chamar o service:
_validar_arquivo(file)
file_content = await file.read()
if len(file_content) > MAX_UPLOAD_BYTES:
    raise HTTPException(400, f"Arquivo muito grande. Máximo: {MAX_UPLOAD_BYTES // 1024 // 1024}MB")
await file.seek(0)  # reset para o service ler novamente
```

**Endpoint `/batch` (linha ~191, dentro do loop):**
```python
# Adicionar no início de cada iteração do loop:
for i, file in enumerate(files, 1):
    try:
        _validar_arquivo(file)  # ← adicionar aqui
        logger.info(...)
```

**Endpoint `/import-planilha` (linha ~264):**
```python
# Adicionar no início do endpoint:
_validar_arquivo(file)
mapeamento_dict = None
```

**Referência:** `docs/performance/SEGURANCA_FRONTEND_BACKEND.md` — seções 1.3 e 1.4

---

### SEC-02 — removeConsole ausente no next.config.ts
**Arquivo:** `app_dev/frontend/next.config.ts`
**Status:** Não implementado.

**O que fazer:**
```typescript
// Adicionar dentro de nextConfig:
const nextConfig: NextConfig = {
  devIndicators: false,
  outputFileTracingRoot: path.join(__dirname),
  output: 'standalone',
  compiler: {
    // Remove console.log e console.debug em produção
    // Mantém console.error e console.warn para monitoramento
    removeConsole: process.env.NODE_ENV === 'production'
      ? { exclude: ['error', 'warn'] }
      : false,
  },
};
```

**Referência:** `docs/performance/SEGURANCA_FRONTEND_BACKEND.md` — seção 3.1

---

### SEC-03 — localStorage com token JWT
**Arquivo:** `app_dev/frontend/src/features/auth/hooks/use-token.ts`
**Arquivo:** `app_dev/frontend/src/lib/api-client.ts` (ou equivalente)
**Status:** Não implementado. Requer investigação de impacto antes de alterar.

**O que fazer:**
1. Verificar todos os lugares onde `localStorage.getItem('authToken')` é chamado
2. Remover `saveToken()` — o backend já seta cookie httpOnly no login
3. No `api-client.ts`, remover leitura do localStorage e adicionar `credentials: 'include'` em todos os fetch
4. Para verificar se o usuário está logado no frontend sem token, usar o endpoint `GET /api/v1/auth/me`

**Atenção:** Testar cuidadosamente o fluxo de login/logout após esta mudança.

**Referência:** `docs/performance/SEGURANCA_FRONTEND_BACKEND.md` — seção 1.2

---

### SEC-04 — dangerouslySetInnerHTML no chart sem validação
**Arquivo:** `app_dev/frontend/src/components/ui/chart.tsx`
**Status:** Não implementado.

**O que fazer:**
```typescript
// Adicionar função de validação:
const isValidColor = (c: string): boolean =>
  /^#[0-9A-Fa-f]{3,8}$/.test(c) ||
  /^(rgb|hsl)a?\([\d\s,%.]+\)$/.test(c) ||
  /^var\(--[\w-]+\)$/.test(c)

// Antes de usar no style tag:
const safeColor = isValidColor(color) ? color : 'transparent'
// usar safeColor em vez de color
```

**Referência:** `docs/performance/SEGURANCA_FRONTEND_BACKEND.md` — seção 2.2

---

## 🔴 Performance — Crítico

### PERF-01 — Queries sem user_id em grupos
**Arquivo:** `app_dev/backend/app/domains/grupos/repository.py` — linha ~79
**Status:** Não corrigido. Bug de integridade + segurança (dados cruzam entre usuários).

**O que fazer:**
Identificar a query que faz contagem ou listagem sem filtro `user_id` e adicionar o filtro.
Verificar o impacto: quais endpoints chamam esse repositório? Os dados retornados podem estar errados para usuários que não são o primeiro cadastrado.

**Referência:** `docs/performance/PERFORMANCE_OPORTUNIDADES.md` — seção 2 (Crítico)

---

### PERF-02 — Queries sem user_id em marcações
**Arquivo:** `app_dev/backend/app/domains/marcacoes/service.py` — linha ~79
**Status:** Não corrigido. Mesmo problema do PERF-01.

**O que fazer:**
Mesma correção do PERF-01: identificar query sem `user_id` e adicionar filtro.

**Referência:** `docs/performance/PERFORMANCE_OPORTUNIDADES.md` — seção 2 (Crítico)

---

## 🟠 Performance — Alto

### PERF-03 — get_cashflow com ~60 queries por request
**Arquivo:** `app_dev/backend/app/domains/dashboard/` (repository ou service)
**Status:** Não corrigido.

**O que fazer:**
Substituir loop mensal com queries individuais por:
1. Uma query que busca todos os dados do ano em uma só chamada
2. Agrupar por mês em Python usando `defaultdict`
3. O resultado final é O(1) por mês em vez de N queries

**Referência:** `docs/performance/PERFORMANCE_OPORTUNIDADES.md` — seção 3.1 (Alto)

---

### PERF-04 — dashboard.get_chart_data() com 12 queries
**Arquivo:** `app_dev/backend/app/domains/dashboard/`
**Status:** Não corrigido.

**O que fazer:** Mesmo padrão do PERF-03 — pré-buscar tudo, agregar em Python.

**Referência:** `docs/performance/PERFORMANCE_OPORTUNIDADES.md` — seção 3.2 (Alto)

---

### PERF-05 — useExpenseSources chamado duas vezes com mesmos params
**Arquivo:** `app_dev/frontend/src/features/dashboard/` (use-dashboard.ts ~linha 170)
**Status:** Não corrigido.

**O que fazer:**
1. Verificar se o hook está sendo instanciado em dois componentes diferentes (solução: elevar estado)
2. Ou verificar se `useEffect` tem objeto como dependência (solução: desestruturar para primitivos)
3. Confirmar com React DevTools ou log no hook

**Referência:** `docs/performance/SEGURANCA_FRONTEND_BACKEND.md` — seção 3.2

---

## 🟢 Dev Experience

### DEV-01 — Backend sem hot reload confiável no macOS
**Arquivo:** `docker-compose.yml`
**Status:** Não corrigido. Frontend já tem o fix equivalente.

**O que fazer:**
```yaml
# Adicionar na seção environment do serviço backend:
backend:
  environment:
    - DATABASE_URL=...
    - WATCHFILES_FORCE_POLLING=true  # ← adicionar esta linha
```

**Por quê:** O Docker no macOS corre em VM. Eventos de filesystem (inotify) não chegam
confiáveis no container. Os frontends já têm `CHOKIDAR_USEPOLLING=true` para o mesmo
problema. O uvicorn usa `watchfiles` internamente — `WATCHFILES_FORCE_POLLING=true`
é o equivalente exato.

**Impacto:** Após essa mudança, qualquer alteração em `.py` do backend reinicia o
servidor automaticamente, sem precisar `docker-compose restart backend`.

---

## 🟡 Deploy

### DEPLOY-01 — Consolidar scripts de deploy
**Pasta:** `scripts/deploy/` (50+ scripts)
**Status:** Não consolidado.

**O que fazer:**
1. Definir o script canônico (ver `DEPLOY.md` nesta pasta)
2. Adicionar aviso no topo dos scripts obsoletos: `# ⚠️ Use ./scripts/deploy/deploy.sh`
3. Mover scripts antigos para `scripts/deploy/archive/`
4. Garantir que `quick_start.sh` e `quick_stop.sh` continuem funcionando para dev local

**Referência:** `docs/features/dev-kit/DEPLOY.md`

---

## Ordem de execução sugerida

| Prioridade | Item | Esforço | Risco |
|------------|------|---------|-------|
| 1 | DEV-01 — hot reload backend | 2 min | Zero |
| 2 | SEC-02 — removeConsole next.config.ts | 5 min | Zero |
| 3 | SEC-01 — validação upload nos endpoints | 20 min | Baixo |
| 4 | PERF-01/02 — user_id em grupos e marcações | 30 min | Médio (testar bem) |
| 5 | SEC-04 — chart.tsx validação de cor | 15 min | Baixo |
| 6 | SEC-03 — localStorage → cookie | 1h | Alto (testar auth flow completo) |
| 7 | PERF-03/04 — dashboard N+1 | 2h | Médio |
| 8 | PERF-05 — useExpenseSources duplicado | 30 min | Baixo |
| 9 | DEPLOY-01 — consolidar scripts | 1h | Baixo |
