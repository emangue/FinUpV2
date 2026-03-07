# 🚀 GUIA RÁPIDO - SERVIDORES FINANCASV3
# =====================================

## ⚡ COMANDOS RÁPIDOS

### 🔧 Iniciar Tudo (Automático)
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
chmod +x start_servers.sh
./start_servers.sh
```

### 🛠️ Manual (Passo a Passo)

#### 1️⃣ Preparar Ambiente
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
source venv/bin/activate
```

#### 2️⃣ Limpar Processos
```bash
pkill -f "uvicorn.*app.main" || true
pkill -f "next dev" || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
```

#### 3️⃣ Backend (Terminal 1)
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend

PYTHONPATH=/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend:/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/codigos_apoio \
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4️⃣ Frontend (Terminal 2)
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/frontend
npm run dev
```

---

## 🌐 URLs

| Serviço | URL | Porta |
|---------|-----|-------|
| **Frontend** | http://localhost:3000 | 3000 |
| **Backend API** | http://localhost:8000 | 8000 |
| **Documentação** | http://localhost:8000/docs | 8000 |

---

## 👤 LOGIN OBRIGATÓRIO

**⚠️ SEMPRE FAZER LOGIN COMO user_id = 1**

- **Email**: `admin@example.com`
- **Senha**: `admin123`  
- **User ID**: `1`

---

## 🗄️ BANCO DE DADOS

**Path**: `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db`

### Verificar Banco
```bash
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db ".tables"
```

### Verificar User ID 1
```bash
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db "SELECT id, nome, email FROM users WHERE id = 1;"
```

---

## 🛑 PARAR SERVIDORES

```bash
pkill -f "uvicorn.*app.main"
pkill -f "next dev"
```

---

## 🚨 TROUBLESHOOTING

### Backend não inicia
- ✅ Verificar se porta 8000 está livre: `lsof -i:8000`
- ✅ Verificar PYTHONPATH correto
- ✅ Verificar ambiente virtual ativado

### Frontend não inicia  
- ✅ Verificar se porta 3000 está livre: `lsof -i:3000`
- ✅ Limpar cache: `rm -rf .next`
- ✅ Verificar package.json no diretório correto

### Erro de Import
- ✅ Verificar alias `@/lib/db-config` no tsconfig.json
- ✅ Verificar path do banco em db-config.ts
- ✅ Limpar cache: `rm -rf .next`

### Level 3 Classification não funciona
- ✅ Verificar banco tem tabela `base_padroes`
- ✅ Verificar user_id = 1 tem padrões cadastrados
- ✅ Testar SQL: `SELECT COUNT(*) FROM base_padroes WHERE user_id = 1;`

---

## 📋 CHECKLIST PRÉ-USO

- [ ] ✅ Ambiente virtual ativado
- [ ] ✅ Backend rodando na porta 8000
- [ ] ✅ Frontend rodando na porta 3000  
- [ ] ✅ Banco de dados acessível
- [ ] ✅ Login feito como user_id = 1
- [ ] ✅ APIs respondendo (health, compatibility)
- [ ] ✅ Level 3 classification funcionando

---

## 🎯 COMANDOS DE VERIFICAÇÃO

```bash
# Verificar servidores
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend OK" || echo "❌ Backend ERRO"
curl -s http://localhost:3000/ > /dev/null && echo "✅ Frontend OK" || echo "❌ Frontend ERRO"

# Verificar classificação Level 3
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
python test_sistema_completo.py
```