#!/bin/bash

# 📝 CHANGELOG AUTOMÁTICO - FinUp
# =================================
# Gera/atualiza CHANGELOG.md baseado em commits git desde última release
#
# Uso: ./scripts/deploy/generate_changelog.sh [--version X.Y.Z]

set -e

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
CHANGELOG_FILE="$PROJECT_ROOT/CHANGELOG.md"

cd "$PROJECT_ROOT"

# Obter última tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [[ -z "$LAST_TAG" ]]; then
    echo "ℹ️  Nenhuma tag encontrada - gerando changelog completo"
    COMMITS=$(git log --oneline --pretty=format:"- %s (%h)" --reverse)
else
    echo "ℹ️  Última tag: $LAST_TAG"
    COMMITS=$(git log "$LAST_TAG"..HEAD --oneline --pretty=format:"- %s (%h)")
fi

# Verificar se há commits novos
if [[ -z "$COMMITS" ]]; then
    echo "✅ Nenhum commit novo desde $LAST_TAG"
    exit 0
fi

# Obter versão
if [[ -n "$1" && "$1" != "--version" ]]; then
    VERSION="$1"
elif [[ -n "$2" ]]; then
    VERSION="$2"
else
    # Auto-incrementar patch version
    if [[ -n "$LAST_TAG" ]]; then
        # Extrair números da versão (v1.2.3 → 1 2 3)
        IFS='.' read -ra VER <<< "${LAST_TAG#v}"
        MAJOR="${VER[0]}"
        MINOR="${VER[1]}"
        PATCH="${VER[2]}"
        PATCH=$((PATCH + 1))
        VERSION="$MAJOR.$MINOR.$PATCH"
    else
        VERSION="1.0.0"
    fi
fi

echo "📝 Gerando changelog para versão: v$VERSION"

# Data atual
DATE=$(date +%Y-%m-%d)

# Categorizar commits
FEATURES=$(echo "$COMMITS" | grep -i "feat\|add\|novo" || true)
FIXES=$(echo "$COMMITS" | grep -i "fix\|corrige\|resolve" || true)
REFACTOR=$(echo "$COMMITS" | grep -i "refactor\|melhora\|otimiza" || true)
DOCS=$(echo "$COMMITS" | grep -i "docs\|doc\|readme" || true)
OUTROS=$(echo "$COMMITS" | grep -v -i "feat\|add\|novo\|fix\|corrige\|resolve\|refactor\|melhora\|otimiza\|docs\|doc\|readme" || true)

# Criar entrada no changelog
NEW_ENTRY=$(cat <<EOF

## [v$VERSION] - $DATE

### ✨ Novas Funcionalidades
$( [[ -n "$FEATURES" ]] && echo "$FEATURES" || echo "- Nenhuma" )

### 🐛 Correções
$( [[ -n "$FIXES" ]] && echo "$FIXES" || echo "- Nenhuma" )

### 🔧 Melhorias e Refatoração
$( [[ -n "$REFACTOR" ]] && echo "$REFACTOR" || echo "- Nenhuma" )

### 📚 Documentação
$( [[ -n "$DOCS" ]] && echo "$DOCS" || echo "- Nenhuma" )

$( [[ -n "$OUTROS" ]] && echo "### 🔄 Outras Mudanças" && echo "$OUTROS" )

---

EOF
)

# Atualizar ou criar CHANGELOG.md
if [[ -f "$CHANGELOG_FILE" ]]; then
    # Inserir após o título (linha 3+)
    HEAD=$(head -n 3 "$CHANGELOG_FILE")
    TAIL=$(tail -n +4 "$CHANGELOG_FILE")
    echo "$HEAD" > "$CHANGELOG_FILE"
    echo "$NEW_ENTRY" >> "$CHANGELOG_FILE"
    echo "$TAIL" >> "$CHANGELOG_FILE"
else
    # Criar novo
    cat > "$CHANGELOG_FILE" <<EOF
# 📝 Changelog - Sistema FinUp

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.
$NEW_ENTRY
EOF
fi

echo "✅ Changelog atualizado: $CHANGELOG_FILE"
echo ""
echo "📋 Preview:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -n 40 "$CHANGELOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Sugerir tag
echo ""
echo "💡 Sugestão: Criar tag git para esta versão"
echo "   git tag -a v$VERSION -m \"Release v$VERSION\""
echo "   git push origin v$VERSION"
