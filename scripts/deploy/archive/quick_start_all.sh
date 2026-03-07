#!/bin/bash
# Quick Start COMPLETO - Backend + BAU (3000) + App Admin (3001)
# Uso: ./scripts/deploy/quick_start_all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Iniciando TUDO (Backend + BAU + App Admin)..."
echo "   Projeto: $PROJECT_ROOT"
echo ""

# 1. Parar processos existentes
echo "🧹 Parando processos nas portas 8000, 3000-3005..."
for PORT in 8000 3000 3001 3002 3003 3004 3005; do
    PIDS=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        echo "   Limpos processos na porta $PORT"
    fi
done
echo ""

# Garantir que temp/ existe
mkdir -p "$PROJECT_ROOT/temp/logs" "$PROJECT_ROOT/temp/pids"

# 2. Backend (porta 8000)
echo "▶️  Backend (porta 8000)..."
cd "$PROJECT_ROOT/app_dev"
if [ ! -f "venv/bin/activate" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt -q
else
    source venv/bin/activate
fi
cd "$PROJECT_ROOT/app_dev/backend"
nohup "$PROJECT_ROOT/app_dev/venv/bin/python" run.py > "$PROJECT_ROOT/temp/logs/backend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/temp/pids/backend.pid"
sleep 3
if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "   ✅ Backend OK"
else
    echo "   ⚠️  Backend iniciando... tail -f temp/logs/backend.log"
fi
echo ""

# 3. Frontend BAU (porta 3000)
echo "▶️  Frontend BAU (porta 3000)..."
cd "$PROJECT_ROOT/app_dev/frontend"
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
fi
nohup npm run dev > "$PROJECT_ROOT/temp/logs/frontend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/temp/pids/frontend.pid"
sleep 2
echo "   ✅ BAU iniciado"
echo ""

# 4. App Admin (porta 3001)
echo "▶️  App Admin (porta 3001)..."
cd "$PROJECT_ROOT/app_admin/frontend"
if [ ! -f ".env.local" ]; then
    echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
fi
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
fi
nohup npm run dev > "$PROJECT_ROOT/temp/logs/admin.log" 2>&1 &
echo $! > "$PROJECT_ROOT/temp/pids/admin.pid"
sleep 3
echo "   ✅ App Admin iniciado"
echo ""

echo "✅ Tudo rodando!"
echo ""
echo "🌐 URLs:"
echo "   Backend:   http://localhost:8000"
echo "   BAU:       http://localhost:3000"
echo "   App Admin: http://localhost:3001"
echo ""
echo "📋 Logs:"
echo "   tail -f $PROJECT_ROOT/temp/logs/backend.log"
echo "   tail -f $PROJECT_ROOT/temp/logs/frontend.log"
echo "   tail -f $PROJECT_ROOT/temp/logs/admin.log"
echo ""
echo "🛑 Parar tudo: $SCRIPT_DIR/quick_stop.sh"
echo ""
