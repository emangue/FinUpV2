# 🚀 Sistema de Finanças - Arquitetura Mista (Backend FastAPI + Frontend Next.js)

✅ **Backend FastAPI funcionando na porta 8000**  
✅ **Frontend Next.js funcionando na porta 3000**  
✅ **Integração completa via API REST**

---

## ⚡ Início Rápido

### 1️⃣ Iniciar Backend

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
source venv/bin/activate
cd app_dev/backend
python run.py
```

✅ Backend: http://localhost:8000  
📚 Documentação: http://localhost:8000/docs

### 2️⃣ Iniciar Frontend

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev
npm run dev
```

✅ Frontend: http://localhost:3000

### 3️⃣ Login

**Credenciais:**
- Email: `admin@financas.com`
- Senha: `admin123`

---

## 📁 Estrutura

```
app_dev/
├── backend/              # FastAPI (Python)
│   ├── app/
│   │   ├── routers/     # auth, dashboard, marcacoes
│   │   ├── models/      # SQLAlchemy
│   │   └── schemas/     # Pydantic
│   └── run.py
├── src/                  # Next.js (TypeScript)
│   ├── app/
│   ├── components/
│   └── lib/
│       └── api-client.ts  # Cliente HTTP
└── financas_dev.db       # SQLite
```

---

## 🔌 Endpoints Principais

**Autenticação:**
- `POST /api/v1/auth/login` - Login (retorna JWT)
- `GET /api/v1/auth/me` - Usuário atual

**Dashboard:**
- `GET /api/v1/dashboard/metrics?year=2025&month=all`
- `GET /api/v1/dashboard/categories?year=2025&month=all`
- `GET /api/v1/dashboard/chart/receitas-despesas`

**Marcações:**
- `GET /api/v1/marcacoes/` - Listar
- `POST /api/v1/marcacoes/` - Criar
- `PUT /api/v1/marcacoes/{id}` - Atualizar
- `DELETE /api/v1/marcacoes/{id}` - Deletar

---

## 🔑 Autenticação

1. Login envia email/senha → Backend retorna JWT
2. Token salvo em `localStorage`
3. Todas as requisições incluem: `Authorization: Bearer <token>`
4. Token expira em 24h

---

## 🛠️ Usando o API Client

```typescript
import { authAPI, dashboardAPI } from '@/lib/api-client';

// Login
await authAPI.login(email, password);

// Dashboard
const metrics = await dashboardAPI.getMetrics(2025, 'all');
const categories = await dashboardAPI.getCategories(2025, 'all');
const chartData = await dashboardAPI.getReceitasDespesasChart();
```

---

## 📊 Banco de Dados

**SQLite:** `app_dev/financas_dev.db`

Tabelas:
- `users` - Usuários e autenticação
- `journal_entries` - Transações financeiras
- `base_marcacoes` - Categorias
- `bank_format_compatibility` - Formatos de bancos

---

## 🧪 Testar Backend

```bash
# Verificar status
curl http://localhost:8000/docs

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"admin123"}'

# Métricas (com token)
curl -H "Authorization: Bearer <TOKEN>" \
  "http://localhost:8000/api/v1/dashboard/metrics?year=2025&month=all"
```

---

## 📝 Próximos Passos

- [ ] **Fase 3**: Upload de arquivos (CSV/XLS)
- [ ] **Fase 4**: Processadores e classificadores
- [ ] **Fase 5**: Deduplicação e parcelas
- [ ] **Fase 6**: Deploy em produção

---

## ⚠️ Troubleshooting

**Backend não inicia:**
```bash
lsof -ti:8000 | xargs kill -9
cd app_dev/backend && python run.py
```

**Frontend não conecta:**
1. Verificar se backend está rodando: `curl http://localhost:8000/docs`
2. Verificar `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
3. Abrir console do navegador (F12) para ver erros

**Erro de autenticação:**
1. Fazer logout e login novamente
2. Verificar token no localStorage: `localStorage.getItem('access_token')`

---

## 🎯 Status Atual

✅ Backend FastAPI funcionando  
✅ Frontend Next.js funcionando  
✅ Autenticação JWT implementada  
✅ Dashboard integrado  
✅ Gráficos funcionais  
✅ Filtros de data/mês  
⏳ Upload de arquivos (próxima fase)

---

**Versão:** 4.0.0-dev  
**Data:** 2026-01-03  
**Arquitetura:** Python FastAPI + TypeScript Next.js
