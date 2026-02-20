# Plano de Ação – Implantação (Git + Docker + Backup)

**Data:** 20/02/2026  
**Objetivo:** Centralizar o que é necessário fazer para Git, infraestrutura (Docker) e backup, em ordem de implantação.

---

## Visão geral

| Área | Situação atual | O que fazer |
|------|----------------|--------------|
| **Git** | Main atrás do remoto; branch padrão GitHub ≠ main; .gitignore permite trackear .db; deploy às vezes direto na main | Alinhar main, remover exceção do .db, regra “branch antes de subir; merge na main só após validar no servidor” (já no safe_deploy.sh) |
| **Backup** | Só local (backups_daily no mesmo disco); nada off-site | Backup off-site (pg_dump + rclone/cron); regra 3-2-1 |
| **Docker** | Não usado; deploy via git + venv + systemd | Opcional: 1 Docker por produto (FinUp = app_dev+app_admin; Ateliê = outro); Nginx continua como proxy |

A ordem abaixo é a recomendada para implantar.

---

## Fase 1 – Git (ajustes imediatos)

**Objetivo:** Repositório consistente com “main = porto seguro” e rollback sem cópia manual da pasta.

### 1.1 Regra de deploy (já implementada)

- [x] **Alteração grande:** criar branch antes de subir no servidor; merge na main só após validar no servidor.
- [x] `safe_deploy.sh` oferece criar branch (ex.: `deploy/YYYY-MM-DD-nome`) quando você está na main.
- [ ] **Prática:** usar sempre que for deploy com mudança grande: rodar safe_deploy, criar a branch quando perguntado, subir essa branch no servidor, validar e só então fazer merge na main.

### 1.2 Ajustes no repositório

| # | Tarefa | Ação |
|---|--------|------|
| 1 | Branch padrão no GitHub | Em Settings → Repositories → Default branch, definir **main** (se main for o porto seguro). |
| 2 | Banco fora do Git | Remover do `.gitignore` da raiz a linha `!app_dev/backend/database/financas_dev.db`. Manter o banco sempre ignorado (ex.: `*.db` em app_dev/.gitignore). |
| 3 | Sincronizar main local | Se tiver trabalho em andamento: criar branch (ex.: `wip/meu-trabalho`), commitar lá, depois `git checkout main` e `git pull origin main`. |

### 1.3 Checklist rápido – antes de cada deploy grande

- [ ] Criei branch (deploy/ ou feature/) antes de subir?
- [ ] No servidor dei pull **dessa branch** e validei?
- [ ] Só depois de validar: merge na main e push da main?

*Detalhes e exemplos: [VALIDACAO_GIT_20FEV2026.md](VALIDACAO_GIT_20FEV2026.md).*

---

## Fase 2 – Backup off-site (prioridade alta)

**Objetivo:** Pelo menos 1 cópia dos dados **fora do servidor** (regra 3-2-1).  
**Escopo:** Backup **apenas da base de dados** (PostgreSQL). Arquivos (uploads, etc.) ficam de fora; se no futuro quiser incluir, pode ser um passo adicional.

### 2.1 Decisão

| # | Tarefa | Status |
|---|--------|--------|
| 1 | Destino off-site | [x] **Google Drive** (definido) |
| 2 | Configurar acesso ao Google Drive (rclone ou API) e credenciais | [ ] (guardar em .env no servidor; nunca no git) |

### 2.2 Implementação

| # | Tarefa | Status |
|---|--------|--------|
| 1 | Script no servidor: `pg_dump` → arquivo .sql/.dump | [ ] |
| 2 | Compactar (gzip) e enviar ao Google Drive (rclone configurado para "gdrive") | [ ] |
| 3 | Agendar no cron (ex.: diário 3h) | [ ] |
| 4 | Documentar: path do script, credenciais, como restaurar | [ ] |
| 5 | Criar/atualizar `backup_offsite.sh` e referenciar em docs/safe_deploy | [ ] |

### 2.3 Regra 3-2-1 (recomendado)

- [ ] Cópia 1: servidor (backup local/diário atual).
- [ ] Cópia 2: off-site (nuvem).
- [ ] Cópia 3: outra mídia/provedor (ex.: segundo bucket ou snapshot).

**Google Drive:** usar `rclone` (rclone config → escolher "Google Drive" e seguir o fluxo de autenticação OAuth). O script de backup fará `pg_dump`, gzip e `rclone copy` (ou `rclone sync`) para um remoto tipo `gdrive:finup-backups/` (ou pasta de sua escolha).

*Detalhes: [PLANO_ACAO_INFRA_DOCKER_BACKUP.md](PLANO_ACAO_INFRA_DOCKER_BACKUP.md) (Fase 1).*

---

## Fase 3 – Docker (opcional, depois do backup)

**Objetivo:** Um Docker por produto; Nginx no host como proxy. **Não** um Docker por “front” e outro por “back”.

### 3.1 Visão por produto

- **FinUp (app_dev + app_admin):** um único `docker-compose` com 3 serviços: backend, frontend BAU, frontend admin. Um branch/compose = um produto.
- **App Ateliê:** outro produto = outro Docker (outro compose), com front e back como serviços desse mesmo compose.

### 3.2 Tarefas (quando for fazer)

| # | Tarefa | Status |
|---|--------|--------|
| 1 | Instalar Docker Engine + Docker Compose no servidor | [ ] |
| 2 | Definir estrutura (ex.: `/opt/apps/finup/` com código + Dockerfile + compose) | [ ] |
| 3 | Dockerfile backend (FastAPI) | [ ] |
| 4 | Dockerfile frontend BAU (Next.js) | [ ] |
| 5 | Dockerfile frontend admin (Next.js) | [ ] |
| 6 | docker-compose.yml: backend, frontend, admin (+ Postgres no host ou no compose) | [ ] |
| 7 | Ajustar Nginx: proxy_pass para portas dos containers | [ ] |
| 8 | Testar em staging; documentar em docs/deploy (ex.: DEPLOY_DOCKER.md) | [ ] |

*Detalhes e análise por bloco: [PLANO_ACAO_INFRA_DOCKER_BACKUP.md](PLANO_ACAO_INFRA_DOCKER_BACKUP.md) (Fase 2).*

---

## Ordem de implantação sugerida

1. **Fase 1 – Git** (hoje): ajustes .gitignore e branch padrão; usar a regra de branch no safe_deploy em todo deploy grande.
2. **Fase 2 – Backup off-site** (próximos dias): destino, script, cron, documentação.
3. **Fase 3 – Docker** (quando quiser isolamento): um compose por produto; Nginx continua no host.

---

## Referências

| Documento | Conteúdo |
|-----------|----------|
| [VALIDACAO_GIT_20FEV2026.md](VALIDACAO_GIT_20FEV2026.md) | Estado do Git, riscos, sincronizar main, exemplo com projeto Plano Aposentadoria. |
| [PLANO_ACAO_INFRA_DOCKER_BACKUP.md](PLANO_ACAO_INFRA_DOCKER_BACKUP.md) | Backup off-site (detalhado), Docker por produto, tarefas e referências. |
| [safe_deploy.sh](../../scripts/deploy/safe_deploy.sh) | Validações e oferta de criar branch de deploy antes de subir. |
| [.cursorrules](../../.cursorrules) / [.github/copilot-instructions.md](../../.github/copilot-instructions.md) | Regras de deploy e branch já incorporadas. |

---

## Resumo em uma frase

**Git:** branch antes de subir no servidor, merge na main só após validar; **Backup:** uma cópia off-site automatizada; **Docker:** um compose por produto (FinUp, Ateliê), quando quiser isolamento.
