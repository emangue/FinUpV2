#!/bin/bash

# ==========================================
# AUDITORIA COMPLETA DO SERVIDOR
# Mapeia TUDO que está no servidor antes de limpar
# ==========================================

SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

echo "🔍 AUDITORIA COMPLETA DO SERVIDOR"
echo "=================================================="
echo "Data: $(date)"
echo "Servidor: $SERVER"
echo ""

# Função SSH com timeout
ssh_cmd() {
    timeout 15 ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SERVER" "$1" 2>/dev/null || echo "FALHA: $1"
}

echo "1. 📊 PROCESSOS EM EXECUÇÃO"
echo "----------------------------------------"
echo "Todos os processos Python/Node/Uvicorn/Next:"
ssh_cmd "ps aux | grep -E '(python|node|uvicorn|next|npm)' | grep -v grep"
echo ""

echo "2. 🔌 PORTAS EM USO"
echo "----------------------------------------"
ssh_cmd "netstat -tlnp | grep -E '(8000|3000|80|443)'"
echo ""

echo "3. 📁 ESTRUTURA DE PASTAS"
echo "----------------------------------------"
echo "Pasta /var/www:"
ssh_cmd "ls -la /var/www/ 2>/dev/null || echo 'Pasta /var/www não existe'"
echo ""

echo "Se /var/www/financas existe:"
ssh_cmd "ls -la /var/www/financas/ 2>/dev/null || echo 'Pasta /var/www/financas não existe'"
echo ""

echo "Subpastas de /var/www/financas:"
ssh_cmd "find /var/www/financas -maxdepth 3 -type d 2>/dev/null || echo 'Nada em /var/www/financas'"
echo ""

echo "4. 🗄️ DADOS E CONFIGURAÇÕES"
echo "----------------------------------------"
echo "Pasta /var/lib/financas:"
ssh_cmd "ls -la /var/lib/financas/ 2>/dev/null || echo 'Pasta /var/lib/financas não existe'"
echo ""

echo "Bancos de dados SQLite:"
ssh_cmd "find / -name '*.db' -type f 2>/dev/null | grep -v proc | head -10"
echo ""

echo "5. 📋 LOGS"
echo "----------------------------------------"
echo "Logs em /var/log:"
ssh_cmd "ls -la /var/log/ | grep -E '(backend|frontend|financas|uvicorn|next)'"
echo ""

echo "Últimas linhas do backend.log (se existir):"
ssh_cmd "tail -5 /var/log/backend.log 2>/dev/null || echo 'backend.log não existe'"
echo ""

echo "6. 🌐 NGINX E APACHE"
echo "----------------------------------------"
echo "Status nginx:"
ssh_cmd "systemctl status nginx 2>/dev/null | head -5 || echo 'nginx não instalado ou não ativo'"
echo ""

echo "Sites nginx habilitados:"
ssh_cmd "ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo 'Nginx sites não encontrados'"
echo ""

echo "7. 🐍 PYTHON E AMBIENTES"
echo "----------------------------------------"
echo "Versão Python:"
ssh_cmd "python3 --version"
echo ""

echo "Ambientes virtuais encontrados:"
ssh_cmd "find / -name 'venv' -type d 2>/dev/null | grep -v proc | head -5"
echo ""

echo "8. 📦 NODE.JS"
echo "----------------------------------------"
echo "Versão Node.js:"
ssh_cmd "node --version 2>/dev/null || echo 'Node.js não instalado'"
echo ""

echo "Versão NPM:"
ssh_cmd "npm --version 2>/dev/null || echo 'NPM não instalado'"
echo ""

echo "9. 🔧 SERVIÇOS SYSTEMD"
echo "----------------------------------------"
echo "Serviços relacionados a financas:"
ssh_cmd "systemctl list-units | grep -i financas || echo 'Nenhum serviço financas encontrado'"
echo ""

echo "10. 💾 USO DE DISCO"
echo "----------------------------------------"
ssh_cmd "df -h | head -5"
echo ""

echo "Pastas que mais ocupam espaço em /var:"
ssh_cmd "du -sh /var/* 2>/dev/null | sort -hr | head -10"
echo ""

echo "11. 🔥 RESUMO CRÍTICO"
echo "=================================================="
echo ""
echo "PROCESSOS CRÍTICOS RODANDO:"
ssh_cmd "ps aux | grep -E '(uvicorn|next)' | grep -v grep | wc -l | xargs echo 'Total:'"
echo ""

echo "PORTAS OCUPADAS:"
ssh_cmd "netstat -tlnp | grep -E ':(8000|3000)' | wc -l | xargs echo 'Total:'"
echo ""

echo "APPS EM /var/www:"
ssh_cmd "ls /var/www/ 2>/dev/null | wc -l | xargs echo 'Total de pastas:'"
echo ""

echo ""
echo "🎯 PRÓXIMO PASSO: Execute clean_server.sh para limpar tudo"
echo "=================================================="