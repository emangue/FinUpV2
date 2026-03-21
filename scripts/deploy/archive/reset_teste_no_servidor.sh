#!/bin/bash
# Executa reset_teste_copiar_admin_10x.py no PostgreSQL do servidor.
# Limpa teste@email.com e copia dados do admin com valores ~10x menores.
#
# Uso: ./scripts/deploy/reset_teste_no_servidor.sh
#
# Pré-requisitos:
#   - SSH configurado (minha-vps-hostinger)
#   - app_dev/backend/.env no servidor com DATABASE_URL ou PROD_DATABASE_URL

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REMOTE_PATH="/var/www/finup"

echo "🔄 RESET TESTE NO SERVIDOR (PostgreSQL)"
echo "========================================"
echo "Limpa teste@email.com e copia dados do admin com valores ~10x menores"
echo ""

read -p "⚠️  Isso vai SUBSTITUIR todos os dados do teste@email.com. Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[sS]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "📤 Copiando script para o servidor..."
ssh minha-vps-hostinger "mkdir -p $REMOTE_PATH/scripts/database"
scp "$PROJECT_ROOT/scripts/database/reset_teste_copiar_admin_10x.py" minha-vps-hostinger:"$REMOTE_PATH/scripts/database/"

echo ""
echo "🔄 Executando reset no servidor..."
ssh minha-vps-hostinger "
    set -e
    cd $REMOTE_PATH
    # O script Python carrega .env automaticamente (evita erro ao source .env no shell)
    if [ -d 'app_dev/venv' ]; then
        source app_dev/venv/bin/activate
    else
        python3 -m venv app_dev/venv
        source app_dev/venv/bin/activate
        pip install -r app_dev/backend/requirements.txt -q
    fi
    python scripts/database/reset_teste_copiar_admin_10x.py --postgres
"

echo ""
echo "✅ Reset concluído! teste@email.com atualizado no PostgreSQL do servidor."
