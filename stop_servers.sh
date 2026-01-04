#!/bin/bash
# 🛑 SCRIPT PARA PARAR TODOS OS SERVIDORES
# ========================================

echo "🛑 PARANDO SERVIDORES FINANCASV3..."

# Parar backend
echo "⏹️  Parando backend (porta 8000)..."
pkill -f "uvicorn.*app.main" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Parar frontend  
echo "⏹️  Parando frontend (porta 3000)..."
pkill -f "next dev" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Parar outros processos relacionados
pkill -f "python.*run.py" 2>/dev/null || true

sleep 2

# Verificar se pararam
BACKEND_RUNNING=$(lsof -ti:8000 | wc -l)
FRONTEND_RUNNING=$(lsof -ti:3000 | wc -l)

if [ "$BACKEND_RUNNING" -eq "0" ]; then
    echo "✅ Backend parado"
else
    echo "❌ Backend ainda rodando"
fi

if [ "$FRONTEND_RUNNING" -eq "0" ]; then
    echo "✅ Frontend parado"
else
    echo "❌ Frontend ainda rodando"
fi

echo ""
echo "🎯 Servidores parados!"
echo "Para reiniciar: ./start_servers.sh"