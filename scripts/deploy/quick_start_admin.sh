#!/bin/bash
# Inicia Backend + App Admin (para desenvolvimento local)
# Uso: ./scripts/deploy/quick_start_admin.sh
#
# Pré-requisito: Backend (app_dev) deve estar rodando na porta 8000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Iniciando Backend + App Admin..."
echo ""

# Backend na 8000
BACKEND_PROCS=$(lsof -ti:8000 2>/dev/null | wc -l | xargs)
if [ "$BACKEND_PROCS" -eq 0 ]; then
    echo "▶️  Iniciando backend (porta 8000)..."
    cd "$PROJECT_ROOT/app_dev"
    if [ ! -f "venv/bin/activate" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r backend/requirements.txt -q
    else
        source venv/bin/activate
    fi
    mkdir -p "$PROJECT_ROOT/temp/logs" "$PROJECT_ROOT/temp/pids"
    nohup "$PROJECT_ROOT/app_dev/venv/bin/python" backend/run.py > "$PROJECT_ROOT/temp/logs/backend.log" 2>&1 &
    echo $! > "$PROJECT_ROOT/temp/pids/backend.pid"
    sleep 3
    if curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        echo "   ✅ Backend OK"
    else
        echo "   ⚠️  Backend pode estar iniciando... verifique: tail -f temp/logs/backend.log"
    fi
    cd "$PROJECT_ROOT"
else
    echo "   ✅ Backend já rodando (porta 8000)"
fi

# App Admin na 3001
echo ""
echo "▶️  Iniciando app_admin (porta 3001)..."
cd "$PROJECT_ROOT/app_admin/frontend"
if [ ! -f ".env.local" ]; then
    echo "   Criando .env.local com NEXT_PUBLIC_BACKEND_URL=http://localhost:8000"
    echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
fi
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
echo $! > "$PROJECT_ROOT/temp/pids/admin.pid"
cd "$PROJECT_ROOT"
sleep 3

echo ""
echo "✅ Pronto!"
echo ""
echo "🌐 URLs:"
echo "   Backend:   http://127.0.0.1:8000"
echo "   App Admin: http://localhost:3001"
echo ""
echo "   Faça login em /login e acesse /admin"
echo ""
