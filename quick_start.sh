#!/bin/bash
# Quick Start - Sistema Financeiro v5
# Uso: ./quick_start.sh
#
# ⚠️ ATENÇÃO: Se você renomeou a pasta (ex: V5 → V6), execute ANTES:
#   python check_version.py          # Valida versões
#   python fix_version.py            # Corrige automaticamente
#   (Ver .github/copilot-instructions.md para detalhes)

echo "🚀 Iniciando servidores..."
echo ""

# === VALIDAÇÃO DE PROCESSOS ÓRFÃOS ===
echo "🔍 Verificando processos órfãos..."

# Contar processos Node (excluindo VS Code)
NODE_COUNT=$(ps aux | grep node | grep -v grep | grep -v "Visual Studio Code" | grep -v "/Applications/" | wc -l | xargs)

# Contar processos Python/Uvicorn
PYTHON_COUNT=$(ps aux | grep -E "(python.*run\.py|uvicorn)" | grep -v grep | wc -l | xargs)

TOTAL=$((NODE_COUNT + PYTHON_COUNT))

echo "   Node.js: $NODE_COUNT processos"
echo "   Python:  $PYTHON_COUNT processos"
echo "   Total:   $TOTAL processos"
echo ""

# Alertar e limpar se necessário
if [ "$NODE_COUNT" -gt 10 ]; then
    echo "🚨 ALERTA: Detectados $NODE_COUNT processos Node.js órfãos!"
    echo "   Limpando automaticamente..."
    pkill -9 node 2>/dev/null || true
    sleep 1
    echo "   ✅ Processos Node.js limpos"
    echo ""
elif [ "$NODE_COUNT" -gt 5 ]; then
    echo "⚠️  AVISO: Mais processos Node.js ($NODE_COUNT) do que o esperado (2-5)"
    echo "   Limpando automaticamente para evitar lentidão..."
    ps aux | grep node | grep -v grep | grep -v "Visual Studio Code" | grep -v "/Applications/" | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "   ✅ Processos excessivos limpos"
    echo ""
fi

# Limpar portas específicas
echo "🧹 Liberando portas 8000 e 3000..."
BACKEND_PROCS=$(lsof -ti:8000 2>/dev/null | wc -l | xargs)
FRONTEND_PROCS=$(lsof -ti:3000 2>/dev/null | wc -l | xargs)

if [ "$BACKEND_PROCS" -gt 0 ]; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "   Limpos $BACKEND_PROCS processos na porta 8000"
fi

if [ "$FRONTEND_PROCS" -gt 0 ]; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "   Limpos $FRONTEND_PROCS processos na porta 3000"
fi

echo "   ✅ Portas liberadas"
echo ""

# Verificar se node_modules existe no frontend
if [ ! -d "/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/node_modules" ]; then
    echo "⚠️  node_modules não encontrado no frontend!"
    echo "   Executando npm install..."
    cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend
    npm install > /dev/null 2>&1
    cd ../..
    echo ""
fi

# Backend (porta 8000)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev
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

# === VALIDAÇÃO PÓS-INICIALIZAÇÃO ===
FINAL_NODE=$(ps aux | grep node | grep -v grep | grep -v "Visual Studio Code" | grep -v "/Applications/" | wc -l | xargs)
FINAL_PYTHON=$(ps aux | grep -E "(python.*run\.py|uvicorn)" | grep -v grep | wc -l | xargs)

echo ""
echo "✅ Servidores iniciados com sucesso!"
echo ""
echo "🌐 URLs:"
echo "   Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Processos ativos:"
echo "   Node.js: $FINAL_NODE"
echo "   Python:  $FINAL_PYTHON"
if [ "$FINAL_NODE" -le 5 ] && [ "$FINAL_PYTHON" -le 3 ]; then
    echo "   Status: ✅ Normal"
else
    echo "   Status: ⚠️  Acima do esperado (monitore a performance)"
fi
echo ""
echo "📋 Logs:"
echo "   tail -f backend.log"
echo "   tail -f frontend.log"
echo ""
echo "🛑 Para parar: ./quick_stop.sh"

