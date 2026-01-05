#!/bin/bash
# Quick Start - Sistema Financeiro v4
# Uso: ./quick_start.sh

echo "🚀 Iniciando servidores..."

# Limpar portas
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Backend (porta 8000)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev
source venv/bin/activate
cd backend
nohup python run.py > ../../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../../backend.pid
cd ../..

sleep 3

# Frontend (porta 3000)
cd app_dev/frontend
nohup npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../frontend.pid
cd ../..

sleep 2

echo ""
echo "✅ Servidores iniciados!"
echo "   Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "📋 Logs:"
echo "   tail -f backend.log"
echo "   tail -f frontend.log"
echo ""
echo "🛑 Para parar: ./quick_stop.sh"
