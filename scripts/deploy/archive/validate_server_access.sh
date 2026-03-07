#!/bin/bash

# 🔍 Validação de Acesso ao Servidor - Executar Antes de Investigações
# Uso: ./scripts/deploy/validate_server_access.sh

set -e

echo "🔍 VALIDAÇÃO DE ACESSO AO SERVIDOR"
echo "===================================="
echo "📅 $(date)"
echo ""

# 1. TESTAR CONECTIVIDADE SSH
echo "🔑 1. TESTANDO ACESSO SSH"
echo "----------------------------------------"

if ssh -o ConnectTimeout=5 -o BatchMode=yes minha-vps-hostinger 'echo "✅ SSH OK"' 2>/dev/null; then
    echo "✅ SSH conecta perfeitamente"
else
    echo "❌ SSH FALHOU - Tentando diagnóstico..."
    
    # Tentar com verbose para ver o erro
    echo "🔍 Diagnóstico detalhado:"
    ssh -o ConnectTimeout=5 -v minha-vps-hostinger 'echo test' 2>&1 | grep -E "(connect|refused|timeout|denied)" || true
    
    echo ""
    echo "💡 SOLUÇÕES:"
    echo "   1. Tentar com senha: ssh -o PreferredAuthentications=password root@148.230.78.91"
    echo "   2. Verificar chave: ls -la ~/.ssh/id_ed25519*"  
    echo "   3. Ver configuração: cat ~/.ssh/config | grep -A5 minha-vps"
    echo ""
    exit 1
fi

# 2. TESTAR SERVIÇOS NO SERVIDOR
echo ""
echo "🔧 2. VALIDANDO SERVIÇOS NO SERVIDOR"
echo "----------------------------------------"

ssh minha-vps-hostinger "
    echo '📋 Status dos serviços:'
    if systemctl is-active --quiet finup-backend; then
        echo '✅ Backend: Ativo'
    else
        echo '❌ Backend: Inativo ou com problemas'
    fi
    
    if systemctl is-active --quiet finup-frontend; then
        echo '✅ Frontend: Ativo'
    else
        echo '❌ Frontend: Inativo ou com problemas'  
    fi
    
    echo ''
    echo '🏥 Health check do backend:'
    HEALTH=\$(curl -s -m 3 localhost:8000/api/health 2>/dev/null || echo 'FAILED')
    if [ \"\$HEALTH\" = 'FAILED' ]; then
        echo '❌ Backend não responde'
    else
        echo \"✅ Backend responde: \$HEALTH\"
    fi
    
    echo ''
    echo '📂 Projeto no servidor:'
    if [ -d '/var/www/finup' ]; then
        echo '✅ Projeto existe em /var/www/finup'
        cd /var/www/finup
        CURRENT_COMMIT=\$(git rev-parse HEAD 2>/dev/null || echo 'ERROR')
        if [ \"\$CURRENT_COMMIT\" = 'ERROR' ]; then
            echo '❌ Git não encontrado no projeto'
        else
            echo \"✅ Git OK - Commit: \${CURRENT_COMMIT:0:7}\"
        fi
    else
        echo '❌ Projeto não encontrado em /var/www/finup'
    fi
"

# 3. VERIFICAR SINCRONIZAÇÃO GIT
echo ""
echo "🔄 3. VERIFICANDO SINCRONIZAÇÃO GIT"  
echo "----------------------------------------"

# Git local
LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo 'ERROR')
if [ "$LOCAL_COMMIT" = 'ERROR' ]; then
    echo "❌ Git local com problemas"
    exit 1
fi

# Git servidor
SERVER_COMMIT=$(ssh minha-vps-hostinger "cd /var/www/finup && git rev-parse HEAD 2>/dev/null || echo 'ERROR'")

echo "📋 Local:    ${LOCAL_COMMIT:0:7}"
echo "📋 Servidor: ${SERVER_COMMIT:0:7}"

if [ "$LOCAL_COMMIT" = "$SERVER_COMMIT" ]; then
    echo "✅ Local e servidor sincronizados"
else
    echo "⚠️  Local e servidor DESSINCRONIZADOS!"
    echo ""
    echo "💡 Para sincronizar:"
    echo "   1. Se local está à frente: git push origin main"
    echo "   2. Se servidor está à frente: ssh servidor 'cd /var/www/finup && git status'"
    echo "   3. Depois fazer deploy: ./scripts/deploy/quick_deploy.sh"
fi

# 4. VERIFICAR VS CODE REMOTE
echo ""
echo "💻 4. TESTANDO VS CODE REMOTE SSH"
echo "----------------------------------------"

if command -v code >/dev/null 2>&1; then
    echo "✅ VS Code instalado"
    echo "💡 Para conectar: Command Palette > Remote-SSH: Connect to Host > minha-vps-hostinger"
    echo "💡 Path remoto: /var/www/finup"
else
    echo "⚠️  VS Code não encontrado no PATH"
fi

# 5. RESUMO FINAL
echo ""
echo "📊 RESUMO DA VALIDAÇÃO"
echo "===================================="

# Contar sucessos
ssh_ok=$(ssh -o ConnectTimeout=5 -o BatchMode=yes minha-vps-hostinger 'echo "1"' 2>/dev/null || echo "0")
backend_ok=$(ssh minha-vps-hostinger "systemctl is-active --quiet finup-backend && echo '1' || echo '0'" 2>/dev/null || echo "0")
health_ok=$(ssh minha-vps-hostinger "curl -s -m 3 localhost:8000/api/health >/dev/null 2>&1 && echo '1' || echo '0'" 2>/dev/null || echo "0")
sync_ok=$([[ "$LOCAL_COMMIT" = "$SERVER_COMMIT" ]] && echo "1" || echo "0")

total_checks=4
success_count=$((ssh_ok + backend_ok + health_ok + sync_ok))

echo "✅ Testes que passaram: $success_count/$total_checks"
echo ""

if [ "$success_count" -eq "$total_checks" ]; then
    echo "🎉 TUDO OK! Servidor pronto para investigações"
    echo ""
    echo "🚀 Comandos úteis:"
    echo "   ssh minha-vps-hostinger                    # Conectar ao servidor"
    echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -f'  # Logs em tempo real"
    echo "   ./scripts/deploy/quick_deploy.sh          # Deploy rápido"
    echo "   ./scripts/deploy/deploy_help.sh           # Guia completo"
else
    echo "⚠️  PROBLEMAS DETECTADOS - Resolver antes de investigar"
    echo ""
    echo "📚 Documentação completa: docs/deploy/SSH_ACCESS.md"
    echo "💡 Troubleshooting: docs/deploy/DEPLOY_PROCESS.md"
fi

echo ""