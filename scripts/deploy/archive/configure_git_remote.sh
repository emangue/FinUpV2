#!/bin/bash
# 🔧 Configurar Git Remote VPS no MacBook
# Executar APÓS setup_git_deploy.sh no servidor

set -e

echo "🔧 CONFIGURAÇÃO GIT REMOTE VPS"
echo "========================================"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "README.md" ] || [ ! -d "app_dev" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto"
    echo "   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
    exit 1
fi

# Configuração
VPS_HOST="root@64.23.241.43"
VPS_REPO="/var/repo/finup.git"

# Verificar se remote já existe
if git remote | grep -q "^vps$"; then
    echo "⚠️  Remote 'vps' já existe. Removendo..."
    git remote remove vps
fi

# Adicionar remote
echo "📡 Adicionando remote VPS..."
git remote add vps "$VPS_HOST:$VPS_REPO"

# Verificar
echo ""
echo "✅ Remote VPS configurado!"
echo ""
echo "📋 Remotes disponíveis:"
git remote -v

echo ""
echo "========================================"
echo "✅ CONFIGURAÇÃO COMPLETA!"
echo "========================================"
echo ""
echo "🚀 Para fazer deploy agora:"
echo "   git push vps main"
echo ""
echo "📝 Nota: Primeira vez vai pedir senha do servidor"
echo "   Senha está em: .env.deploy"
echo ""
echo "💡 Dica: Configure chave SSH para não pedir senha"
echo "   Ver docs/guides/git-deploy.md"
echo ""
