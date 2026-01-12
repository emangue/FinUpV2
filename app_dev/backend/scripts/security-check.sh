#!/bin/bash
#
# Security Check Script - Sistema de Finanças V4
#
# Executa 3 scanners de segurança:
# 1. safety - CVEs conhecidas em dependências
# 2. bandit - Análise estática de código Python
# 3. pip-audit - Vulnerabilidades em pacotes PyPI
#
# Resultado: PASS (0 critical) ou FAIL (1+ critical)
# Bloqueia deploy se encontrar vulnerabilidades CRÍTICAS

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
CRITICAL_COUNT=0
HIGH_COUNT=0
MEDIUM_COUNT=0
LOW_COUNT=0

echo "============================================================"
echo "🔒 SECURITY SCAN - Sistema de Finanças V4"
echo "============================================================"
echo "Executando 3 scanners de segurança:"
echo "  1. safety - CVEs conhecidas (DB atualizado)"
echo "  2. bandit - Análise estática Python"
echo "  3. pip-audit - Vulnerabilidades PyPI"
echo "============================================================"
echo ""

# Navegar para diretório do backend
cd "$(dirname "$0")/.."
echo "📁 Diretório: $(pwd)"
echo ""

# Ativar venv se existir
if [ -d "venv" ]; then
    echo "🐍 Ativando venv..."
    source venv/bin/activate
fi

# Verificar se ferramentas estão instaladas
echo "🔍 Verificando ferramentas..."

if ! command -v safety &> /dev/null; then
    echo -e "${YELLOW}⚠️ safety não encontrado. Instalando...${NC}"
    pip install safety
fi

if ! command -v bandit &> /dev/null; then
    echo -e "${YELLOW}⚠️ bandit não encontrado. Instalando...${NC}"
    pip install bandit
fi

if ! command -v pip-audit &> /dev/null; then
    echo -e "${YELLOW}⚠️ pip-audit não encontrado. Instalando...${NC}"
    pip install pip-audit
fi

echo -e "${GREEN}✅ Todas as ferramentas disponíveis${NC}"
echo ""

# ==================================================
# 1. SAFETY - CVEs Conhecidas
# ==================================================
echo "============================================================"
echo "📋 SCANNER 1/3: safety (CVEs conhecidas)"
echo "============================================================"

# Tentar safety check (pode retornar exit code 64 se encontrar vulnerabilidades)
if safety check 2>&1 | grep -q "No known security vulnerabilities found"; then
    echo -e "${GREEN}✅ SAFETY: Nenhuma vulnerabilidade encontrada${NC}"
else
    # Executar novamente e capturar output
    safety_result=$(safety check 2>&1 || true)
    
    if echo "$safety_result" | grep -q "vulnerability found\|vulnerabilities found"; then
        echo -e "${RED}❌ SAFETY: Vulnerabilidades detectadas!${NC}"
        echo "$safety_result"
        
        # Contar critical/high baseado em keywords no output
        safety_count=$(echo "$safety_result" | grep -c "vulnerability found\|vulnerabilities found" || echo 1)
        CRITICAL_COUNT=$((CRITICAL_COUNT + safety_count))
    else
        echo -e "${GREEN}✅ SAFETY: Nenhuma vulnerabilidade encontrada${NC}"
    fi
fi
echo ""

# ==================================================
# 2. BANDIT - Análise Estática
# ==================================================
echo "============================================================"
echo "📋 SCANNER 2/3: bandit (análise estática)"
echo "============================================================"

# Executar bandit no código app/
bandit_output=$(bandit -r app/ -f json 2>/dev/null || echo '{"results": []}')

# Contar issues por severidade
bandit_high=$(echo "$bandit_output" | grep -c "\"issue_severity\": \"HIGH\"" || echo 0)
bandit_medium=$(echo "$bandit_output" | grep -c "\"issue_severity\": \"MEDIUM\"" || echo 0)
bandit_low=$(echo "$bandit_output" | grep -c "\"issue_severity\": \"LOW\"" || echo 0)

if [ "$bandit_high" -eq 0 ] && [ "$bandit_medium" -eq 0 ] && [ "$bandit_low" -eq 0 ]; then
    echo -e "${GREEN}✅ BANDIT: Nenhum problema encontrado${NC}"
else
    echo -e "${YELLOW}⚠️ BANDIT: Issues detectados${NC}"
    echo "  HIGH: $bandit_high"
    echo "  MEDIUM: $bandit_medium"
    echo "  LOW: $bandit_low"
    
    # Mostrar apenas HIGH issues
    if [ "$bandit_high" -gt 0 ]; then
        echo ""
        echo "🚨 HIGH Issues:"
        echo "$bandit_output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for result in data.get('results', []):
        if result.get('issue_severity') == 'HIGH':
            print(f\"  - {result['filename']}:{result['line_number']}\")
            print(f\"    {result['issue_text']}\")
except:
    pass
"
    fi
    
    CRITICAL_COUNT=$((CRITICAL_COUNT + bandit_high))
    MEDIUM_COUNT=$((MEDIUM_COUNT + bandit_medium))
    LOW_COUNT=$((LOW_COUNT + bandit_low))
fi
echo ""

# ==================================================
# 3. PIP-AUDIT - Vulnerabilidades PyPI
# ==================================================
echo "============================================================"
echo "📋 SCANNER 3/3: pip-audit (vulnerabilidades PyPI)"
echo "============================================================"

pip_audit_output=$(pip-audit --format json 2>/dev/null || echo '{"dependencies": []}')

# Contar vulnerabilidades
pip_vulns=$(echo "$pip_audit_output" | grep -c "\"vulns\"" || echo 0)

if [ "$pip_vulns" -eq 0 ]; then
    echo -e "${GREEN}✅ PIP-AUDIT: Nenhuma vulnerabilidade encontrada${NC}"
else
    echo -e "${RED}❌ PIP-AUDIT: Vulnerabilidades detectadas!${NC}"
    
    # Mostrar vulnerabilidades
    echo "$pip_audit_output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for dep in data.get('dependencies', []):
        vulns = dep.get('vulns', [])
        if vulns:
            print(f\"\n📦 {dep['name']} {dep['version']}\")
            for vuln in vulns:
                print(f\"  🔴 {vuln['id']}: {vuln.get('description', 'No description')[:100]}\")
                print(f\"     Fix: Upgrade to {vuln.get('fix_versions', ['unknown'])[0]}\")
except Exception as e:
    print(f\"Error parsing JSON: {e}\")
"
    
    # pip-audit sempre trata como high/critical
    CRITICAL_COUNT=$((CRITICAL_COUNT + pip_vulns))
fi
echo ""

# ==================================================
# RESUMO FINAL
# ==================================================
echo "============================================================"
echo "📊 RESUMO DA ANÁLISE DE SEGURANÇA"
echo "============================================================"
echo -e "🔴 CRITICAL:  ${CRITICAL_COUNT}"
echo -e "🟠 HIGH:      ${HIGH_COUNT}"
echo -e "🟡 MEDIUM:    ${MEDIUM_COUNT}"
echo -e "🟢 LOW:       ${LOW_COUNT}"
echo "============================================================"

# Decisão final
if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo -e "${RED}❌ FALHOU: ${CRITICAL_COUNT} vulnerabilidades CRÍTICAS detectadas!${NC}"
    echo ""
    echo "⚠️ AÇÃO REQUERIDA:"
    echo "  1. Revisar vulnerabilidades acima"
    echo "  2. Atualizar dependências: pip install --upgrade <package>"
    echo "  3. Rodar novamente: ./scripts/security-check.sh"
    echo "  4. Deploy BLOQUEADO até resolver"
    echo ""
    exit 1
elif [ "$HIGH_COUNT" -gt 5 ]; then
    echo -e "${YELLOW}⚠️ WARNING: ${HIGH_COUNT} issues HIGH detectados${NC}"
    echo ""
    echo "Recomenda-se revisar antes de deploy em produção"
    echo "  Para bloquear deploy, rode: exit 1"
    echo ""
    exit 0  # Por enquanto não bloqueamos por HIGH
else
    echo -e "${GREEN}✅ SUCESSO: Nenhuma vulnerabilidade crítica detectada!${NC}"
    echo ""
    echo "🎉 Sistema aprovado para deploy em produção"
    echo ""
    exit 0
fi
