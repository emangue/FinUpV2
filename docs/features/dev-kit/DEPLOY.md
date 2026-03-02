# Processo Canônico de Deploy — FinUp

Este documento define o único processo correto de deploy. Qualquer outro script em
`scripts/deploy/` é legado e deve ser substituído por este fluxo.

---

## Mapa de portas (referência rápida)

| Serviço | Dev local | Prod (interno container) | Prod (host/externo) |
|---------|-----------|--------------------------|---------------------|
| Backend API | 8000 | 8000 | 8000 |
| Frontend app | 3000 | 3000 | **3003** → Nginx → meufinup.com.br |
| Frontend admin | 3001 | 3000 | **3001** |
| PostgreSQL | 5432 | — (rede interna Docker) | não exposto |
| Redis | 6379 | — (rede interna Docker) | não exposto |

⚠️ **Armadilha comum:** o frontend app usa porta **3003** no host em produção, não 3000.
O Nginx é quem recebe na 80/443 e faz proxy para 3003.

---

## Ambientes

| Ambiente | Como rodar | Docker Compose |
|----------|-----------|----------------|
| **Desenvolvimento local** | `./scripts/deploy/quick_start.sh` | `docker-compose.yml` |
| **Teste de build prod (local)** | `docker-compose -f docker-compose.prod.yml up --build` | `docker-compose.prod.yml` |
| **Produção (VM)** | `./scripts/deploy/deploy.sh` (a definir) | `docker-compose.prod.yml` na VM |

Não existe staging formal. O "staging" é rodar `docker-compose.prod.yml` localmente
para validar que o build funciona antes de subir para a VM.

---

## Processo de deploy — passo a passo

### Fase 1 — Pré-voo (local, antes de qualquer coisa)

Executar antes de conectar na VM:

```bash
# 1. Tudo commitado?
git status

# 2. Branch atualizada com main?
git log origin/main..HEAD --oneline

# 3. Build de produção funciona localmente?
docker-compose -f docker-compose.prod.yml build

# 4. Novas variáveis de ambiente documentadas em .env.prod.example?
git diff .env.prod.example  # deve incluir qualquer nova var

# 5. Migrations testadas localmente?
# (já devem ter sido rodadas no ambiente de dev antes de chegar aqui)
```

❌ Não avançar se qualquer um desses falhar.

---

### Fase 2 — Segurança antes de tocar produção

**Obrigatório antes de qualquer alteração na VM:**

```bash
# Conectar na VM
ssh <usuario>@<ip-vm>

# 1. Verificar saúde atual (todos os serviços UP?)
docker-compose -f docker-compose.prod.yml ps

# 2. Fazer backup do banco ANTES de qualquer mudança
./scripts/deploy/backup_daily.sh
# Confirmar que o backup foi criado com sucesso antes de continuar

# 3. Anotar versão atual como ponto de rollback
git rev-parse HEAD > /tmp/deploy_rollback_ref.txt
echo "Deploy iniciado: $(date)" >> /tmp/deploy_rollback_ref.txt
```

---

### Fase 3 — Deploy (ordem importa)

```bash
# 1. Pull do código novo
git pull origin main

# 2. Verificar se há migrations novas
# Se sim: rodar ANTES de reiniciar qualquer serviço
alembic -c app_dev/backend/alembic.ini upgrade head

# ⚠️ Migrations DEVEM rodar antes do restart.
# O código novo pode exigir colunas que o banco ainda não tem.
# O código velho ainda aguenta o schema novo (backward compatible).

# 3. Rebuild e restart do backend
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend

# 4. Aguardar health check do backend
# (retry até 30s antes de continuar)
for i in $(seq 1 6); do
  curl -sf http://localhost:8000/api/health && break
  echo "Aguardando backend... ($i/6)"
  sleep 5
done

# 5. Rebuild e restart dos frontends
docker-compose -f docker-compose.prod.yml up -d --build --no-deps frontend-app frontend-admin
```

---

### Fase 4 — Verificação pós-deploy

```bash
# Backend
curl -s http://localhost:8000/api/health
# Esperado: {"status": "ok"}

# Frontend app (porta interna do container)
curl -s http://localhost:3003 | head -5
# Esperado: HTML do Next.js

# Frontend admin
curl -s http://localhost:3001 | head -5
# Esperado: HTML do Next.js

# Verificar logs por 2-3 minutos
docker-compose -f docker-compose.prod.yml logs --tail=50 -f backend
```

✅ Deploy bem-sucedido quando todos os health checks passam e logs sem erro.

---

### Fase 5 — Rollback (se algo falhar)

#### Rollback de código (mais rápido, 2 minutos)

```bash
# Pegar ref do rollback
cat /tmp/deploy_rollback_ref.txt

# Reverter para commit anterior
git reset --hard <commit-anterior>

# Redeploy com código antigo
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend frontend-app frontend-admin
```

#### Rollback de migration (necessário se migration destrutiva falhou)

```bash
# 1. Reverter migration
alembic -c app_dev/backend/alembic.ini downgrade -1

# 2. Se houve perda de dados (DROP COLUMN/TABLE), restaurar backup
# O backup está em: database/backups_daily/
# Identificar o backup pré-deploy pelo timestamp

# 3. Reverter código
git reset --hard <commit-anterior>

# 4. Redeploy
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend
```

#### Rollback de emergência (serviço completamente fora)

```bash
# Manter banco intacto, só reiniciar com imagem anterior
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml up -d backend
# O Docker usa a imagem mais recente que estava funcionando se o build falhou
```

---

## Tipos de mudança e risco de rollback

| Tipo de mudança | Risco | Rollback |
|----------------|-------|----------|
| Só código (sem migration) | Baixo | 2 min — redeploy código anterior |
| Migration additive (ADD COLUMN nullable) | Baixo | Reverter migration + código |
| Migration destrutiva (DROP COLUMN/TABLE) | **Alto** | Restaurar backup + reverter migration + código |
| Nova variável de ambiente | Médio | Adicionar var + restart |
| Alteração de porta/Nginx | Médio | Reverter config Nginx + restart |

### Regra de ouro para migrations destrutivas

Nunca fazer DROP direto em produção. Processo de 2 deploys:
1. **Deploy 1:** Deprecar a coluna (remover do código, manter no banco)
2. **Deploy 2:** Dropar a coluna (com backup garantido antes)

---

## Desenvolvimento local — referência rápida

```bash
# Subir tudo
./scripts/deploy/quick_start.sh
# ou: docker-compose up -d

# Parar tudo
./scripts/deploy/quick_stop.sh
# ou: docker-compose down

# Ver logs do backend
docker-compose logs -f backend

# Restart só do backend (após mudança de código que não auto-reloadou)
docker-compose restart backend

# Rodar migration localmente
docker-compose exec backend alembic upgrade head

# Abrir shell no container do backend
docker-compose exec backend bash
```

---

## Consolidação dos scripts legados

A pasta `scripts/deploy/` tem 50+ scripts acumulados ao longo do tempo.
Situação atual: nenhum é claramente "o processo correto", gerando confusão.

**Plano de consolidação (ver PENDENCIAS.md — DEPLOY-01):**
1. Este documento (`DEPLOY.md`) é o processo canônico
2. Criar script único `scripts/deploy/deploy.sh` que implementa as fases 1-4 deste doc
3. Scripts de desenvolvimento local: manter `quick_start.sh` e `quick_stop.sh`
4. Todos os outros: mover para `scripts/deploy/archive/` com aviso no cabeçalho

**Scripts a manter:**
- `quick_start.sh` — dev local
- `quick_stop.sh` — dev local
- `backup_daily.sh` — backup do banco
- `deploy.sh` — **o script canônico a criar**

**Scripts a arquivar:**
- Todos os outros (deploy_safe_v2, deploy_branch_vm, quick_deploy, etc.)
