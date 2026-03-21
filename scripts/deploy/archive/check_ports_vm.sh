#!/bin/bash

# =============================================================================
# check_ports_vm.sh — Verifica conflitos de porta na VM antes do deploy Docker
# =============================================================================
#
# Uso: ./scripts/deploy/check_ports_vm.sh
#
# Verifica se as portas usadas pelo docker-compose.prod.yml estão disponíveis:
#   8000 → Backend FastAPI
#   3003 → Frontend App (meufinup.com.br)
#   3001 → Frontend Admin
# =============================================================================

set -e

VM_HOST="${VM_HOST:-minha-vps-hostinger}"
PORTS=(8000 3003 3001)
CONTAINER_NAMES=("finup_backend_prod" "finup_frontend_app_prod" "finup_frontend_admin_prod")

echo "🔍 Verificando portas na VM ($VM_HOST)..."
echo "=========================================="

ssh -o ConnectTimeout=15 "$VM_HOST" "
set -e

check_port() {
    local PORT=\$1
    # ss: lista sockets TCP em escuta
    local INFO=\$(ss -tlnp 2>/dev/null | awk -v p=\":${1}\" '\$4 ~ p {print \$0}' | head -1)

    if [ -z \"\$INFO\" ]; then
        echo \"  ✅ Porta \$PORT: LIVRE\"
        return 0
    fi

    # Tentar extrair PID
    local PID=\$(echo \"\$INFO\" | grep -oP 'pid=\K[0-9]+' | head -1)
    local PROC=\"desconhecido\"
    if [ -n \"\$PID\" ]; then
        PROC=\$(ps -p \"\$PID\" -o comm= 2>/dev/null || echo 'desconhecido')
    fi

    # Verificar se é nosso Docker
    if docker ps --format '{{.Ports}}' 2>/dev/null | grep -q \":\$PORT->\"; then
        local CONTAINER=\$(docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null | grep \":\$PORT->\" | awk '{print \$1}')
        echo \"  ♻️  Porta \$PORT: ocupada pelo container Docker '\$CONTAINER' — será substituído\"
    elif echo \"\$PROC\" | grep -qE 'docker|containerd|dockerd'; then
        echo \"  ♻️  Porta \$PORT: gerenciada pelo Docker daemon — OK\"
    elif echo \"\$PROC\" | grep -qE 'node|uvicorn|python|nginx'; then
        echo \"  ⚠️  Porta \$PORT: processo '\$PROC' (PID \$PID) — deploy anterior não-Docker\"
        echo \"         Pare antes: pkill -f 'PORT \$PORT'\"
    else
        echo \"  ❌ Porta \$PORT: ocupada por '\$PROC' (PID \$PID) — CONFLITO!\"
    fi
}

# ─── Verificar portas ─────────────────────────────────────────────
echo \"\"
echo \"📡 Verificando portas do docker-compose.prod.yml:\"
for PORT in 8000 3003 3001; do
    check_port \$PORT
done

# ─── Status Docker ────────────────────────────────────────────────
echo \"\"
echo \"📦 Containers rodando na VM:\"
if docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null | head -10; then
    :
else
    echo \"  Docker não disponível ou sem containers\"
fi

# ─── Memória disponível ───────────────────────────────────────────
echo \"\"
echo \"💾 Recursos do servidor:\"
free -h | awk 'NR==2{printf \"  RAM: %s livre de %s\\n\", \$4, \$2}'
df -h / | awk 'NR==2{printf \"  Disco /: %s livre de %s\\n\", \$4, \$2}'

echo \"\"
echo \"✅ Verificação concluída\"
"

echo ""
echo "💡 Se tudo OK, execute: ./scripts/deploy/deploy_docker_vm.sh"
