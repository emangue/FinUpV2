#!/bin/bash
# 🚀 GUIA DEFINITIVO - COMO LIGAR OS SERVIDORES
# =============================================
#
# ⚠️  SEMPRE SEGUIR ESTA ORDEM E ESTES COMANDOS!
# ⚠️  SEMPRE FAZER LOGIN COMO user_id = 1
#
# 📁 Diretório Base: /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
#

echo "🚀 INICIANDO SERVIDORES - PROJETO FINANCASV3"
echo "============================================="

# 1️⃣ ATIVAR AMBIENTE VIRTUAL
echo ""
echo "1️⃣  ATIVANDO AMBIENTE VIRTUAL..."
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
source venv/bin/activate
echo "✅ Ambiente virtual ativado"

# 2️⃣ PARAR SERVIDORES ANTIGOS (LIMPEZA)
echo ""
echo "2️⃣  LIMPANDO PROCESSOS ANTIGOS..."
pkill -f "python.*run.py" 2>/dev/null || true
pkill -f "uvicorn.*app.main" 2>/dev/null || true  
pkill -f "next dev" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Processos antigos limpos"

# 3️⃣ INICIAR BACKEND (FastAPI)
echo ""
echo "3️⃣  INICIANDO BACKEND..."
echo "📁 Caminho: /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend"
echo "🌐 Porta: 8000"

cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend

# ⭐ COMANDO CORRETO DO BACKEND COM PYTHONPATH
PYTHONPATH=/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend:/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio \
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

BACKEND_PID=$!
echo "✅ Backend iniciado (PID: $BACKEND_PID)"
echo "🔗 URL: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"

# Aguardar backend estar pronto
echo "⏳ Aguardando backend ficar pronto..."
sleep 5

# Verificar se backend está funcionando
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null; then
        echo "✅ Backend está respondendo!"
        break
    fi
    echo "⏳ Tentativa $i/10..."
    sleep 2
done

# 4️⃣ INICIAR FRONTEND (Next.js)
echo ""
echo "4️⃣  INICIANDO FRONTEND..."
echo "📁 Caminho: /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend"
echo "🌐 Porta: 3000"

cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend

# Limpar cache do Next.js se necessário
if [ -d ".next" ]; then
    echo "🧹 Limpando cache do Next.js..."
    rm -rf .next
fi

# ⭐ COMANDO CORRETO DO FRONTEND
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
echo "🔗 URL: http://localhost:3000"

# Aguardar frontend estar pronto
echo "⏳ Aguardando frontend ficar pronto..."
sleep 8

# 5️⃣ VERIFICAÇÕES FINAIS
echo ""
echo "5️⃣  VERIFICAÇÕES FINAIS..."

# Verificar backend
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend FastAPI: http://localhost:8000 (OK)"
else
    echo "❌ Backend FastAPI: ERRO!"
fi

# Verificar frontend  
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend Next.js: http://localhost:3000 (OK)"
else
    echo "❌ Frontend Next.js: ERRO!"
fi

# Verificar banco de dados
DB_PATH="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db"
if [ -f "$DB_PATH" ]; then
    echo "✅ Banco de dados: $DB_PATH (OK)"
else
    echo "❌ Banco de dados: NÃO ENCONTRADO!"
fi

# 6️⃣ INSTRUÇÕES DE USO
echo ""
echo "🎯 SISTEMA PRONTO!"
echo "=================="
echo ""
echo "📋 URLs IMPORTANTES:"
echo "   🌐 Frontend:     http://localhost:3000"
echo "   ⚙️  Backend API:  http://localhost:8000"
echo "   📖 Documentação: http://localhost:8000/docs"
echo ""
echo "👤 LOGIN OBRIGATÓRIO:"
echo "   ⚠️  SEMPRE FAZER LOGIN COMO user_id = 1"
echo "   📧 Email: admin@example.com"
echo "   🔑 Senha: admin123"
echo ""
echo "🛑 PARA PARAR OS SERVIDORES:"
echo "   pkill -f \"uvicorn.*app.main\""
echo "   pkill -f \"next dev\""
echo ""
echo "📝 PIDs dos processos:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🎉 Bom desenvolvimento!"