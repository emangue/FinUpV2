# Análise de Performance: PC vs VM — FinUpV2

> Data: 10/03/2026 | Versão analisada: 3.0.2  
> **Atualizado:** 10/03/2026 com medições reais da VM via SSH

---

## TL;DR

**Não refatore.** A arquitetura está saudável. O problema é quase certamente a combinação de **Next.js em modo dev** + **CHOKIDAR_USEPOLLING** + **pressão de memória na VM**. O app em si tem pontos de melhoria (Redis não usado, queries sem paginação), mas esses não causam travamento — causam lentidão pontual.

> ⚠️ **Atualização pós-medição real:** As três hipóteses acima foram testadas contra dados coletados diretamente na VM. Os resultados revisam parcialmente o diagnóstico — veja a Seção 8.

---

## 8. Medição Real na VM — O que os Dados Dizem

> Coletado em 10/03/2026 via SSH + `docker stats` + `ps aux` + `free -h`

### 8.1 Specs reais da VM (muito acima do estimado)

| Recurso | Estimado (análise original) | Real (medido) |
|---|---|---|
| RAM total | "2–4 GB" | **15.6 GB** |
| RAM usada | "1.3–2.4 GB só de baseline" | **1.5 GB (total do sistema)** |
| RAM disponível | ~200 MB – 2.7 GB | **14 GB livres** |
| CPUs | "VM típica com CPU limitada" | **4 vCPUs (AMD EPYC 9354P)** |
| Disco | desconhecido | **193 GB (22 GB usados, 172 GB livres)** |
| Swap | provavelmente ativo | **0 B — sem swap configurado** |
| Load average | desconhecido | **0.44, 0.29, 0.20 — essencialmente idle** |

**Conclusão:** A VM é bem mais robusta do que o diagnóstico original assumiu. Pressão de memória não é o problema.

---

### 8.2 Containers rodando na VM — modo PRODUÇÃO, não dev

```
NAMES                       STATUS          PORTS
finup_frontend_app_prod     Up 21h          0.0.0.0:3003->3000/tcp
finup_frontend_admin_prod   Up 21h          0.0.0.0:3001->3000/tcp
finup_backend_prod          Up 21h (healthy) 0.0.0.0:8000->8000/tcp
finup_postgres_prod         Up 4d (healthy) 5432/tcp
finup_redis_prod            Up 4d (healthy) 6379/tcp
infra_nginx                 Up 4d (unhealthy) 0.0.0.0:80, 443->tcp
```

**A VM roda `docker-compose.prod.yml`, não o `docker-compose.yml` de dev.** Isso invalida duas das três hipóteses originais.

---

### 8.3 Consumo real de recursos por container

| Container | CPU (medido) | RAM real | RAM estimada (original) | Status |
|---|---|---|---|---|
| finup_frontend_app_prod | 0.00% | **36 MB** | ~800 MB – 1.5 GB | ✅ Muito abaixo do estimado |
| finup_frontend_admin_prod | 0.00% | 32 MB | — | ✅ Saudável |
| finup_backend_prod | 0.59% ¹ | **312 MB** | 200–350 MB | ✅ Dentro do esperado |
| finup_postgres_prod | 0.00% | **30 MB** | 200–400 MB | ✅ Muito abaixo do estimado |
| finup_redis_prod | 0.59% | **3.3 MB** | 50–100 MB | ⚠️ Saudável, mas ainda não usado |
| infra_nginx | 0.00% | 11 MB | — | ⚠️ Unhealthy (ver 8.5) |
| **TOTAL** | **< 2%** | **~424 MB** | **~1.3–2.4 GB** | ✅ 2.7% dos 15.6 GB |

¹ *Uma primeira medição apontou 39.34% — foi snapshot durante health check interno (a cada 30s). Segunda medição imediata: 0.59%. O load average de 0.44 confirma que não há pressão contínua.*

---

### 8.4 Revisão das três hipóteses originais

#### ❌ Hipótese 1 — Next.js em modo dev

**DESCARTADA.** O container frontend roda `node server.js` com `NODE_ENV=production`. É o build estático otimizado do Next.js Next.js standalone. Consumo: 36 MB (não 800 MB–1.5 GB). Sem compilação on-the-fly, sem watchers de TypeScript.

#### ❌ Hipótese 2 — CHOKIDAR_USEPOLLING derrubando CPU

**DESCARTADA.** A variável não existe no ambiente de produção. `docker exec finup_frontend_app_prod env | grep CHOKIDAR` retornou vazio. Nenhum polling ativo.

#### ⚠️ Hipótese 3 — Pressão de memória

**PARCIALMENTE DESCARTADA.** A VM tem 15.6 GB e os containers usam 424 MB (2.7%). Não há swap ativo porque não é necessário. Pressão de memória não é o bottleneck atual.

---

### 8.5 Achados reais da VM (novos — não estavam no diagnóstico original)

#### 🔴 Achado 1 — Nginx com healthcheck quebrado (unhealthy)

O nginx está marcado `unhealthy` porque seu healthcheck interno tenta `wget http://localhost/` *dentro do container*, e o localhost interno não responde na porta 80. O tráfego real entra pelo docker-proxy do host e chega ao nginx via rede Docker — o nginx serve normalmente (HTTP→HTTPS redirect, reverse proxy). **É um falso alarme operacional, mas precisa ser corrigido** pois qualquer automação que pare containers `unhealthy` vai derrubar o nginx.

```bash
# Fix: corrigir o healthcheck do nginx para testar via rede interna
# docker-compose.prod.yml:
healthcheck:
  test: ["CMD", "nginx", "-t"]   # testa config, não conectividade
  interval: 30s
```

#### 🔴 Achado 2 — Segundo backend rodando na mesma VM (fora do Docker)

Existe um segundo uvicorn **fora do Docker** na porta 8001:

```
deploy  1800385  0.2%  /var/www/atelie/app_dev/backend/venv/bin/uvicorn
                       app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

Esse é outro projeto (`atelie`) rodando no mesmo servidor, consumindo ~220 MB adicionais de RAM e ~0.6% de CPU contínuo. Não causa lentidão agora (a VM aguenta folgado), mas é um **risco de colisão de recursos** se o atelie crescer ou se houver pico no finup.

#### ✅ Achado 3 — Redis confirmado sem uso

3.3 MB de RAM no Redis confirma que **zero caching acontece** — toda requisição vai direto ao PostgreSQL. É a melhoria de maior retorno disponível agora.

#### ✅ Achado 4 — Health check do backend é normal

O backend recebe ~2 requests/minuto no `/api/health` — originados pelo Docker healthcheck configurado com `interval: 30s`. Os logs cheios de `GET /api/health 200 OK` são operação normal, não sintoma de problema.

---

### 8.6 Veredicto revisado

```
VM está saudável. O problema de lentidão reportado é situacional, não estrutural.
```

| Hipótese | Status original | Status após medição |
|---|---|---|
| Next.js dev mode | Alta probabilidade | ❌ Descartada — roda em prod |
| CHOKIDAR_USEPOLLING | Alta probabilidade | ❌ Descartada — não existe em prod |
| RAM insuficiente | Alta probabilidade | ❌ Descartada — 14 GB livres |
| Redis sem uso | Média | ✅ Confirmada — 3.3 MB no Redis |
| Nginx unhealthy | Não identificado | 🔴 Novo achado — healthcheck quebrado |
| Segundo app na VM | Não identificado | 🟡 Novo achado — risco latente |

**Se a lentidão ainda ocorre**, as causas prováveis agora são:
1. **Latência de rede** entre o cliente e o servidor (VM em datacenter remoto — primeira conexão SSL + DNS)
2. **Cold start do PostgreSQL** nas primeiras queries do dia (índices saem do cache após idle longo)
3. **Redis sem uso** — endpoints pesados (dashboard, investimentos) fazem queries repetidas sem cache
4. **Ambiente de desenvolvimento local** — se a lentidão é percebida ao desenvolver *na* VM via Remote-SSH + `docker-compose.yml` (dev), aí os cenários 1 e 2 do diagnóstico original se aplicam, mas apenas nesse contexto específico

---

### 8.7 Ações atualizadas (pós-medição)

| Prioridade | Ação | Impacto esperado |
|---|---|---|
| 🔴 Alta | Corrigir healthcheck do nginx | Elimina `unhealthy` falso, evita restart automático indesejado |
| 🔴 Alta | Ativar Redis caching (dashboard + investimentos, TTL 5min) | Reduz latência de API em 60–80% nas rotas pesadas |
| 🟡 Média | Documentar e monitorar o `atelie` na porta 8001 | Evita surpresas de colisão de recursos |
| 🟢 Baixa | Adicionar swap (4 GB) como segurança | Proteção contra OOM se os dois apps crescerem |
| 🟢 Baixa | `EXPLAIN ANALYZE` nas queries de dashboard | Confirmar se há full table scan |

---

## 9. Medição Real de Performance — Playwright no Site de Produção

> Coletado em 10/03/2026 às 20:47 via Playwright (Chromium headless, viewport 390x844 mobile)  
> Site: https://meufinup.com.br | Script: `scripts/testing/perf_measure.py`

### 9.1 Tempos de carregamento por tela

| Tela | Tempo | Avaliação | Causa principal |
|---|---|---|---|
| Dashboard (mobile) | **~20s** ❌ | Timeout | Múltiplas APIs lentas simultâneas |
| Investimentos | **10.285ms** ❌ | Muito lento | Tela carrega mas sem dados de API rápidos |
| Budget/Plano | **5.839ms** ❌ | Lento | `/api/v1/plano/cashflow` demora 4.4s |
| Transações | **1.889ms** ⚠️ | Aceitável | `/transactions/list` ~788ms |
| Upload | **1.440ms** ⚠️ | Aceitável | APIs rápidas (~480ms máx) |

**Média geral: 4.863ms** — bem acima do ideal de < 1s.

---

### 9.2 As APIs culpadas — ranking de lentidão

#### 🔴 Dashboard (20+ segundos de carregamento)

```
7019ms  GET  /api/v1/onboarding/progress          ← chamado 2x (!!)
6322ms  GET  /api/v1/onboarding/progress          ← duplicata da mesma chamada
5182ms  GET  /api/v1/plano/cashflow/mes?ano=2026&mes=2&modo_plano=true
4771ms  GET  /api/v1/budget/planning?mes_referencia=2026-02
4767ms  GET  /api/v1/dashboard/budget-vs-actual?year=2026&month=1
```

**Problema crítico:** `/api/v1/onboarding/progress` é chamado **2 vezes** (provavelmente por dois componentes independentes) e cada chamada demora mais de 6s. Essas duas chamadas sozinhas bloqueiam o carregamento do dashboard.

#### 🔴 Budget/Plano (5.8s)

```
4382ms  GET  /api/v1/plano/cashflow?ano=2026      ← chamado 2x (!!)
2188ms  GET  /api/v1/plano/cashflow?ano=2026      ← duplicata
2187ms  GET  /api/v1/plano/projecao?ano=2026&meses=12
1400ms  GET  /api/v1/budget/planning?mes_referencia=2026-03
 884ms  GET  /api/v1/plano/aporte-investimento?ano=2026&mes=3
```

**Mesmo padrão:** `/plano/cashflow` chamado 2x. Query pesada sem cache.

#### 🔴 Investimentos (10.3s)

```
185ms  GET  /api/v1/onboarding/progress
179ms  GET  /api/v1/auth/me
 80ms  GET  /api/v1/dashboard/last-month-with-data
```

Curioso: as APIs capturadas são rápidas. O tempo de 10s provavelmente é renderização pesada no cliente (cálculos de portfólio, simulador), não APIs lentas. Requer investigação adicional com DevTools.

#### ✅ Transações (1.9s — aceitável)

```
788ms  GET  /api/v1/transactions/list?limit=100&page=1  ← chamado 2x
594ms  GET  /api/v1/transactions/resumo?
```

Mesma lista chamada 2x, mas tempo total ainda aceitável.

#### ✅ Troca de modo Mês/YTD/Ano (300–370ms — excelente)

```
Mês  →  370ms  ✅
YTD  →  363ms  ✅
Ano  →  337ms  ✅
```

Filtros de modo **funcionam bem** — o React reutiliza dados já carregados. A experiência ao trocar de modo é fluida.

---

### 9.3 Padrão identificado: chamadas de API duplicadas

O maior problema **não é a VM, não é o hardware** — é que **os mesmos endpoints são chamados 2x por cada carregamento de tela**:

| Endpoint duplicado | Tempo duplicado | Tela afetada |
|---|---|---|
| `/api/v1/onboarding/progress` | 7s + 6.3s = **13.3s** | Dashboard |
| `/api/v1/plano/cashflow` | 4.4s + 2.2s = **6.6s** | Budget/Plano |
| `/api/v1/transactions/list` | 788ms + 692ms = **1.5s** | Transações |

**Por que isso acontece:** Provavelmente dois componentes React distintos (ex: layout + página) fazem o mesmo `useEffect` ou `fetch` sem compartilhamento de estado. A solução é:
1. **Curto prazo:** Cache no Redis com TTL curto (os dados voltariam em <50ms na 2ª chamada)
2. **Longo prazo:** React Query / SWR para deduplicar chamadas idênticas no frontend

---

### 9.4 Veredicto final revisado

```
O travamento é 100% do app, não do ambiente.
A VM é saudável. O problema são queries lentas + chamadas duplicadas.
```

| Causa | Status | Prova |
|---|---|---|
| VM com hardware fraco | ❌ Descartado | 15.6 GB RAM, 4 vCPUs, 0.44 load avg |
| Next.js dev mode | ❌ Descartado | Roda `node server.js` (produção) |
| CHOKIDAR polling | ❌ Descartado | Variável não existe em produção |
| `/onboarding/progress` lento (7s) | ✅ **CONFIRMADO** | Medido: 7s por chamada |
| `/plano/cashflow` lento (4.4s) | ✅ **CONFIRMADO** | Medido: 4.4s por chamada |
| Chamadas de API duplicadas | ✅ **CONFIRMADO** | Mesmo endpoint 2x por tela |
| Redis sem cache | ✅ **CONFIRMADO** | Toda query vai ao PostgreSQL |
| Investimentos com renderização pesada | 🔍 Suspeito | APIs rápidas mas tela demora 10s |

---

### 9.5 Plano de ação atualizado (prioridade real)

| # | Ação | Impacto estimado | Esforço |
|---|---|---|---|
| 1 | Investigar e otimizar `/api/v1/onboarding/progress` (7s → <200ms) | Dashboard: 20s → ~6s | Médio |
| 2 | Investigar e otimizar `/api/v1/plano/cashflow` (4.4s → <500ms) | Budget: 5.8s → ~1.5s | Médio |
| 3 | Redis cache em endpoints pesados (TTL 5min) | Elimina duplicatas 2ª chamada | Baixo |
| 4 | Deduplicar chamadas no frontend (React Query/SWR ou contexto compartilhado) | Elimina 30-50% das chamadas | Alto |
| 5 | `EXPLAIN ANALYZE` nas queries de `/onboarding/progress` e `/plano/cashflow` | Identifica índices faltando | Baixo |
| 6 | Investigar os 10s de Investimentos com DevTools (Performance tab) | Identifica se é JS ou API | Baixo |

> **Próximo passo imediato:** `EXPLAIN ANALYZE` no PostgreSQL das duas queries mais lentas — provavelmente faltam índices em `journal_entries` (Ano, Mes, user_id).



---

## 1. Diagnóstico: Por que trava na VM?

### 1.1 Next.js em modo dev é o maior culprit

O `docker-compose.yml` sobe o frontend com o servidor de desenvolvimento do Next.js:

```yaml
# docker-compose.yml (dev)
command: next dev   # ← compilação on-the-fly, watchers ativos
```

Em dev mode, o Next.js:
- Compila TypeScript de **333 arquivos** sob demanda (nenhum bundle pré-gerado)
- Mantém watchers ativos em todos os arquivos
- Re-compila qualquer rota na primeira visita
- Não usa os otimizações de produção (tree-shaking, minification, etc.)

No PC, isso é imperceptível porque o hardware aguenta. Na VM, cada compilação congela o processo.

### 1.2 CHOKIDAR_USEPOLLING: CPU 100% em VM

```yaml
environment:
  CHOKIDAR_USEPOLLING: "true"  # ← polling de arquivos, CPU-intensivo
```

Essa flag existe para compatibilidade com macOS. Em VM Linux (especialmente com volumes Docker montados), o Chokidar faz **polling ativo de todos os arquivos** a cada intervalo fixo. Com 333 arquivos TypeScript + `node_modules`, isso sozinho pode segurar a CPU.

### 1.3 Pressão de memória: 4 containers simultâneos

| Serviço | RAM estimada (mínima) |
|---|---|
| PostgreSQL 16 | ~200–400 MB |
| Redis 7 | ~50–100 MB |
| FastAPI + Uvicorn | ~200–350 MB |
| Next.js dev server | **~800 MB – 1.5 GB** |
| **Total** | **~1.3 – 2.4 GB** só de baseline |

Se a VM tem 2–4 GB de RAM, já está no limite antes de qualquer carga real. O Next.js dev server é particularmente guloso porque carrega o compilador TypeScript inteiro em memória.

### 1.4 Double virtualization overhead

Na VM, o Docker corre sobre um hypervisor que já está sobre o OS da VM. Isso adiciona latência em I/O de disco (compilação TypeScript é I/O-intensiva) e em chamadas de rede entre containers.

---

## 2. O que o App tem de "pesado" (mas não é o problema principal)

### 2.1 Redis configurado, mas não utilizado

Redis está no docker-compose mas **nenhum domínio do backend usa caching**. Isso significa que endpoints como dashboard e investimentos fazem queries pesadas no banco a **cada request**, sem cache.

Impacto: lentidão nas respostas da API, não travamento de UI.

### 2.2 Queries sem paginação explícita

O modelo `JournalEntry` tem 52 colunas e pode crescer muito. Não há evidência de paginação nas queries de listagem. Se o usuário tem milhares de transações, isso se sentirá.

Impacto: lentidão gradual conforme o banco cresce.

### 2.3 OCR / PyMuPDF no import

Dependências como `rapidocr-onnxruntime` e `PyMuPDF` são carregadas no startup do backend. Em VM com CPU limitada, isso pode atrasar o cold start.

Impacto: apenas no primeiro boot.

### 2.4 57 dependências NPM + Radix UI x26

O bundle inicial do frontend é substancial. Em produção (Next.js build), isso é otimizado. Em dev, cada componente Radix é carregado sem otimização.

Impacto: primeira carga de página lenta em dev.

---

## 3. O que está bem na arquitetura

- **DDD com 17 domínios isolados**: correto, escalável, sem god-objects
- **Connection pooling** no SQLAlchemy (pool_size=10, max_overflow=20): bem configurado
- **Virtualization no frontend** (react-window, react-virtuoso): existe e está implementado
- **Lazy loading + Suspense**: implementado no investimentos
- **Deduplicação FNV-1a**: eficiente, não é bottleneck
- **Autenticação com httpOnly cookies**: correto e seguro
- **Separação dev/prod** nos docker-compose: a estrutura está certa

---

## 4. Veredicto: VM ou App?

```
Travamento na VM: 90% ambiente, 10% app
```

| Causa | Probabilidade | Impacto |
|---|---|---|
| Next.js dev mode na VM | **Alta** | Travamento real |
| CHOKIDAR_USEPOLLING ativo | **Alta** | CPU constante |
| RAM insuficiente na VM | **Alta** | Swap = travamento |
| Redis não utilizado | Média | Lentidão de API |
| Queries sem paginação | Baixa (agora) | Lentidão futura |
| Arquitetura ruim | **Não** | — |

---

## 5. Ações recomendadas (por prioridade)

### Prioridade 1 — Ambiente (resolve o travamento imediato)

**A. Usar build de produção na VM**

```bash
# Em vez de docker-compose.yml (dev), usar:
docker compose -f docker-compose.prod.yml up
```

O build de produção do Next.js gera bundle estático otimizado. A VM vai a 10–20% do consumo atual do frontend.

**B. Desativar CHOKIDAR_USEPOLLING na VM Linux**

```yaml
# docker-compose.yml — remover ou condicionar:
# CHOKIDAR_USEPOLLING: "true"  ← remover em VM Linux
```

**C. Aumentar RAM da VM para pelo menos 4 GB**

Mínimo recomendado para rodar o stack completo com conforto.

### Prioridade 2 — Quick wins no App

**D. Ativar Redis caching nos endpoints críticos**

```python
# Backend: cache de dashboard, investimentos (TTL 5 min)
# O Redis já está no stack, só falta usar
```

**E. Confirmar paginação nas queries de JournalEntry**

```python
# Garantir .limit() e .offset() em listagens
# Retornar total_count no response para o frontend
```

### Prioridade 3 — Monitoramento

**F. Medir antes de otimizar mais**

Antes de qualquer refatoração adicional, medir com:
- `docker stats` para ver CPU/RAM real por container
- Chrome DevTools Performance para ver onde a UI trava
- `EXPLAIN ANALYZE` no PostgreSQL para queries lentas

---

## 6. Refatorar o app inteiro?

**Não.** Seria um erro estratégico. A arquitetura está bem desenhada:

- Migrar de DDD para outra coisa não resolve nada
- Trocar Next.js não resolve nada (o problema é dev mode, não o framework)
- O código de negócio (upload, deduplicação, investimentos) está maduro

O que vale evoluir no futuro:
- Implementar camada de cache (Redis já está no stack)
- Adicionar Server-Sent Events para uploads longos (feedback em tempo real)
- Considerar React Query ou SWR para cache inteligente no frontend (substitui parte dos custom hooks)

---

## 7. Conclusão

O app funciona bem no PC porque o PC tem RAM e CPU sobrand. Na VM, o gargalo é o ambiente de desenvolvimento (dev server + polling), não a qualidade do código.

**Próximo passo recomendado:** testar a VM com `docker-compose.prod.yml` e ver se o travamento some. Se sumir, o diagnóstico está confirmado. Se persistir, aí vale medir com `docker stats` durante o uso e compartilhar os números.

---

*Análise gerada com base na exploração completa da codebase FinUpV2 v3.0.2*
