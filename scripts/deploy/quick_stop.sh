#!/bin/bash
# Quick Stop - Sistema Financeiro v5
# Uso: ./quick_stop.sh

echo "🛑 Parando servidores..."

# Função para matar processo e seus filhos
kill_tree() {
    local pid=$1
    local children=$(pgrep -P $pid)
    for child in $children; do
        kill_tree $child
    done
    kill -9 $pid 2>/dev/null || true
}

# Parar via PIDs (mata processo pai E filhos)
if [ -f temp/pids/backend.pid ]; then
    PID=$(cat temp/pids/backend.pid)
    kill_tree $PID
    echo "✅ Backend parado (PID: $PID + filhos)"
    rm temp/pids/backend.pid
fi

if [ -f temp/pids/frontend.pid ]; then
    PID=$(cat temp/pids/frontend.pid)
    kill_tree $PID
    echo "✅ Frontend parado (PID: $PID + filhos)"
    rm temp/pids/frontend.pid
fi

# Garantir que portas estão livres (mata processos órfãos)
BACKEND_ORPHANS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_ORPHANS" ]; then
    echo "$BACKEND_ORPHANS" | xargs kill -9 2>/dev/null
    echo "🧹 Limpos $(echo $BACKEND_ORPHANS | wc -w | xargs) processos órfãos na porta 8000"
fi

# Frontend: limpar portas 3000-3005 (Next.js pode usar portas alternativas)
for PORT in 3000 3001 3002 3003 3004 3005; do
    FRONTEND_ORPHANS=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$FRONTEND_ORPHANS" ]; then
        echo "$FRONTEND_ORPHANS" | xargs kill -9 2>/dev/null
        echo "🧹 Limpos $(echo $FRONTEND_ORPHANS | wc -w | xargs) processos órfãos na porta $PORT"
    fi
done

echo "✅ Portas 8000 e 3000-3005 liberadas"
