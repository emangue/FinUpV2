#!/bin/bash
# Salva o estado local atual em um branch de backup
# Uso: ./scripts/deploy/salvar_branch_versao_atual.sh

set -e
cd "$(dirname "$0")/../.."

BRANCH_NAME="backup-versao-$(date +%Y%m%d-%H%M)"
echo "📦 Salvando estado local em branch: $BRANCH_NAME"
echo ""

# Criar branch a partir do estado atual (preserva alterações não commitadas)
git checkout -b "$BRANCH_NAME"

# Adicionar tudo e commitar
git add .
if git diff --staged --quiet 2>/dev/null; then
    echo "✅ Nada para commitar - branch $BRANCH_NAME já está atualizado."
else
    git commit -m "chore: snapshot versão local $(date +%Y-%m-%d)"
    echo "✅ Commit criado."
fi

# Push para origin
git push -u origin "$BRANCH_NAME" 2>/dev/null || echo "⚠️ Push falhou - branch criado localmente: $BRANCH_NAME"

echo ""
echo "✅ Branch salvo: $BRANCH_NAME"
echo "   Para substituir main: git checkout main && git reset --hard $BRANCH_NAME && git push origin main --force"
