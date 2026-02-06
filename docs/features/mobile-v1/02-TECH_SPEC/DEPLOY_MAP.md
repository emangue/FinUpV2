# Deploy Map - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0  
**Objetivo:** Mapeamento EXATO de onde criar cada arquivo no deploy

---

## 📂 Estrutura de Pastas a Criar

### Frontend (Local e Servidor)

**Base:** `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend` (local)  
**Base Prod:** `/var/www/finup/app_dev/frontend` (servidor)

```bash
# 1. Criar estrutura de rotas mobile
mkdir -p src/app/mobile/dashboard
mkdir -p src/app/mobile/transactions
mkdir -p src/app/mobile/budget/edit
mkdir -p src/app/mobile/upload
mkdir -p src/app/mobile/profile

# 2. Criar pasta de componentes mobile
mkdir -p src/components/mobile

# 3. Criar pasta de configuração (design tokens)
mkdir -p src/config
```

---

## 📝 Arquivos Frontend - Paths Absolutos

### Rotas Mobile (`src/app/mobile/`)

| Arquivo | Path Completo (Local) | Path Completo (Prod) |
|---------|----------------------|---------------------|
| Layout Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/layout.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/layout.tsx` |
| Dashboard Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/dashboard/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/dashboard/page.tsx` |
| Transações Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/transactions/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/transactions/page.tsx` |
| Budget Mobile (View) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/budget/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/budget/page.tsx` |
| Budget Mobile (Edit) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/budget/edit/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/budget/edit/page.tsx` |
| Upload Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/upload/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/upload/page.tsx` |
| Profile Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/app/mobile/profile/page.tsx` | `/var/www/finup/app_dev/frontend/src/app/mobile/profile/page.tsx` |

---

### Componentes Mobile (`src/components/mobile/`)

| Componente | Path Completo (Local) | Path Completo (Prod) |
|------------|----------------------|---------------------|
| MobileHeader | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/mobile-header.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/mobile-header.tsx` |
| BottomNavigation | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/bottom-navigation.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/bottom-navigation.tsx` |
| MonthScrollPicker | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/month-scroll-picker.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/month-scroll-picker.tsx` |
| YtdToggle | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/ytd-toggle.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/ytd-toggle.tsx` |
| TrackerCard | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/tracker-card.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/tracker-card.tsx` |
| TrackerList | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/tracker-list.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/tracker-list.tsx` |
| CategoryRowInline | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/category-row-inline.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/category-row-inline.tsx` |
| DonutChart | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/donut-chart.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/donut-chart.tsx` |
| IconButton | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/icon-button.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/icon-button.tsx` |
| BudgetEditBottomSheet | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/budget-edit-bottom-sheet.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/budget-edit-bottom-sheet.tsx` |
| GrupoBreakdownSheet | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/grupo-breakdown-sheet.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/grupo-breakdown-sheet.tsx` |
| CategoryExpensesMobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/components/mobile/category-expenses-mobile.tsx` | `/var/www/finup/app_dev/frontend/src/components/mobile/category-expenses-mobile.tsx` |

---

### Design Tokens (`src/config/`)

| Arquivo | Path Completo (Local) | Path Completo (Prod) |
|---------|----------------------|---------------------|
| Cores Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/config/mobile-colors.ts` | `/var/www/finup/app_dev/frontend/src/config/mobile-colors.ts` |
| Dimensões Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/config/mobile-dimensions.ts` | `/var/www/finup/app_dev/frontend/src/config/mobile-dimensions.ts` |
| Tipografia Mobile | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/frontend/src/config/mobile-typography.ts` | `/var/www/finup/app_dev/frontend/src/config/mobile-typography.ts` |

---

## 📝 Arquivos Backend - Paths Absolutos

### Backend (Local e Servidor)

**Base:** `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend` (local)  
**Base Prod:** `/var/www/finup/app_dev/backend` (servidor)

```bash
# Estrutura JÁ EXISTE, apenas modificar arquivos existentes
```

---

### Endpoints Novos (Modificar arquivos existentes)

| Endpoint | Arquivo a Modificar (Path Local) | Path Prod |
|----------|----------------------------------|-----------|
| `POST /budget/geral/copy-to-year` | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/budget/router.py` | `/var/www/finup/app_dev/backend/app/domains/budget/router.py` |
| `POST /budget/geral/copy-to-year` (service) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/budget/service.py` | `/var/www/finup/app_dev/backend/app/domains/budget/service.py` |
| `POST /budget/geral/copy-to-year` (repo) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/budget/repository_geral.py` | `/var/www/finup/app_dev/backend/app/domains/budget/repository_geral.py` |
| `GET /transactions/grupo-breakdown` | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/transactions/router.py` | `/var/www/finup/app_dev/backend/app/domains/transactions/router.py` |
| `GET /transactions/grupo-breakdown` (service) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/transactions/service.py` | `/var/www/finup/app_dev/backend/app/domains/transactions/service.py` |
| `GET /transactions/grupo-breakdown` (repo) | `/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/app/domains/transactions/repository.py` | `/var/www/finup/app_dev/backend/app/domains/transactions/repository.py` |

---

## 🔄 Workflow de Deploy

### 1. Desenvolvimento Local

```bash
# 1. Criar branch
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
git checkout -b feature/mobile-v1

# 2. Criar estrutura frontend
cd app_dev/frontend
mkdir -p src/app/mobile/dashboard
mkdir -p src/app/mobile/transactions
mkdir -p src/app/mobile/budget/edit
mkdir -p src/app/mobile/upload
mkdir -p src/app/mobile/profile
mkdir -p src/components/mobile
mkdir -p src/config

# 3. Implementar arquivos (seguir IMPLEMENTATION_GUIDE.md)

# 4. Testar localmente
npm run dev # Frontend (porta 3000)
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload # Backend (porta 8000)

# 5. Commit e push
git add .
git commit -m "feat(mobile): implementa [componente/tela]"
git push origin feature/mobile-v1
```

---

### 2. Deploy no Servidor (após aprovação)

```bash
# 1. SSH no servidor
ssh minha-vps-hostinger

# 2. Navegar para projeto
cd /var/www/finup

# 3. Pull da branch
git fetch origin
git checkout feature/mobile-v1
git pull origin feature/mobile-v1

# 4. Aplicar migrations (se houver)
cd app_dev/backend
source venv/bin/activate
alembic upgrade head

# 5. Rebuild frontend
cd ../frontend
npm install
npm run build

# 6. Restart serviços
sudo systemctl restart finup-backend
sudo systemctl restart finup-frontend

# 7. Verificar logs
sudo journalctl -u finup-backend -f
sudo journalctl -u finup-frontend -f
```

---

## ⚠️ Arquivos a NÃO Modificar

| Arquivo | Motivo |
|---------|--------|
| `app_dev/backend/database/financas_dev.db` | Banco único, modificar via Alembic |
| `.env` | Secrets, NUNCA commitar |
| `node_modules/` | Gerado automaticamente |
| `venv/` | Ambiente virtual Python |
| `__pycache__/` | Cache Python |
| `.next/` | Build Next.js |

---

## 📊 Checklist de Deploy

### Frontend
- [ ] Estrutura de pastas criada (`mobile/`, `components/mobile/`, `config/`)
- [ ] Todos os 12 componentes implementados
- [ ] Todos os 7 arquivos de rota criados
- [ ] Design tokens (3 arquivos `mobile-*.ts`) criados
- [ ] `npm run build` sem erros
- [ ] Lighthouse score ≥ 90

### Backend
- [ ] 2 endpoints novos implementados (router + service + repository)
- [ ] Testes unitários criados
- [ ] Migrations aplicadas (se necessário)
- [ ] `pytest` passa 100%
- [ ] Servidor reiniciado

### Infraestrutura
- [ ] Branch `feature/mobile-v1` criada
- [ ] Push para GitHub completo
- [ ] Pull no servidor executado
- [ ] Serviços reiniciados (backend + frontend)
- [ ] Logs sem erros críticos
- [ ] Rollback plan pronto (ver TESTING_STRATEGY.md)

---

## 🎯 Ordem de Implementação

**Seguir ordem do IMPLEMENTATION_GUIDE.md:**

1. **Sprint 0:** Backend (2 endpoints novos)
2. **Sprint 1:** Componentes base + Dashboard mobile
3. **Sprint 2:** Transações mobile + Upload mobile
4. **Sprint 3:** Budget mobile (Metas)
5. **Sprint 4:** Profile mobile + Polish

---

## 📞 Comandos Úteis

### Local
```bash
# Ver estrutura de pastas frontend
tree app_dev/frontend/src -L 3 -I 'node_modules|.next'

# Ver estrutura backend
tree app_dev/backend/app/domains -L 2

# Testar build frontend
cd app_dev/frontend && npm run build

# Rodar testes backend
cd app_dev/backend && source venv/bin/activate && pytest
```

### Servidor
```bash
# Ver logs backend
sudo journalctl -u finup-backend -n 100 --no-pager

# Ver logs frontend
sudo journalctl -u finup-frontend -n 100 --no-pager

# Status dos serviços
sudo systemctl status finup-backend finup-frontend

# Restart rápido
sudo systemctl restart finup-backend finup-frontend
```

---

**IMPORTANTE:** SEMPRE seguir fluxo Local → Git → Servidor. NUNCA editar código diretamente no servidor!

---

**Data:** 31/01/2026  
**Status:** ✅ Completo  
**Próximo:** Implementar Sprint 0 (backend)
