#!/bin/bash
# Quick Stop - Sistema Financeiro v4
# Uso: ./quick_stop.sh

echo "🛑 Parando servidores..."

# Parar via PIDs
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null && echo "✅ Backend parado" || echo "⚠️  Backend já estava parado"
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null && echo "✅ Frontend parado" || echo "⚠️  Frontend já estava parado"
    rm frontend.pid
fi

# Garantir que portas estão livres
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "✅ Portas 8000 e 3000 liberadas"
