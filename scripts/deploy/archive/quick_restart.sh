#!/bin/bash
# Quick Restart - Sistema Financeiro v5
# Uso: ./quick_restart.sh (para reiniciar servidores)
#
# Stop + sleep 2 + Start. Útil para o AI e para aplicar mudanças.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Reiniciando servidores..."
echo ""

"$SCRIPT_DIR/quick_stop.sh"
sleep 2
"$SCRIPT_DIR/quick_start.sh"
