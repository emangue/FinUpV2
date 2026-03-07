# Mapeamento Completo da VM — 07/03/2026

**VM:** Hostinger VPS — São Paulo, BR (`148.230.78.91`)
**OS:** Linux (Hostinger)
**RAM:** 15 GB total / 1.5 GB usado
**Disco:** 193 GB total / 16 GB usado

---

## Arquitetura geral

```
Internet (HTTPS)
       │
       ▼
  infra_nginx  ← Docker container, porta 80/443
  /var/www/infra/docker-compose.yml
       │
       ├─── meufinup.com.br ──────────────────► finup_frontend_app_prod:3000
       │                                         (Docker, /var/www/finup)
       │
       ├─── admin.meufinup.com.br ────────────► finup_frontend_admin_prod:3000
       │                                         (Docker, /var/www/finup)
       │
       └─── gestao.atelieilmaguerra.com.br ──► host-gateway:3004
                                                (processo OS, /var/www/atelie)

APIs:
  /api/*  ──────────────────────────────────► finup_backend_prod:8000
                                              (Docker, /var/www/finup)
  gestao /api/*  ──────────────────────────► host:8001
                                              (processo OS, /var/www/atelie)
```

---

## Projeto 1: FinUp (`/var/www/finup/`)

**Compose file:** `docker-compose.prod.yml`
**Project name:** `finup`

### Containers

| Container | Imagem | Porta | Status |
|-----------|--------|-------|--------|
| `finup_backend_prod` | `finup-backend:latest` | 8000 | healthy |
| `finup_frontend_app_prod` | `finup-frontend-app:latest` | 3003→3000 | up |
| `finup_frontend_admin_prod` | `finup-frontend-admin:latest` | 3001→3000 | up |
| `finup_postgres_prod` | `postgres:16-alpine` | interna | healthy |
| `finup_redis_prod` | `redis:7-alpine` | interna | healthy |

### Redes Docker

| Rede | Membros |
|------|---------|
| `finup_finup-net` | infra_nginx (0.2), backend (0.3), frontend-admin (0.4), frontend-app (0.5) |
| `finup_default` | postgres, redis, backend |

### Arquivos na VM

```
/var/www/finup/
├── app_dev/          ← código fonte do app usuário
│   ├── frontend/     ← Next.js (meufinup.com.br)
│   └── backend/      ← FastAPI (Python)
├── app_admin/        ← código fonte do painel admin
│   └── frontend/     ← Next.js (admin.meufinup.com.br)
├── docker-compose.prod.yml   ← ATIVO
├── docker-compose.vm.yml     ← OBSOLETO (remover)
├── docker-compose.yml        ← dev local (não usar na VM)
└── docker-compose.prod.yml.bak
```

### Banco de dados

- **Postgres em container** (`finup_postgres_prod`)
- `DATABASE_URL=postgresql://finup_user:***@finup_postgres_prod:5432/finup_db`
- Dados persistidos em Docker volume `finup_postgres_data`

---

## Projeto 2: Ateliê Gestão (`/var/www/atelie/`)

**Modelo:** Processos diretos no OS (sem Docker)

### Processos

| Serviço | Tecnologia | Porta | PID |
|---------|-----------|-------|-----|
| Frontend | Next.js 15.1.3 (`next start`) | 3004 | 155355 |
| Backend | FastAPI (uvicorn 2 workers) | 8001 | 29616 |

### Banco de dados

- **Postgres no host** (processo OS, `127.0.0.1:5432`)
- Esta é a segunda instância de Postgres identificada na VM

### Arquivos

```
/var/www/atelie/
├── app_dev/
│   ├── frontend/     ← Next.js
│   └── backend/      ← FastAPI
├── scripts/
│   ├── quick_start.sh   ← inicia os processos
│   ├── quick_stop.sh    ← para os processos
│   └── deploy.sh        ← deploy manual
└── nginx/            ← configs nginx locais (não usadas)
```

---

## Projeto 3: Infra (`/var/www/infra/`)

**Compose file:** `docker-compose.yml`
**Project name:** `infra`

### Containers

| Container | Imagem | Porta | Status |
|-----------|--------|-------|--------|
| `infra_nginx` | `nginx:stable-alpine` | 80, 443 | up (healthcheck falso-negativo) |

### Configs nginx

```
/var/www/infra/nginx/conf.d/
├── meufinup.com.br.conf          ← FinUp app (→ finup_frontend_app_prod:3000)
├── admin.meufinup.com.br.conf    ← FinUp admin (→ finup_frontend_admin_prod:3000)
└── gestao.atelieilmaguerra.com.br.conf  ← Ateliê (→ host-gateway:3004)
```

### Rate limits (nginx.conf)

| Zona | Taxa | Burst | Uso |
|------|------|-------|-----|
| `login_limit` | 10r/m | 5 | `/api/v1/auth/login` |
| `api_limit` | 120r/m | 20 | `/api/*` |
| `app_limit` | 240r/m | 30 | `/` (frontend) |

**Bug de rate limiting:** O Docker NAT faz todos os clientes aparecerem como `172.20.0.1`. O rate limit aplica-se por servidor inteiro, não por usuário. Baixo impacto atual (poucos usuários), mas incorreto.

---

## Instalação legada: `/opt/finup/`

Instalação anterior do FinUp (migrada para `/var/www/finup/`). **Não deletar** — os certificados SSL ainda são usados:

```
/opt/finup/
├── certbot/conf/    ← SSL certs (meufinup.com.br) — USADO pelo infra_nginx
├── certbot/www/     ← ACME challenge files
├── .env.prod        ← secrets da instalação anterior (não mais usado pelos containers)
├── docker-compose.prod.yml  ← versão antiga (não ativo)
└── nginx/           ← configs nginx antigas
```

**Container `finup_nginx_prod`** (Exited): era o nginx da instalação `/opt/finup/`. Substituído pelo `infra_nginx`.

---

## Imagens Docker — Uso e Desperdício

```
Total: 9.96 GB
Reclaimable: 3.02 GB (30%)
Build cache: 1.83 GB (1.42 GB reclaimable)
```

### Imagens em uso

| Imagem | Tamanho | Projeto |
|--------|---------|---------|
| `finup-backend:latest` | 1.18 GB | FinUp backend |
| `finup-frontend-app:latest` | 313 MB | FinUp frontend |
| `finup-frontend-admin:latest` | 295 MB | FinUp admin |
| `postgres:16-alpine` | 395 MB | FinUp postgres |
| `redis:7-alpine` | 61 MB | FinUp redis |
| `nginx:stable-alpine` | 93 MB | infra_nginx |

### Imagens ociosas (podem ser removidas)

| Imagem | Tamanho | Observação |
|--------|---------|-----------|
| `ghcr.io/emangue/finup-backend` (4 tags) | 1.26 GB × 4 | Tentativa de fluxo GHCR — não ativo |
| `ghcr.io/emangue/finup-frontend` (4 tags) | 312 MB × 4 | Idem |
| `ghcr.io/emangue/finup-admin` (4 tags) | 293 MB × 4 | Idem |
| `easypanel/easypanel` | 1.7 GB | Easypanel (ainda instalado?) |
| `traefik` (2 versões) | 242 + 286 MB | Não em uso |

**Limpeza estimada:** `docker image prune -a` (apenas imagens não usadas) → libera ~3 GB

---

## Portas em uso na VM

| Porta | Processo | Domínio |
|-------|---------|---------|
| 80 | `infra_nginx` (Docker) | redirect HTTPS |
| 443 | `infra_nginx` (Docker) | todos os domínios |
| 3003 | `finup_frontend_app_prod` (Docker) | via nginx |
| 3001 | `finup_frontend_admin_prod` (Docker) | via nginx |
| 3004 | next-server Ateliê (host) | via nginx |
| 8000 | `finup_backend_prod` (Docker) | via nginx |
| 8001 | uvicorn Ateliê (host) | via nginx |
| 5432 | postgres host (OS) | Ateliê |
| 5432 | `finup_postgres_prod` (Docker, interno) | FinUp |
| 6379 | `finup_redis_prod` (Docker, interno) | FinUp |

---

## Problemas estruturais da VM

### P1 — `docker-compose.vm.yml` obsoleto
Não reflete a realidade (VM usa Postgres em container, não no host). Remover.

### P2 — Dois modelos de deploy coexistindo
- FinUp: Docker (moderno, correto)
- Ateliê: pkill+nohup (antigo, sem Docker)
Risco: a experiência com o Ateliê pode contaminar scripts e decisões do FinUp.

### P3 — Healthcheck do `infra_nginx` falso-negativo
`wget http://localhost/` → 301 HTTPS → wget falha. Já acumula 543 falhas. Nunca disparará alerta real porque sempre está "unhealthy". Corrigir ou suprimir.

### P4 — Imagens GHCR órfãs
~3 GB de imagens de uma tentativa de pipeline via GitHub Container Registry que foi abandonada.

### P5 — Build cache acumulado
1.83 GB. Rodar `docker builder prune` libera ~1.4 GB.

### P6 — Rate limiting por servidor, não por usuário
Bug de configuração (Docker NAT). Todos os clientes compartilham o bucket de rate limit.
