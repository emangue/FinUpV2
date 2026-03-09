# Guia de Deploy — FinUp

**Última atualização:** 07/03/2026

---

## Fluxo padrão

```bash
./scripts/deploy/deploy_docker_build_local.sh
```

Faz o build das imagens **localmente** (evita OOM na VM), envia via SCP e sobe os containers.

**Pré-requisitos:**
1. `git status -uno` limpo
2. `git push origin <branch>` feito
3. SSH `minha-vps-hostinger` configurado

---

## Fluxo alternativo (quando VM tem RAM disponível para buildar)

```bash
./scripts/deploy/deploy_docker_vm.sh
# Ou com rebuild completo:
./scripts/deploy/deploy_docker_vm.sh --no-cache
# Ou sem rebuild (só restart):
./scripts/deploy/deploy_docker_vm.sh --skip-build
```

A VM tem 15 GB RAM — o build direto na VM é viável mas mais lento.

---

## Configuração

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `VM_HOST` | `minha-vps-hostinger` | Alias SSH da VM |
| `VM_PATH` | `/var/www/finup` | Caminho do projeto na VM |

Compose file ativo: `docker-compose.prod.yml` (projeto `finup`)

---

## Containers em produção

| Container | Porta | Descrição |
|-----------|-------|-----------|
| `finup_backend_prod` | 8000 | FastAPI |
| `finup_frontend_app_prod` | 3003→3000 | Next.js (meufinup.com.br) |
| `finup_frontend_admin_prod` | 3001→3000 | Next.js (admin.meufinup.com.br) |
| `finup_postgres_prod` | interna | PostgreSQL |
| `finup_redis_prod` | interna | Redis |

Nginx centralizado: `infra_nginx` (Docker, `/var/www/infra/`) — dono das portas 80/443.

---

## Validação pós-deploy

```bash
./scripts/deploy/validate_deploy.sh
```

Ou manualmente:
```bash
# Health check backend
curl https://meufinup.com.br/api/health

# Containers rodando
ssh minha-vps-hostinger "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Logs em tempo real
ssh minha-vps-hostinger "docker logs finup_backend_prod --tail=50 -f"
```

---

## Migrations

As migrations Alembic rodam automaticamente no script de deploy. Se precisar rodar manualmente:

```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"
```

---

## Rollback

`deploy_docker_vm.sh` faz rollback automático para o commit anterior se o deploy falhar.

Rollback manual:
```bash
ssh minha-vps-hostinger "
  cd /var/www/finup
  git checkout <commit-anterior>
  docker compose -p finup -f docker-compose.prod.yml --env-file .env.prod up -d
"
```
