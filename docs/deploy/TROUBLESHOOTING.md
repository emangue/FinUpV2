# Troubleshooting de Deploy

---

## Build falha na VM (OOM / npm ci trava)

**Sintoma:** `deploy_docker_vm.sh` falha com "Killed", "Exit status 137" ou npm ci trava sem mensagem.

**Causa:** RAM insuficiente para o build do Next.js na VM.

**Fix:** Usar o script de build local:
```bash
./scripts/deploy/deploy_docker_build_local.sh
```

---

## `next: not found` no Dockerfile

**Sintoma:** Build falha com `sh: next: not found` ou `./node_modules/.bin/next: not found`.

**Causa:** Cache Docker corrompido de build anterior com instalação incompleta.

**Fix:** Build sem cache:
```bash
./scripts/deploy/deploy_docker_vm.sh --no-cache
# ou para build local:
DOCKER_BUILDKIT=1 docker compose -p finup -f docker-compose.prod.yml build --no-cache
```

---

## `docker compose up` falha com "network not found"

**Sintoma:** `Network finup_finup-net declared as external, but could not be found`.

**Causa:** Rede Docker não existe na VM.

**Fix:**
```bash
ssh minha-vps-hostinger "docker network create finup_finup-net 2>/dev/null || true"
```

---

## Backend não inicia (unhealthy)

**Sintoma:** `finup_backend_prod` fica em `unhealthy` ou reiniciando.

**Diagnóstico:**
```bash
ssh minha-vps-hostinger "docker logs finup_backend_prod --tail=50"
```

**Causas comuns:**
- `.env.prod` ausente ou com variável errada → verificar `DATABASE_URL`
- Migration pendente → `docker exec finup_backend_prod alembic upgrade head`
- Postgres não iniciou → `docker ps | grep postgres`

---

## Site retorna 502/504

**Sintoma:** meufinup.com.br retorna 502 Bad Gateway ou 504.

**Diagnóstico:**
```bash
ssh minha-vps-hostinger "
  docker ps
  docker exec infra_nginx nginx -t
  docker logs infra_nginx --tail=20
"
```

**Causas comuns:**
- Container do frontend não subiu → `docker ps | grep frontend`
- Nginx não consegue resolver `finup_frontend_app_prod` → verificar rede `finup_finup-net`

---

## `git push` bloqueado (branch não existe no remote)

```bash
git push -u origin $(git branch --show-current)
```

---

## Imagens GHCR na VM ocupando espaço

Imagens `ghcr.io/emangue/finup-*` são de um pipeline antigo e não estão em uso.

**Limpeza:**
```bash
ssh minha-vps-hostinger "
  docker images | grep ghcr.io/emangue
  docker image prune -a --filter 'until=24h'
  # ou remover explicitamente:
  docker rmi \$(docker images 'ghcr.io/emangue/*' -q) 2>/dev/null || true
"
```

---

## `infra_nginx` aparece como unhealthy

**É ruído — não é incidente.** O healthcheck faz `wget http://localhost/` e o nginx responde 301 (redirect HTTPS), que o wget interpreta como erro. O nginx está funcionando corretamente.

Para confirmar:
```bash
curl -sf https://meufinup.com.br/api/health
```
