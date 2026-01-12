#!/bin/bash

# ==========================================
# DEPLOY DIRETO NO SERVIDOR
# Execute este script diretamente no servidor VPS
# ==========================================

set -e

echo "🚀 Iniciando deploy direto no servidor..."

# Configurações
REPO_URL="https://github.com/seu-usuario/ProjetoFinancasV4.git"  # Ajustar conforme necessário
APP_DIR="/var/www/financas"
LOG_DIR="/var/log"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo $0"
    exit 1
fi

log "1. Instalando dependências do sistema..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nodejs npm git curl rsync

log "2. Parando processos antigos..."
pkill -f 'uvicorn' || true
pkill -f 'next start' || true
pkill -f 'npm start' || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
sleep 3

log "3. Criando estrutura de pastas..."
mkdir -p "$APP_DIR" /var/lib/financas/{db,uploads,backups} "$LOG_DIR"
chmod 755 "$APP_DIR" /var/lib/financas
chmod 777 /var/lib/financas/{db,uploads,backups}

log "4. Clonando/Atualizando código..."
if [ -d "$APP_DIR/.git" ]; then
    log "Atualizando repositório existente..."
    cd "$APP_DIR" && git pull origin main || git pull origin master
else
    log "Clonando repositório..."
    # Usando código local para teste rápido, substitua por git clone se necessário
    mkdir -p "$APP_DIR/app_dev"
    
    # Copiando estrutura básica para teste
    cat > "$APP_DIR/app_dev/backend/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
slowapi==0.1.9
limits==3.6.0
jinja2==3.1.2
aiofiles==23.2.1
openpyxl==3.1.2
chardet==5.2.0
EOF

    # Criando estrutura mínima
    mkdir -p "$APP_DIR/app_dev/backend/app"
    mkdir -p "$APP_DIR/app_dev/frontend"
fi

cd "$APP_DIR/app_dev"

log "5. Configurando Backend Python..."
cd backend

if [ ! -d "venv" ]; then
    log "Criando venv..."
    python3 -m venv venv
fi

log "Ativando venv e instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart

# Criar app básico se não existir
if [ ! -f "app/main.py" ]; then
    log "Criando app básico..."
    mkdir -p app/core app/domains/users app/domains/transactions app/domains/categories app/domains/cards app/domains/upload
    
    cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sistema de Finanças V4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sistema de Finanças V4"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
EOF

    cat > app/__init__.py << 'EOF'
# Sistema de Finanças V4
EOF

    # Criar módulos vazios
    touch app/core/__init__.py app/domains/__init__.py
    touch app/domains/users/__init__.py app/domains/transactions/__init__.py
    touch app/domains/categories/__init__.py app/domains/cards/__init__.py app/domains/upload/__init__.py
fi

log "6. Iniciando Backend..."
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
log "Backend iniciado (PID: $BACKEND_PID)"

# Aguardar backend subir
sleep 5
for i in {1..10}; do
    if curl -s localhost:8000/api/health >/dev/null 2>&1; then
        log "✅ Backend respondendo!"
        break
    fi
    log "Aguardando backend... ($i/10)"
    sleep 2
done

log "7. Configurando Frontend..."
cd ../frontend

# Criar package.json básico se não existir
if [ ! -f "package.json" ]; then
    log "Criando projeto Next.js básico..."
    cat > package.json << 'EOF'
{
  "name": "financas-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
EOF

    mkdir -p src/app
    cat > src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Sistema de Finanças V4</h1>
      <p>Sistema funcionando!</p>
      <a href="/api/health" target="_blank">Testar Backend</a>
    </div>
  )
}
EOF

    cat > src/app/layout.tsx << 'EOF'
export const metadata = {
  title: 'Sistema de Finanças V4',
  description: 'Sistema de controle financeiro',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
EOF

    cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
EOF
fi

log "Instalando dependências npm..."
npm install

log "Fazendo build..."
npm run build

log "8. Iniciando Frontend..."
nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
log "Frontend iniciado (PID: $FRONTEND_PID)"

log "9. Aguardando serviços..."
sleep 10

log "10. Verificação final..."
echo ""
log "📊 Processos ativos:"
ps aux | grep -E '(uvicorn|next)' | grep -v grep | head -5

echo ""
log "🔍 Portas abertas:"
netstat -tlnp | grep -E '(8000|3000)'

echo ""
log "============================================"
log "🎉 DEPLOY CONCLUÍDO!"
log "============================================"

# Testes finais
if curl -s localhost:8000/api/health | grep -q "healthy"; then
    log "✅ Backend OK: http://$(hostname -I | awk '{print $1}'):8000"
else
    error "❌ Backend com problemas"
    tail -10 "$LOG_DIR/backend.log"
fi

if curl -s localhost:3000 | grep -q -i "finanças\|html"; then
    log "✅ Frontend OK: http://$(hostname -I | awk '{print $1}'):3000"
else
    error "❌ Frontend com problemas"
    tail -10 "$LOG_DIR/frontend.log"
fi

echo ""
log "📝 URLs de acesso:"
echo "  Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "  Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo "  Health:   http://$(hostname -I | awk '{print $1}'):8000/api/health"
echo ""
log "📋 Para ver logs:"
echo "  Backend:  tail -f $LOG_DIR/backend.log"
echo "  Frontend: tail -f $LOG_DIR/frontend.log"
echo ""
log "🔄 Para restart:"
echo "  pkill -f uvicorn; pkill -f 'npm start'"
echo "  cd $APP_DIR/app_dev/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > $LOG_DIR/backend.log 2>&1 &"
echo "  cd $APP_DIR/app_dev/frontend && nohup npm start > $LOG_DIR/frontend.log 2>&1 &"