# Análise da Falha do Deploy – Branch feature/revisao-completa-do-app

**Data:** 21/02/2026  
**Objetivo:** Entender por que o deploy falhou e como colocar o app da branch em produção.

---

## Diagnóstico de memória (21/02/2026)

**Resposta:** O problema é mais de **processos ineficientes/duplicados** do que falta de RAM.

### Uso real na VM (8 GB total, ~7 GB usados)

| Processo | RAM (RSS) | Observação |
|----------|-----------|------------|
| **dockerd** | ~300 MB | Docker daemon – pode não ser necessário |
| **n8n** (main + webhook + worker + 2 task-runners) | **~600 MB** | Automação de workflows – fora do FinUp |
| **next-server v15.1.3** | ~158 MB | **Frontend antigo** (provavelmente atelier) |
| **next-server v16.1.1** | ~116 MB + ~91 MB | **2 instâncias** do FinUp frontend |
| **FinUp backend** (uvicorn + 4 workers multiprocessing) | **~550 MB** | 4 workers spawn – verificar necessidade |
| **containerd** | ~135 MB | Acompanha Docker |
| **atelie** (uvicorn) | ~34 MB | Outro app no mesmo servidor |

### Problemas identificados

1. **3 instâncias de Next.js** – v15 (1) + v16 (2) → ~365 MB só em frontends.
2. **n8n** – ~600 MB para automação; avaliar se é essencial nessa VM.
3. **Docker** – ~430 MB; se não houver containers em uso, pode ser desativado.
4. **FinUp backend** – 4 workers multiprocessing além do uvicorn; revisar se todos são necessários.

### Ações sugeridas (ordem de impacto)

1. **Unificar frontends** – Manter só 1 instância do FinUp (porta 3000 ou 3002).
2. **Revisar workers do backend** – `--workers 2` no uvicorn já gera 2 processos; multiprocessing interno pode estar criando mais.
3. **n8n** – Mover para outro servidor ou desativar se não for crítico.
4. **Docker** – Desativar se não estiver em uso.
5. **Swap** – Adicionar 2 GB de swap como margem de segurança.

---

## O que aconteceu (falha do deploy)

O script `deploy_branch_vm.sh` foi executado e falhou durante o **build do frontend na VM**.

### Evidência (terminal)

```
📦 Frontend - build (NODE_OPTIONS para evitar OOM)...
npm warn deprecated ...
...
bash: line 21: 1941218 Killed                  npm ci --quiet

---
exit_code: 137
elapsed_ms: 380115
```

### Interpretação

| Sinal | Significado |
|-------|-------------|
| **exit_code: 137** | 128 + 9 = processo morto por **SIGKILL** |
| **Killed** | O kernel Linux encerrou o processo |
| **1941218** | Provável uso de memória em KB (~1,9 GB) no momento do kill |

**Causa provável:** **OOM (Out of Memory)** – o OOM Killer do Linux matou o `npm ci` porque a VM ficou sem memória RAM.

---

## Por que o build falha na VM

1. **`npm ci`** instala dependências e consome bastante RAM.
2. **`npm run build`** (Next.js) também usa muita memória.
3. VPS com **1–2 GB de RAM** costumam não suportar esse fluxo.
4. Mesmo com `NODE_OPTIONS=--max-old-space-size=4096`, o `npm ci` pode ser morto antes do `npm run build`.

---

## Soluções para colocar o app da branch no site

### Opção A: Build local + upload (recomendada)

Fazer o build na sua máquina e enviar o resultado para a VM.

**Passos:**

1. **Local – build do frontend:**
   ```bash
   cd app_dev/frontend
   npm ci
   npm run build
   ```

2. **Enviar `.next` para a VM:**
   ```bash
   rsync -avz --delete app_dev/frontend/.next/ minha-vps-hostinger:/var/www/finup/app_dev/frontend/.next/
   ```

3. **Na VM – pull do código e restart:**
   ```bash
   ssh minha-vps-hostinger
   cd /var/www/finup
   git fetch origin
   git checkout feature/revisao-completa-do-app
   git pull origin feature/revisao-completa-do-app
   cd app_dev/backend && source venv/bin/activate && alembic upgrade head
   cd ..
   systemctl restart finup-backend finup-frontend
   ```

**Vantagens:** Não depende da RAM da VM para build.  
**Desvantagens:** Exige `rsync` e build local antes de cada deploy.

---

### Opção B: Script de deploy com build local

Automatizar a Opção A em um script que:

1. Faz build local.
2. Faz `rsync` do `.next`.
3. Executa via SSH: pull, migrations, restart.

---

### Opção C: Aumentar swap na VM

Criar swap temporário para o build:

```bash
# Na VM (como root ou sudo)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# Depois rodar o deploy normalmente
```

**Vantagens:** Permite rodar o build na VM.  
**Desvantagens:** Build mais lento; swap em disco é bem mais lento que RAM.

---

### Opção D: Upgrade de RAM na VM

Se a VPS tiver menos de 2 GB, considerar plano com mais RAM (ex.: 4 GB).

---

## Próximos passos sugeridos

1. Implementar **Opção A** ou **Opção B** para o próximo deploy.
2. Criar script `deploy_branch_vm_build_local.sh` que:
   - Faz build local.
   - Envia `.next` via rsync.
   - Executa pull + migrations + restart na VM.
3. Documentar o fluxo em `docs/deploy/`.

---

## Checklist para deploy com build local

- [ ] Build local passa (`npm run build`)
- [ ] `rsync` configurado (ou scp)
- [ ] SSH `minha-vps-hostinger` funcionando
- [ ] Path na VM: `/var/www/finup`
- [ ] Migrations aplicadas na VM
- [ ] `finup-backend` e `finup-frontend` reiniciados
