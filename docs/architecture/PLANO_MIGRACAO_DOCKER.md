# 🐳 Plano de Migração para Docker

**Data:** 22/02/2026  
**Motivo:** Isolar dependências crescentes (OCR, PDF, Excel) e garantir paridade dev-prod  
**Status:** 📋 Planejamento

---

## 🎯 Por Que Migrar para Docker AGORA?

### **Problemas Atuais (Sem Docker)**

1. **Dependências conflitantes:**
   - `rapidocr-onnxruntime` instala modelos ONNX (~50MB) no venv
   - `PyMuPDF` pode conflitar com outras libs de imagem
   - `msoffcrypto-tool` depende de `cryptography` (pode quebrar outras deps)

2. **"Funciona na minha máquina":**
   - Dev local: macOS + Python 3.9 + SQLite
   - Servidor: Linux + Python 3.9 + PostgreSQL
   - Diferenças sutis podem causar bugs

3. **Onboarding difícil:**
   - Novo dev precisa instalar: Python, Node, PostgreSQL, dependências do sistema
   - Setup demora ~30-60min

4. **Deploy arriscado:**
   - `pip install` pode quebrar versões existentes
   - `npm run build` OOM no servidor (2GB RAM)
   - Rollback difícil (precisa reinstalar deps antigas)

5. **Escalabilidade limitada:**
   - Adicionar workers/queues requer gerenciamento manual de processos
   - Sem isolamento de recursos

---

### **Benefícios do Docker**

✅ **Isolamento completo:** Cada projeto tem suas dependências (Python, Node, libs sistema)  
✅ **Reproduzibilidade:** `docker-compose up` funciona igual em dev/prod  
✅ **Rollback fácil:** Voltar para tag anterior da imagem  
✅ **Deploy seguro:** Build da imagem valida TODAS as dependências antes  
✅ **Onboarding rápido:** 1 comando (`docker-compose up`), 5 minutos  
✅ **CI/CD simples:** GitHub Actions pode buildar e pushar imagens  
✅ **Escalabilidade:** Fácil adicionar workers, Redis, Celery, etc.

---

## 📋 Estratégia de Migração (Gradual, Sem Quebrar)

### **Fase 1: Desenvolvimento Local (1-2 dias)** 🏠

**Objetivo:** Rodar projeto inteiro com `docker-compose up` no macOS

**Entregáveis:**
- `docker-compose.yml` (backend + frontend + postgres + redis opcional)
- `Dockerfile.backend` (multi-stage: deps → build → runtime)
- `Dockerfile.frontend` (multi-stage: deps → build → nginx)
- `.dockerignore` (otimizar build)
- `docs/docker/GUIA_DESENVOLVIMENTO.md`

**Validação:**
- ✅ `docker-compose up` inicia tudo
- ✅ Backend responde em `http://localhost:8000`
- ✅ Frontend responde em `http://localhost:3000`
- ✅ Hot reload funciona (editar código → vê mudanças sem rebuild)

---

### **Fase 2: Servidor Local/Testes (2-3 dias)** 🧪

**Objetivo:** Rodar no servidor VPS sem quebrar setup atual

**Estratégia:**
- Manter setup atual rodando (porta 8000/3003)
- Docker roda em portas paralelas (8001/3001)
- Testar por 1 semana antes de trocar

**Entregáveis:**
- `docker-compose.prod.yml` (otimizado para produção)
- Scripts de deploy dockerizado (`deploy_docker.sh`)
- Nginx config para proxy reverso
- Backup automático antes de cada deploy

**Validação:**
- ✅ Docker + setup antigo rodam juntos (portas diferentes)
- ✅ Todos os processadores funcionam (BTG, Mercado Pago, etc.)
- ✅ Upload, OCR, PDF, tudo OK
- ✅ Performance igual ou melhor

---

### **Fase 3: Migração Produção (1 dia)** 🚀

**Objetivo:** Trocar setup antigo por Docker como padrão

**Estratégia:**
- Backup completo do banco
- Parar servidores antigos
- Trocar portas (Docker assume 8000/3003)
- Nginx aponta para containers Docker

**Rollback Plan:**
- Se algo quebrar: parar Docker, voltar setup antigo (< 5min)

---

## 🏗️ Arquitetura Docker Proposta

### **Serviços (docker-compose.yml)**

```yaml
services:
  postgres:       # Banco de dados (compartilhado)
  redis:          # Cache/Queue (opcional, futuro)
  backend:        # FastAPI + uvicorn (ÚNICO backend para ambos frontends)
  frontend-app:   # Next.js app_dev (usuário final) - porta 3000
  frontend-admin: # Next.js app_admin (admin) - porta 3001
  nginx:          # Proxy reverso (dev opcional, prod obrigatório)
```

**⚠️ IMPORTANTE:** Um ÚNICO backend serve AMBOS os frontends (app_dev e app_admin)

### **Volumes**

```yaml
volumes:
  postgres_data:          # Persistir banco
  backend_uploads:        # Arquivos enviados
  backend_database:       # SQLite (dev) ou vazio (prod usa postgres)
  backend_backups:        # Backups diários
```

---

## 📦 Estrutura de Arquivos Docker

```
ProjetoFinancasV5/
├── docker-compose.yml                # Dev local (macOS)
├── docker-compose.prod.yml           # Produção (VPS Linux)
├── .dockerignore                     # Otimizar build
├── .env.example                      # Template de variáveis
│
├── app_dev/
│   ├── backend/
│   │   ├── Dockerfile                # Backend (multi-stage)
│   │   ├── requirements.txt          # Deps Python
│   │   └── .dockerignore
│   │
│   └── frontend/
│       ├── Dockerfile                # Frontend app_dev (multi-stage)
│       ├── Dockerfile.dev            # Dev com hot reload
│       ├── nginx.conf                # Servir build estático (prod)
│       └── .dockerignore
│
├── app_admin/
│   └── frontend/
│       ├── Dockerfile                # Frontend admin (multi-stage)
│       ├── Dockerfile.dev            # Dev com hot reload
│       ├── nginx.conf                # Servir build estático (prod)
│       └── .dockerignore
│
├── nginx/
│   ├── nginx.conf                    # Proxy reverso (prod)
│   └── ssl/                          # Certificados SSL
│
├── scripts/
│   └── docker/
│       ├── build.sh                  # Build imagens
│       ├── deploy.sh                 # Deploy dockerizado
│       ├── dev.sh                    # Subir dev local
│       └── cleanup.sh                # Limpar imagens antigas
│
└── docs/
    └── docker/
        ├── GUIA_DESENVOLVIMENTO.md   # Como usar no dia-a-dia
        ├── GUIA_DEPLOY.md            # Deploy em prod
        └── TROUBLESHOOTING.md        # Problemas comuns
```

---

## 🔨 Implementação Detalhada

### **1. Dockerfile.backend (Multi-Stage)**

```dockerfile
# ============================================
# Stage 1: Builder - Instalar dependências
# ============================================
FROM python:3.9-slim as builder

# Instalar deps do sistema para compilar
RUN apt-get update && apt-get install -y \
    gcc g++ make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar apenas requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar deps em venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Imagem final otimizada
# ============================================
FROM python:3.9-slim

# Instalar apenas runtime deps
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copiar código
COPY . .

# Criar user não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Otimizações:**
- ✅ **Multi-stage:** Imagem final ~300MB (vs ~800MB sem)
- ✅ **Cache layers:** `requirements.txt` muda pouco → rebuild rápido
- ✅ **Não-root:** Segurança
- ✅ **Health check:** Docker sabe quando app está pronta

---

### **2. Dockerfile.frontend (Multi-Stage)**

```dockerfile
# ============================================
# Stage 1: Builder - Build Next.js
# ============================================
FROM node:20-alpine as builder

WORKDIR /app

# Copiar package files primeiro (cache layer)
COPY package*.json ./
RUN npm ci --only=production

# Copiar código e buildar
COPY . .
RUN npm run build

# ============================================
# Stage 2: Runtime - Nginx servindo build
# ============================================
FROM nginx:alpine

# Copiar build do Next.js
COPY --from=builder /app/.next /usr/share/nginx/html/.next
COPY --from=builder /app/public /usr/share/nginx/html/public

# Copiar config nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

**Otimizações:**
- ✅ **Multi-stage:** Imagem final ~50MB (vs ~500MB com Node.js)
- ✅ **Nginx:** Serve estático ultra-rápido
- ✅ **Cache npm:** `npm ci` muito mais rápido

---

### **3. docker-compose.yml (Desenvolvimento)**

```yaml
version: '3.8'

services:
  # ==========================================
  # PostgreSQL - Banco de dados
  # ==========================================
  postgres:
    image: postgres:16-alpine
    container_name: finup_postgres_dev
    environment:
      POSTGRES_USER: finup_user
      POSTGRES_PASSWORD: finup_dev_password
      POSTGRES_DB: finup_db_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U finup_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==========================================
  # Redis - Cache/Queue (opcional)
  # ==========================================
  redis:
    image: redis:7-alpine
    container_name: finup_redis_dev
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # ==========================================
  # Backend - FastAPI
  # ==========================================
  backend:
    build:
      context: ./app_dev/backend
      dockerfile: Dockerfile
    container_name: finup_backend_dev
    environment:
      - DATABASE_URL=postgresql://finup_user:finup_dev_password@postgres:5432/finup_db_dev
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
      - BACKEND_CORS_ORIGINS=http://localhost:3000
    ports:
      - "8000:8000"
    volumes:
      # Hot reload: monta código como volume
      - ./app_dev/backend:/app
      # Persistir uploads
      - backend_uploads:/app/uploads
      # Persistir backups
      - backend_backups:/app/database/backups_daily
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      uvicorn app.main:app 
      --host 0.0.0.0 
      --port 8000 
      --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ==========================================
  # Frontend App - Next.js (dev mode com hot reload)
  # ==========================================
  frontend-app:
    build:
      context: ./app_dev/frontend
      dockerfile: Dockerfile.dev
      target: development
    container_name: finup_frontend_app_dev
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      # Hot reload
      - ./app_dev/frontend:/app
      - /app/node_modules  # Evitar sobrescrever node_modules
      - /app/.next         # Evitar sobrescrever .next
    depends_on:
      - backend
    command: npm run dev

  # ==========================================
  # Frontend Admin - Next.js (dev mode com hot reload)
  # ==========================================
  frontend-admin:
    build:
      context: ./app_admin/frontend
      dockerfile: Dockerfile.dev
      target: development
    container_name: finup_frontend_admin_dev
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    ports:
      - "3001:3000"  # Admin roda na porta 3001 do host
    volumes:
      # Hot reload
      - ./app_admin/frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
  backend_uploads:
  backend_backups:
```

**Recursos Dev:**
- ✅ **Hot reload:** Edita código → vê mudanças instantaneamente (ambos frontends)
- ✅ **Volumes:** Uploads e backups persistem
- ✅ **Health checks:** Containers só ficam "healthy" quando prontos
- ✅ **Depends_on:** Backend só inicia após Postgres estar pronto
- ✅ **2 Frontends:** App (porta 3000) + Admin (porta 3001), mesmo backend

---

### **4. docker-compose.prod.yml (Produção)**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: finup_postgres_prod
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend_network
    restart: unless-stopped
    # NÃO expor porta 5432 publicamente!

  redis:
    image: redis:7-alpine
    container_name: finup_redis_prod
    volumes:
      - redis_data:/data
    networks:
      - backend_network
    restart: unless-stopped

  backend:
    build:
      context: ./app_dev/backend
      dockerfile: Dockerfile
      args:
        - BUILD_DATE=${BUILD_DATE}
        - VCS_REF=${VCS_REF}
    container_name: finup_backend_prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=false
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
    volumes:
      - backend_uploads:/app/uploads
      - backend_backups:/app/database/backups_daily
    networks:
      - backend_network
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    # NÃO expor porta 8000 publicamente!

  frontend-app:
    build:
      context: ./app_dev/frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    container_name: finup_frontend_app_prod
    networks:
      - frontend_network
    restart: unless-stopped
    # NÃO expor porta 3000 publicamente!

  frontend-admin:
    build:
      context: ./app_admin/frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    container_name: finup_frontend_admin_prod
    networks:
      - frontend_network
    restart: unless-stopped
    # NÃO expor porta 3000 publicamente!

  nginx:
    image: nginx:alpine
    container_name: finup_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    networks:
      - frontend_network
      - backend_network
    depends_on:
      - backend
      - frontend-app
      - frontend-admin
    restart: unless-stopped

networks:
  backend_network:
    driver: bridge
  frontend_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  backend_uploads:
  backend_backups:
  nginx_logs:
```

**Recursos Prod:**
- ✅ **Isolamento:** Backend/Frontend em redes separadas
- ✅ **Segurança:** Nenhum serviço exposto diretamente (só Nginx)
- ✅ **Secrets:** Variáveis em `.env` (NUNCA commitar!)
- ✅ **Restart:** Containers reiniciam automaticamente
- ✅ **Logs:** Nginx logs persistidos

---

## 🔄 Workflow de Desenvolvimento (Dia-a-Dia)

### **Iniciar Projeto**

```bash
# Clone e suba tudo
git clone <repo>
cd ProjetoFinancasV5

# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Acesso
# Frontend App: http://localhost:3000
# Frontend Admin: http://localhost:3001
# Backend: http://localhost:8000/docs
# Postgres: localhost:5432
```

**Tempo:** ~2-3 minutos na primeira vez, ~30s depois (cache de imagens)

**URLs de Acesso:**
- **App Principal:** http://localhost:3000 (usuário final)
- **Painel Admin:** http://localhost:3001 (administração)
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

---

### **Desenvolver (Hot Reload)**

```bash
# Editar app_dev/backend/app/domains/*/
# → Backend recarrega automaticamente (uvicorn --reload)

# Editar app_dev/frontend/src/
# → Frontend App recarrega automaticamente (npm run dev - porta 3000)

# Editar app_admin/frontend/src/
# → Frontend Admin recarrega automaticamente (npm run dev - porta 3001)

# Ver logs em tempo real
docker-compose logs -f backend frontend-app frontend-admin
```

---

### **Rodar Migrations**

```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic revision --autogenerate -m "adiciona campo X"
```

---

### **Acessar Banco**

```bash
# psql
docker-compose exec postgres psql -U finup_user -d finup_db_dev

# Ou via ferramenta externa (DBeaver, pgAdmin)
# Host: localhost
# Port: 5432
# User: finup_user
# Password: finup_dev_password
```

---

### **Rebuild Após Mudanças em Deps**

```bash
# Mudou requirements.txt ou package.json?
docker-compose build backend frontend

# Ou rebuild tudo
docker-compose build

# Subir com rebuild forçado
docker-compose up -d --build
```

---

### **Parar Tudo**

```bash
docker-compose down

# Parar E remover volumes (CUIDADO: apaga banco!)
docker-compose down -v
```

---

## 🚀 Deploy em Produção (VPS)

### **Pré-requisitos no Servidor**

```bash
# Instalar Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose V2
sudo apt-get install docker-compose-plugin

# Adicionar user ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar
docker --version
docker compose version
```

---

### **Deploy Steps**

```bash
# 1. Clonar/Pull código
cd /var/www/finup
git pull origin main

# 2. Criar .env (NUNCA commitar!)
cat > .env << 'EOF'
POSTGRES_USER=finup_user
POSTGRES_PASSWORD=<senha_forte_aqui>
POSTGRES_DB=finup_db
DATABASE_URL=postgresql://finup_user:<senha>@postgres:5432/finup_db
JWT_SECRET_KEY=<secret_64_chars>
BACKEND_CORS_ORIGINS=https://meufinup.com.br
NEXT_PUBLIC_API_URL=https://meufinup.com.br
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)
EOF

# 3. Build imagens
docker compose -f docker-compose.prod.yml build

# 4. Migrar banco (primeira vez)
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 5. Subir tudo
docker compose -f docker-compose.prod.yml up -d

# 6. Verificar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f

# 7. Validar
curl http://localhost/api/health
curl http://localhost
```

---

### **Nginx Reverse Proxy (Produção)**

```nginx
# /var/www/finup/nginx/nginx.conf

upstream backend {
    server backend:8000;
}

upstream frontend_app {
    server frontend-app:3000;
}

upstream frontend_admin {
    server frontend-admin:3000;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name meufinup.com.br;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # API (compartilhada entre app e admin)
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin Panel
    location /admin {
        proxy_pass http://frontend_admin;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # App Principal (default)
    location / {
        proxy_pass http://frontend_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Rotas:**
- `https://meufinup.com.br/` → Frontend App (usuário final)
- `https://meufinup.com.br/admin` → Frontend Admin (painel admin)
- `https://meufinup.com.br/api/*` → Backend (compartilhado)

---

## 🔧 Otimizações e Boas Práticas

### **1. .dockerignore (Backend)**

```
# app_dev/backend/.dockerignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testes
.pytest_cache/
htmlcov/
.coverage

# Banco local
*.db
*.db-journal
database/backups_daily/

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore
```

---

### **2. .dockerignore (Frontend)**

```
# app_dev/frontend/.dockerignore

# Next.js
.next/
out/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDEs
.vscode/
.idea/
*.swp

# Env
.env
.env.local
.env.production.local

# OS
.DS_Store

# Git
.git/
.gitignore
```

---

### **3. Multi-Stage Build do Frontend (Otimizado)**

```dockerfile
# Dockerfile.frontend (produção)

# ============================================
# Stage 1: Dependencies
# ============================================
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# ============================================
# Stage 2: Builder
# ============================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ============================================
# Stage 3: Runner (Next.js standalone)
# ============================================
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

**Otimização:** Usa Next.js standalone output (~80MB vs ~300MB)

---

### **4. Cache de Layers (BuildKit)**

```bash
# Ativar BuildKit (mais rápido)
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build com cache
docker compose build --build-arg BUILDKIT_INLINE_CACHE=1

# Push para registry (GitHub Container Registry)
docker tag finup_backend ghcr.io/<user>/finup-backend:latest
docker push ghcr.io/<user>/finup-backend:latest
```

---

## 📊 Comparação: Com vs Sem Docker

| Aspecto | Sem Docker | Com Docker |
|---------|-----------|-----------|
| **Setup inicial** | 30-60min (instalar Python, Node, Postgres) | 5min (`docker-compose up`) |
| **Paridade dev-prod** | ⚠️ Diferenças sutis (macOS vs Linux) | ✅ 100% igual |
| **Isolamento** | ❌ Deps globais podem conflitar | ✅ Cada projeto isolado |
| **Deploy** | ⚠️ `pip install` pode quebrar | ✅ Build valida antes |
| **Rollback** | ⚠️ Reinstalar deps antigas | ✅ Trocar tag da imagem |
| **CI/CD** | ⚠️ Configurar runner com deps | ✅ Build + push imagem |
| **Escalabilidade** | ❌ Gerenciar processos manual | ✅ Docker Swarm/Kubernetes |
| **Recursos** | ✅ Mínimo (~500MB RAM) | ⚠️ +200-300MB RAM |
| **Complexidade** | ✅ Simples (venv + npm) | ⚠️ Aprender Docker |

**Conclusão:** Trade-off vale a pena quando dependências crescem!

---

## 🎯 Roadmap de Implementação (Timeline)

### **Semana 1: Desenvolvimento Local**

**Dia 1-2:**
- [ ] Criar `Dockerfile.backend` (multi-stage)
- [ ] Criar `Dockerfile.frontend` (multi-stage)
- [ ] Criar `docker-compose.yml`
- [ ] Testar `docker-compose up` → tudo funciona

**Dia 3:**
- [ ] Configurar hot reload (volumes)
- [ ] Testar desenvolvimento (editar código → ver mudanças)
- [ ] Validar processadores (BTG, Mercado Pago, OCR)

**Dia 4:**
- [ ] Documentar workflow (`GUIA_DESENVOLVIMENTO.md`)
- [ ] Criar scripts auxiliares (`build.sh`, `logs.sh`)
- [ ] Commitar Dockerfiles na branch

---

### **Semana 2: Servidor Local/Testes**

**Dia 5-6:**
- [ ] Criar `docker-compose.prod.yml`
- [ ] Configurar Nginx reverse proxy
- [ ] Setup SSL/HTTPS (Let's Encrypt)

**Dia 7:**
- [ ] Deploy paralelo no servidor (porta 8001/3001)
- [ ] Validar TODOS os fluxos (upload, OCR, transações)
- [ ] Comparar performance (Docker vs setup antigo)

**Dia 8-11:**
- [ ] Rodar em produção paralela (1 semana de testes)
- [ ] Monitorar logs, recursos, erros
- [ ] Ajustar configs se necessário

---

### **Semana 3: Migração Produção**

**Dia 12:**
- [ ] Backup COMPLETO do banco
- [ ] Trocar portas (Docker assume 8000/3003)
- [ ] Nginx aponta para Docker
- [ ] Parar setup antigo

**Dia 13-14:**
- [ ] Monitorar intensivamente
- [ ] Ajustar se necessário
- [ ] Documentar problemas/soluções

---

## 🚨 Troubleshooting Comum

### **1. "Cannot connect to Docker daemon"**

```bash
# Daemon não está rodando
sudo systemctl start docker

# User não está no grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

---

### **2. "Port already in use"**

```bash
# Ver qual processo está usando porta 8000
lsof -i :8000
sudo kill -9 <PID>

# Ou mudar porta no docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

---

### **3. "Out of memory" ao buildar**

```bash
# Aumentar memória do Docker Desktop (macOS)
# Settings → Resources → Memory → 4GB+

# No Linux, limpar cache
docker system prune -a
```

---

### **4. Hot reload não funciona**

```bash
# macOS: Adicionar no docker-compose.yml
environment:
  - CHOKIDAR_USEPOLLING=true  # Frontend
  - WATCHFILES_FORCE_POLLING=true  # Backend
```

---

### **5. Build muito lento**

```bash
# Usar BuildKit
export DOCKER_BUILDKIT=1

# Cache externo (registro)
docker build --cache-from ghcr.io/<user>/finup-backend:latest .
```

---

## 📚 Recursos de Aprendizado

### **Documentação Oficial**
- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Multi-stage builds: https://docs.docker.com/build/building/multi-stage/

### **Tutoriais**
- FastAPI + Docker: https://fastapi.tiangolo.com/deployment/docker/
- Next.js + Docker: https://nextjs.org/docs/deployment#docker-image

### **Boas Práticas**
- Docker best practices: https://docs.docker.com/develop/dev-best-practices/
- Security: https://docs.docker.com/engine/security/

---

## ✅ Checklist Antes de Começar

Você está pronto para migrar se:

- [ ] ✅ Entende básico de Docker (imagens, containers, volumes)
- [ ] ✅ Tem Docker Desktop instalado (macOS) ou Docker Engine (Linux)
- [ ] ✅ Projeto atual funciona 100% sem Docker
- [ ] ✅ Tem backup do banco atualizado
- [ ] ✅ Tem 1-2 semanas para implementação gradual
- [ ] ✅ Sabe fazer rollback se algo quebrar

---

## 🎯 Decisão Final

**Recomendação:** ✅ **SIM, migrar para Docker**

**Quando começar:** Agora! Próximo sprint.

**Por quê:**
1. Dependências estão crescendo (OCR, PDF, Excel)
2. Risco de quebrar ambiente atual só aumenta
3. Deploy ficará mais seguro e rápido
4. Facilita onboarding de novos devs
5. Prepara para escalabilidade futura (workers, queues)

**Trade-off aceitável:**
- Investimento inicial: 1-2 semanas
- Complexidade adicional: Aprender Docker (mas vale a pena)
- Recursos: +200-300MB RAM (servidor tem 2GB, é ok)

---

## 📞 Próximos Passos

Se decidir implementar:

1. **Commitar documentação:**
   ```bash
   git add docs/architecture/PLANO_MIGRACAO_DOCKER.md
   git commit -m "docs: plano de migração para Docker"
   ```

2. **Criar branch:**
   ```bash
   git checkout -b feature/docker-migration
   ```

3. **Começar Fase 1:**
   - Criar Dockerfiles
   - Testar localmente
   - Documentar workflow

4. **Pedir review:**
   - Validar com equipe (se houver)
   - Testar em outro ambiente

---

**Documentado por:** GitHub Copilot  
**Data:** 22/02/2026  
**Status:** 📋 Aguardando decisão
