# Backend FastAPI - Sistema de Finanças

## 🚀 Como Rodar

### 1. Instalar Dependências

```bash
cd app_dev/backend
pip install -r requirements.txt
```

### 2. Rodar Servidor

```bash
python run.py
```

Servidor estará em: **http://localhost:8000**

### 3. Documentação da API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Estrutura

```
backend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Configurações
│   ├── database.py      # SQLAlchemy setup
│   ├── models/          # Modelos do banco
│   ├── schemas/         # Pydantic schemas
│   └── routers/         # Endpoints
│       ├── auth.py      # Autenticação JWT
│       ├── dashboard.py # Métricas
│       ├── marcacoes.py # Configurações
│       └── compatibility.py # Bancos
├── requirements.txt
└── run.py
```

## 🔐 Autenticação

Usa JWT tokens em httpOnly cookies.

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "senha123"}'
```

## 🔄 Endpoints Principais

### Dashboard
- `GET /api/v1/dashboard/metrics?year=2025&month=all`
- `GET /api/v1/dashboard/categories?year=2025&month=all`
- `GET /api/v1/dashboard/chart/receitas-despesas`

### Marcações (Configurações)
- `GET /api/v1/marcacoes/` - Lista todas
- `POST /api/v1/marcacoes/` - Cria nova
- `PUT /api/v1/marcacoes/{id}` - Atualiza
- `DELETE /api/v1/marcacoes/{id}` - Deleta

### Compatibilidade
- `GET /api/v1/compatibility/` - Lista bancos/formatos

## 📊 Banco de Dados

Usa o banco existente: `app_dev/financas_dev.db` (SQLite)

Não precisa criar tabelas - backend lê o banco que já existe.

## 🔧 Desenvolvimento

**Hot reload ativo:** Mudanças no código reiniciam o servidor automaticamente.

**Logs detalhados:** SQLAlchemy mostra todas as queries no console.
