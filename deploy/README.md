# 🚀 FinUp Deploy — Central de Deploy

> **Fonte única de verdade** para tudo relacionado a pré-deploy, deploy e validação.

---

## 📂 Estrutura

```
deploy/
├── README.md                         ← este arquivo (guia mestre)
├── scripts/
│   ├── predeploy.sh                  ← 🔑 RODAR ANTES DE TODO DEPLOY
│   ├── predeploy.py                  ← lógica do checklist automatizado
│   ├── deploy_docker_build_local.sh  ← 🔑 DEPLOY PRINCIPAL
│   ├── deploy_docker_vm.sh           ← deploy alternativo (build na VM)
│   └── validate_deploy.sh            ← validação pós-deploy na produção
├── validations/
│   └── ui_tests.py                   ← testes de UI automatizados (Playwright)
├── docs/
│   ├── GUIA_DEPLOY.md                ← fluxo detalhado de deploy
│   └── TROUBLESHOOTING.md            ← soluções para problemas comuns
└── history/
    ├── screenshots/                  ← capturas de falhas do Playwright
    └── TEST_PRE_DEPLOY_*.md          ← histórico de checklists (gerado automaticamente)
```

---

## 🔄 Fluxo de Deploy (Resumo)

```
1. Código commitado + push
       ↓
2. ./deploy/scripts/predeploy.sh          ← validação completa (~2 min)
       ↓
3. Resultado ok? (0 falhas)
       ↓ sim                          ↓ não
4. ./deploy/scripts/deploy_docker_build_local.sh    Investigar falhas
       ↓
5. ./deploy/scripts/validate_deploy.sh    ← smoke test em produção
```

---

## ⚡ Comandos Rápidos

### Pré-deploy (obrigatório antes de todo deploy)
```bash
./deploy/scripts/predeploy.sh
```
Gera automaticamente um relatório em `deploy/history/TEST_PRE_DEPLOY_YYYY-MM-DD_[commit].md`.

### Deploy para produção (build local → SCP → VM)
```bash
./deploy/scripts/deploy_docker_build_local.sh
```
> Use quando a VM não tem RAM suficiente para o build Next.js.

### Deploy alternativo (build na VM)
```bash
./deploy/scripts/deploy_docker_vm.sh
```

### Validar deploy em produção
```bash
./deploy/scripts/validate_deploy.sh
```

### Testes de UI somente (Playwright — headless)
```bash
source app_dev/venv/bin/activate
python3 deploy/validations/ui_tests.py
```

### Testes de UI com janela visível (debug)
```bash
source app_dev/venv/bin/activate
python3 deploy/validations/ui_tests.py --headed
```

---

## 📋 O que o predeploy.sh verifica

| Categoria | Qtde | O que checa |
|-----------|------|-------------|
| 🔒 Bloqueantes | 4 | Docker (5 containers), health, login JWT, git status |
| 🔌 API Smoke | 11 | Endpoints principais do backend |
| 🗄️ Banco | 7 | Contagem de rows nas tabelas críticas |
| 🖥️ UI (Playwright) | 13 | Login, dashboard modos, transações, budget, investimentos, upload, logout |
| 📋 Manuais | ~15 | Checklist no markdown para validação humana |

### Saída gerada
Arquivo: `deploy/history/TEST_PRE_DEPLOY_YYYY-MM-DD_[commit8].md`

---

## 🖥️ Testes de UI — Cobertura

| ID | Tela | O que valida |
|----|------|--------------|
| UI-01 | Login | Inputs de email/senha renderizam |
| UI-02 | Login | Login bem-sucedido → redirect |
| UI-03 | Dashboard | Conteúdo carrega |
| UI-04 | Dashboard | Botão "Mês" visível |
| UI-05 | Dashboard | Botão "YTD" clicável |
| UI-06 | Dashboard Mobile | Toggle Mês/YTD/Ano Completo funciona |
| UI-07 | Transações | Tabela visível |
| UI-08 | Budget | Página carrega |
| UI-09 | Investimentos | Página carrega |
| UI-10 | Simulador | Página carrega |
| UI-11 | Upload | Zona de upload visível |
| UI-12 | Settings | Página carrega |
| UI-13 | Logout | Redirecionamento para login |

---

## 🔐 Credenciais Locais

Armazenadas em `.env.local` (gitignored):
```
ADMIN_EMAIL=admin@financas.com
ADMIN_PASSWORD=<senha>
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```
O `predeploy.sh` carrega automaticamente este arquivo.

---

## 🐳 Ambiente de Desenvolvimento

**Iniciar:** `./scripts/deploy/quick_start_docker.sh`  
**Parar:** `./scripts/deploy/quick_stop_docker.sh`

| Serviço | URL local |
|---------|-----------|
| Frontend App | http://localhost:3000 |
| Frontend Admin | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/health |

---

## 📚 Documentação

- [Guia detalhado de deploy](docs/GUIA_DEPLOY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Arquitetura Docker](../docs/docker/GUIA_DESENVOLVIMENTO.md)
- [SSH e acesso ao servidor](../docs/deploy/SSH_ACCESS.md)

---

## 🔒 Regras de Deploy (NUNCA pular)

1. **Sempre rodar `predeploy.sh` antes de fazer deploy**
2. **0 falhas bloqueantes** antes de prosseguir
3. **Commit limpo** (`git status` sem arquivos modificados)
4. **Nunca editar código direto no servidor** (sempre: local → git → servidor)
5. **Migrations via Alembic** (`docker exec finup_backend_dev alembic upgrade head`)
6. **Em alteração grande: criar branch** antes de subir; merge na main só após validar

---

*Atualizado automaticamente. Fonte: `.github/copilot-instructions.md` seção Deploy.*
