# Análise de Performance: PC vs VM — FinUpV2

> Data: 10/03/2026 | Versão analisada: 3.0.2

---

## TL;DR

**Não refatore.** A arquitetura está saudável. O problema é quase certamente a combinação de **Next.js em modo dev** + **CHOKIDAR_USEPOLLING** + **pressão de memória na VM**. O app em si tem pontos de melhoria (Redis não usado, queries sem paginação), mas esses não causam travamento — causam lentidão pontual.

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
