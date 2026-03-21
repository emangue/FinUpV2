# Skill: Deploy

## Contexto do projeto
- Host SSH: `minha-vps-hostinger`
- Path na VM: `/var/www/finup`
- Compose prod: `docker-compose.prod.yml`
- Containers: `finup_backend_prod` (:8000), `finup_frontend_app_prod` (:3003), `finup_frontend_admin_prod` (:3001)
- Scripts: `scripts/deploy/deploy_docker_build_local.sh` e `scripts/deploy/deploy_docker_vm.sh`

## Antes de executar, verifique
1. `git status -uno` → sem mudanças não commitadas
2. Branch atual está correta para o deploy
3. `ssh minha-vps-hostinger echo ok` → SSH acessível

## Passos

### 1. Push
```bash
git push origin $(git branch --show-current)
```

### 2. Escolha o script
- VM com memória suficiente (> 1GB livre): usar `deploy_docker_vm.sh` (build na VM)
- VM com risco de OOM: usar `deploy_docker_build_local.sh` (build local + SCP)

### 3. Execute
```bash
# Opção A — build na VM
bash scripts/deploy/deploy_docker_vm.sh

# Opção B — build local
bash scripts/deploy/deploy_docker_build_local.sh
```

### 4. Aguardar health checks
O script aguarda automaticamente. Se falhar manualmente:
```bash
ssh minha-vps-hostinger "curl -s http://localhost:8000/health"
```

### 5. Migrations
```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"
```

### 6. Validar
```bash
bash scripts/deploy/validate_deploy.sh
```

## Regras
- NUNCA editar arquivos diretamente na VM
- Sempre push antes de pull na VM
- Em caso de falha: `ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml rollback"`
- Registrar o commit de rollback: `git log --oneline -1`
