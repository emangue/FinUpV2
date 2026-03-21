# Avaliação Completa do Processo de Deploy — 07/03/2026

**Branch:** `perf/performance-v2-n0-n4`
**Contexto:** Reavaliação solicitada após dificuldades consecutivas com o deploy.

---

## Diagnóstico: Por que o deploy não avançava

### 1. Problema imediato — `docker-compose.prod.yml` com rede externa

O `docker-compose.prod.yml` declara uma rede externa obrigatória:

```yaml
networks:
  finup-net:
    external: true
    name: finup_finup-net
```

Se a rede `finup_finup-net` não existisse na VM, o `docker compose up -d` falhava. O script não criava a rede antes de usar. A rede **existe** atualmente na VM — mas nenhum script garante isso de forma defensiva.

### 2. Ambiguidade de qual compose usar

| Arquivo | Postgres | Redis | Status |
|---------|----------|-------|--------|
| `docker-compose.yml` | container | container | Dev local — OK |
| `docker-compose.prod.yml` | container | container | **PROD ATIVO** |
| `docker-compose.vm.yml` | host OS | — | Obsoleto — remover |

O `docker-compose.vm.yml` foi criado para uma VM com Postgres no host. A VM atual usa Postgres em container. Esse arquivo é confusão garantida e deve ser deletado.

### 3. Risco operacional: 46 scripts de deploy

O histórico de commits da branch mostra que os últimos 5 commits são todos sobre **consertar o deploy**, não sobre features. O processo de deploy estava consumindo o tempo de desenvolvimento.

**Dois fluxos coexistindo sem separação clara:**

```
Fluxo A (antigo, pkill+nohup, sem Docker):
  deploy.sh → deploy_build_local.sh → deploy_branch_vm.sh

Fluxo B (atual, Docker):
  deploy_docker_vm.sh → deploy_docker_build_local.sh
```

A documentação `DEPLOY_PROCESSO_CONSOLIDADO.md` ainda descrevia o Fluxo A como padrão.

---

## Estado da VM após inspeção (07/03/2026)

### Deploy funcionando

O `deploy_docker_build_local.sh` concluiu com sucesso. Commit `064a2c49` rodando na VM.

```
finup_backend_prod        healthy   porta 8000
finup_frontend_app_prod   up        porta 3003
finup_frontend_admin_prod up        porta 3001
finup_postgres_prod       healthy
finup_redis_prod          healthy
```

Backend health: `{"status":"healthy","database":"connected"}` ✅

### Problemas identificados na VM

**Dois nginx ativos (confusão histórica):**

| Nginx | Tipo | Portas | Status |
|-------|------|--------|--------|
| `infra_nginx` | Docker container (`/var/www/infra/`) | 80, 443 | **ATIVO** — serve todo o tráfego |
| host nginx | Processo OS (`/etc/nginx/sites-enabled/finup`) | — | Parado (infra_nginx ocupa 80/443) |

O `infra_nginx` tem 543 falhas de healthcheck porque o health check faz `wget http://localhost/` e o nginx responde 301 (redirect HTTPS), que o wget trata como erro. O site funciona normalmente — é ruído de monitoramento, não incidente.

**`/opt/finup/` ainda existe:**
- É de uma instalação anterior do FinUp (`finup_nginx_prod` usava `/opt/finup/`)
- Os **certificados SSL** ainda estão em `/opt/finup/certbot/conf/` e são usados pelo `infra_nginx`
- Não deletar

**Duas instâncias de Postgres:**

| Postgres | Onde | Porta | Quem usa |
|----------|------|-------|----------|
| `finup_postgres_prod` | Docker | interna | Backend FinUp |
| `postgres` (OS) | Host | 127.0.0.1:5432 | Ateliê Gestão |

---

## Plano de ação: Deploy

### Agora — manter o que funciona

Script oficial: `./scripts/deploy/deploy_docker_build_local.sh`

### Curto prazo — Limpeza

**Manter 3 scripts:**
- `deploy_docker_build_local.sh` — fluxo padrão atual
- `deploy_docker_vm.sh` — alternativa quando VM tem RAM suficiente para buildar
- `validate_deploy.sh` — validação pós-deploy

**Arquivar** os outros 43+ em `scripts/deploy/archive/`.

**Deletar** `docker-compose.vm.yml` — não reflete a realidade.

**Manter** 2 docs de deploy:
- `docs/deploy/GUIA_DEPLOY.md` — fluxo Docker atual (a criar)
- `docs/deploy/TROUBLESHOOTING.md` — erros conhecidos

### Médio prazo — Robustez

Adicionar ao início do `deploy_docker_build_local.sh`, antes do `up -d`:
```bash
# Garantir rede Docker antes de subir containers
ssh "$VM_HOST" "docker network create finup_finup-net 2>/dev/null || true"
```
