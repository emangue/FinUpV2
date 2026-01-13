#!/bin/bash
# Script de limpeza profunda - Reduzir tamanho do projeto

echo "🧹 Limpeza Profunda do Projeto"
echo "======================================"
echo ""

# Calcular tamanho inicial
TAMANHO_INICIAL=$(du -sh . 2>/dev/null | cut -f1)
echo "📏 Tamanho inicial: $TAMANHO_INICIAL"
echo ""

# 1. Deletar build cache do Next.js (.next)
if [ -d "app_dev/frontend/.next" ]; then
    echo "🗑️  Removendo .next/ (build cache do Next.js)..."
    TAMANHO_NEXT=$(du -sh app_dev/frontend/.next 2>/dev/null | cut -f1)
    rm -rf app_dev/frontend/.next
    echo "   ✅ Liberados: $TAMANHO_NEXT"
fi

# 2. Limpar backups antigos do banco (manter apenas os 2 mais recentes)
echo ""
echo "🗄️  Limpando backups antigos do banco..."
cd app_dev/backend/database

# Remover backups individuais antigos (manter apenas 2 mais recentes)
echo "   Backups individuais:"
ls -t financas_dev_backup_*.db 2>/dev/null | tail -n +3 | while read arquivo; do
    TAMANHO=$(du -sh "$arquivo" 2>/dev/null | cut -f1)
    rm "$arquivo"
    echo "   ✅ Removido: $arquivo ($TAMANHO)"
done

# Remover banco corrompido
if [ -f "financas_dev_CORRUPTED_20260110_212304.db" ]; then
    TAMANHO=$(du -sh financas_dev_CORRUPTED_20260110_212304.db 2>/dev/null | cut -f1)
    rm financas_dev_CORRUPTED_20260110_212304.db
    echo "   ✅ Removido: financas_dev_CORRUPTED_20260110_212304.db ($TAMANHO)"
fi

# Limpar pastas backups antigas (manter estrutura vazia)
if [ -d "backups" ]; then
    TAMANHO=$(du -sh backups 2>/dev/null | cut -f1)
    rm -rf backups/*
    echo "   ✅ Limpo: backups/ ($TAMANHO)"
fi

if [ -d "backups_test" ]; then
    TAMANHO=$(du -sh backups_test 2>/dev/null | cut -f1)
    rm -rf backups_test
    echo "   ✅ Removido: backups_test/ ($TAMANHO)"
fi

cd ../../../../

# 3. Limpar node_modules da raiz (se existir)
if [ -d "node_modules" ]; then
    echo ""
    echo "📦 Removendo node_modules/ da raiz..."
    TAMANHO=$(du -sh node_modules 2>/dev/null | cut -f1)
    rm -rf node_modules
    echo "   ✅ Removido: $TAMANHO"
fi

# 4. Remover backup_cleanup antigo
if [ -d "backup_cleanup_20260112_170454" ]; then
    echo ""
    echo "🗑️  Removendo backup_cleanup_20260112_170454/..."
    TAMANHO=$(du -sh backup_cleanup_20260112_170454 2>/dev/null | cut -f1)
    rm -rf backup_cleanup_20260112_170454
    echo "   ✅ Removido: $TAMANHO"
fi

# 5. Limpar __pycache__ e .pyc
echo ""
echo "🐍 Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Cache Python limpo"

# Calcular economia
echo ""
echo "======================================"
TAMANHO_FINAL=$(du -sh . 2>/dev/null | cut -f1)
echo "📏 Tamanho final: $TAMANHO_FINAL"
echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📝 Observações:"
echo "   • .next/ será regenerado no próximo 'npm run dev'"
echo "   • Backups mantidos: 2 mais recentes"
echo "   • node_modules do frontend: MANTIDO (necessário)"
echo "   • venv do backend: MANTIDO (necessário)"
echo ""
