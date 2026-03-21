#!/bin/bash
# Sincroniza investimentos (ativo/passivo) do SQLite local para PostgreSQL no servidor.
# Copia o DB local para o servidor e executa o sync lá (PostgreSQL está em localhost no servidor).
#
# Uso: ./scripts/deploy/sync_investimentos_para_servidor.sh
#
# Pré-requisitos:
#   - financas_dev.db local com dados atualizados
#   - SSH configurado (minha-vps-hostinger)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SQLITE_LOCAL="$PROJECT_ROOT/app_dev/backend/database/financas_dev.db"
REMOTE_PATH="/var/www/finup"

if [ ! -f "$SQLITE_LOCAL" ]; then
    echo "❌ SQLite não encontrado: $SQLITE_LOCAL"
    exit 1
fi

echo "🔄 SYNC INVESTIMENTOS: Local → Servidor (PostgreSQL)"
echo "========================================"
echo "📂 Local:  $SQLITE_LOCAL"
echo "🖥️  Servidor: $REMOTE_PATH"
echo ""

read -p "⚠️  Isso vai SUBSTITUIR investimentos no PostgreSQL do servidor. Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[sS]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "📤 Copiando SQLite para o servidor..."
scp "$SQLITE_LOCAL" minha-vps-hostinger:"$REMOTE_PATH/app_dev/backend/database/financas_dev.db"

echo ""
echo "🔄 Executando sync no servidor..."
ssh minha-vps-hostinger "
    set -e
    cd $REMOTE_PATH
    # Usar DATABASE_URL do .env do backend (nunca hardcodar senha)
    if [ -f app_dev/backend/.env ]; then
        set -a
        source app_dev/backend/.env
        set +a
    fi
    export PROD_DATABASE_URL=\"\${PROD_DATABASE_URL:-\$DATABASE_URL}\"
    if [ -z \"\$PROD_DATABASE_URL\" ]; then
        echo '❌ DATABASE_URL ou PROD_DATABASE_URL não definido no app_dev/backend/.env'
        exit 1
    fi
    if [ -d 'app_dev/venv' ]; then
        source app_dev/venv/bin/activate
    else
        python3 -m venv app_dev/venv
        source app_dev/venv/bin/activate
        pip install -r app_dev/backend/requirements.txt -q
    fi
    cd app_dev/backend
    python ../../scripts/migration/sync_investimentos_local_para_servidor.py --yes
"

echo ""
echo "✅ Sync concluído! Investimentos (ativo/passivo) atualizados no PostgreSQL."
