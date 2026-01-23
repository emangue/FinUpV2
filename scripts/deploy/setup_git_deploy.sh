#!/bin/bash
# 🚀 Script de Setup - Git Auto-Deploy na VPS
# Executar UMA VEZ no servidor via terminal web
# 
# Uso: bash setup_git_deploy.sh

set -e

echo "🔧 SETUP GIT AUTO-DEPLOY"
echo "========================================"
echo ""

# Configurações
REPO_PATH="/var/repo/finup.git"
APP_PATH="/var/www/finup"
HOOK_PATH="$REPO_PATH/hooks/post-receive"

# 1. Instalar Git (se necessário)
echo "📦 1/4: Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "   Instalando Git..."
    apt update && apt install -y git
fi
echo "   ✅ Git instalado: $(git --version)"

# 2. Criar repositório bare
echo ""
echo "📁 2/4: Criando repositório bare..."
mkdir -p "$REPO_PATH" "$APP_PATH"
cd "$REPO_PATH"
git init --bare
echo "   ✅ Repositório criado: $REPO_PATH"

# 3. Criar hook post-receive
echo ""
echo "🔗 3/4: Criando hook de auto-deploy..."
cat > "$HOOK_PATH" << 'HOOK_EOF'
#!/bin/bash
# Hook executado após git push
# Faz deploy automático da aplicação

set -e

APP_PATH="/var/www/finup"
LOG_FILE="/var/log/finup-deploy.log"

echo "========================================" >> "$LOG_FILE"
echo "🚀 DEPLOY INICIADO: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. Checkout do código
echo "📥 1/6: Atualizando código..." | tee -a "$LOG_FILE"
GIT_WORK_TREE="$APP_PATH" git checkout -f main 2>&1 | tee -a "$LOG_FILE"

# 2. Backup do banco (segurança)
echo "💾 2/6: Fazendo backup..." | tee -a "$LOG_FILE"
cd "$APP_PATH"
if [ -f "scripts/deploy/backup_daily.sh" ]; then
    ./scripts/deploy/backup_daily.sh >> "$LOG_FILE" 2>&1 || echo "⚠️  Backup falhou" | tee -a "$LOG_FILE"
fi

# 3. Instalar dependências Python
echo "📦 3/6: Instalando dependências..." | tee -a "$LOG_FILE"
cd "$APP_PATH/app_dev"
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r backend/requirements.txt --quiet >> "$LOG_FILE" 2>&1
    echo "   ✅ Dependências atualizadas" | tee -a "$LOG_FILE"
else
    echo "   ⚠️  venv não encontrado" | tee -a "$LOG_FILE"
fi

# 4. Migrations (se houver)
echo "🗄️  4/6: Aplicando migrations..." | tee -a "$LOG_FILE"
cd "$APP_PATH/app_dev/backend"
if [ -d "migrations" ]; then
    source ../venv/bin/activate
    alembic upgrade head >> "$LOG_FILE" 2>&1 || echo "   ⚠️  Sem migrations" | tee -a "$LOG_FILE"
fi

# 5. Reiniciar backend
echo "🔄 5/6: Reiniciando backend..." | tee -a "$LOG_FILE"
systemctl restart finup-backend >> "$LOG_FILE" 2>&1
sleep 3
if systemctl is-active --quiet finup-backend; then
    echo "   ✅ Backend reiniciado" | tee -a "$LOG_FILE"
else
    echo "   ❌ Erro ao reiniciar backend" | tee -a "$LOG_FILE"
    systemctl status finup-backend --no-pager | tee -a "$LOG_FILE"
fi

# 6. Reiniciar frontend (se existir)
echo "🎨 6/6: Reiniciando frontend..." | tee -a "$LOG_FILE"
if systemctl list-units --full -all | grep -q finup-frontend; then
    systemctl restart finup-frontend >> "$LOG_FILE" 2>&1
    echo "   ✅ Frontend reiniciado" | tee -a "$LOG_FILE"
else
    echo "   ⚠️  Frontend service não encontrado" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "✅ DEPLOY CONCLUÍDO: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
HOOK_EOF

chmod +x "$HOOK_PATH"
echo "   ✅ Hook criado: $HOOK_PATH"

# 4. Configurar log
echo ""
echo "📝 4/4: Configurando logs..."
touch /var/log/finup-deploy.log
chmod 644 /var/log/finup-deploy.log
echo "   ✅ Log criado: /var/log/finup-deploy.log"

echo ""
echo "========================================"
echo "✅ SETUP COMPLETO!"
echo "========================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. No seu MacBook, adicione o remote VPS:"
echo "   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
echo "   git remote add vps root@64.23.241.43:/var/repo/finup.git"
echo ""
echo "2. Faça o primeiro push:"
echo "   git push vps main"
echo ""
echo "3. A partir de agora, todo 'git push vps main' fará deploy automático!"
echo ""
echo "📊 Para ver logs de deploy:"
echo "   tail -f /var/log/finup-deploy.log"
echo ""
