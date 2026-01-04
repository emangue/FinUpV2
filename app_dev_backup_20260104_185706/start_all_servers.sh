#!/bin/bash

# Script para iniciar todos os servidores do projeto
# Frontend Next.js + Backend FastAPI

echo "🚀 Iniciando Sistema de Finanças - Arquitetura Mista"
echo "======================================================="

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3"
APP_DEV_ROOT="$PROJECT_ROOT/app_dev"

# Função para limpar processos anteriores
cleanup_ports() {
    echo "🧹 Limpando portas..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
    echo "✅ Portas 3000 e 8000 livres"
}

# Função para iniciar backend
start_backend() {
    echo "⚡ Iniciando Backend FastAPI (porta 8000)..."
    cd "$APP_DEV_ROOT/backend"
    
    # Ativar ambiente virtual
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Instalar dependências se necessário
    pip install -q -r requirements.txt
    
    # Iniciar em background
    nohup python run.py > backend.log 2>&1 &
    echo $! > backend.pid
    
    # Aguardar inicialização
    sleep 3
    
    if lsof -ti:8000 > /dev/null; then
        echo "✅ Backend iniciado com sucesso na porta 8000"
        echo "   Swagger: http://localhost:8000/docs"
        echo "   Health: http://localhost:8000/api/health"
    else
        echo "❌ Erro ao iniciar backend"
        return 1
    fi
}

# Função para iniciar frontend
start_frontend() {
    echo "⚡ Iniciando Frontend Next.js (porta 3000)..."
    cd "$APP_DEV_ROOT/frontend"
    
    # Iniciar em background
    nohup npm run dev > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    
    # Aguardar inicialização
    sleep 4
    
    if lsof -ti:3000 > /dev/null; then
        echo "✅ Frontend iniciado com sucesso na porta 3000"
        echo "   Login: http://localhost:3000/login"
        echo "   Dashboard: http://localhost:3000/dashboard"
    else
        echo "❌ Erro ao iniciar frontend"
        return 1
    fi
}

# Função principal
main() {
    cleanup_ports
    
    if ! start_backend; then
        echo "❌ Falha ao iniciar backend. Abortando."
        exit 1
    fi
    
    if ! start_frontend; then
        echo "❌ Falha ao iniciar frontend. Abortando."
        exit 1
    fi
    
    echo ""
    echo "🎉 SISTEMA INICIADO COM SUCESSO!"
    echo "======================================================="
    echo "Frontend:  http://localhost:3000"
    echo "Backend:   http://localhost:8000"
    echo "Swagger:   http://localhost:8000/docs"
    echo "Credenciais: admin@financas.com / cahriZ-qonby8-cahdud"
    echo ""
    echo "Para parar os servidores:"
    echo "  ./stop_all_servers.sh"
    echo ""
    echo "Logs em tempo real:"
    echo "  tail -f frontend.log"
    echo "  tail -f backend/backend.log"
}

# Executar script principal
main "$@"