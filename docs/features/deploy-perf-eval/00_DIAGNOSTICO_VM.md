# Diagnóstico Completo da VM — 07/03/2026

**Branch:** `perf/performance-v2-n0-n4`
**Executor:** Claude (sessão interativa via SSH)

---

## Estado atual dos containers

```
finup_backend_prod        Up (healthy)   0.0.0.0:8000->8000/tcp
finup_frontend_app_prod   Up             0.0.0.0:3003->3000/tcp
finup_frontend_admin_prod Up             0.0.0.0:3001->3000/tcp
finup_postgres_prod       Up (healthy)   5432/tcp (interno)
finup_redis_prod          Up (healthy)   6379/tcp (interno)
infra_nginx               Up (unhealthy) 0.0.0.0:80->80, 0.0.0.0:443->443
```

**Backend health:** `{"status":"healthy","database":"connected"}` ✅
**Site:** `curl https://meufinup.com.br` → responde (redirect para `/mobile/dashboard`) ✅
**Branch na VM:** `perf/performance-v2-n0-n4`, sincronizado com origin ✅
**Commit ativo:** `064a2c49`

---

## Compose e projeto Docker

- **Arquivo:** `docker-compose.prod.yml`
- **Project name:** `finup`
- **Imagens ativas:** `finup-backend:latest`, `finup-frontend-app:latest`, `finup-frontend-admin:latest`
- **Criadas em:** 2026-03-07 02:10 UTC (build local via `deploy_docker_build_local.sh`)

---

## Recursos da VM

| Recurso | Total | Usado | Livre |
|---------|-------|-------|-------|
| RAM | 15 GB | 1.5 GB | 7.8 GB (+ 6.8 cache) |
| Disco | 193 GB | 16 GB | 177 GB |
| Swap | 0 | 0 | — |

RAM abundante — OOM não é o problema atual.

---

## Problemas identificados

### 1. Dois Postgres rodando — risco de confusão

| Instância | Onde | Porta | Quem usa |
|-----------|------|-------|----------|
| `finup_postgres_prod` | Container Docker | interna | Backend (via `DATABASE_URL`) |
| `postgres` (OS) | Host | `127.0.0.1:5432` | Provavelmente Ateliê ou legado |

O `docker-compose.vm.yml` foi criado para uma VM com Postgres no host, mas nesta VM o backend usa Postgres em container. O arquivo `docker-compose.vm.yml` **não reflete a realidade atual** e deve ser removido.

### 2. Dois nginx — arquitetura confusa

**Host nginx** (`/etc/nginx/sites-enabled/finup`): config do meufinup.com.br com Certbot/SSL presente, mas o serviço nginx do host pode estar parado (infra_nginx ocupa as portas 80/443).

**`infra_nginx`** (Docker, projeto `infra`, gerenciado pelo Easypanel):
- Escuta em `0.0.0.0:80` e `0.0.0.0:443`
- Tem configs em `/etc/nginx/conf.d/`: `meufinup.com.br.conf`, `admin.meufinup.com.br.conf`, `gestao.atelieilmaguerra.com.br.conf`
- **Este é o nginx ativo** que serve o tráfego real

**Healthcheck do `infra_nginx`:** 543 falhas consecutivas (`wget http://localhost/` recebe redirect para HTTPS e falha). O site funciona normalmente — a falha é no health check, não no nginx. É ruído de monitoramento, não incidente.

### 3. Terceiro fluxo de deploy (GHCR) — imagens órfãs

Há imagens `ghcr.io/emangue/finup-*` na VM de 2026-03-06, evidenciando uma tentativa de usar o GitHub Container Registry como pipeline. Esse fluxo não está documentado como ativo. As imagens ocupam espaço mas não afetam o funcionamento.

### 4. Script correto de deploy

O fluxo que funciona hoje:

```bash
./scripts/deploy/deploy_docker_build_local.sh
```

- Build das imagens localmente (linux/amd64)
- SCP do tar para a VM
- `docker load` + `docker compose -p finup -f docker-compose.prod.yml up -d`

---

## Rede Docker

```
finup_finup-net (bridge):
  infra_nginx:               172.20.0.2
  finup_backend_prod:        172.20.0.3
  finup_frontend_admin_prod: 172.20.0.4
  finup_frontend_app_prod:   172.20.0.5
```

A rede `finup_finup-net` existe e está correta.

---

## Ações recomendadas

| Prioridade | Ação |
|-----------|------|
| Alta | Remover `docker-compose.vm.yml` (não reflete a realidade) |
| Alta | Arquivar ~43 scripts de deploy obsoletos (manter 3) |
| Alta | Arquivar ~35 docs de deploy acumulados (manter 2) |
| Média | Limpar imagens GHCR da VM (`docker image prune` ou remoção manual) |
| Baixa | Corrigir health check do `infra_nginx` (ruído, não incidente) |
| Baixa | Confirmar se host nginx está parado e remover configs órfãs de `/etc/nginx/sites-enabled/` |
