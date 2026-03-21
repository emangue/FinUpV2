# Oportunidades de Otimização de Memória (sem remover serviços)

**Data:** 21/02/2026  
**Contexto:** Manter app_dev, app_admin, n8n, Docker. Buscar eficiência antes de comprar mais RAM. Docker será usado para segmentação.

---

## Resumo executivo

| Área | Ganho estimado | Esforço | Risco |
|------|----------------|---------|-------|
| Next.js (app_dev + app_admin) | 100–200 MB | Baixo | Baixo |
| Backend FinUp (workers) | 150–250 MB | Baixo | Médio |
| n8n (concurrency) | 100–200 MB | Baixo | Baixo |
| Systemd (MemoryMax) | Evita OOM | Baixo | Baixo |
| Docker (segmentação + limites) | Controle por app | Médio | Baixo |
| Swap 2 GB | Margem de segurança | Muito baixo | Nenhum |

---

## 1. Next.js (app_dev + app_admin)

### 1.1 `output: 'standalone'`

Reduz tamanho do deploy e memória em runtime. Cria `.next/standalone` com apenas o necessário.

```ts
// next.config.ts (app_dev e app_admin)
const nextConfig = {
  output: 'standalone',
  // ... resto
};
```

**Build:** `next build` gera `app_dev/frontend/.next/standalone/`. O `next start` usa essa pasta (menos arquivos = menos memória).

**Ganho:** ~50–100 MB por instância.

---

### 1.2 `experimental.webpackMemoryOptimizations`

Next.js 15+ – reduz pico de memória no build (útil para VM com pouco RAM).

```ts
const nextConfig = {
  experimental: {
    webpackMemoryOptimizations: true,
  },
};
```

**Ganho:** Menor pico no build; runtime similar.

---

### 1.3 `experimental.preloadEntriesOnStart: false`

Desativa pré-carregamento de todas as páginas na inicialização. Memória cresce conforme as rotas são acessadas.

```ts
experimental: {
  preloadEntriesOnStart: false,
}
```

**Ganho:** ~30–80 MB no arranque.  
**Trade-off:** Primeira visita a cada página pode ser um pouco mais lenta.

---

### 1.4 `NODE_OPTIONS` no systemd

Limitar heap do Node em produção evita que um app consuma toda a RAM.

```ini
# /etc/systemd/system/finup-frontend.service
[Service]
Environment="NODE_OPTIONS=--max-old-space-size=512"
```

**Ganho:** Cada Next.js fica limitado a ~512 MB; em caso de leak, não derruba o servidor.

---

## 2. Backend FinUp (uvicorn)

### 2.1 Reduzir workers de 2 para 1

FastAPI é tipicamente I/O-bound (DB, rede). Um worker costuma ser suficiente.

```bash
# Atual: --workers 2
# Proposto: --workers 1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**Ganho:** ~130–150 MB (um processo a menos).  
**Risco:** Sob carga alta, pode haver fila. Monitorar latência após a mudança.

---

### 2.2 Processos multiprocessing

Os 4 processos `spawn` vêm do uvicorn com `--workers 2` (1 master + 2 workers + resource_tracker). Com `--workers 1` isso cai naturalmente.

---

## 3. n8n

### 3.1 Reduzir concurrency do worker

Hoje: `--concurrency=10`. Para menos workflows simultâneos, reduzir para 4–5.

```bash
# Em /etc/systemd/system/n8n-worker.service ou equivalente
n8n worker --concurrency=4
```

**Ganho:** ~100–150 MB.  
**Trade-off:** Menos workflows em paralelo.

---

### 3.2 Limite de memória no systemd

```ini
[Service]
MemoryMax=768M
```

---

## 4. Systemd – limites por serviço

Definir `MemoryMax` em cada serviço evita que um app consuma toda a RAM e dispare OOM em outros.

```ini
# Exemplo: finup-backend.service
[Service]
MemoryMax=512M

# finup-frontend.service
MemoryMax=512M

# n8n (se tiver unit)
MemoryMax=768M
```

Quando o limite é atingido, o systemd pode reiniciar o serviço em vez de matar processos aleatórios.

---

## 5. Docker para segmentação

### 5.1 Uso planejado

Docker para isolar e limitar recursos por app:

- **app_dev** (frontend + backend) em um container
- **app_admin** em outro
- **n8n** em outro (se fizer sentido)

### 5.2 Limites por container

```yaml
# docker-compose.yml
services:
  finup-backend:
    deploy:
      resources:
        limits:
          memory: 512M
  finup-frontend:
    deploy:
      resources:
        limits:
          memory: 512M
```

**Vantagens:** Isolamento, limites claros, rollback por container.

---

## 6. Swap (margem de segurança)

Adicionar 2 GB de swap dá folga para picos (builds, uploads grandes).

```bash
# Na VM (como root)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Ganho:** Evita OOM em situações de pico.  
**Trade-off:** Swap em disco é mais lento que RAM.

---

## 7. PostgreSQL

Verificar `shared_buffers` e `work_mem`:

```bash
# Na VM
sudo -u postgres psql -c "SHOW shared_buffers;"
sudo -u postgres psql -c "SHOW work_mem;"
```

Valores típicos para 8 GB:
- `shared_buffers`: 1–2 GB (evitar > 4 GB)
- `work_mem`: 64–128 MB

Se estiverem altos, reduzir pode liberar RAM.

---

## 8. Ordem sugerida de implementação

| # | Ação | Impacto | Esforço |
|---|------|---------|---------|
| 1 | Adicionar swap 2 GB | Evita OOM | 5 min |
| 2 | `MemoryMax` nos services systemd | Controle | 15 min |
| 3 | `NODE_OPTIONS=--max-old-space-size=512` nos Next.js | Limite por app | 5 min |
| 4 | n8n `--concurrency=4` | ~100 MB | 5 min |
| 5 | Backend `--workers 1` | ~150 MB | 5 min + teste |
| 6 | Next.js `output: 'standalone'` | ~100 MB + deploy menor | 30 min |
| 7 | Next.js `preloadEntriesOnStart: false` | ~50 MB | 5 min |
| 8 | Docker com limites (quando for usar) | Segmentação | Planejamento |

---

## 9. Monitoramento

Após as mudanças:

```bash
# Uso de memória por processo
ps aux --sort=-rss | head -20

# Memória total
free -h
```

Rodar `./scripts/deploy/diagnostico_memoria_vm.sh` antes e depois para comparar.
