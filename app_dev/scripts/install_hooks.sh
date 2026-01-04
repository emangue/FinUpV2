#!/bin/bash
# Script de instalação de git hooks

echo "🔧 Instalando git hooks..."

# Cria diretório de hooks se não existir
mkdir -p .git/hooks

# Copia pre-commit hook
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks instalados com sucesso!"
echo ""
echo "📋 Hooks configurados:"
echo "   - pre-commit: Valida versões antes de commit"
echo ""
echo "💡 Para bypass (não recomendado):"
echo "   git commit --no-verify -m \"mensagem\""
