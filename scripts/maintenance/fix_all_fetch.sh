#!/bin/bash

# ============================================================================
# Script para Corrigir TODOS os fetch() diretos nas features
# FASE 3 - Adiciona autenticação automática em todos os componentes
# ============================================================================

set -e

echo "🔧 Corrigindo TODOS os fetch() diretos nas features..."
echo ""

# Função para adicionar import se não existir
add_import_if_missing() {
    local file="$1"
    local import_line="import { fetchWithAuth } from '@/core/utils/api-client';"
    
    if ! grep -q "fetchWithAuth" "$file"; then
        # Encontrar linha com primeiro import e adicionar depois
        local first_import_line=$(grep -n "^import" "$file" | head -1 | cut -d: -f1)
        if [ ! -z "$first_import_line" ]; then
            # Inserir import na linha após o primeiro import
            sed -i '' "${first_import_line}a\\
$import_line  // ✅ FASE 3 - Autenticação obrigatória
" "$file"
            echo "  ✅ Import adicionado em $(basename $file)"
        fi
    fi
}

# Função para substituir fetch( por fetchWithAuth(
replace_fetch_calls() {
    local file="$1"
    local count_before=$(grep -c "fetch(" "$file" 2>/dev/null || echo "0")
    
    # Substituir apenas fetch( que não são fetchWithAuth( ou fetchData(
    sed -i '' 's/await fetch(/await fetchWithAuth(/g' "$file"
    sed -i '' 's/= fetch(/= fetchWithAuth(/g' "$file"
    
    local count_after=$(grep -c "fetch(" "$file" 2>/dev/null || echo "0")
    local fixed=$((count_before - count_after))
    
    if [ "$fixed" -gt 0 ]; then
        echo "  ✅ $fixed fetch() → fetchWithAuth() em $(basename $file)"
    fi
}

cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Lista de arquivos com fetch() diretos (excluindo testes)
FILES=$(grep -r "fetch(" app_dev/frontend/src/features/ --include="*.tsx" --include="*.ts" -l | grep -v node_modules | grep -v __tests__)

echo "📋 Arquivos a corrigir:"
for file in $FILES; do
    echo "  - $(basename $file)"
done
echo ""

# Processar cada arquivo
for file in $FILES; do
    echo "🔧 Processando $file"
    
    # 1. Adicionar import se necessário
    add_import_if_missing "$file"
    
    # 2. Substituir fetch() calls
    replace_fetch_calls "$file"
    
    echo ""
done

echo "======================================================================"
echo "📊 RESULTADO FINAL"
echo "======================================================================"

# Verificar quantos fetch() restam
REMAINING=$(grep -r "fetch(" app_dev/frontend/src/features/ --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v "fetchWithAuth\|fetchData\|fetchJsonWithAuth\|__tests__" | wc -l)

echo "fetch() diretos restantes: $REMAINING"

if [ "$REMAINING" -eq 0 ]; then
    echo "🎉 SUCESSO! Todos os fetch() foram convertidos para fetchWithAuth()"
    echo ""
    echo "Próximos passos:"
    echo "  1. Reiniciar servidores: ./quick_stop.sh && ./quick_start.sh"
    echo "  2. Testar no browser: http://localhost:3000/login"
    echo "  3. Verificar console.log e Network tab (F12)"
else
    echo "⚠️  Ainda restam $REMAINING fetch() diretos. Verificar manualmente:"
    grep -r "fetch(" app_dev/frontend/src/features/ --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v "fetchWithAuth\|fetchData\|fetchJsonWithAuth\|__tests__" | head -10
fi

echo ""