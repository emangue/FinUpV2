#!/usr/bin/env bash
# =============================================================================
# predeploy.sh — Wrapper para o checklist pré-deploy automatizado FinUp
#
# Uso:
#   ./scripts/deploy/predeploy.sh
#
# Variáveis de ambiente opcionais (ou digitadas no prompt):
#   ADMIN_EMAIL      Padrão: admin@financas.com
#   ADMIN_PASSWORD   Senha do admin (se não definida, será solicitada)
#   BACKEND_URL      Padrão: http://localhost:8000
#   FRONTEND_URL     Padrão: http://localhost:3000
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/predeploy.py"

# ── Carregar .env.local se existir ────────────────────────────────────────────
ENV_LOCAL="$PROJECT_ROOT/.env.local"
if [ -f "$ENV_LOCAL" ]; then
    # Ler e exportar linha por linha (robusto, sem problemas com set -u)
    while IFS='=' read -r key value; do
        # Ignorar comentários e linhas em branco
        [[ -z "$key" || "$key" == \#* ]] && continue
        # Remover aspas opcionais do valor
        value="${value%\"}" ; value="${value#\"}" ; value="${value%\'}"; value="${value#\'}"
        export "${key}=${value}"
    done < "$ENV_LOCAL"
fi

# ── Localizar Python com venv ──────────────────────────────────────────────────
VENV_PYTHON=""

# Tentar venvs em ordem de preferência
for candidate in \
    "$PROJECT_ROOT/app_dev/venv/bin/python3" \
    "$PROJECT_ROOT/.venv/bin/python3" \
    "python3" \
    "python"
do
    if command -v "$candidate" &>/dev/null 2>&1 || [ -x "$candidate" ]; then
        VENV_PYTHON="$candidate"
        break
    fi
done

if [ -z "$VENV_PYTHON" ]; then
    echo "❌ Python não encontrado. Instale Python 3.8+ ou ative o venv."
    exit 1
fi

# ── Executar script Python ─────────────────────────────────────────────────────
exec "$VENV_PYTHON" "$PYTHON_SCRIPT" "$@"
