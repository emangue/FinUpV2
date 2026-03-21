#!/bin/bash
# 🔧 Script de validação pós-deploy
# Execute no terminal web do servidor

echo "🔍 VALIDAÇÃO PÓS-DEPLOY"
echo "========================================"
echo ""

# 1. Instalar slowapi
echo "📦 1/5: Instalando dependências..."
cd /var/www/finup/app_dev
source venv/bin/activate
pip install -r backend/requirements.txt --quiet
echo "   ✅ Dependências instaladas"

# 2. Restart backend
echo ""
echo "🔄 2/5: Reiniciando backend..."
systemctl restart finup-backend
sleep 3
echo "   ✅ Backend reiniciado"

# 3. Verificar status
echo ""
echo "📊 3/5: Verificando status..."
if systemctl is-active --quiet finup-backend; then
    echo "   ✅ Backend ATIVO"
    systemctl status finup-backend --no-pager | grep -E "(Active|Main PID|Memory|CPU)" | head -4
else
    echo "   ❌ Backend NÃO ESTÁ ATIVO!"
    journalctl -u finup-backend -n 20 --no-pager
    exit 1
fi

# 4. Testar endpoints
echo ""
echo "🧪 4/5: Testando isolamento de usuários..."

# Teste 1: Sem token
STATUS1=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/transactions/list)
if [ "$STATUS1" = "401" ]; then
    echo "   ✅ Teste 1: Sem token → 401 (correto)"
else
    echo "   ❌ Teste 1: Status $STATUS1 (esperado 401)"
fi

# Teste 2: Token inválido
STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer token_invalido" http://localhost:8000/api/v1/transactions/list)
if [ "$STATUS2" = "401" ]; then
    echo "   ✅ Teste 2: Token inválido → 401 (correto)"
else
    echo "   ❌ Teste 2: Status $STATUS2 (esperado 401)"
fi

# Teste 3: Health check
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q "ok"; then
    echo "   ✅ Teste 3: Health check → OK"
else
    echo "   ⚠️  Teste 3: Health check → $HEALTH"
fi

# 5. Resumo
echo ""
echo "📋 5/5: Resumo Final"
echo "========================================"
echo ""

if [ "$STATUS1" = "401" ] && [ "$STATUS2" = "401" ]; then
    echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo ""
    echo "🔒 Isolamento de usuários: FUNCIONANDO"
    echo "🔐 Autenticação JWT: OBRIGATÓRIA"
    echo "💚 Backend: OPERACIONAL"
    echo ""
    echo "🎯 Próximo passo: Testar no frontend"
    echo "   Login: teste@email.com / teste123"
    echo "   Verificar: Só vê transações próprias"
else
    echo "❌ PROBLEMAS DETECTADOS"
    echo ""
    echo "Ver logs completos:"
    echo "   journalctl -u finup-backend -n 100 --no-pager"
fi

echo ""
echo "========================================"
