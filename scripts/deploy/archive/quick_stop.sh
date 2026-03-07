#!/bin/bash
# Quick Stop - Sistema Financeiro v5
# Uso: ./quick_stop.sh (pode rodar de qualquer pasta)
#
# Mata APENAS processos nas portas 8000 e 3000-3005.
# Nunca mata processos por nome (evita afetar Cursor/IDE).

# Ir para raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🛑 Parando servidores..."
echo "   Projeto: $PROJECT_ROOT"
echo ""

# Função para matar processo e seus filhos (evita órfãos)
kill_tree() {
    local pid=$1
    [ -z "$pid" ] && return
    local children=$(pgrep -P $pid 2>/dev/null)
    for child in $children; do
        kill_tree $child
    done
    kill -9 $pid 2>/dev/null || true
}

# 1. Parar via PIDs salvos (mais limpo)
if [ -f "$PROJECT_ROOT/temp/pids/backend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/temp/pids/backend.pid")
    kill_tree $PID
    echo "✅ Backend parado (PID: $PID)"
    rm -f "$PROJECT_ROOT/temp/pids/backend.pid"
fi

if [ -f "$PROJECT_ROOT/temp/pids/frontend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/temp/pids/frontend.pid")
    kill_tree $PID
    echo "✅ Frontend parado (PID: $PID)"
    rm -f "$PROJECT_ROOT/temp/pids/frontend.pid"
fi

if [ -f "$PROJECT_ROOT/temp/pids/admin.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/temp/pids/admin.pid")
    kill_tree $PID
    echo "✅ App Admin parado (PID: $PID)"
    rm -f "$PROJECT_ROOT/temp/pids/admin.pid"
fi

# 2. Garantir portas livres (processos órfãos que não foram registrados)
BACKEND_ORPHANS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_ORPHANS" ]; then
    echo "$BACKEND_ORPHANS" | xargs kill -9 2>/dev/null
    echo "🧹 Limpos processos órfãos na porta 8000"
fi

for PORT in 3000 3001 3002 3003 3004 3005; do
    FRONTEND_ORPHANS=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$FRONTEND_ORPHANS" ]; then
        echo "$FRONTEND_ORPHANS" | xargs kill -9 2>/dev/null
        echo "🧹 Limpos processos órfãos na porta $PORT"
    fi
done

echo ""
echo "✅ Servidores parados. Portas 8000 e 3000-3005 liberadas."
