#!/bin/bash

# ==========================================
# DEPLOY FRESCO E ORGANIZADO
# Deploy limpo do zero após limpeza completa
# ==========================================

set -e

echo "🚀 DEPLOY FRESCO - SISTEMA DE FINANÇAS V4"
echo "=================================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo $0"
    exit 1
fi

# Verificar se server está limpo
log "0. Verificando se servidor está limpo..."
PROCESSOS=$(ps aux | grep -E "(uvicorn|next.*financas)" | grep -v grep | wc -l)
if [ "$PROCESSOS" -gt 0 ]; then
    error "Servidor não está limpo! Execute clean_server.sh primeiro"
    exit 1
fi

if [ -d "/var/www/financas" ]; then
    error "Pasta /var/www/financas ainda existe! Execute clean_server.sh primeiro"
    exit 1
fi

log "✅ Servidor está limpo, prosseguindo..."

log "1. Instalando dependências do sistema..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv git curl rsync htop
log "✅ Dependências instaladas"

log "2. Criando estrutura organizada..."
mkdir -p /var/www/financas/{backend,frontend,shared}
mkdir -p /var/lib/financas/{db,uploads,backups,config}
mkdir -p /var/log/financas
chmod 755 /var/www/financas /var/lib/financas
chmod 777 /var/lib/financas/{db,uploads,backups}
chmod 755 /var/log/financas
log "✅ Estrutura criada"

log "3. Configurando Backend Python..."
cd /var/www/financas/backend

# Requirements específicos
cat > requirements.txt << 'EOF'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Utils
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
jinja2==3.1.2
aiofiles==23.2.1

# File Processing
openpyxl==3.1.2
chardet==5.2.0
EOF

# Criar venv isolado
log "Criando ambiente Python isolado..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
log "✅ Ambiente Python configurado"

log "4. Criando aplicação backend estruturada..."

# Estrutura de pastas
mkdir -p app/{core,domains,shared}
mkdir -p app/domains/{users,transactions,categories,cards,upload}

# Main app
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Sistema de Finanças V4",
    description="Sistema de controle financeiro pessoal",
    version="4.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Página inicial
@app.get("/")
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Finanças V4</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                padding: 20px;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 16px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 600px; 
                width: 100%;
                text-align: center;
            }
            h1 { color: #2c3e50; margin-bottom: 10px; font-size: 2.5em; }
            .subtitle { color: #7f8c8d; margin-bottom: 30px; font-size: 1.1em; }
            .status { 
                background: #d5f4e6; 
                color: #16a085; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0;
                font-weight: bold;
            }
            .links { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 15px; 
                margin: 30px 0; 
            }
            .link { 
                background: #3498db; 
                color: white; 
                padding: 15px 20px; 
                text-decoration: none; 
                border-radius: 8px; 
                transition: all 0.3s;
                font-weight: 500;
            }
            .link:hover { background: #2980b9; transform: translateY(-2px); }
            .link.docs { background: #e74c3c; }
            .link.docs:hover { background: #c0392b; }
            .info { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 20px 0; 
                text-align: left;
                border-left: 4px solid #3498db;
            }
            .info h3 { color: #2c3e50; margin-bottom: 10px; }
            .info p { color: #5a6c7d; line-height: 1.6; margin-bottom: 8px; }
            code { background: #ecf0f1; padding: 2px 6px; border-radius: 4px; font-family: 'Monaco', monospace; }
            .version { color: #95a5a6; font-size: 0.9em; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏦 Sistema de Finanças</h1>
            <p class="subtitle">Controle financeiro pessoal moderno</p>
            
            <div class="status">
                ✅ Sistema funcionando perfeitamente!
            </div>
            
            <div class="links">
                <a href="/api/health" class="link">Health Check</a>
                <a href="/api/docs" class="link docs">API Docs</a>
            </div>
            
            <div class="info">
                <h3>📊 Status do Sistema</h3>
                <p><strong>Backend:</strong> ✅ FastAPI + Uvicorn</p>
                <p><strong>Version:</strong> 4.0.0</p>
                <p><strong>Deploy:</strong> Fresh & Clean</p>
                <p><strong>Environment:</strong> Production Ready</p>
            </div>
            
            <div class="info">
                <h3>🔧 Próximos Passos</h3>
                <p>• Configurar autenticação de usuários</p>
                <p>• Implementar upload de extratos</p>
                <p>• Desenvolver dashboard financeiro</p>
                <p>• Adicionar relatórios personalizados</p>
            </div>
            
            <div class="version">
                Deployed: $(date)
            </div>
        </div>
    </body>
    </html>
    """)

# Health check robusto
@app.get("/api/health")
def health_check():
    import psutil
    import sys
    
    return JSONResponse({
        "status": "healthy",
        "service": "Sistema de Finanças V4",
        "version": "4.0.0",
        "timestamp": "$(date -Iseconds)",
        "system": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "database": "not_configured",
        "features": {
            "authentication": "not_implemented",
            "file_upload": "not_implemented", 
            "dashboard": "not_implemented",
            "reports": "not_implemented"
        }
    })

@app.get("/api/status")
def detailed_status():
    import os
    return {
        "backend": "running",
        "frontend": "not_deployed",
        "pid": os.getpid(),
        "working_directory": os.getcwd(),
        "environment": "production",
        "deployment": "fresh_clean"
    }

# Endpoints de desenvolvimento
@app.get("/api/test")
def test():
    return {"message": "API funcionando!", "success": True}

@app.get("/api/info")
def info():
    return {
        "project": "Sistema de Finanças V4",
        "architecture": "FastAPI + Modular Domains",
        "deployment_method": "fresh_deploy_clean",
        "status": "production_ready"
    }
EOF

# Init files
touch app/__init__.py
for domain in core domains shared domains/users domains/transactions domains/categories domains/cards domains/upload; do
    touch app/$domain/__init__.py
done

log "✅ Aplicação backend criada"

log "5. Instalando dependência adicional..."
source venv/bin/activate
pip install psutil  # Para monitoring no health check
log "✅ Dependências adicionais instaladas"

log "6. Iniciando serviços..."

# Backend
log "Iniciando Backend FastAPI..."
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > /var/log/financas/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /var/run/financas-backend.pid
log "✅ Backend iniciado (PID: $BACKEND_PID)"

# Aguardar backend
log "Aguardando backend ficar disponível..."
for i in {1..20}; do
    if curl -s localhost:8000/api/health >/dev/null 2>&1; then
        log "✅ Backend respondendo!"
        break
    fi
    if [ $i -eq 20 ]; then
        error "Backend não respondeu em 60 segundos"
        tail -20 /var/log/financas/backend.log
        exit 1
    fi
    sleep 3
done

log "7. Configurando monitoramento..."

# Script de status
cat > /usr/local/bin/financas-status << 'EOF'
#!/bin/bash
echo "=== Sistema de Finanças V4 - Status ==="
echo "Data: $(date)"
echo ""

echo "Backend:"
if curl -s localhost:8000/api/health | grep -q healthy; then
    echo "  ✅ Funcionando (http://$(hostname -I | awk '{print $1}'):8000)"
else
    echo "  ❌ Problema"
fi

echo ""
echo "Processos:"
ps aux | grep uvicorn | grep -v grep | head -3

echo ""
echo "Portas:"
netstat -tlnp | grep -E ":(8000|3000)"

echo ""
echo "Recursos:"
echo "  CPU: $(cat /proc/loadavg | cut -d' ' -f1)% | Mem: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}') | Disk: $(df / | tail -1 | awk '{print $5}')"

echo ""
echo "Logs recentes:"
tail -5 /var/log/financas/backend.log
EOF

chmod +x /usr/local/bin/financas-status

log "✅ Monitoramento configurado"

log "8. Verificação final..."
sleep 5

# Status final
echo ""
log "============================================"
log "🎉 DEPLOY FRESCO CONCLUÍDO!"
log "============================================"
echo ""

# Testes finais
if curl -s localhost:8000/api/health | grep -q healthy; then
    log "✅ Backend funcionando: http://$(hostname -I | awk '{print $1}'):8000"
    log "✅ API Docs: http://$(hostname -I | awk '{print $1}'):8000/api/docs"
else
    error "❌ Problema no backend"
    tail -10 /var/log/financas/backend.log
    exit 1
fi

echo ""
info "📊 Sistema implementado:"
echo "  🔹 Backend FastAPI estruturado"
echo "  🔹 Arquitetura modular (domains)"
echo "  🔹 Ambiente Python isolado"
echo "  🔹 Logs organizados (/var/log/financas/)"
echo "  🔹 Monitoring com /usr/local/bin/financas-status"
echo ""

info "🔧 Comandos úteis:"
echo "  Status:   financas-status"
echo "  Logs:     tail -f /var/log/financas/backend.log"
echo "  Restart:  pkill uvicorn && cd /var/www/financas/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > /var/log/financas/backend.log 2>&1 &"
echo ""

warn "📝 Próximos passos:"
echo "  1. Implementar autenticação"
echo "  2. Configurar database SQLite"
echo "  3. Desenvolver frontend Next.js"
echo "  4. Implementar upload de arquivos"
echo ""
log "Sistema pronto para desenvolvimento incremental! 🚀"