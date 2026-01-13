#!/bin/bash

# Script de deploy simplificado - Executa no servidor
# Uso: scp deploy_simple.sh root@148.230.78.91:/tmp/ && ssh root@148.230.78.91 "bash /tmp/deploy_simple.sh"

set -e

echo "🚀 Deploy Simplificado - Sistema Finanças V4"
echo "================================================"

cd /var/www/financas/app_dev

# 1. Backend Python
echo "📦 Configurando Backend Python..."
cd backend

if [ ! -d "venv" ]; then
    echo "  → Criando venv..."
    python3 -m venv venv
fi

echo "  → Ativando venv e instalando dependências..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 2. Inicializar banco de dados
echo "💾 Inicializando banco de dados..."
mkdir -p /var/lib/financas/{db,uploads,backups}
chmod 777 /var/lib/financas/{db,uploads,backups}

if [ ! -f "/var/lib/financas/db/financas.db" ]; then
    echo "  → Criando banco..."
    python -c "
from app.core.database import engine, Base
from app.domains.users.models import User
from app.domains.transactions.models import JournalEntry
from app.domains.categories.models import BaseMarcacao, TipoGasto
from app.domains.cards.models import Card
from app.domains.upload.history_models import UploadHistory
from app.domains.upload.models import IgnorarDashboard

Base.metadata.create_all(bind=engine)
print('✅ Database criado com sucesso!')
"
fi

# 3. Iniciar Backend
echo "🔥 Iniciando Backend..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/financas-backend.log 2>&1 &
echo "  → Backend rodando na porta 8000 (PID: $!)"

# 4. Frontend Next.js
echo "⚛️  Configurando Frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "  → Instalando dependências npm..."
    npm install
fi

echo "  → Building Next.js..."
npm run build

echo "🚀 Iniciando Frontend..."
pkill -f "next start" 2>/dev/null || true
nohup npm start > /var/log/financas-frontend.log 2>&1 &
echo "  → Frontend rodando na porta 3000 (PID: $!)"

# 5. Nginx (se instalado)
if command -v nginx &> /dev/null; then
    echo "🌐 Configurando Nginx..."
    
    if [ ! -f "/etc/nginx/sites-available/financas" ]; then
        cat > /etc/nginx/sites-available/financas << 'EOF'
server {
    listen 80;
    server_name 148.230.78.91;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
        ln -sf /etc/nginx/sites-available/financas /etc/nginx/sites-enabled/
        nginx -t && systemctl restart nginx
        echo "  → Nginx configurado"
    fi
else
    echo "⚠️  Nginx não instalado - acesse diretamente:"
    echo "   Backend:  http://148.230.78.91:8000"
    echo "   Frontend: http://148.230.78.91:3000"
fi

echo ""
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "📊 Status dos serviços:"
ps aux | grep -E "(uvicorn|next start)" | grep -v grep
echo ""
echo "📝 Logs:"
echo "  Backend:  tail -f /var/log/financas-backend.log"
echo "  Frontend: tail -f /var/log/financas-frontend.log"
