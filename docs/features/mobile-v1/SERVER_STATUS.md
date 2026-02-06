# 🚨 Status dos Servidores - Sprint 0

**Data:** 01/02/2026  
**Status:** ⚠️ Ambiente virtual corrompido - Requer correção manual

---

## ❌ Problemas Encontrados

### 1. Backend (Porta 8000)
**Problema:** Ambiente virtual Python corrompido
```
ModuleNotFoundError: No module named 'uvicorn.middleware.message_logger'
ModuleNotFoundError: No module named 'pip._vendor.tenacity._asyncio'
```

**Causa:** Possível conflito de versões ou instalação incompleta

---

### 2. Frontend (Porta 3000)
**Problema:** Módulo não encontrado
```
Error: Cannot find module '@/lib/utils'
```

**Causa:** Função `cn()` usada nos componentes mobile não existe ainda

---

## ✅ Solução Rápida

### Passo 1: Recriar Ambiente Virtual Python
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev

# Desativar e remover venv antigo
deactivate 2>/dev/null || true
rm -rf venv

# Criar novo venv
python3 -m venv venv
source venv/bin/activate

# Reinstalar dependências
pip install --upgrade pip
pip install -r backend/requirements.txt

# Testar
cd backend
python run.py
# Deve aparecer: "Uvicorn running on http://0.0.0.0:8000"
```

---

### Passo 2: Criar Função Utils Faltante
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend

# Criar arquivo se não existir
mkdir -p src/lib
cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

# Instalar dependências se necessário
npm install clsx tailwind-merge

# Testar
npm run dev
# Deve abrir em http://localhost:3000
```

---

### Passo 3: Usar Quick Start
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Parar processos anteriores
./scripts/deploy/quick_stop.sh

# Iniciar ambos os servidores
./scripts/deploy/quick_start.sh

# Verificar logs
tail -f temp/logs/backend.log
tail -f temp/logs/frontend.log
```

---

## 🧪 Testar Implementação

### 1. Backend - Testar Novos Endpoints

```bash
# Abrir Swagger Docs
open http://localhost:8000/docs

# OU testar com curl:

# 1. GET /budget/planning
curl -X GET "http://localhost:8000/api/v1/budget/planning?mes_referencia=2026-02" \
  -H "Authorization: Bearer SEU_TOKEN"

# 2. POST /budget/planning/bulk-upsert
curl -X POST "http://localhost:8000/api/v1/budget/planning/bulk-upsert" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "mes_referencia": "2026-02",
    "budgets": [
      {"grupo": "Alimentação", "valor_planejado": 2000},
      {"grupo": "Transporte", "valor_planejado": 500}
    ]
  }'

# 3. POST /budget/geral/copy-to-year
curl -X POST "http://localhost:8000/api/v1/budget/geral/copy-to-year" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "mes_origem": "2026-02",
    "ano_destino": 2026,
    "substituir_existentes": false
  }'

# 4. GET /transactions/grupo-breakdown
curl -X GET "http://localhost:8000/api/v1/transactions/grupo-breakdown?grupo=Cartão%20de%20Crédito&year=2026&month=2" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

### 2. Frontend - Testar Rotas Mobile

```bash
# Abrir no navegador (ou mobile)
open http://localhost:3000/mobile/dashboard
open http://localhost:3000/mobile/transactions
open http://localhost:3000/mobile/budget
open http://localhost:3000/mobile/upload
open http://localhost:3000/mobile/profile
```

**Verificar:**
- [ ] Bottom Navigation aparece (5 tabs)
- [ ] FAB central (Metas) está destacado
- [ ] Clicar em cada tab navega corretamente
- [ ] Header mobile aparece com título correto
- [ ] Componentes renderizam sem erros (console)

---

### 3. Testar Componentes Base

**Abrir DevTools (F12) e verificar:**
- [ ] Sem erros de import no console
- [ ] Design tokens carregam (`mobile-colors.ts`, etc)
- [ ] Componentes mobile renderizam (`IconButton`, `MobileHeader`, `BottomNavigation`)

---

## 📊 Arquivos Criados - Checklist

### Design Tokens (4 arquivos) ✅
- [x] `src/config/mobile-colors.ts`
- [x] `src/config/mobile-dimensions.ts`
- [x] `src/config/mobile-typography.ts`
- [x] `src/config/mobile-animations.ts`

### Componentes Base (3 arquivos) ✅
- [x] `src/components/mobile/icon-button.tsx`
- [x] `src/components/mobile/mobile-header.tsx`
- [x] `src/components/mobile/bottom-navigation.tsx`

### Rotas Mobile (6 arquivos) ✅
- [x] `src/app/mobile/layout.tsx`
- [x] `src/app/mobile/dashboard/page.tsx`
- [x] `src/app/mobile/transactions/page.tsx`
- [x] `src/app/mobile/budget/page.tsx`
- [x] `src/app/mobile/upload/page.tsx`
- [x] `src/app/mobile/profile/page.tsx`

### Backend Endpoints (2 arquivos editados) ✅
- [x] `app_dev/backend/app/domains/budget/router.py` (3 endpoints)
- [x] `app_dev/backend/app/domains/budget/service.py` (4 métodos)
- [x] `app_dev/backend/app/domains/transactions/router.py` (1 endpoint)
- [x] `app_dev/backend/app/domains/transactions/service.py` (1 método)

### Utilitário Faltante (1 arquivo) ⚠️ CRIAR
- [ ] `src/lib/utils.ts` (função `cn()`)

---

## 🎯 Próximos Passos (Após Correção)

1. ✅ Corrigir ambiente virtual Python
2. ✅ Criar `src/lib/utils.ts`
3. ✅ Reiniciar servidores com `quick_start.sh`
4. ✅ Testar 4 endpoints backend no Swagger
5. ✅ Testar 5 rotas mobile no navegador
6. ✅ Verificar Bottom Navigation funcional
7. 🚀 Iniciar **Sprint 1** (MonthScrollPicker, YTDToggle, Dashboard completo)

---

## 📞 Referências

- **TECH_SPEC.md:** `/docs/features/mobile-v1/02-TECH_SPEC/TECH_SPEC.md`
- **IMPLEMENTATION_GUIDE.md:** `/docs/features/mobile-v1/02-TECH_SPEC/IMPLEMENTATION_GUIDE.md`
- **DEPLOY_PROGRESS.md:** `/docs/features/mobile-v1/DEPLOY_PROGRESS.md`

---

**Última atualização:** 01/02/2026 20:30
