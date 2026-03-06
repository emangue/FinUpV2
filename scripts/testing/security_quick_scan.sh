#!/usr/bin/env bash
# webapp-security-audit: Quick automated recon scan
# Usage: bash scripts/testing/security_quick_scan.sh [target_directory]
# Outputs findings to stdout with severity labels
#
# Exemplo:
#   bash scripts/testing/security_quick_scan.sh app_dev/backend
#   bash scripts/testing/security_quick_scan.sh app_dev/frontend/src

TARGET="${1:-.}"
FINDINGS=0

echo "======================================"
echo "  Web App Security Quick Scan"
echo "  Target: $TARGET"
echo "  Date: $(date)"
echo "======================================"
echo ""

# -------------------------------------------------------
check() {
  local label="$1"
  local severity="$2"
  local pattern="$3"
  local include="$4"

  results=$(grep -rn "$pattern" "$TARGET" $include \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude-dir=vendor \
    --exclude-dir=.next \
    --exclude-dir=__pycache__ \
    2>/dev/null)

  if [ -n "$results" ]; then
    echo "[$severity] $label"
    echo "$results" | head -10
    if [ $(echo "$results" | wc -l) -gt 10 ]; then
      echo "  ... and $(( $(echo "$results" | wc -l) - 10 )) more"
    fi
    echo ""
    FINDINGS=$((FINDINGS + 1))
  fi
}

# -------------------------------------------------------
echo "--- 🔴 CRITICAL PATTERNS ---"
echo ""

check "Hardcoded Secrets / API Keys" "CRITICAL" \
  'api[_-]key\s*[=:]\s*["'"'"'][^${"'"'"'"\n]\{10,\}' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php --include=*.rb'

check "AWS Access Keys" "CRITICAL" \
  'AKIA[0-9A-Z]\{16\}' \
  '--include=*.js --include=*.ts --include=*.py --include=*.env --include=*.json'

check "Hardcoded Password/Secret in Code" "CRITICAL" \
  'password\s*=\s*["'"'"'][^${"'"'"'"\n]\{6,\}\|secret\s*=\s*["'"'"'][^${"'"'"'"\n]\{6,\}' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php'

check "SQL String Concatenation (Potential SQLi)" "CRITICAL" \
  'query\s*[+=]\s*.*\$\|query\s*[+=]\s*.*+\s*req\.\|cursor\.execute(f"\|execute(\s*".*+' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php'

check "eval() with Dynamic Input" "CRITICAL" \
  'eval(\s*req\.\|eval(\s*\$_\|eval(\s*request\.' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php'

check "Command Injection Risk" "CRITICAL" \
  'os\.system(\|shell_exec(\|child_process\.exec(\|subprocess\.call.*shell=True' \
  '--include=*.py --include=*.js --include=*.php'

check "Unsafe Deserialization" "CRITICAL" \
  'pickle\.loads(\|unserialize(\$_\|yaml\.load(' \
  '--include=*.py --include=*.php'

check "Path Traversal Risk" "CRITICAL" \
  'open(\s*.*\$_GET\|open(\s*.*req\.params\|readFile(\s*.*req\.\|include(\s*\$_GET' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php'

echo "--- 🟠 HIGH RISK PATTERNS ---"
echo ""

check "dangerouslySetInnerHTML (XSS)" "HIGH" \
  'dangerouslySetInnerHTML' \
  '--include=*.jsx --include=*.tsx --include=*.js'

check "innerHTML with Variable (XSS)" "HIGH" \
  '\.innerHTML\s*=\s*[^'"'"'"]\|\.innerHTML\s*+=\s*[^'"'"'"]' \
  '--include=*.js --include=*.ts'

check "JWT Without Algorithm Pinning" "HIGH" \
  'jwt\.verify([^,)]*,[^,)]*)[^{]' \
  '--include=*.js --include=*.ts'

check "CORS Wildcard" "HIGH" \
  "origin:\s*['\"]\\*['\"]" \
  '--include=*.js --include=*.ts --include=*.py'

check "Debug Mode Enabled" "HIGH" \
  'DEBUG\s*=\s*True\|app\.run(debug=True\|debug:\s*true' \
  '--include=*.py --include=*.js --include=*.ts --include=*.env'

check "JWT/Token in localStorage" "HIGH" \
  'localStorage\.setItem.*[Tt]oken\|localStorage\.setItem.*jwt\|localStorage\.setItem.*auth' \
  '--include=*.js --include=*.ts --include=*.jsx --include=*.tsx'

check "MD5/SHA1 for Passwords" "HIGH" \
  'md5(\|sha1(\|hashlib\.md5\|hashlib\.sha1' \
  '--include=*.js --include=*.ts --include=*.py --include=*.php'

check "Mass Assignment Risk" "HIGH" \
  '\.create(\s*req\.body\|new.*Model(\s*req\.body\|\.update(\s*req\.body' \
  '--include=*.js --include=*.ts'

echo "--- 🟡 MEDIUM RISK PATTERNS ---"
echo ""

check "Sensitive Data in Logs" "MEDIUM" \
  'console\.log.*password\|console\.log.*token\|print.*password\|logger.*secret' \
  '--include=*.js --include=*.ts --include=*.py'

check "Open Redirect Risk" "MEDIUM" \
  'res\.redirect(\s*req\.\|redirect(\s*request\.\|location\.href\s*=\s*.*req\.' \
  '--include=*.js --include=*.ts --include=*.py'

check "No Rate Limiting on Auth Routes" "MEDIUM" \
  'router\.\(post\|put\).*login\|router\.\(post\|put\).*password' \
  '--include=*.js --include=*.ts'

# Check for .env files present
echo "[CHECK] .env files encontrados (verificar se estão no .gitignore):"
found_envs=$(find "$TARGET" -name ".env" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null)
if [ -n "$found_envs" ]; then
  echo "$found_envs"
  echo ""
fi

echo "--- ℹ️  INFO ---"
echo ""

# Check for package.json
if find "$TARGET" -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | grep -q .; then
  echo "[INFO] package.json encontrado — rode: npm audit --audit-level=high"
fi

# Check for requirements.txt
if find "$TARGET" -name "requirements*.txt" 2>/dev/null | grep -q .; then
  echo "[INFO] requirements.txt encontrado — rode: pip-audit"
fi

# Check for Dockerfile
if find "$TARGET" -name "Dockerfile" 2>/dev/null | grep -q .; then
  echo "[INFO] Dockerfile encontrado — verificar: sem secrets em ENV, USER não-root"
fi

echo ""
echo "======================================"
echo "  Scan Completo — $FINDINGS categorias com padrões suspeitos"
echo ""
echo "  ⚠️  Este é um scan baseado em grep."
echo "  Falsos positivos são possíveis — revisar cada finding manualmente."
echo "  Para análise com contexto completo, usar GitHub Copilot com:"
echo "  #copilot-instructions-security.md + #security-owasp-checklist.md"
echo "======================================"
