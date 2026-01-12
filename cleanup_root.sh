#!/bin/bash
# Script de limpeza de arquivos desnecessários na raiz do projeto

echo "🧹 Limpeza de arquivos desnecessários"
echo "======================================"
echo ""

# Criar backup antes de deletar (segurança)
BACKUP_DIR="./backup_cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Arrays de arquivos a remover
SCRIPTS_TESTE=(
    "test_angelo_hash.py"
    "test_hash_v42.py"
    "test_hash_v421.py"
    "test_normalizacao_condicional.py"
    "test_validacao_final.py"
    "test_extrato_filter.py"
    "test_parcela_regex.py"
    "test_settings_page.html"
    "test_duplicatas.csv"
    "test_upload.csv"
)

SCRIPTS_CHECK=(
    "check_duplicates.py"
    "check_futuras.py"
    "check_hash_duplicates.py"
    "check_idparcela_final.py"
    "check_parcelas_vpd.py"
    "check_vpd_parcelas.py"
)

SCRIPTS_DEBUG=(
    "debug_dropna.py"
    "debug_filter.py"
    "debug_idparcela.py"
)

SCRIPTS_DEPLOY_ANTIGOS=(
    "deploy_backend_only.sh"
    "deploy_clean_orchestrator.sh"
    "deploy_direct.sh"
    "deploy_final.sh"
    "deploy_robust.sh"
    "deploy_server.sh"
    "deploy_simple.sh"
    "deploy_simple_fixed.sh"
    "deploy_via_scp.sh"
    "diagnose_ssh.sh"
    "fix_ssh.sh"
    "fix_ssh_port.sh"
    "fresh_deploy.sh"
    "prepare_manual_deploy.sh"
    "deploy_manual.tar.gz"
)

SCRIPTS_MIGRACAO_ANTIGOS=(
    "migrate_add_valor_medio.py"
    "regenerate_quick.py"
    "regenerate_sql_backup.py"
    "regenerate_v4.py"
    "recalcular_medias.py"
    "popular_budget_planning.py"
    "popular_budget_simples.py"
)

SCRIPTS_VALIDACAO=(
    "compare_uploads.py"
    "validate_upload_vs_journal.py"
    "validar_upload.sh"
)

ARQUIVOS_TEMPORARIOS=(
    "backend.pid"
    "frontend.pid"
    "backend.log"
    "frontend.log"
    "simple_frontend.js"
    "frontend_final.js"
    "simple_package.json"
    "package.json"
    "package-lock.json"
    "arquivo_teste_n8n.json"
)

SCRIPTS_DEV_ANTIGOS=(
    "run_dev_api.py"
    "start_dev.sh"
    "audit_server.sh"
    "clean_server.sh"
)

# Função para mover arquivo para backup e deletar
remover_arquivo() {
    local arquivo=$1
    if [ -f "$arquivo" ]; then
        cp "$arquivo" "$BACKUP_DIR/"
        rm "$arquivo"
        echo "  ✅ Removido: $arquivo"
        return 0
    fi
    return 1
}

# Remover por categoria
echo "📝 Scripts de teste..."
for arquivo in "${SCRIPTS_TESTE[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "🔍 Scripts de verificação..."
for arquivo in "${SCRIPTS_CHECK[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "🐛 Scripts de debug..."
for arquivo in "${SCRIPTS_DEBUG[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "🚀 Scripts de deploy antigos..."
for arquivo in "${SCRIPTS_DEPLOY_ANTIGOS[@]}"; do
    remover_arquivo "$arquivo"
done
# Remover pasta deploy_manual se existir
if [ -d "deploy_manual" ]; then
    cp -r "deploy_manual" "$BACKUP_DIR/"
    rm -rf "deploy_manual"
    echo "  ✅ Removido: deploy_manual/"
fi
echo ""

echo "🔄 Scripts de migração/regeneração antigos..."
for arquivo in "${SCRIPTS_MIGRACAO_ANTIGOS[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "✓ Scripts de validação..."
for arquivo in "${SCRIPTS_VALIDACAO[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "🗑️  Arquivos temporários..."
for arquivo in "${ARQUIVOS_TEMPORARIOS[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

echo "⚙️  Scripts dev antigos..."
for arquivo in "${SCRIPTS_DEV_ANTIGOS[@]}"; do
    remover_arquivo "$arquivo"
done
echo ""

# Remover symlinks backend e frontend se existirem
if [ -L "backend" ]; then
    rm "backend"
    echo "  ✅ Removido symlink: backend"
fi
if [ -L "frontend" ]; then
    rm "frontend"
    echo "  ✅ Removido symlink: frontend"
fi

echo ""
echo "======================================"
echo "✅ Limpeza concluída!"
echo ""
echo "📦 Backup criado em: $BACKUP_DIR"
echo "   (Pode ser deletado após confirmar que tudo está OK)"
echo ""
echo "📋 Arquivos mantidos (importantes):"
echo "   • quick_start.sh / quick_stop.sh (gerenciamento de servidores)"
echo "   • regenerate_sql.py (regeneração de hashes)"
echo "   • *.md (documentação)"
echo "   • app_dev/ (código principal)"
echo "   • _csvs_historico/ (arquivos históricos)"
echo "   • codigos_apoio/ (código de apoio)"
echo ""
