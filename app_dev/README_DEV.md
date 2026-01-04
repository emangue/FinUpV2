# 🚀 App Dev - Ambiente de Desenvolvimento Isolado

## Estrutura Completamente Separada

```
app_dev/
├── backend/              # Backend API (Flask + SQLAlchemy)
├── frontend/             # Frontend React (Vite + TypeScript)
├── financas_dev.db       # ✅ Banco de dados DEV (SEPARADO)
├── uploads_temp/         # ✅ Uploads temporários DEV (SEPARADO)
├── static/               # ✅ Arquivos estáticos DEV (SEPARADO)
└── flask_session/        # ✅ Sessions Flask DEV (SEPARADO)
```

## 🔐 Recursos Separados

### ✅ Banco de Dados
- **Dev:** `app_dev/financas_dev.db`
- **Prod:** `financas.db` (root)
- **Isolamento:** 100% separado - dados dev não afetam prod

### ✅ Uploads
- **Dev:** `app_dev/uploads_temp/`
- **Prod:** `uploads_temp/` (root)
- **Isolamento:** Arquivos de teste não poluem prod

### ✅ Static Files
- **Dev:** `app_dev/static/`
- **Prod:** `static/` (root)
- **Isolamento:** Logos e assets separados

### ✅ Sessions
- **Dev:** `app_dev/flask_session/`
- **Prod:** `flask_session/` (root)
- **Isolamento:** Sessions de dev não interferem

## 🚀 Como Executar

### Backend API (Porta 8000)
```bash
cd app_dev
python run.py
# OU da raiz do projeto:
python run_dev_api.py
```

### Frontend React (Porta 3000)
```bash
cd app_dev/frontend
npm run dev
```

### Acessar
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Login: admin@email.com / admin123

## 📦 Deploy

Apenas **código** é copiado para produção:
```bash
./deploy.sh validate   # Validar
./deploy.sh deploy     # Deploy
```

**✅ SÃO copiados:**
- ✅ `backend/` (código Python)
- ✅ `frontend/` (código React)

**❌ NÃO são copiados:**
- ❌ `financas_dev.db` (banco dev fica em dev)
- ❌ `uploads_temp/` (arquivos dev ficam em dev)
- ❌ `static/uploads/` (assets dev ficam em dev)
- ❌ `flask_session/` (sessions dev ficam em dev)
- ❌ `node_modules/` (dependências não commitadas)
- ❌ `dist/` (build não commitado)

## 🔧 Configurações

### Backend (`backend/config_dev.py`)
```python
# Banco SEPARADO
SQLALCHEMY_DATABASE_URI = "sqlite:///app_dev/financas_dev.db"

# Uploads SEPARADOS
UPLOAD_FOLDER = "app_dev/uploads_temp"

# Static SEPARADO
STATIC_FOLDER = "app_dev/static"

# Sessions SEPARADAS
SESSION_FOLDER = "app_dev/flask_session"
```

## 🔄 Resetar Dev

### Resetar Banco
```bash
rm app_dev/financas_dev.db
cp financas.db app_dev/financas_dev.db
```

### Limpar Uploads
```bash
rm -rf app_dev/uploads_temp/*
```

### Limpar Sessions
```bash
rm -rf app_dev/flask_session/*
```

### Limpar Frontend Build
```bash
cd app_dev/frontend
rm -rf dist node_modules .vite
npm install
```

## 🎯 Stack Tecnológico

### Backend
- Flask 3.0.0
- Flask-SQLAlchemy 2.0
- Flask-JWT-Extended
- Flask-CORS
- SQLite (banco separado)

### Frontend
- React 18.2
- Vite 5.4
- TypeScript 5.2
- Tailwind CSS 3.3
- shadcn/ui components
- TanStack Query (React Query)
- Zustand (state management)
- Recharts (gráficos)

## 📚 Documentação

- [Separação Completa Dev vs Prod](../docs/SEPARACAO_DEV_PROD.md) ⭐
- [Workflow de Deploy](../docs/WORKFLOW_DEPLOY.md)
- [Checklist de Deploy](../docs/DEPLOY_CHECKLIST.md)
- [README Principal](../README.md)

## ⚠️ Regras Importantes

### ✅ SEMPRE
- ✅ Desenvolver em `app_dev/`
- ✅ Usar `financas_dev.db` em dev
- ✅ Testar em dev antes de deploy
- ✅ Validar antes de deploy (`./deploy.sh validate`)

### ❌ NUNCA
- ❌ Editar `app/` diretamente
- ❌ Usar `financas.db` (prod) em dev
- ❌ Compartilhar uploads entre dev e prod
- ❌ Fazer deploy sem validar

---

**Status**: ✅ Ambiente completamente isolado  
**Versão**: 4.0.0-dev  
**Última atualização**: Janeiro 2026

## 📋 PRÓXIMOS PASSOS (VOCÊ PRECISA FAZER)

### 1. Instalar dependências do frontend

```bash
cd app_dev/frontend
npm install
npm install tailwindcss-animate  # Plugin adicional
```

### 2. Instalar dependências Python no backend

```bash
pip install flask-cors flask-jwt-extended
```

### 3. Criar arquivos que faltam (vou criar agora)

Preciso criar:
- ✅ Stores (Zustand para autenticação)
- ✅ Services (API client com Axios)
- ✅ Pages (Login, Dashboard)
- ✅ Components (Cards, Sidebar, Charts, etc)
- ✅ Utilitários

### 4. Como rodar o app DEV

**Terminal 1 - Backend API:**
```bash
python run_dev_api.py
# Roda em http://localhost:5002
```

**Terminal 2 - Frontend React:**
```bash
cd app_dev/frontend
npm run dev
# Roda em http://localhost:5173
```

### 5. Atualizar .gitignore

Adicionar ao .gitignore (IMPORTANTE - não commitar até testar!):
```
# App DEV (não validado)
app_dev/
run_dev_api.py
```

## 🎯 ESTRUTURA FINAL

```
ProjetoFinancasV3/
├── app/                          # ✅ App original (NÃO TOCAR)
├── app_dev/                      # 🆕 Novo app desenvolvimento
│   ├── backend/                  # Flask API
│   │   ├── api/
│   │   │   └── blueprints/
│   │   │       ├── auth_dev.py
│   │   │       ├── dashboard_dev.py
│   │   │       └── transactions_dev.py
│   │   ├── config_dev.py
│   │   ├── models.py
│   │   └── __init__.py
│   └── frontend/                 # React + Vite
│       ├── src/
│       │   ├── components/       # Componentes reutilizáveis
│       │   ├── pages/            # Páginas (Login, Dashboard)
│       │   ├── services/         # API client
│       │   ├── stores/           # Zustand stores
│       │   ├── hooks/            # Custom hooks
│       │   ├── lib/              # Utilitários
│       │   ├── App.tsx
│       │   ├── main.tsx
│       │   └── index.css
│       ├── package.json
│       ├── vite.config.ts
│       ├── tailwind.config.js
│       └── tsconfig.json
├── run_dev_api.py                # Servidor backend DEV
└── run.py                        # ✅ App original (NÃO MUDOU)
```

## 🔧 COMO FUNCIONA

1. **Backend (porta 5002)**: API REST pura (JSON)
2. **Frontend (porta 5173)**: React SPA consumindo a API
3. **Vite Proxy**: Frontend faz requests para `/api/*` que são redirecionados para `localhost:5002`
4. **Autenticação**: JWT tokens (access + refresh)
5. **Estado Global**: Zustand
6. **Data Fetching**: TanStack Query (React Query)
7. **UI**: Tailwind CSS + componentes shadcn/ui style

## 🎨 DASHBOARD LAYOUT (inspirado shadcn/ui)

```
┌────────────────────────────────────────┐
│  Sidebar       │  Header               │
│  (fixa)        │  (user, logout)       │
│                ├───────────────────────┤
│  - Dashboard   │  Métricas (4 cards):  │
│  - Transações  │  - Total Gastos       │
│  - Upload      │  - Receitas           │
│  - Admin       │  - Saldo              │
│                │  - Qtd Transações     │
│                ├───────────────────────┤
│                │  Gráfico de Área      │
│                │  (gastos por mês)     │
│                ├───────────────────────┤
│                │  Tabela Transações    │
│                │  (últimas 10)         │
└────────────────────────────────────────┘
```

## ⚠️ IMPORTANTE

- **NÃO COMMITAR** app_dev/ até testarmos completamente
- **NÃO MODIFICAR** app/ (original permanece intocado)
- **GIT IGNORE** configurado para ignorar app_dev/
- **Banco de dados**: Usa o mesmo `financas.db` do app original para testes

## 🚀 QUANDO TERMINAR E VALIDAR

Depois de testar e aprovar:
1. Remover `app_dev/` do .gitignore
2. Commit do novo app
3. Opcionalmente: renomear `app/` para `app_legacy/` e `app_dev/` para `app/`

---

**Status Atual**: ⚙️ Em desenvolvimento (60% completo)
**Próximo**: Criar stores, services, pages e components React
