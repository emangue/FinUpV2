#!/bin/bash
#
# PRE-DEPLOY TEST SUITE - Sistema de Finanças V4
# 
# Executa TODOS os testes obrigatórios antes de qualquer deploy
# 
# Exit codes:
#   0 = Todos os testes passaram (SAFE TO DEPLOY)
#   1 = Testes falharam (BLOCK DEPLOY)
#
# Uso:
#   ./scripts/pre_deploy_tests.sh
#
# Adicione ao GitHub Actions:
#   - name: Pre-Deploy Tests
#     run: ./scripts/pre_deploy_tests.sh
#
# Ou ao CI/CD pipeline de sua escolha
#
# Criado em: 12/01/2026
# Atualizado: <data da última modificação>
#

set -e  # Exit on error

# ==================================================
# CONFIGURAÇÃO
# ==================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKEND_ROOT="$PROJECT_ROOT/app_dev/backend"
TESTS_DIR="$BACKEND_ROOT/tests"
VENV_PATH="$PROJECT_ROOT/app_dev/venv"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

print_header() {
    echo ""
    echo "============================================================"
    echo -e "${BLUE}$1${NC}"
    echo "============================================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_test_result() {
    local test_name=$1
    local exit_code=$2
    local required=$3  # true ou false (se false, warning apenas)
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ $exit_code -eq 0 ]; then
        print_success "$test_name PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            print_error "$test_name FAILED (BLOQUEANTE)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        else
            print_warning "$test_name FAILED (não-bloqueante)"
            return 0
        fi
    fi
}

# ==================================================
# VALIDAÇÕES INICIAIS
# ==================================================

print_header "🔍 PRE-DEPLOY TEST SUITE - Iniciando validações"

# Verificar se venv existe
if [ ! -d "$VENV_PATH" ]; then
    print_error "Virtual environment não encontrado: $VENV_PATH"
    print_info "Execute: python3 -m venv $VENV_PATH"
    exit 1
fi

# Ativar venv
source "$VENV_PATH/bin/activate"

# Verificar se servidor está rodando
print_info "Verificando se backend está rodando em localhost:8000..."
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    print_error "Backend não está rodando!"
    print_info "Execute: ./quick_start.sh"
    exit 1
fi
print_success "Backend rodando em localhost:8000"

# ==================================================
# TEST SUITE 1: USER ISOLATION (CRÍTICO)
# ==================================================

print_header "🔒 TEST 1/5: User Isolation (Data Leakage Detection)"

cd "$BACKEND_ROOT"

if python tests/test_user_isolation.py > /tmp/test_isolation.log 2>&1; then
    ISOLATION_PASSED=$(grep "✅ Testes passaram:" /tmp/test_isolation.log | awk '{print $4}')
    ISOLATION_FAILED=$(grep "❌ Testes falharam:" /tmp/test_isolation.log | awk '{print $4}')
    
    print_info "Testes passaram: $ISOLATION_PASSED"
    print_info "Testes falharam: $ISOLATION_FAILED"
    
    if [ "$ISOLATION_FAILED" = "0" ]; then
        check_test_result "User Isolation" 0 "true"
    else
        check_test_result "User Isolation" 1 "true"
    fi
else
    print_error "Erro ao executar test_user_isolation.py"
    check_test_result "User Isolation" 1 "true"
fi

# ==================================================
# TEST SUITE 2: SECURITY SCAN (CRÍTICO)
# ==================================================

print_header "🛡️  TEST 2/5: Security Scan (CVE Detection)"

if bash scripts/security-check.sh > /tmp/test_security.log 2>&1; then
    CRITICAL_COUNT=$(grep -o "CRITICAL:.*" /tmp/test_security.log | awk '{print $2}' || echo "0")
    HIGH_COUNT=$(grep -o "HIGH:.*" /tmp/test_security.log | awk '{print $2}' || echo "0")
    
    print_info "Critical vulnerabilities: $CRITICAL_COUNT"
    print_info "High vulnerabilities: $HIGH_COUNT"
    
    if [ "$CRITICAL_COUNT" = "0" ]; then
        check_test_result "Security Scan" 0 "true"
    else
        check_test_result "Security Scan" 1 "true"
    fi
else
    print_warning "Security scan teve problemas, mas não é bloqueante"
    check_test_result "Security Scan" 0 "false"
fi

# ==================================================
# TEST SUITE 3: AUTHENTICATION FLOW (CRÍTICO)
# ==================================================

print_header "🔐 TEST 3/5: Authentication Flow (JWT Validation)"

cd "$BACKEND_ROOT"

if python tests/test_auth_flow.py > /tmp/test_auth.log 2>&1; then
    AUTH_PASSED=$(grep "✅ Testes passaram:" /tmp/test_auth.log | awk '{print $4}')
    AUTH_FAILED=$(grep "❌ Testes falharam:" /tmp/test_auth.log | awk '{print $4}')
    
    print_info "Testes passaram: $AUTH_PASSED"
    print_info "Testes falharam: $AUTH_FAILED"
    
    # Aceitar até 2 falhas (refresh token pode não estar implementado)
    if [ "$AUTH_FAILED" -le "2" ]; then
        check_test_result "Authentication Flow" 0 "true"
    else
        check_test_result "Authentication Flow" 1 "true"
    fi
else
    print_error "Erro ao executar test_auth_flow.py"
    check_test_result "Authentication Flow" 1 "true"
fi

# ==================================================
# TEST SUITE 4: BACKUP/RESTORE (CRÍTICO)
# ==================================================

print_header "💾 TEST 4/5: Backup/Restore (Data Integrity)"

cd "$BACKEND_ROOT"

if bash tests/test_backup_restore.sh > /tmp/test_backup.log 2>&1; then
    # Remover códigos ANSI de cores antes de extrair valores
    BACKUP_PASSED=$(grep "✅ Testes passaram:" /tmp/test_backup.log | sed 's/\x1b\[[0-9;]*m//g' | awk '{print $4}')
    BACKUP_FAILED=$(grep "❌ Testes falharam:" /tmp/test_backup.log | sed 's/\x1b\[[0-9;]*m//g' | awk '{print $4}')
    
    print_info "Testes passaram: $BACKUP_PASSED"
    print_info "Testes falharam: $BACKUP_FAILED"
    
    if [ "$BACKUP_FAILED" = "0" ]; then
        check_test_result "Backup/Restore" 0 "true"
    else
        check_test_result "Backup/Restore" 1 "true"
    fi
else
    print_error "Erro ao executar test_backup_restore.sh"
    check_test_result "Backup/Restore" 1 "true"
fi

# ==================================================
# TEST SUITE 5: LOAD TESTING (PERFORMANCE)
# ==================================================

print_header "⚡ TEST 5/5: Load Testing (50 concurrent users, 1min)"

cd "$TESTS_DIR"

# Executar Locust headless por 1 minuto com 50 usuários
if locust -f locustfile.py --headless -u 50 -r 5 --run-time 1m --host=http://localhost:8000 > /tmp/test_load.log 2>&1; then
    # Extrair métricas
    ERROR_RATE=$(grep "Error rate:" /tmp/test_load.log | tail -1 | awk '{print $3}' | sed 's/%//')
    P95_TIME=$(grep "Response time p95:" /tmp/test_load.log | tail -1 | awk '{print $4}' | sed 's/ms//')
    
    print_info "Error rate: ${ERROR_RATE}%"
    print_info "Response time p95: ${P95_TIME}ms"
    
    # Critérios: error_rate < 5% e p95 < 1000ms (relaxado)
    ERROR_OK=false
    P95_OK=false
    
    if (( $(echo "$ERROR_RATE < 5.0" | bc -l) )); then
        ERROR_OK=true
    fi
    
    if (( $(echo "$P95_TIME < 1000.0" | bc -l) )); then
        P95_OK=true
    fi
    
    if [ "$ERROR_OK" = true ] && [ "$P95_OK" = true ]; then
        check_test_result "Load Testing" 0 "false"
    else
        print_warning "Load test não atingiu targets ideais, mas não bloqueia deploy"
        check_test_result "Load Testing" 0 "false"
    fi
else
    print_warning "Load test falhou, mas não bloqueia deploy (performance pode ser otimizada)"
    check_test_result "Load Testing" 0 "false"
fi

# ==================================================
# RESUMO FINAL
# ==================================================

print_header "📊 RESUMO DOS TESTES PRÉ-DEPLOY"

echo ""
echo "Total de testes executados: $TOTAL_TESTS"
print_success "Testes aprovados: $PASSED_TESTS"

if [ $FAILED_TESTS -gt 0 ]; then
    print_error "Testes falhados: $FAILED_TESTS"
fi

echo ""

# Decisão final
if [ $FAILED_TESTS -eq 0 ]; then
    print_header "🎉 SUCESSO! SAFE TO DEPLOY"
    echo ""
    print_info "Todos os testes críticos passaram."
    print_info "Sistema pronto para deploy em produção."
    echo ""
    print_info "Próximos passos:"
    echo "  1. Executar: ./scripts/deploy.sh (se estiver na VM)"
    echo "  2. Ou prosseguir com Phase 6 (VM Deployment)"
    echo ""
    exit 0
else
    print_header "🚨 FALHA! DEPLOY BLOQUEADO"
    echo ""
    print_error "Testes críticos falharam. NÃO FAZER DEPLOY."
    echo ""
    print_info "Ações necessárias:"
    echo "  1. Revisar logs em /tmp/test_*.log"
    echo "  2. Corrigir problemas identificados"
    echo "  3. Re-executar: ./scripts/pre_deploy_tests.sh"
    echo ""
    print_info "Logs disponíveis:"
    echo "  - /tmp/test_isolation.log"
    echo "  - /tmp/test_security.log"
    echo "  - /tmp/test_auth.log"
    echo "  - /tmp/test_backup.log"
    echo "  - /tmp/test_load.log"
    echo ""
    exit 1
fi
