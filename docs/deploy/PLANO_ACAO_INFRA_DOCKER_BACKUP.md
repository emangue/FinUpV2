# Plano de Ação: Infraestrutura (Docker + Backup Off-site)

**Plano de ação central (Git + Docker + Backup):** [PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md](PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md)

**Data:** 20/02/2026  
**Origem:** Conversa com Gemini sobre múltiplos projetos na mesma VM, isolamento e backup.  
**Objetivo:** Organizar deploy (opcional Docker) e garantir backup dos dados **fora do servidor** (regra 3-2-1).

---

## Resumo da conversa (Gemini)

1. **Problema:** Vários projetos na mesma VM “no metal” → risco de “inferno de dependências”.
2. **Solução recomendada:** Isolamento com **Docker** + **Nginx como proxy reverso** (que você já tem).
3. **Backup:** Regra **3-2-1**: 3 cópias, 2 mídias, 1 cópia off-site. Melhores opções: Object Storage (S3/R2), snapshots do provedor, scripts de dump + envio (rclone, restic, cron).
4. **Custo Docker:** Zero (Docker CE gratuito); impacto em RAM baixo.

---

## Situação atual do projeto (FinUp / ProjetoFinancasV5)

| Aspecto | Situação |
|--------|----------|
| **Nginx** | Já em uso no servidor (proxy reverso). |
| **Docker** | Não utilizado (deploy via git + venv + systemd). |
| **Backup** | `scripts/deploy/backup_daily.sh`: copia o banco para `backups_daily/` **no mesmo disco** (local ou servidor). **Nenhum envio off-site.** |
| **Produção** | VPS (148.230.78.91), PostgreSQL em produção; SQLite em dev local. |
| **Outros deploys na VPS** | Vários (Easypanel, financas, financas_completo) – ver `docs/deploy/AUDITORIA_SERVIDOR_VPS.md`. |

Conclusão: o ganho imediato e de maior impacto é **backup off-site**. Docker é opcional e pode vir depois.

---

## Visão geral do plano

- **Fase 1 – Backup off-site (prioridade alta)**  
  Garantir que dados (DB + uploads críticos) tenham cópia fora do servidor, automatizada.

- **Fase 2 – Docker (opcional, depois)**  
  Se quiser isolamento entre projetos na mesma VM, introduzir Docker mantendo o Nginx como “porteiro”.

---

## Fase 1 – Backup off-site (recomendado fazer primeiro)

### Objetivo
Cumprir a regra 3-2-1: pelo menos **1 cópia fora do servidor** (e idealmente em outra mídia/serviço).

### Opções (da mais simples à mais robusta)

| Opção | Ferramenta | Destino | Custo | Esforço |
|-------|------------|---------|--------|---------|
| **A** | Script cron + `pg_dump` + **rclone** | Google Drive, S3, Cloudflare R2, Dropbox | Baixo (centavos/GB ou free tier) | Médio (1–2 dias) |
| **B** | **Snapshots** do provedor (Hostinger/VPS) | Mesmo provedor, outra região se disponível | Incluso ou barato | Baixo |
| **C** | **Restic** ou **Borg** | Servidor remoto ou S3/R2 | Baixo | Médio (criptografia + deduplicação) |

**Destino definido:** Google Drive (rclone). Recomendação: script com `pg_dump` + gzip + rclone copy/sync para uma pasta no Drive (ex.: `finup-backups/`).

### Tarefas concretas – Fase 1

1. **Definir destino off-site**
   - [ ] Escolher: Google Drive, AWS S3, Cloudflare R2 ou outro (ex.: Backblaze B2).
   - [ ] Criar bucket/conta e obter credenciais (nunca commitar; usar `.env` no servidor).

2. **Backup do banco (produção = PostgreSQL)**
   - [ ] Script no servidor: `pg_dump` (ou `pg_dumpall` se quiser todos os DBs) → arquivo `.sql` ou `.dump`.
   - [ ] Compactar (gzip) e opcionalmente criptografar (ex.: `gpg` ou restic).
   - [ ] Enviar para o destino off-site (rclone ou CLI do provedor).
   - [ ] Agendar via **cron** (ex.: diário 3h da manhã).

3. **Backup de arquivos críticos (se houver)**
   - [ ] Identificar pastas importantes (ex.: uploads, anexos, configs não versionados).
   - [ ] Incluir no mesmo script ou em script separado com rclone/restic.

4. **Documentar**
   - [ ] Onde está o script de backup off-site (path no servidor).
   - [ ] Onde estão as credenciais (`.env`, variáveis).
   - [ ] Como restaurar (passo a passo em `docs/deploy/` ou em README do script).
   - [ ] Atualizar `scripts/deploy/backup_daily.sh` ou criar `scripts/deploy/backup_offsite.sh` e referenciar no `safe_deploy`/documentação.

5. **Regra 3-2-1 (opcional mas recomendado)**
   - [ ] Cópia 1: servidor (backup local/diário atual).
   - [ ] Cópia 2: off-site (nuvem ou outro servidor).
   - [ ] Cópia 3: outro provedor ou outra mídia (ex.: segundo bucket ou snapshot em outro lugar).

---

## Fase 2 – Docker (opcional, depois do backup)

### Objetivo
Isolar aplicações na mesma VM (evitar conflito de Node/Python/libs) mantendo o Nginx como proxy reverso.

### Benefícios
- Isolamento de dependências (ex.: um app em Node 14, outro em Node 20).
- Deploy reproduzível: `docker-compose up` em outra máquina.
- Menos conflito de portas (rede interna do Docker).

### O que NÃO muda
- Nginx continua na máquina host como “porteiro”.
- Só muda o `proxy_pass`: em vez de `localhost:8000` (processo no host), aponta para a porta do container (ex.: `finup-backend:8000` ou porta mapeada).

### Tarefas concretas – Fase 2 (quando decidir fazer)

1. **Preparação**
   - [ ] Instalar Docker Engine + Docker Compose no servidor (gratuito).
   - [ ] Definir estrutura: ex. `/opt/apps/finup/` com código, `Dockerfile` e `docker-compose.yml`.

2. **Containerizar**
   - [ ] `Dockerfile` para o backend (FastAPI/Python).
   - [ ] `Dockerfile` para o frontend (Next.js) ou servir build estático via Nginx.
   - [ ] `docker-compose.yml`: backend, frontend (se aplicável), e uso do PostgreSQL (host ou container).
   - [ ] Variáveis de ambiente em `.env` (nunca no repositório).

3. **Nginx**
   - [ ] Ajustar `proxy_pass` para as portas dos containers (ou rede Docker).
   - [ ] Manter SSL/certificados no host (Nginx).

4. **Migração**
   - [ ] Testar em staging ou em outra pasta antes de desligar o deploy “no metal”.
   - [ ] Documentar em `docs/deploy/` (ex.: `DEPLOY_DOCKER.md`).

---

## Ordem sugerida

1. **Agora:** Fase 1 – Backup off-site (script dump + rclone + cron + documentação).
2. **Depois:** Manter `backup_daily.sh` para backup local e como parte da rotina (ex.: antes de deploy).
3. **Opcional:** Fase 2 – Docker quando quiser consolidar vários projetos na mesma VM com isolamento.

---

## Referências no repositório

- Backup atual: `scripts/deploy/backup_daily.sh` (apenas local/same disk).
- Deploy seguro: `scripts/deploy/safe_deploy.sh` (chama backup antes de deploy).
- Servidor: `docs/deploy/AUDITORIA_SERVIDOR_VPS.md`, `.cursorrules` (path `/var/www/finup`, PostgreSQL).
- Segurança: `docs/deploy/PLANO_ACAO_SEGURANCA.md`.

---

## Próximo passo imediato

Escolher **destino off-site** (Google Drive, S3, R2, etc.) e então:

- Criar um script `backup_offsite.sh` (ou equivalente) que:
  1. Roda `pg_dump` no PostgreSQL de produção.
  2. Compacta o dump.
  3. Envia com rclone (ou CLI do provedor) para o destino.
- Agendar no cron do servidor.
- Documentar o processo e a restauração em `docs/deploy/`.

Se quiser, no próximo passo podemos escrever o esboço do `backup_offsite.sh` e o exemplo de cron para o seu ambiente (Hostinger/VPS + PostgreSQL).
