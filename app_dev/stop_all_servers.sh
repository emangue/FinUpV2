#!/bin/bash

# Script para parar todos os servidores
echo "🛑 Parando todos os servidores..."

APP_DEV_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev"

# Parar por PIDs se existirem
if [ -f "$APP_DEV_ROOT/frontend.pid" ]; then
    kill $(cat "$APP_DEV_ROOT/frontend.pid") 2>/dev/null && echo "✅ Frontend parado"
    rm -f "$APP_DEV_ROOT/frontend.pid"
fi

if [ -f "$APP_DEV_ROOT/backend/backend.pid" ]; then
    kill $(cat "$APP_DEV_ROOT/backend/backend.pid") 2>/dev/null && echo "✅ Backend parado"
    rm -f "$APP_DEV_ROOT/backend/backend.pid"
fi

# Força parada por porta
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✅ Porta 3000 limpa"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Porta 8000 limpa"

echo "🏁 Todos os servidores foram parados"