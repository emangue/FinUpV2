# 🐳 Desenvolvimento com Docker - Guia Rápido

## ⚡ Quick Start

```bash
# 1. Subir tudo (detecta rebuild automático se necessário)
./scripts/docker/dev.sh start

# 2. Acessar
# App Principal:  http://localhost:3000
# Painel Admin:   http://localhost:3001
# Backend API:    http://localhost:8000/docs
```

## 📋 Comandos Úteis

```bash
# Ver status com saúde de cada container
./scripts/docker/dev.sh status

# Ver logs em tempo real
./scripts/docker/dev.sh logs           # todos
./scripts/docker/dev.sh logs app       # Frontend App
./scripts/docker/dev.sh logs admin     # Frontend Admin
./scripts/docker/dev.sh logs backend   # Backend

# Parar tudo
./scripts/docker/dev.sh stop

# Reiniciar (sem rebuild) - suporta serviço específico
./scripts/docker/dev.sh restart
./scripts/docker/dev.sh restart backend

# Rebuild após mudar dependências (requirements.txt / package.json)
./scripts/docker/dev.sh rebuild backend    # só o backend
./scripts/docker/dev.sh rebuild app        # só o frontend app
./scripts/docker/dev.sh rebuild-all        # tudo

# Acessar shell do backend
./scripts/docker/dev.sh shell

# Acessar PostgreSQL
./scripts/docker/dev.sh db
```

## 🔧 Hot Reload

**Funciona automaticamente!** Edite código e veja mudanças instantaneamente:

- **Backend:** `app_dev/backend/app/**/*.py` → uvicorn --reload
- **Frontend App:** `app_dev/frontend/src/**/*` → npm run dev
- **Frontend Admin:** `app_admin/frontend/src/**/*` → npm run dev

## 🗄️ Migrations

```bash
# Rodar migrations
docker-compose exec backend alembic upgrade head

# Criar nova migration
docker-compose exec backend alembic revision --autogenerate -m "descrição"
```

## 🚨 Troubleshooting

### "Port already in use"

```bash
# Parar containers Docker
./scripts/docker/dev.sh stop

# Ou matar processos manualmente
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

### "Cannot connect to Docker daemon"

```bash
# Iniciar Docker Desktop (macOS)
open /Applications/Docker.app
```

### Rebuild completo

```bash
# Rebuilda todas as imagens e reinicia tudo
./scripts/docker/dev.sh rebuild-all
```

### Módulo não encontrado (ex: @tanstack/react-query)

```bash
# A imagem foi rebuilda mas o volume anônimo de node_modules está desatualizado
# Solucionar: usar rebuild (remove volume anônimo automaticamente)
./scripts/docker/dev.sh rebuild app
```

## 📚 Documentação Completa

- **Plano Completo:** [`docs/architecture/PLANO_MIGRACAO_DOCKER.md`](docs/architecture/PLANO_MIGRACAO_DOCKER.md)
- **Deploy Produção:** (em breve)
- **Troubleshooting:** (em breve)

## ⚙️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Frontend    │     │ Frontend    │     │             │
│ App         ├────►│ Admin       ├────►│  Backend    │
│ :3000       │     │ :3001       │     │  :8000      │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┴────┐
                    │                               │
              ┌─────▼─────┐                  ┌──────▼──────┐
              │ PostgreSQL│                  │   Redis     │
              │  :5432    │                  │   :6379     │
              └───────────┘                  └─────────────┘
```

- **1 Backend** (FastAPI) serve **2 Frontends** (Next.js)
- PostgreSQL para dados persistentes
- Redis para cache/queues (futuro)
- Tudo isolado em containers

## ✅ Próximos Passos

1. Testar upload com processadores (BTG, Mercado Pago)
2. Validar todas as funcionalidades
3. Preparar para produção (docker-compose.prod.yml)
4. Deploy no servidor VPS
