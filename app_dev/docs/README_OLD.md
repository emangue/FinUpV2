# 🏗️ Sistema de Finanças - Arquitetura Mista

**Backend Python (FastAPI) + Frontend TypeScript (Next.js 16)**

## 📦 Estrutura do Projeto

```
app_dev/
├── backend/              # 🆕 Backend Python FastAPI (API REST)
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── routers/     # Endpoints (auth, dashboard, etc)
│   │   ├── models/      # SQLAlchemy models
│   │   └── schemas/     # Pydantic validation
│   ├── requirements.txt
│   └── run.py
│
├── src/                  # Frontend Next.js 16 (TypeScript)
│   ├── app/
│   │   ├── (dashboard)/ # Páginas do dashboard
│   │   └── settings/    # Configurações
│   └── components/      # Componentes React
│
├── financas_dev.db      # Banco de dados SQLite (compartilhado)
└── package.json         # Frontend dependencies
```

## 🚀 Como Rodar o Sistema Completo

### 1. Backend (FastAPI) - Terminal 1

```bash
cd backend
pip install -r requirements.txt
python run.py
```

✅ Backend: **http://localhost:8000**  
📖 Docs: http://localhost:8000/docs

### 2. Frontend (Next.js) - Terminal 2

```bash
npm install
npm run dev
```

✅ Frontend: **http://localhost:3000**

## 🔄 Fluxo de Dados

```
Frontend (Next.js:3000) ──HTTP/JSON──> Backend (FastAPI:8000) ──> financas_dev.db
```

- **Autenticação:** JWT em httpOnly cookies
- **CORS:** Configurado para localhost:3000 → localhost:8000

## 📋 Endpoints da API

### 🔐 Auth
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### 📊 Dashboard
- `GET /api/v1/dashboard/metrics?year=2025&month=all`
- `GET /api/v1/dashboard/categories?year=2025&month=all`
- `GET /api/v1/dashboard/chart/receitas-despesas`

### ⚙️ Configurações
- `GET /api/v1/marcacoes/` - Categorias
- `POST /api/v1/marcacoes/` - Criar
- `PUT /api/v1/marcacoes/{id}` - Atualizar
- `DELETE /api/v1/marcacoes/{id}` - Deletar

### 🏦 Compatibilidade
- `GET /api/v1/compatibility/` - Bancos/formatos

## 📚 Documentação

- **Backend:** [backend/README.md](backend/README.md)
- **API Docs:** http://localhost:8000/docs
- **Next.js:** https://nextjs.org/docs
