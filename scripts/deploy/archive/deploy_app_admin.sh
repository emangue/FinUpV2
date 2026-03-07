#!/bin/bash
# Deploy app_admin para admin.meufinup.com.br
# Uso: ./scripts/deploy/deploy_app_admin.sh
#
# Pré-requisitos:
#   - DNS: admin.meufinup.com.br → 148.230.78.91
#   - SSH: minha-vps-hostinger configurado

set -e

echo "🚀 DEPLOY APP_ADMIN"
echo "========================================"

ssh -o ConnectTimeout=10 minha-vps-hostinger "
    set -e
    cd /var/www/finup

    echo '📥 Git pull...'
    git pull origin main

    echo ''
    echo '📦 App Admin - build...'
    cd app_admin/frontend
    export NEXT_PUBLIC_BACKEND_URL=https://meufinup.com.br
    npm ci --quiet
    npm run build
    cd ../..

    echo ''
    echo '✅ Build concluído!'
"

echo ""
echo "📋 Próximos passos (executar no servidor com sudo):"
echo ""
echo "1. Criar serviço systemd:"
echo "   sudo cp /var/www/finup/scripts/deploy/finup-admin.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable finup-admin"
echo "   sudo systemctl start finup-admin"
echo ""
echo "2. Adicionar Nginx para admin.meufinup.com.br"
echo "3. CORS: adicionar https://admin.meufinup.com.br no .env do backend"
echo "4. SSL: sudo certbot --nginx -d admin.meufinup.com.br"
echo ""
