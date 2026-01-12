#!/bin/bash

# ==========================================
# DEPLOY SIMPLIFICADO - APENAS BACKEND
# ==========================================

set -e

echo "🚀 Deploy simplificado (apenas backend)..."

# Configurações
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

log "1. Instalando apenas Python (sem Node.js)..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl

log "2. Parando processos antigos..."
pkill -f 'uvicorn' || true
fuser -k 8000/tcp 2>/dev/null || true
sleep 3

log "3. Criando estrutura..."
mkdir -p "$APP_DIR/backend" /var/lib/financas/{db,uploads,backups} "$LOG_DIR"
chmod 755 "$APP_DIR" /var/lib/financas
chmod 777 /var/lib/financas/{db,uploads,backups}

cd "$APP_DIR"

log "4. Criando aplicação backend mínima..."
cd backend

# Criar requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
jinja2==3.1.2
pydantic==2.5.0
EOF

# Criar venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Criar estrutura da aplicação
mkdir -p app

cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sistema de Finanças V4",
    description="Sistema de controle financeiro pessoal",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Finanças V4</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .status { text-align: center; margin: 30px 0; }
            .status.ok { color: #27ae60; }
            .links { display: flex; justify-content: center; gap: 20px; margin: 30px 0; }
            .link { background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }
            .link:hover { background: #2980b9; }
            .info { background: #ecf0f1; padding: 20px; border-radius: 6px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏦 Sistema de Finanças V4</h1>
            <div class="status ok">✅ Sistema funcionando!</div>
            
            <div class="links">
                <a href="/api/health" class="link">Health Check</a>
                <a href="/docs" class="link">API Docs</a>
                <a href="/redoc" class="link">ReDoc</a>
            </div>
            
            <div class="info">
                <h3>📊 Status do Deploy</h3>
                <p><strong>Backend:</strong> ✅ Funcionando (FastAPI + Uvicorn)</p>
                <p><strong>Frontend:</strong> ⚠️ Não implementado nesta versão simplificada</p>
                <p><strong>Database:</strong> 📝 Configuração manual necessária</p>
            </div>
            
            <div class="info">
                <h3>🔧 Próximos Passos</h3>
                <p>1. Configurar banco de dados</p>
                <p>2. Implementar autenticação</p>
                <p>3. Adicionar frontend (Next.js separadamente)</p>
                <p>4. Configurar upload de arquivos</p>
            </div>
            
            <div class="info">
                <h3>📝 Logs</h3>
                <p>Backend: <code>tail -f /var/log/backend.log</code></p>
                <p>Processos: <code>ps aux | grep uvicorn</code></p>
                <p>Restart: <code>pkill uvicorn && cd /var/www/financas/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /var/log/backend.log 2>&1 &</code></p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/api/health")
def health_check():
    return JSONResponse({
        "status": "healthy",
        "service": "Sistema de Finanças V4",
        "version": "1.0.0",
        "database": "not_configured",
        "timestamp": "2026-01-12T15:30:00Z"
    })

@app.get("/api/status")
def status():
    import os
    return JSONResponse({
        "backend": "running",
        "frontend": "not_deployed",
        "pid": os.getpid(),
        "working_directory": os.getcwd(),
        "python_version": "3.12+",
        "framework": "FastAPI + Uvicorn"
    })

@app.get("/api/test")
def test_endpoint():
    return {"message": "Endpoint de teste funcionando!", "success": True}
EOF

cat > app/__init__.py << 'EOF'
# Sistema de Finanças V4
__version__ = "1.0.0"
EOF

log "5. Iniciando servidor backend..."
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

log "Backend iniciado (PID: $BACKEND_PID)"

# Aguardar backend subir
sleep 5
for i in {1..15}; do
    if curl -s localhost:8000/api/health >/dev/null 2>&1; then
        log "✅ Backend respondendo!"
        break
    fi
    log "Aguardando backend... ($i/15)"
    sleep 2
done

log "6. Verificação final..."
echo ""
log "📊 Processos:"
ps aux | grep uvicorn | grep -v grep

echo ""
log "🔍 Porta 8000:"
netstat -tlnp | grep 8000 || true

echo ""
log "============================================"
log "🎉 DEPLOY BACKEND CONCLUÍDO!"
log "============================================"

# Teste final
if curl -s localhost:8000/api/health | grep -q "healthy"; then
    log "✅ Backend funcionando!"
    echo ""
    echo "🌐 Acesse pelo navegador:"
    echo "   http://$(hostname -I | awk '{print $1}'):8000/"
    echo "   http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo "   http://$(hostname -I | awk '{print $1}'):8000/api/health"
else
    error "❌ Backend com problemas"
    echo ""
    echo "📋 Verificar logs:"
    tail -20 "$LOG_DIR/backend.log"
fi

echo ""
log "🔄 Comandos úteis:"
echo "  Ver logs:     tail -f $LOG_DIR/backend.log"
echo "  Ver processo: ps aux | grep uvicorn"
echo "  Restart:      pkill uvicorn && cd $APP_DIR/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > $LOG_DIR/backend.log 2>&1 &"
echo "  Parar:        pkill uvicorn"

echo ""
warn "📝 Este é um deploy MÍNIMO apenas com backend."
warn "Para frontend completo, resolver conflitos Node.js separadamente."