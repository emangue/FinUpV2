#!/bin/bash

# 💡 Deploy Helper - Comandos e Lembretes
# Uso: ./scripts/deploy/deploy_help.sh

echo "🚀 GUIA RÁPIDO DE DEPLOY - ProjetoFinancasV5"
echo "============================================="
echo ""

echo "📋 REGRA FUNDAMENTAL:"
echo "   LOCAL → GIT → SERVIDOR"
echo "   ❌ NUNCA editar código diretamente no servidor!"
echo ""

echo "🔧 COMANDOS DISPONÍVEIS:"
echo "   ./scripts/deploy/quick_deploy.sh              # Deploy rápido (após commit+push)"
echo "   ./scripts/deploy/deploy_safe_v2.sh            # Deploy com validações completas" 
echo "   ./scripts/deploy/deploy_safe_v2.sh --with-migrations  # Deploy + migrations"
echo "   ./scripts/deploy/deploy_help.sh               # Este guia"
echo ""

echo "📝 WORKFLOW TÍPICO:"
echo "   1. Modificar código LOCALMENTE"
echo "   2. git add . && git commit -m 'descrição'"
echo "   3. git push origin main"
echo "   4. ./scripts/deploy/quick_deploy.sh"
echo ""

echo "🔍 VALIDAR ANTES DO DEPLOY:"
echo "   git status                    # Deve estar limpo"
echo "   git log --oneline -3          # Ver últimos commits"
echo "   python3 -c 'import app_dev.backend.app.main'  # Testar imports"
echo ""

echo "🛠️ COMANDOS DO SERVIDOR (após deploy):"
echo "   ssh minha-vps-hostinger 'systemctl status finup-backend'"
echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -f'"
echo "   ssh minha-vps-hostinger 'curl -s localhost:8000/api/health'"
echo ""

echo "🚨 EM CASO DE PROBLEMA:"
echo "   # Logs do servidor"
echo "   ssh minha-vps-hostinger 'journalctl -u finup-backend -n 50'"
echo ""
echo "   # Rollback rápido"
echo "   ssh minha-vps-hostinger 'cd /var/www/finup && git checkout HEAD~1'"
echo "   ssh minha-vps-hostinger 'systemctl restart finup-backend'"
echo ""
echo "   # Restaurar backup do banco"
echo "   ssh minha-vps-hostinger 'cd /var/www/finup/app_dev/backend/database'"
echo "   ssh minha-vps-hostinger 'ls -lt backups_daily/ | head -5'"
echo "   ssh minha-vps-hostinger 'cp backups_daily/backup_xxx.db financas_dev.db'"
echo ""

echo "✅ URLS PARA TESTE:"
echo "   🌐 Frontend: https://finup.srv1045889.hstgr.cloud/"
echo "   🔌 API Health: https://finup.srv1045889.hstgr.cloud/api/health"  
echo "   📚 API Docs: https://finup.srv1045889.hstgr.cloud/docs"
echo ""

echo "💡 LEMBRETE:"
echo "   Sempre seguir: LOCAL → GIT → SERVIDOR"
echo "   Nunca editar código diretamente no servidor!"
echo "   Sempre fazer backup antes de mudanças importantes!"
echo ""

# Verificar se estamos na pasta correta
if [ ! -f "app_dev/backend/app/main.py" ]; then
    echo "⚠️  AVISO: Execute este script da raiz do projeto ProjetoFinancasV5!"
    echo "   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
fi