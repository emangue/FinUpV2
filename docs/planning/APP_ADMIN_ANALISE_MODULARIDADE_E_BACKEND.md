# Análise: app_admin – Modularidade e Backend Independente

**Data:** 15/02/2026  
**Contexto:** Dúvidas sobre regras de modularidade (Copilot instructions) e necessidade de backend próprio.

---

## 1. Problema: Site não funcionando

**Causa identificada:** CORS bloqueando requisições do app_admin.

- app_admin roda em **porta 3001** (`next dev -p 3001`)
- Backend (app_dev) aceitava apenas `localhost:3000` e `127.0.0.1:3000`
- Requisições de `localhost:3001` eram bloqueadas pelo navegador

**Correção aplicada:** Inclusão de `localhost:3001` e `127.0.0.1:3001` em `BACKEND_CORS_ORIGINS` no `app_dev/backend/app/core/config.py`.

**Para testar:**
1. Backend rodando: `./scripts/deploy/quick_start.sh` (ou `cd app_dev/backend && python run.py`)
2. app_admin: `cd app_admin/frontend && npm run dev`
3. Acessar http://localhost:3001 e fazer login com admin@financas.com

---

## 2. Modularidade – Copilot Instructions

### 2.1 Regras do Copilot (frontend)

| Regra | app_admin atual | Status |
|-------|-----------------|--------|
| **features/** com components, hooks, services, types | Não existe – lógica em `app/admin/*/page.tsx` | ❌ |
| **core/** para config e utils | Existe `core/config`, `core/utils` | ✅ |
| **components/** apenas para compartilhados | Existe `components/ui`, `RequireAdmin` | ⚠️ Parcial |
| API calls em **services/** | URLs em `api.config`, fetch direto nas páginas | ❌ |
| Lógica de estado em **hooks/** | useState direto nas páginas | ❌ |
| Imports de `api.config` centralizado | Usa `API_CONFIG` | ✅ |
| Sem imports cruzados entre features | N/A (sem features) | - |

### 2.2 Estrutura recomendada (feature-based)

```
app_admin/frontend/src/
├── core/
│   ├── config/api.config.ts      ✅ Já existe
│   └── utils/api-client.ts       ✅ Já existe
│
├── features/
│   ├── contas/
│   │   ├── components/
│   │   │   ├── contas-list.tsx
│   │   │   ├── contas-modal.tsx
│   │   │   └── index.ts
│   │   ├── hooks/use-contas.ts
│   │   ├── services/contas-api.ts
│   │   └── index.ts
│   ├── screens/          (placeholder)
│   ├── bancos/           (placeholder)
│   └── ...
│
├── components/           # Compartilhados
│   ├── ui/
│   └── RequireAdmin.tsx
│
└── app/
    └── admin/
        └── contas/page.tsx   # Apenas importa da feature
```

### 2.3 Próximos passos para modularidade

1. Criar `features/contas/` com:
   - `services/contas-api.ts` – chamadas à API
   - `hooks/use-contas.ts` – estado e lógica
   - `components/` – lista, modais, etc.
2. Deixar `app/admin/contas/page.tsx` apenas montando a feature.
3. Replicar o padrão para screens, bancos, backup, categorias quando forem implementados.

---

## 3. Backend: decisão de custo-benefício

### 3.1 Situação atual

- app_admin usa o backend de `app_dev` (porta 8000).
- app_admin não importa código de app_dev; só usa HTTP.
- Dependência: `NEXT_PUBLIC_BACKEND_URL` apontando para o backend de app_dev.

### 3.2 Opções avaliadas

| Opção | Segurança | Duplicação | Manutenção futura |
|-------|-----------|------------|-------------------|
| **A)** Backend compartilhado | require_admin já existe | Zero | Corrigir em 1 lugar |
| **B)** Backend próprio | Isolado | auth + users duplicados | Bug fix em 2 lugares |
| **C)** Pacote shared_backend | Reutiliza | Zero | Refatoração grande |

### 3.3 Recomendação: Opção A (backend compartilhado) + salvaguardas

**Melhor custo-benefício:** mais segura, sem duplicar, sem complicar futuros ajustes.

**Por quê:**
- **Segurança:** O backend já tem `require_admin` em todos os endpoints admin. CORS específico (sem `*`). Autenticação JWT.
- **Sem duplicação:** Um único backend, uma única fonte de verdade. Bug em auth/users? Corrige uma vez.
- **Manutenção:** app_admin usa uma superfície pequena e estável (auth + users). Mudanças em outros domínios não afetam.
- **Deploy:** Frontends podem ser deployados separadamente (BAU em meufinup.com.br, admin em admin.meufinup.com.br). O backend é um só.

**Salvaguardas para reduzir risco:**

1. **Contrato de API documentado** – Listar os endpoints que app_admin usa. Ao alterar auth ou users, verificar impacto no admin.
2. **CORS explícito** – Já configurado: apenas origens permitidas (localhost:3001 em dev, admin.meufinup.com.br em prod).
3. **Modularidade no frontend** – Refatorar app_admin com `features/` para organização e manutenção mais fáceis (sem mexer no backend).

---

## 4. Resumo

| Item | Status | Ação |
|------|--------|------|
| Site não funcionando | Corrigido | CORS adicionado para porta 3001 |
| Modularidade (features/) | Pendente | Refatorar contas e demais telas |
| Backend | Decidido | Manter compartilhado (Opção A) |

---

## 5. Checklist de validação

**Para testar o app_admin:**

- [ ] Backend app_dev rodando (porta 8000)
- [ ] `.env` do backend com `BACKEND_CORS_ORIGINS` incluindo `localhost:3001` (ou usar default do config.py)
- [ ] app_admin: `cd app_admin/frontend && npm run dev`
- [ ] Acessar http://localhost:3001
- [ ] Login com usuário admin
- [ ] Tela de Contas carregando e listando usuários
