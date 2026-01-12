#!/bin/bash
#
# Test Backup and Restore - Sistema de Finanças V4
#
# Testa o fluxo completo de backup/restore do banco de dados SQLite:
# 1. Faz backup do banco atual
# 2. Modifica o banco (adiciona dados de teste)
# 3. Restaura o banco do backup
# 4. Valida que os dados foram restaurados corretamente
#
# Nota: Este teste simula localmente. Em produção, usar backup-to-s3.sh

set -e  # Exit on error

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4"
DB_PATH="$PROJECT_ROOT/app_dev/backend/database/financas_dev.db"
BACKUP_DIR="$PROJECT_ROOT/app_dev/backend/database/backups_test"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/financas_backup_${TIMESTAMP}.db"

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0

echo "============================================================"
echo "💾 TESTE DE BACKUP E RESTORE - Sistema Finanças V4"
echo "============================================================"
echo "Database: $DB_PATH"
echo "Backup Dir: $BACKUP_DIR"
echo "============================================================"
echo ""

# Função de assert
assert_equal() {
    local actual="$1"
    local expected="$2"
    local message="$3"
    
    if [ "$actual" == "$expected" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✅ PASS:${NC} $message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}❌ FAIL:${NC} $message"
        echo -e "     Esperado: $expected"
        echo -e "     Obtido: $actual"
    fi
}

assert_file_exists() {
    local file="$1"
    local message="$2"
    
    if [ -f "$file" ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "  ${GREEN}✅ PASS:${NC} $message"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "  ${RED}❌ FAIL:${NC} $message (arquivo não existe)"
    fi
}

# ==================================================
# TESTE 1: Verificar que database existe
# ==================================================
echo "🔍 TESTE 1: Verificar database original"
assert_file_exists "$DB_PATH" "Database dev deve existir"

# Contar registros antes do backup
ORIGINAL_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM journal_entries;")
ORIGINAL_USERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users;")

echo "  📊 Estado atual do banco:"
echo "     - Transações: $ORIGINAL_COUNT"
echo "     - Usuários: $ORIGINAL_USERS"
echo ""

# ==================================================
# TESTE 2: Criar backup do banco
# ==================================================
echo "🔍 TESTE 2: Criar backup do banco"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Método 1: Backup SQLite nativo (.backup command)
echo "  Criando backup via SQLite .backup..."
sqlite3 "$DB_PATH" ".backup $BACKUP_FILE"

assert_file_exists "$BACKUP_FILE" "Arquivo de backup deve ser criado"

# Verificar tamanho do backup
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | awk '{print $1}')
echo "  📦 Tamanho do backup: $BACKUP_SIZE"

# Verificar integridade do backup
echo "  Verificando integridade do backup..."
INTEGRITY_CHECK=$(sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" 2>&1)

if [ "$INTEGRITY_CHECK" == "ok" ]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "  ${GREEN}✅ PASS:${NC} Backup íntegro (integrity_check ok)"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "  ${RED}❌ FAIL:${NC} Backup corrompido!"
    echo "     $INTEGRITY_CHECK"
fi
echo ""

# ==================================================
# TESTE 3: Modificar banco original (simular alterações)
# ==================================================
echo "🔍 TESTE 3: Modificar banco original"

# Adicionar usuário de teste
echo "  Adicionando usuário de teste..."
sqlite3 "$DB_PATH" "INSERT INTO users (email, password_hash, nome, ativo, role, created_at) VALUES ('teste_backup@test.com', 'hash123', 'Teste Backup', 1, 'user', datetime('now'));"

# Contar após modificação
MODIFIED_USERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users;")
EXPECTED_MODIFIED=$((ORIGINAL_USERS + 1))

assert_equal "$MODIFIED_USERS" "$EXPECTED_MODIFIED" "Banco modificado deve ter +1 usuário"

echo "  📊 Estado modificado:"
echo "     - Usuários antes: $ORIGINAL_USERS"
echo "     - Usuários depois: $MODIFIED_USERS"
echo ""

# ==================================================
# TESTE 4: Restaurar do backup
# ==================================================
echo "🔍 TESTE 4: Restaurar banco do backup"

# Fazer backup do banco modificado (para não perder dados reais)
TEMP_MODIFIED="$BACKUP_DIR/modified_temp.db"
cp "$DB_PATH" "$TEMP_MODIFIED"

# Restaurar do backup
echo "  Restaurando do backup..."
cp "$BACKUP_FILE" "$DB_PATH"

# Verificar que banco foi restaurado
RESTORED_USERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users;")

assert_equal "$RESTORED_USERS" "$ORIGINAL_USERS" "Usuários devem voltar ao estado original após restore"

echo "  📊 Estado restaurado:"
echo "     - Usuários originais: $ORIGINAL_USERS"
echo "     - Usuários restaurados: $RESTORED_USERS"
echo ""

# ==================================================
# TESTE 5: Validar dados restaurados
# ==================================================
echo "🔍 TESTE 5: Validar dados específicos"

# Verificar que usuário de teste NÃO existe (foi restaurado)
TEST_USER_EXISTS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE email='teste_backup@test.com';")

assert_equal "$TEST_USER_EXISTS" "0" "Usuário de teste NÃO deve existir após restore"

# Verificar que admin ainda existe
ADMIN_EXISTS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE email='admin@email.com';")

if [ "$ADMIN_EXISTS" -gt 0 ]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "  ${GREEN}✅ PASS:${NC} Usuário admin preservado"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "  ${RED}❌ FAIL:${NC} Usuário admin perdido!"
fi

# Verificar transações
RESTORED_TRANSACTIONS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM journal_entries;")

assert_equal "$RESTORED_TRANSACTIONS" "$ORIGINAL_COUNT" "Transações devem ser restauradas completamente"

echo ""

# ==================================================
# TESTE 6: Backup comprimido (gzip)
# ==================================================
echo "🔍 TESTE 6: Backup comprimido (gzip)"

COMPRESSED_BACKUP="$BACKUP_DIR/financas_backup_${TIMESTAMP}.db.gz"

echo "  Comprimindo backup..."
gzip -c "$BACKUP_FILE" > "$COMPRESSED_BACKUP"

assert_file_exists "$COMPRESSED_BACKUP" "Backup comprimido deve ser criado"

# Comparar tamanhos
ORIGINAL_SIZE=$(stat -f%z "$BACKUP_FILE")
COMPRESSED_SIZE=$(stat -f%z "$COMPRESSED_BACKUP")
COMPRESSION_RATIO=$(echo "scale=2; ($ORIGINAL_SIZE - $COMPRESSED_SIZE) / $ORIGINAL_SIZE * 100" | bc)

echo "  📦 Compressão:"
echo "     - Original: $(du -h "$BACKUP_FILE" | awk '{print $1}')"
echo "     - Comprimido: $(du -h "$COMPRESSED_BACKUP" | awk '{print $1}')"
echo "     - Economia: ${COMPRESSION_RATIO}%"

if (( $(echo "$COMPRESSION_RATIO > 0" | bc -l) )); then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "  ${GREEN}✅ PASS:${NC} Compressão funcionando (${COMPRESSION_RATIO}% economia)"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "  ${RED}❌ FAIL:${NC} Compressão não reduziu tamanho"
fi
echo ""

# ==================================================
# TESTE 7: Restore de backup comprimido
# ==================================================
echo "🔍 TESTE 7: Restore de backup comprimido"

DECOMPRESSED_FILE="$BACKUP_DIR/restored_from_gz.db"

echo "  Descomprimindo e restaurando..."
gunzip -c "$COMPRESSED_BACKUP" > "$DECOMPRESSED_FILE"

assert_file_exists "$DECOMPRESSED_FILE" "Backup descomprimido deve existir"

# Verificar integridade
DECOMPRESSED_INTEGRITY=$(sqlite3 "$DECOMPRESSED_FILE" "PRAGMA integrity_check;" 2>&1)

if [ "$DECOMPRESSED_INTEGRITY" == "ok" ]; then
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "  ${GREEN}✅ PASS:${NC} Backup descomprimido íntegro"
else
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "  ${RED}❌ FAIL:${NC} Backup descomprimido corrompido"
fi

# Verificar dados
DECOMPRESSED_USERS=$(sqlite3 "$DECOMPRESSED_FILE" "SELECT COUNT(*) FROM users;")

assert_equal "$DECOMPRESSED_USERS" "$ORIGINAL_USERS" "Dados devem ser idênticos ao backup original"

echo ""

# ==================================================
# LIMPEZA
# ==================================================
echo "🧹 Limpeza de arquivos temporários..."

# Manter apenas o backup mais recente
rm -f "$TEMP_MODIFIED"
rm -f "$DECOMPRESSED_FILE"

echo "  Arquivos de backup mantidos:"
echo "     - $BACKUP_FILE"
echo "     - $COMPRESSED_BACKUP"
echo ""

# ==================================================
# RESUMO FINAL
# ==================================================
echo "============================================================"
echo "📊 RESUMO DOS TESTES DE BACKUP/RESTORE"
echo "============================================================"
echo -e "✅ Testes passaram: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Testes falharam: ${RED}$TESTS_FAILED${NC}"
echo "📋 Total de testes: $((TESTS_PASSED + TESTS_FAILED))"
echo "============================================================"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 SUCESSO! Backup e restore funcionando corretamente!${NC}"
    echo ""
    echo "✅ Validações bem-sucedidas:"
    echo "   - Backup SQLite nativo (.backup)"
    echo "   - Restore completo de dados"
    echo "   - Integridade verificada"
    echo "   - Compressão gzip (${COMPRESSION_RATIO}% economia)"
    echo "   - Restore de backup comprimido"
    echo ""
    echo "📁 Backups criados:"
    echo "   - $BACKUP_FILE"
    echo "   - $COMPRESSED_BACKUP"
    echo ""
    echo "🚀 Próximos passos para produção:"
    echo "   1. Configurar rclone com S3: ./scripts/setup-rclone.sh"
    echo "   2. Testar upload S3: ./scripts/backup-to-s3.sh"
    echo "   3. Configurar cron diário"
    echo ""
    exit 0
else
    echo -e "${RED}🚨 FALHA! Problemas detectados no backup/restore!${NC}"
    echo ""
    echo "⚠️ AÇÃO REQUERIDA: Revisar falhas acima"
    echo ""
    exit 1
fi
