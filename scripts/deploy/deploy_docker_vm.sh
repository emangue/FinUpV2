#!/bin/bash

# =============================================================================
# deploy_docker_vm.sh — Deploy Docker na VM com rollback automático
# =============================================================================
#
# Uso: ./scripts/deploy/deploy_docker_vm.sh [--skip-build]
#
# Fluxo:
#   1. Validar pré-requisitos (git limpo, push feito, .env.prod na VM)
#   2. Registrar commit atual na VM (âncora de rollback)
#   3. SSH → git pull → docker-compose build + up
#   4. Alembic migrations dentro do container
#   5. Health check (3 tentativas)
#   6. Se falhar → rollback automático para commit anterior
#
# Requisitos:
#   - SSH configurado: ssh minha-vps-hostinger
#   - .env.prod presente na VM em /var/www/finup/
#   - Docker instalado na VM
# =============================================================================

set -e

# ─── Configurações ────────────────────────────────────────────────────────────
VM_HOST="${VM_HOST:-minha-vps-hostinger}"
VM_PATH="${VM_PATH:-/var/www/finup}"
COMPOSE_FILE="docker-compose.prod.yml"
BRANCH=$(git branch --show-current)
SKIP_BUILD="${1:-}"

# ─── Cores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✅ $*${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_err()  { echo -e "${RED}❌ $*${NC}"; }
log_info() { echo -e "${BLUE}🔹 $*${NC}"; }

echo ""
echo "🚀 DEPLOY DOCKER FinUp → VM"
echo "    Branch : $BRANCH"
echo "    Host   : $VM_HOST"
echo "    Path   : $VM_PATH"
echo "    Compose: $COMPOSE_FILE"
echo "=========================================="

# =============================================================================
# FASE 1 — Pré-requisitos locais
# =============================================================================
log_info "Fase 1: Validando pré-requisitos locais..."

# Raiz do projeto
if [ ! -f "app_dev/backend/app/main.py" ]; then
    log_err "Execute da raiz do projeto!"
    exit 1
fi

# Git limpo (ignora untracked)
if [ -n "$(git status --porcelain -uno)" ]; then
    log_err "Há mudanças não commitadas. Faça commit + push primeiro."
    git status --short -uno
    exit 1
fi

# Push feito
git fetch origin "$BRANCH" 2>/dev/null || {
    log_err "git fetch falhou. Verifique: git remote -v"
    exit 1
}
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "none")
if [ "$REMOTE" = "none" ] || [ "$LOCAL" != "$REMOTE" ]; then
    log_err "Execute: git push origin $BRANCH (local e remoto divergem)"
    exit 1
fi

log_ok "Pré-requisitos OK (commit ${LOCAL:0:7})"

# =============================================================================
# FASE 2 — Verificar .env.prod e obter commit atual na VM (rollback anchor)
# =============================================================================
log_info "Fase 2: Verificando VM e registrando âncora de rollback..."

ROLLBACK_COMMIT=$(ssh -o ConnectTimeout=15 "$VM_HOST" "
    # Verificar .env.prod
    if [ ! -f '$VM_PATH/.env.prod' ]; then
        echo 'MISSING_ENV'
        exit 0
    fi
    # Retornar commit atual
    cd '$VM_PATH' && git rev-parse HEAD 2>/dev/null || echo 'no_git'
")

if [ "$ROLLBACK_COMMIT" = "MISSING_ENV" ]; then
    log_err ".env.prod não encontrado na VM em $VM_PATH/"
    echo ""
    echo "   Crie na VM:"
    echo "   ssh $VM_HOST"
    echo "   cp $VM_PATH/.env.prod.example $VM_PATH/.env.prod"
    echo "   nano $VM_PATH/.env.prod   # Preencher secrets"
    echo "   chmod 600 $VM_PATH/.env.prod"
    exit 1
fi

log_ok "Âncora de rollback: ${ROLLBACK_COMMIT:0:7}"

# =============================================================================
# FASE 3 — Deploy na VM
# =============================================================================
log_info "Fase 3: Executando deploy na VM..."

DEPLOY_SUCCESS=false

ssh -o ConnectTimeout=30 -o ServerAliveInterval=60 "$VM_HOST" "
    set -e
    cd '$VM_PATH' || exit 1

    echo '📥 Git pull...'
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    echo \"   Commit: \$(git rev-parse --short HEAD)\"

    echo ''
    echo '🔍 Verificando portas antes do build...'
    for PORT in 8000 3003 3001; do
        USED=\$(ss -tlnp 2>/dev/null | awk -v p=\":$PORT\" '\$4 ~ p' | wc -l)
        if [ \"\$USED\" -gt 0 ]; then
            # Verificar se é nosso container (OK) ou outro processo (warn)
            CONTAINER=\$(docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null | grep \":$PORT->\" | awk '{print \$1}')
            if [ -n \"\$CONTAINER\" ]; then
                echo \"   ♻️  Porta \$PORT: container '\$CONTAINER' (será substituído)\"
            else
                echo \"   ⚠️  Porta \$PORT: outro processo — verifique manualmente\"
            fi
        else
            echo \"   ✅ Porta \$PORT: livre\"
        fi
    done

    echo ''
$(if [ "$SKIP_BUILD" = "--skip-build" ]; then
    echo "    echo '⚡ --skip-build: pulando rebuild de imagens...'"
    echo "    docker compose -f '$COMPOSE_FILE' --env-file .env.prod up -d"
else
    echo "    echo '🔨 Build das imagens Docker (pode levar alguns minutos)...'"
    echo "    docker compose -f '$COMPOSE_FILE' --env-file .env.prod build"
    echo "    echo ''"
    echo "    echo '🐳 Subindo containers...'"
    echo "    docker compose -f '$COMPOSE_FILE' --env-file .env.prod up -d"
fi)

    echo ''
    echo '🗄️  Aguardando backend ficar pronto...'
    for i in \$(seq 1 12); do
        if docker exec finup_backend_prod curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
            echo '   Backend pronto!'
            break
        fi
        if [ \"\$i\" -eq 12 ]; then
            echo '   Timeout aguardando backend'
            exit 1
        fi
        echo \"   Tentativa \$i/12...\"
        sleep 5
    done

    echo ''
    echo '🗄️  Executando migrations Alembic...'
    docker exec finup_backend_prod alembic upgrade head
    echo '   Migrations OK'
" && DEPLOY_SUCCESS=true || DEPLOY_SUCCESS=false

# =============================================================================
# FASE 4 — Health Check
# =============================================================================
log_info "Fase 4: Health check pós-deploy..."

HEALTH_OK=false
for i in 1 2 3; do
    sleep 5
    STATUS=$(ssh -o ConnectTimeout=10 "$VM_HOST" \
        "curl -sf http://localhost:8000/api/health 2>/dev/null" 2>/dev/null || echo "fail")
    if echo "$STATUS" | grep -q '"healthy"'; then
        HEALTH_OK=true
        log_ok "Health check OK: $STATUS"
        break
    else
        log_warn "Tentativa $i/3 falhou: $STATUS"
    fi
done

# =============================================================================
# FASE 5 — Rollback se necessário
# =============================================================================
if [ "$DEPLOY_SUCCESS" = "false" ] && [ "$HEALTH_OK" = "false" ]; then
    echo ""
    log_err "DEPLOY FALHOU! Iniciando rollback automático..."
    log_info "Rollback para commit: ${ROLLBACK_COMMIT:0:7}"

    ssh -o ConnectTimeout=30 "$VM_HOST" "
        set -e
        cd '$VM_PATH'

        echo '⏪ Revertendo para commit $ROLLBACK_COMMIT...'
        git fetch origin
        git checkout '$ROLLBACK_COMMIT' -- .
        git checkout '$BRANCH'
        git reset --hard '$ROLLBACK_COMMIT'

        echo '🛑 Parando containers atuais...'
        docker compose -f '$COMPOSE_FILE' --env-file .env.prod down 2>/dev/null || true

        echo '🔨 Rebuild imagens com código anterior...'
        docker compose -f '$COMPOSE_FILE' --env-file .env.prod build

        echo '🐳 Subindo containers com versão anterior...'
        docker compose -f '$COMPOSE_FILE' --env-file .env.prod up -d

        echo '⏳ Aguardando backend...'
        sleep 15
        curl -sf http://localhost:8000/api/health && echo '  ✅ Rollback OK' || echo '  ❌ Backend ainda falhando!'
    " || true

    echo ""
    log_err "Verifique os logs: ssh $VM_HOST 'docker compose -f $VM_PATH/$COMPOSE_FILE logs --tail=50'"
    exit 1
fi

# =============================================================================
# SUCESSO
# =============================================================================
echo ""
echo "=========================================="
log_ok "DEPLOY CONCLUÍDO COM SUCESSO!"
echo ""
echo "   Commit deployado: ${LOCAL:0:7}"
echo "   Rollback âncora : ${ROLLBACK_COMMIT:0:7}"
echo ""
echo "   Frontend App  → https://meufinup.com.br"
echo "   Frontend Admin→ http://$VM_HOST:3001"
echo "   Backend API   → http://$VM_HOST:8000/docs"
echo ""
echo "   Logs: ssh $VM_HOST 'docker compose -f $VM_PATH/$COMPOSE_FILE logs -f backend'"
echo "=========================================="
