# 🗄️ CONFIGURAÇÃO DE BANCO DE DADOS - ÚNICA FONTE DE VERDADE

## ⚠️ REGRA CRÍTICA: UM ÚNICO BANCO PARA TODA APLICAÇÃO

**Path absoluto do banco:**
```
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db
```

## 📍 Onde está configurado:

### Backend FastAPI
**Arquivo:** `app_dev/backend/app/config.py`
```python
DATABASE_PATH: Path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
```

### Frontend Next.js
**Arquivo:** `app_dev/frontend/src/lib/db-config.ts`
```typescript
const DB_ABSOLUTE_PATH = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db'
```

## 🚫 NUNCA FAÇA:

❌ Criar outro banco de dados  
❌ Usar paths relativos diferentes  
❌ Modificar apenas um dos arquivos (backend OU frontend)  
❌ Criar cópias do banco  

## ✅ SEMPRE FAÇA:

✅ Use o path absoluto completo  
✅ Se precisar mudar, mude nos 2 arquivos simultaneamente  
✅ Teste backend E frontend após mudanças  
✅ Faça backup antes de mudanças estruturais  

## 🔍 Como verificar:

### Backend
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend
python -c "from app.config import settings; print(settings.DATABASE_PATH)"
```

### Frontend
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/frontend
node -e "const { getDbInfo } = require('./src/lib/db-config.ts'); console.log(getDbInfo())"
```

### SQLite direto
```bash
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db ".tables"
```

## 🛡️ Proteção

Este arquivo existe para evitar bugs de "dados não aparecem" causados por:
- Backend e frontend usando bancos diferentes
- Paths relativos que resolvem para locais diferentes
- Múltiplas cópias do banco sincronizadas

## 📝 Histórico de mudanças

- **2026-01-05:** Unificação para path absoluto único em backend E frontend
