#!/bin/bash
# =============================================================================
# FinUp - Gerenciador do Ambiente Docker de Desenvolvimento
# =============================================================================
# Uso: ./scripts/docker/dev.sh [COMANDO] [SERVIÇO]
#
# Comandos:
#   start              Sobe containers + aguarda saúde + mostra URLs
#   stop               Para containers (preserva dados)
#   restart [svc]      Reinicia containers (sem rebuild)
#   rebuild <svc>      Rebuild imagem + restart do serviço
#   rebuild-all        Rebuild todas as imagens + restart completo
#   status             Status detalhado com saúde de cada container
#   logs [svc]         Logs em tempo real (svc: backend|app|admin|db|all)
#   shell              Abre bash no container do backend
#   db                 Abre psql no PostgreSQL
#   clean              Para e remove volumes (APAGA DADOS - pede confirmação)
#   help               Exibe esta ajuda
#
# Serviços disponíveis: backend, app (frontend-app), admin (frontend-admin), db
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
HEALTH_TIMEOUT=90   # segundos máximos aguardando health
HEALTH_INTERVAL=2   # segundos entre verificações

# Containers com healthcheck configurado
HEALTHY_CONTAINERS=(
    "finup_backend_dev"
    "finup_postgres_dev"
    "finup_redis_dev"
)

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
info()    { echo -e "${GREEN}▶${NC}  $*"; }
warn()    { echo -e "${YELLOW}⚠${NC}  $*"; }
error()   { echo -e "${RED}✖${NC}  $*" >&2; }
step()    { echo -e "${CYAN}   $*${NC}"; }
ok()      { echo -e "${GREEN}✔${NC}  $*"; }
header()  { echo ""; echo -e "${BOLD}$*${NC}"; echo ""; }

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Inicie o Docker Desktop e tente novamente."
        exit 1
    fi
}

# Aguarda container atingir status "healthy" (ou "running" se não tem healthcheck)
wait_healthy() {
    local container="$1"
    local label="${2:-$container}"
    local elapsed=0

    printf "   %-35s" "$label"

    while [ $elapsed -lt $HEALTH_TIMEOUT ]; do
        local health
        health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container" 2>/dev/null || echo "missing")

        case "$health" in
            healthy|running)
                echo -e " ${GREEN}✔ healthy${NC}"
                return 0
                ;;
            unhealthy)
                echo -e " ${RED}✖ unhealthy${NC}"
                return 1
                ;;
            missing)
                echo -e " ${RED}✖ não encontrado${NC}"
                return 1
                ;;
        esac

        printf "."
        sleep $HEALTH_INTERVAL
        elapsed=$((elapsed + HEALTH_INTERVAL))
    done

    echo -e " ${YELLOW}⏱ timeout${NC}"
    return 1
}

# Aguarda todos os containers com healthcheck ficarem saudáveis
wait_all_healthy() {
    local any_failed=0
    step "Aguardando serviços ficarem prontos..."

    for container in "${HEALTHY_CONTAINERS[@]}"; do
        local label
        case "$container" in
            finup_backend_dev)   label="Backend (FastAPI)" ;;
            finup_postgres_dev)  label="PostgreSQL" ;;
            finup_redis_dev)     label="Redis" ;;
            *)                   label="$container" ;;
        esac
        wait_healthy "$container" "$label" || any_failed=1
    done

    return $any_failed
}

# Mostra URLs de acesso
show_urls() {
    echo ""
    echo -e "${BOLD}   URLs de acesso:${NC}"
    echo -e "   ${GREEN}●${NC} App Principal   ${BOLD}http://localhost:3000${NC}"
    echo -e "   ${YELLOW}●${NC} Painel Admin    ${BOLD}http://localhost:3001${NC}"
    echo -e "   ${CYAN}●${NC} Backend API     ${BOLD}http://localhost:8000/docs${NC}"
    echo -e "   ${DIM}●  Health Check   http://localhost:8000/api/health${NC}"
    echo ""
    echo -e "   ${DIM}Login: admin@financas.com / Admin123!${NC}"
    echo ""
}

# Mostra status colorido de todos os containers
show_status() {
    local containers=("finup_postgres_dev" "finup_redis_dev" "finup_backend_dev" "finup_frontend_app_dev" "finup_frontend_admin_dev")
    local labels=("PostgreSQL" "Redis" "Backend" "Frontend App" "Frontend Admin")

    echo ""
    printf "   %-22s %-12s %-12s %s\n" "SERVIÇO" "STATUS" "SAÚDE" "PORTA(S)"
    printf "   %-22s %-12s %-12s %s\n" "-------" "------" "-----" "-------"

    for i in "${!containers[@]}"; do
        local container="${containers[$i]}"
        local label="${labels[$i]}"

        local state health ports
        state=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "stopped")
        health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}-{{end}}' "$container" 2>/dev/null || echo "-")
        ports=$(docker inspect --format='{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{(index $conf 0).HostPort}} {{end}}{{end}}' "$container" 2>/dev/null | xargs 2>/dev/null || echo "-")

        local state_color="$NC"
        local health_color="$NC"
        case "$state" in
            running) state_color="$GREEN" ;;
            exited|dead) state_color="$RED" ;;
        esac
        case "$health" in
            healthy) health_color="$GREEN" ;;
            unhealthy) health_color="$RED" ;;
            starting) health_color="$YELLOW" ;;
        esac

        printf "   %-22s ${state_color}%-12s${NC} ${health_color}%-12s${NC} %s\n" \
            "$label" "$state" "$health" "${ports:--}"
    done
    echo ""
}

# Detecta se rebuild é necessário (Dockerfile ou requirements/package.json modificados)
needs_rebuild() {
    local service="$1"
    local image_name="projetofinancasv5-${service}"

    # Se imagem não existe, precisa build
    if ! docker image inspect "$image_name" > /dev/null 2>&1; then
        return 0
    fi

    local image_created
    image_created=$(docker image inspect --format='{{.Created}}' "$image_name" 2>/dev/null | cut -c1-19 | tr 'T' ' ')
    local image_epoch
    image_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$image_created" "+%s" 2>/dev/null || \
                  date -d "$image_created" "+%s" 2>/dev/null || echo "0")

    local check_files=()
    case "$service" in
        backend)
            check_files=("$ROOT_DIR/app_dev/backend/requirements.txt" "$ROOT_DIR/app_dev/backend/Dockerfile")
            ;;
        frontend-app)
            check_files=("$ROOT_DIR/app_dev/frontend/package.json")
            ;;
        frontend-admin)
            check_files=("$ROOT_DIR/app_admin/frontend/package.json")
            ;;
    esac

    for f in "${check_files[@]}"; do
        if [ -f "$f" ]; then
            local file_epoch
            file_epoch=$(date -r "$f" "+%s" 2>/dev/null || echo "0")
            if [ "$file_epoch" -gt "$image_epoch" ]; then
                return 0  # precisa rebuild
            fi
        fi
    done

    return 1
}

# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

cmd_start() {
    check_docker
    header "🐳 FinUp — Iniciando ambiente de desenvolvimento"

    # Detectar serviços que precisam de rebuild
    local rebuild_needed=()
    for svc in backend frontend-app frontend-admin; do
        if needs_rebuild "$svc"; then
            rebuild_needed+=("$svc")
        fi
    done

    if [ ${#rebuild_needed[@]} -gt 0 ]; then
        warn "Mudanças detectadas em: ${rebuild_needed[*]}"
        step "Rebuilding imagens modificadas..."
        (cd "$ROOT_DIR" && docker-compose build "${rebuild_needed[@]}" 2>&1 | \
            grep -E "^Step|^#[0-9]+ \[|Successfully built|ERROR" | sed 's/^/   /') || true
        echo ""
    fi

    info "Subindo containers..."
    (cd "$ROOT_DIR" && docker-compose up -d 2>&1 | grep -v "^$" | sed 's/^/   /') || true
    echo ""

    wait_all_healthy && show_urls || {
        echo ""
        warn "Algum serviço não ficou saudável. Verifique os logs:"
        step "./scripts/docker/dev.sh logs backend"
    }
}

cmd_stop() {
    check_docker
    header "🐳 FinUp — Parando ambiente"
    info "Parando containers (dados preservados)..."
    (cd "$ROOT_DIR" && docker-compose down 2>&1 | grep -v "^$" | sed 's/^/   /') || true
    ok "Containers parados."
    echo ""
}

cmd_restart() {
    local service="${1:-}"
    check_docker
    header "🐳 FinUp — Reiniciando"

    if [ -n "$service" ]; then
        local compose_svc
        case "$service" in
            app) compose_svc="frontend-app" ;;
            admin) compose_svc="frontend-admin" ;;
            db) compose_svc="postgres" ;;
            *) compose_svc="$service" ;;
        esac
        info "Reiniciando: $compose_svc"
        (cd "$ROOT_DIR" && docker-compose restart "$compose_svc")
        ok "Serviço $compose_svc reiniciado."
    else
        info "Reiniciando todos os containers..."
        (cd "$ROOT_DIR" && docker-compose restart)
        echo ""
        wait_all_healthy && ok "Todos os serviços prontos." || \
            warn "Verifique: ./scripts/docker/dev.sh status"
    fi
    echo ""
}

cmd_rebuild() {
    local service="${1:-}"
    check_docker

    if [ -z "$service" ]; then
        warn "Especifique um serviço: backend | app | admin"
        step "Para rebuild de tudo: ./scripts/docker/dev.sh rebuild-all"
        exit 1
    fi

    local compose_svc
    case "$service" in
        app) compose_svc="frontend-app" ;;
        admin) compose_svc="frontend-admin" ;;
        *) compose_svc="$service" ;;
    esac

    header "🐳 FinUp — Rebuild: $compose_svc"
    info "Rebuilding imagem..."
    (cd "$ROOT_DIR" && docker-compose build "$compose_svc")
    info "Recriando container (volumes anônimos renovados)..."
    # -v remove volumes anônimos (ex: node_modules) para pegar a nova imagem
    (cd "$ROOT_DIR" && docker-compose stop "$compose_svc" 2>/dev/null || true)
    (cd "$ROOT_DIR" && docker-compose rm -f -v "$compose_svc" 2>/dev/null || true)
    (cd "$ROOT_DIR" && docker-compose up -d "$compose_svc")
    echo ""

    # Aguardar health apenas para serviços que têm healthcheck
    case "$compose_svc" in
        backend)
            wait_healthy "finup_backend_dev" "Backend" || \
                warn "Backend não ficou healthy. Verifique: ./scripts/docker/dev.sh logs backend"
            ;;
        postgres)
            wait_healthy "finup_postgres_dev" "PostgreSQL" || true
            ;;
        redis)
            wait_healthy "finup_redis_dev" "Redis" || true
            ;;
        *)
            sleep 5  # frontends não têm healthcheck, aguardar brevemente
            ok "$compose_svc recriado."
            ;;
    esac
    echo ""
}

cmd_rebuild_all() {
    check_docker
    header "🐳 FinUp — Rebuild completo"
    warn "Isso pode levar alguns minutos..."

    info "Parando containers..."
    (cd "$ROOT_DIR" && docker-compose down)
    echo ""

    info "Rebuilding todas as imagens..."
    (cd "$ROOT_DIR" && docker-compose build 2>&1 | \
        grep -E "^Step|^#[0-9]+ \[|Successfully built|ERROR" | sed 's/^/   /') || true
    echo ""

    info "Subindo containers..."
    (cd "$ROOT_DIR" && docker-compose up -d 2>&1 | grep -v "^$" | sed 's/^/   /') || true
    echo ""

    wait_all_healthy && show_urls || \
        warn "Verifique: ./scripts/docker/dev.sh logs"
}

cmd_status() {
    check_docker
    header "🐳 FinUp — Status dos containers"
    show_status

    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        ok "Backend API respondendo em http://localhost:8000"
    else
        warn "Backend API não está respondendo em localhost:8000"
    fi
    echo ""
}

cmd_logs() {
    local target="${1:-all}"
    check_docker

    case "$target" in
        backend|back)   (cd "$ROOT_DIR" && docker-compose logs -f backend) ;;
        app|frontend)   (cd "$ROOT_DIR" && docker-compose logs -f frontend-app) ;;
        admin)          (cd "$ROOT_DIR" && docker-compose logs -f frontend-admin) ;;
        db|postgres)    (cd "$ROOT_DIR" && docker-compose logs -f postgres) ;;
        redis)          (cd "$ROOT_DIR" && docker-compose logs -f redis) ;;
        all|*)          (cd "$ROOT_DIR" && docker-compose logs -f) ;;
    esac
}

cmd_shell() {
    check_docker
    info "Abrindo shell no backend..."
    (cd "$ROOT_DIR" && docker-compose exec backend /bin/bash)
}

cmd_db() {
    check_docker
    info "Abrindo PostgreSQL (finup_db)..."
    (cd "$ROOT_DIR" && docker-compose exec postgres psql -U finup_user -d finup_db)
}

cmd_clean() {
    check_docker
    echo ""
    echo -e "${RED}${BOLD}⚠️  ATENÇÃO: OPERAÇÃO DESTRUTIVA${NC}"
    echo ""
    echo "   Isso vai parar todos os containers e APAGAR TODOS OS VOLUMES,"
    echo "   incluindo o banco de dados PostgreSQL e dados do Redis."
    echo ""
    read -p "   Tem certeza? Digite 'sim' para confirmar: " -r
    echo ""
    if [[ $REPLY == "sim" ]]; then
        (cd "$ROOT_DIR" && docker-compose down -v)
        ok "Volumes removidos."
    else
        info "Operação cancelada."
    fi
    echo ""
}

cmd_help() {
    echo ""
    echo -e "${BOLD}🐳 FinUp — Gerenciador Docker de Desenvolvimento${NC}"
    echo ""
    echo -e "   ${BOLD}Uso:${NC} ./scripts/docker/dev.sh [COMANDO] [SERVIÇO]"
    echo ""
    echo -e "   ${BOLD}Comandos principais:${NC}"
    echo "   start              Sobe tudo + detecta rebuilds + aguarda saúde"
    echo "   stop               Para todos os containers (dados preservados)"
    echo "   restart [svc]      Reinicia sem rebuild. Sem svc = reinicia tudo"
    echo "   rebuild <svc>      Rebuild imagem + recria container do serviço"
    echo "   rebuild-all        Rebuild completo + restart"
    echo "   status             Status detalhado com saúde de cada container"
    echo ""
    echo -e "   ${BOLD}Utilitários:${NC}"
    echo "   logs [svc]         Logs em tempo real"
    echo "   shell              Bash no container backend"
    echo "   db                 psql no PostgreSQL (finup_db)"
    echo "   clean              Para + apaga volumes (DESTRUTIVO)"
    echo ""
    echo -e "   ${BOLD}Serviços:${NC} backend, app, admin, db, redis"
    echo ""
    echo -e "   ${BOLD}Exemplos:${NC}"
    echo "   ./scripts/docker/dev.sh start"
    echo "   ./scripts/docker/dev.sh rebuild backend   # após mudar requirements.txt"
    echo "   ./scripts/docker/dev.sh logs backend      # acompanhar logs do backend"
    echo "   ./scripts/docker/dev.sh restart app       # reiniciar só o frontend"
    echo "   ./scripts/docker/dev.sh status            # ver saúde de tudo"
    echo ""
}

# ---------------------------------------------------------------------------
# Roteamento de comandos
# ---------------------------------------------------------------------------
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    start)        cmd_start ;;
    stop)         cmd_stop ;;
    restart)      cmd_restart "${1:-}" ;;
    rebuild)      cmd_rebuild "${1:-}" ;;
    rebuild-all)  cmd_rebuild_all ;;
    status)       cmd_status ;;
    logs)         cmd_logs "${1:-all}" ;;
    shell)        cmd_shell ;;
    db)           cmd_db ;;
    clean)        cmd_clean ;;
    help|--help|-h) cmd_help ;;
    # aliases legados (compatibilidade)
    up)           cmd_start ;;
    down)         cmd_stop ;;
    ps)           cmd_status ;;
    build)        cmd_rebuild_all ;;
    exec-back)    cmd_shell ;;
    exec-db)      cmd_db ;;
    logs-back)    cmd_logs backend ;;
    logs-app)     cmd_logs app ;;
    logs-admin)   cmd_logs admin ;;
    *)
        error "Comando desconhecido: $COMMAND"
        cmd_help
        exit 1
        ;;
esac
