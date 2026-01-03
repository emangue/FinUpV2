# 🚀 GUIA DE INSTALAÇÃO E EXECUÇÃO - App DEV

## ✅ O QUE ESTÁ PRONTO

### Backend (Flask API)
- ✅ API REST completa (Auth, Dashboard, Transactions)
- ✅ JWT authentication
- ✅ CORS configurado
- ✅ Models copiados do app original

### Frontend (React + TypeScript)
- ✅ Páginas: Login, Dashboard
- ✅ Componentes: Sidebar, Header, Cards, Charts, Table
- ✅ Services: API client com Axios + interceptors
- ✅ Stores: Zustand para autenticação
- ✅ Utils: Formatação de moeda e data
- ✅ Tailwind CSS configurado

---

## 📦 PASSO 1: Instalar Dependências

### Backend (Python)
```bash
# Certifique-se que venv está ativo
source venv/bin/activate

# Instalar dependências adicionais
pip install flask-cors flask-jwt-extended
```

### Frontend (Node.js)
```bash
cd app_dev/frontend

# Instalar dependências
npm install

# Instalar plugin Tailwind adicional
npm install -D tailwindcss-animate
```

---

## 🚀 PASSO 2: Executar os Servidores

### Terminal 1 - Backend API (Porta 5002)
```bash
# Na raiz do projeto
python run_dev_api.py
```

Você verá:
```
============================================================
  🚀 Backend API DEV - Sistema Financeiro v4.0.0-dev
============================================================
  📍 API: http://localhost:5002/api/v1
  ❤️  Health: http://localhost:5002/api/health
```

### Terminal 2 - Frontend React (Porta 5173)
```bash
cd app_dev/frontend
npm run dev
```

Você verá:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

---

## 🌐 PASSO 3: Acessar a Aplicação

Abra o navegador em: **http://localhost:5173**

### Login:
- **Email:** admin@email.com
- **Senha:** (a senha do usuário admin do banco `financas.db`)

Se não lembrar a senha, crie um novo usuário:
```python
# No Python
from app.models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///instance/financas.db')
Session = sessionmaker(bind=engine)
session = Session()

new_user = User(email='test@test.com', nome='Teste')
new_user.set_password('123456')
session.add(new_user)
session.commit()
```

---

## 🎨 O QUE VOCÊ VAI VER

### Dashboard com:
1. **4 Cards de Métricas**
   - Total Gastos (vermelho)
   - Total Receitas (verde)
   - Saldo (azul)
   - Total Transações (roxo)

2. **Gráfico de Área Interativo**
   - Gastos dos últimos 6 meses
   - Tooltip com valores formatados

3. **Tabela de Transações Recentes**
   - Últimas 10 transações
   - Data, Estabelecimento, Grupo, Marcação, Valor
   - Cores diferentes para Débito/Crédito

4. **Sidebar Fixa**
   - Navegação (Dashboard, Transações, Upload, Admin)
   - Logo FinUp DEV

5. **Header**
   - Nome do usuário
   - Botão de logout

---

## 🐛 TROUBLESHOOTING

### Erro: "Cannot find module 'zustand/middleware'"
```bash
cd app_dev/frontend
npm install zustand
```

### Erro: "Module not found: Error: Can't resolve '@'"
O alias `@` está configurado. Se der erro:
```bash
npm install -D @types/node
```

### Erro CORS no navegador
Verifique se:
1. Backend está rodando na porta 5002
2. Frontend está rodando na porta 5173
3. Vite proxy está configurado (`/api` → `http://localhost:5002`)

### Backend não encontra módulos
```bash
# Reinstalar dependências
pip install -r requirements.txt
pip install flask-cors flask-jwt-extended
```

---

## 📊 ARQUITETURA

```
┌─────────────────────────────────────────────┐
│  Frontend (React)                           │
│  http://localhost:5173                      │
│  ├─ Login Page                              │
│  ├─ Dashboard Page                          │
│  ├─ Components (Sidebar, Header, etc)      │
│  └─ API Client (Axios + JWT interceptors)  │
└─────────────┬───────────────────────────────┘
              │ HTTP Requests (/api/v1/*)
              ↓
┌─────────────────────────────────────────────┐
│  Backend (Flask API)                        │
│  http://localhost:5002                      │
│  ├─ /api/v1/auth (login, register)         │
│  ├─ /api/v1/dashboard (metrics, charts)    │
│  ├─ /api/v1/transactions (CRUD)            │
│  └─ JWT Authentication                      │
└─────────────┬───────────────────────────────┘
              │ SQLAlchemy ORM
              ↓
┌─────────────────────────────────────────────┐
│  Database (SQLite)                          │
│  instance/financas.db                       │
│  (mesmo banco do app original)              │
└─────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE FUNCIONAMENTO

- [ ] Backend rodando em http://localhost:5002
- [ ] Frontend rodando em http://localhost:5173
- [ ] Health check: http://localhost:5002/api/health retorna `{"status": "ok"}`
- [ ] Login funciona
- [ ] Dashboard carrega métricas
- [ ] Gráfico renderiza
- [ ] Tabela de transações aparece
- [ ] Logout funciona
- [ ] Redirect funciona (não logado → /login)

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Testar toda a aplicação
2. 📝 Criar página de Transações completa (lista, filtros, edição)
3. 📤 Criar página de Upload
4. ⚙️ Criar página de Admin
5. 🚀 Deploy na VM (quando validado)

---

## 📝 NOTAS IMPORTANTES

- **NÃO ESTÁ NO GIT**: `app_dev/` está no .gitignore
- **NÃO MODIFICA APP ORIGINAL**: `app/` permanece intocado
- **USA MESMO BANCO**: Cuidado ao testar (dados compartilhados)
- **VERSÃO DE DEV**: Não usar em produção ainda

---

**Criado em:** 02/01/2026  
**Versão:** 4.0.0-dev  
**Status:** ✅ Pronto para testes!
