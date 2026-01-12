#!/bin/bash
# Deploy script para executar no servidor

set -e

echo "🚀 Iniciando deploy sem Docker..."

cd /var/www/financas/app_dev

# 1. Backend
echo "📦 Configurando Backend..."
cd backend

# Ativar venv e instalar dependências
source venv/bin/activate
pip install --quiet -r requirements.txt

# 2. Criar diretórios
echo "📁 Criando diretórios..."
mkdir -p /var/lib/financas/{db,uploads,backups}
chmod 777 /var/lib/financas/{db,uploads,backups}

# 3. Inicializar banco se não existir
if [ ! -f "/var/lib/financas/db/financas.db" ]; then
    echo "💾 Inicializando banco..."
    python -c "
from app.core.database import engine, Base
from app.domains.users.models import User
from app.domains.transactions.models import JournalEntry
from app.domains.categories.models import BaseMarcacao
from app.domains.upload.history_models import UploadHistory

Base.metadata.create_all(bind=engine)

# Criar usuário admin se não existir
from sqlalchemy.orm import sessionmaker
from app.domains.users.service import hash_password
Session = sessionmaker(bind=engine)
session = Session()
admin = session.query(User).filter(User.email == 'admin@financas.com').first()
if not admin:
    admin = User(
        name='Admin',
        email='admin@financas.com', 
        password_hash=hash_password('admin123')
    )
    session.add(admin)
    session.commit()
    print('✅ Usuario admin criado')
else:
    print('✅ Usuario admin já existe')
session.close()
"
fi

# 4. Iniciar backend
echo "🚀 Iniciando backend..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend iniciado (PID: $BACKEND_PID)"

# 5. Frontend
echo "⚛️  Configurando frontend..."
cd ../frontend

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências npm..."
    npm install
fi

# Build
echo "🔧 Building Next.js..."
npm run build

# Iniciar frontend  
echo "🚀 Iniciando frontend..."
pkill -f "next start" 2>/dev/null || true
nohup npm start > /var/log/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend iniciado (PID: $FRONTEND_PID)"

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "🌐 URLs:"
echo "  Backend:  http://148.230.78.91:8000"
echo "  Frontend: http://148.230.78.91:3000"
echo "  API Docs: http://148.230.78.91:8000/docs"
echo ""
echo "📊 Processos:"
echo "  Backend PID:  $BACKEND_PID"  
echo "  Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "  Backend:  tail -f /var/log/backend.log"
echo "  Frontend: tail -f /var/log/frontend.log"
echo ""
echo "👤 Login padrão:"
echo "  Email:    admin@financas.com"
echo "  Senha:    admin123"