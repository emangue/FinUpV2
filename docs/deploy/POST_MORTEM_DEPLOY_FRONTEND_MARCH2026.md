# Post-Mortem: Deploy Frontend VM — Março 2026

**Data:** 21/03/2026  
**Duração total:** > 3 horas  
**Resultado final:** ✅ Deploy bem-sucedido após 3 root causes identificadas e corrigidas  
**Scripts usados:** `deploy_docker_vm.sh` (tentativa parcial) + `deploy_docker_build_local.sh` (deploy final)  
**Commits de fix:** `dbd9c5c4` → `ea990996` → `14f83f2f`

---

## Contexto inicial

O usuário reportou que o deploy do frontend na VM estava falhando. A mensagem inicial era genérica — o frontend não subia na VM. Não havia mensagem de erro clara ainda. O ponto de partida foi simplesmente: **"não conseguimos fazer o deploy do front na VM"**.

---

## Linha do tempo completa

### Fase 1 — Diagnóstico inicial (ambiente aparentemente OK)

Ao iniciar o diagnóstico, os primeiros comandos retornaram resultados que pareciam normais:

```bash
git branch --show-current   # → main ✅
git status --short          # → limpo ✅
git log --oneline -1        # → c405da6c ✅
```

A VM também parecia saudável:

```bash
ssh minha-vps-hostinger "cd /var/www/finup && git log --oneline -1"
# → c405da6c (mesmo commit local) ✅

ssh minha-vps-hostinger "df -h / | tail -1"
# → 166G livre ✅

docker ps | grep finup
# → todos os 5 containers rodando ✅

curl http://localhost:8000/api/health
# → {"status":"healthy","database":"connected"} ✅
```

Tudo parecia OK. O ambiente local estava funcionando. A VM estava no mesmo commit. Disco farto. Saúde do backend confirmada. **Nenhum blocker óbvio detectado.**

---

### Fase 2 — Primeiro build na VM: o erro real aparece

Com o ambiente aparentemente saudável, foi disparado o deploy via `deploy_docker_vm.sh` (build acontece diretamente na VM):

```bash
bash deploy/scripts/deploy_docker_vm.sh
```

O build do backend foi em frente, mas o **build do frontend travou** com este erro:

```
#12 [builder 7/9] RUN node node_modules/next/dist/bin/next build
#12 CACHED

...

ERROR: Cannot find module '/app/node_modules/next/dist/bin/next'
```

A primeira leitura deste erro sugeriu um problema com o `npm ci` — os módulos não estavam sendo instalados. A suspeita inicial foi:

- ❓ `node_modules` corrompido na imagem anterior (cache stale)
- ❓ `package-lock.json` inconsistente
- ❓ Incompatibilidade de versão do Node

**Tentativa 1 — Forçar rebuild sem cache:**

```bash
ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml build --no-cache frontend-app"
```

O build com `--no-cache` começou e revelou mais logs. Agora era possível ver o que estava acontecendo **antes** do erro do Next.js:

```
#8 [builder 4/9] RUN npm ci --only=production
#8 0.743 npm warn config production Use `--omit=dev` instead.
#8 1.021 npm error code EAI_AGAIN
#8 1.022 npm error errno EAI_AGAIN
#8 1.023 npm error network request to https://registry.npmjs.org/next failed, reason: getaddrinfo EAI_AGAIN registry.npmjs.org
#8 1.023 npm error network This is a problem related to network connectivity.
```

**Novo suspeito: problema de rede/DNS.** O `EAI_AGAIN` significa "DNS lookup temporariamente indisponível".

---

### Fase 3 — Investigação do DNS (confusa e demorada)

Este foi o período mais longo da investigação. O erro `EAI_AGAIN` pode ter várias causas:

- ❓ VM sem conexão com a internet
- ❓ DNS do Docker configurado errado
- ❓ Firewall bloqueando saída
- ❓ Rate limit do registry.npmjs.org
- ❓ Problema temporário de rede

**Verificação 1 — A VM tem internet?**

```bash
ssh minha-vps-hostinger "curl -s https://registry.npmjs.org/next --max-time 5 | head -c 100"
# → {"_id":"next","name":"next",...}  ✅ VM acessa normalmente
```

A VM tinha internet. O problema era **dentro do container Docker durante o build**, não na VM em si. Isso confundiu bastante, porque:

> "A VM acessa a internet, mas o container durante o build não consegue resolver DNS"

**Verificação 2 — DNS dentro de containers em runtime:**

```bash
ssh minha-vps-hostinger "docker exec finup_backend_prod nslookup registry.npmjs.org"
# → Server: 127.0.0.11 (DNS interno do Docker)
# → Address: 104.16.x.x ✅ resolve normalmente
```

Os containers **em execução** resolviam DNS. Só durante o **build** falhava. Isso era ainda mais confuso.

**Verificação 3 — Testar DNS durante build explicitamente:**

```bash
ssh minha-vps-hostinger "docker run --rm alpine nslookup registry.npmjs.org"
# → nslookup: write to '127.0.0.53': connection refused
# → connection timed out; no servers could be reached
```

**Aqui o problema ficou claro.** O container Alpine (sem rede personalizada, usando bridge padrão) não conseguia resolver DNS. O endereço `127.0.0.53` é o `systemd-resolved` do host — e ele é um endereço **loopback**, inacessível de dentro da rede bridge do Docker.

**Verificação 4 — Por que a bridge não funciona?**

```bash
ssh minha-vps-hostinger "cat /etc/docker/daemon.json"
```

```json
{
  "iptables": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Root cause #1 encontrada:** `"iptables": false`

Com `iptables` desabilitado, o Docker não consegue configurar as regras NAT necessárias para que os containers na rede bridge acessem a internet. O DNS do host (`127.0.0.53`, systemd-resolved) é um endereço loopback — funciona no host, mas é inacessível de qualquer interface de rede, incluindo a bridge Docker.

**Por que os containers em runtime funcionavam?**  
Porque eles já estavam rodando antes de `iptables: false` ser configurado, ou porque a rede prod usava configurações específicas. O build cria containers temporários em uma bridge padrão — esses containers não têm as regras NAT necessárias.

**Verificação 5 — Confirmar que `--network=host` resolve:**

```bash
ssh minha-vps-hostinger "docker run --rm --network=host alpine nslookup registry.npmjs.org"
# → Server: 127.0.0.53 (agora acessível porque está na rede do host)
# → Address: 104.16.x.x  ✅
```

Com `--network=host`, o container usa a pilha de rede do host diretamente. O `127.0.0.53` torna-se acessível.

---

### Fase 4 — Fix #1: network:host no build

A solução foi adicionar `network: host` nas seções `build:` do `docker-compose.prod.yml` para os 3 serviços:

```yaml
# docker-compose.prod.yml
backend:
  build:
    context: ./app_dev/backend
    dockerfile: Dockerfile
    network: host  # ← FIX: usa DNS do host durante o build

frontend-app:
  build:
    context: ./app_dev/frontend
    dockerfile: Dockerfile
    network: host  # ← FIX
    args:
      - NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

frontend-admin:
  build:
    context: ./app_admin/frontend
    dockerfile: Dockerfile
    network: host  # ← FIX
    args:
      - NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
```

Aproveitando o mesmo commit, foram corrigidos os **Dockerfiles dos frontends** que usavam sintaxe `ENV` legada (depreciada no Docker Engine):

```dockerfile
# ❌ Legado (depreciado, gera warning)
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
ENV PORT 3000

# ✅ Correto
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV PORT=3000
```

**Commit:** `dbd9c5c4` — `fix(deploy): corrige build Docker na VM com iptables:false`

---

### Fase 5 — Segundo build: erro no backend (pip ConnectionReset)

Com o fix do DNS aplicado, foi rodado `deploy_docker_vm.sh` novamente. O **frontend build passou**. Porém, o **build do backend falhou**:

```
Downloading opencv-python-headless-4.8.1.78-cp39-cp39-linux_x86_64.whl (60.0 MB)
     ━━━━━━━━━━━━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━ 31.5/60.0 MB 3.2 MB/s eta 0:00:09

error: subprocess-exited-with-error

pip._internal.exceptions.NetworkConnectionError: There was a problem confirming
the ssl certificate: HTTPSConnectionPool(host='files.pythonhosted.org', port=443):
Read timed out. (read timeout=15)

ConnectionResetError: [Errno 104] Connection reset by peer
```

O `pip` estava baixando o `opencv-python-headless` (60MB) e a conexão era resetada no meio do download. O timeout padrão do pip (15s) era insuficiente para um arquivo grande em uma conexão de VM com latência variável.

**Fix #2 — Adicionar `--retries 5 --timeout 120` ao pip install:**

```dockerfile
# app_dev/backend/Dockerfile
RUN pip install --no-cache-dir --retries 5 --timeout 120 -r requirements.txt && \
    pip uninstall -y opencv-python && \
    pip install --no-cache-dir --retries 5 --timeout 120 opencv-python-headless
```

**Commit:** `ea990996` — `fix(deploy): pip install com --retries 5 --timeout 120 no backend`

---

### Fase 6 — Troca de estratégia: build local + SCP

Dado que o build na VM estava sendo instável (DNS issues + timeouts de rede em downloads grandes), foi decidido usar o script alternativo `deploy_docker_build_local.sh`, que:

1. Faz o build das imagens **localmente** (macOS, conexão estável)
2. Salva as imagens como `.tar.gz`
3. Faz SCP para a VM
4. Na VM: `docker load` + `docker compose up -d`

```bash
bash deploy/scripts/deploy_docker_build_local.sh
```

Builds locais passaram sem problemas. SCP para a VM foi concluído. Containers subiram. Mas ao executar as migrations:

---

### Fase 7 — Erro Alembic: Multiple head revisions

```
FAILED: Multiple head revisions are present for given argument 'head';
please specify a target revision:
<b52feac5cd7f> (head)
<bbc24ab11c33> (head)
```

O Alembic encontrou **dois cabeças** na árvore de migrations — o que é inválido. Cada cadeia de migrations deve ter exatamente um `head`.

**Investigação:**

```bash
ls -la app_dev/backend/migrations/versions/ | grep -v __pycache__
```

```
-rw-r--r--  b52feac5cd7f_add_composite_indexes_to_journal_entries.py
-rw-r--r--  b52feac5cd7f_add_composite_indexes_to_journal_entries 2.py   ← ❗
-rw-r--r--  bbc24ab11c33_add_plano_cashflow_mes_table.py
-rw-r--r--  bbc24ab11c33_add_plano_cashflow_mes_table 2.py               ← ❗
```

**Root cause #3 encontrada:** **Arquivos duplicados criados pelo macOS**

O macOS tem o comportamento de criar cópias de arquivos com o sufixo ` 2` (com espaço) quando detecta conflito de nome em operações de arrastar/soltar, iCloud sync, ou certos comandos de cópia. Esses arquivos duplicados:

- **Não estavam no git** (eram arquivos não-rastreados locais)
- **Entravam no contexto do Docker build** via volume/SCP
- O Alembic os lia como migrations válidas com o mesmo `revision` ID, criando dois nós com o mesmo ID — o que faz o grafo de migrations ter dois `head`s

**Fix #3 — Dois passos:**

**Passo 1 — Remover os arquivos duplicados localmente:**
```bash
rm "app_dev/backend/migrations/versions/b52feac5cd7f_add_composite_indexes_to_journal_entries 2.py"
rm "app_dev/backend/migrations/versions/bbc24ab11c33_add_plano_cashflow_mes_table 2.py"
```

**Passo 2 — Adicionar padrão ao `.dockerignore` do backend** para proteger builds futuros:
```
# app_dev/backend/.dockerignore

# Duplicatas macOS (cópias acidentais com " 2.py" causam multiple heads no Alembic)
migrations/versions/* 2.py
```

**Commit:** `14f83f2f` — `fix(deploy): exclui duplicatas macOS ' 2.py' das migrations no build Docker`

---

### Fase 8 — Deploy final bem-sucedido

```bash
bash deploy/scripts/deploy_docker_build_local.sh
```

```
✅ Build backend    → OK
✅ Build frontend   → OK
✅ Build admin      → OK
✅ SCP para VM      → OK
✅ docker load      → OK
✅ containers up    → OK
✅ alembic upgrade  → bbc24ab11c33 (head)
✅ DEPLOY CONCLUÍDO!
```

**Validação final:**

```
finup_frontend_admin_prod   Up 3 minutes
finup_frontend_app_prod     Up 3 minutes (healthy)
finup_backend_prod          Up 3 minutes (healthy)
finup_postgres_prod         Up 2 weeks (healthy)
finup_redis_prod            Up 2 weeks (healthy)
---
bbc24ab11c33 (head)
---
{"status":"healthy","database":"connected"}
Frontend :3003 → 200
```

---

## Resumo dos 3 root causes

| # | Problema | Sintoma | Causa | Fix |
|---|----------|---------|-------|-----|
| 1 | DNS falha durante `docker build` | `EAI_AGAIN` no npm ci / `Cannot find module '/app/node_modules/next/dist/bin/next'` | `"iptables": false` no `daemon.json` da VM — bridge network não consegue alcançar `127.0.0.53` (systemd-resolved) | `network: host` nas seções `build:` do `docker-compose.prod.yml` |
| 2 | pip `ConnectionResetError` | Download do `opencv-python-headless` (60MB) abortado no meio | Timeout padrão de 15s do pip insuficiente para arquivo grande com latência de VM | `--retries 5 --timeout 120` no `pip install` do `Dockerfile` backend |
| 3 | Alembic `Multiple head revisions` | `alembic upgrade head` falhou com dois `head` na árvore | macOS criou cópias ` 2.py` dos arquivos de migration — não rastreadas pelo git mas incluídas no build context | Remover arquivos ` 2.py` localmente + adicionar `migrations/versions/* 2.py` ao `.dockerignore` |

---

## O que tornou o diagnóstico difícil e demorado

### 1. O erro superficial escondia o real
A mensagem `Cannot find module '/app/node_modules/next/dist/bin/next'` parecia um problema de `npm ci` ou dependência do Next.js. Só com `--no-cache` foi possível ver o `npm ci` falhando **antes** com `EAI_AGAIN`. Sem o `--no-cache`, o Docker usava cache de uma etapa anterior e pulava o `npm ci`, indo direto para o build — que falhava por ausência dos módulos.

### 2. A VM tinha internet — o container durante o build, não
Esse foi o ponto mais confuso. Um `curl` na VM funcionava. Os containers em execução resolviam DNS. Mas os containers temporários criados durante o `docker build` usavam uma bridge padrão sem as regras iptables, quebrando o NAT. Descobrir que o problema era **específico do contexto de build** (não de runtime) levou tempo.

### 3. `iptables: false` é uma configuração opaca
Essa linha no `daemon.json` foi colocada por alguma razão (provavelmente pelo provedor Hostinger ou por configuração anterior) e seu efeito não é óbvio. A documentação do Docker menciona que desabilitar iptables pode causar problemas de rede, mas a mensagem de erro (`EAI_AGAIN`) não aponta para essa causa.

### 4. O erro do Alembic apareceu só no final
Os dois primeiros problemas foram resolvidos, o deploy pareceu funcionar, e então o Alembic falhou. Esse erro aparece **após** o `docker compose up`, dentro do container backend já rodando. Passou pela fase de build inteira, SCP, load, `up -d`, e só então falhou — dando a falsa impressão de que "quase funcionou".

### 5. Arquivos ` 2.py` são invisíveis no git
Os arquivos duplicados do macOS não estavam no `.gitignore`, portanto não eram rastreados. O `git status` os mostrava como "untracked" mas como a pasta tem muitos arquivos `.py`, eles passaram despercebidos em inspeções rápidas. O `git diff` e `git log` não os mostravam porque nunca foram commitados.

---

## Lições aprendidas e ações preventivas

### A. Adicionar ao checklist de pré-deploy
```bash
# Verificar duplicatas macOS em migrations ANTES do deploy
find app_dev/backend/migrations/versions -name "* 2.py" 2>/dev/null
# Deve retornar vazio. Se não retornar → deletar antes de deploiar.
```

### B. Verificar DNS do Docker durante builds (novo check de diagnóstico)
```bash
# Na VM: testar DNS de container em bridge padrão
ssh minha-vps-hostinger "docker run --rm alpine nslookup registry.npmjs.org"
# Se falhar → network:host é necessário no build
```

### C. Documentar `daemon.json` da VM
O arquivo `/etc/docker/daemon.json` com `"iptables": false` é uma configuração crítica que afeta todos os builds Docker. Deve estar documentado em `docs/deploy/` para consulta futura.

### D. Preferir `deploy_docker_build_local.sh` para builds grandes
Com `iptables: false` na VM, `deploy_docker_vm.sh` depende do `network: host` para funcionar e é mais suscetível a timeouts de rede (problema 2). O script local elimina a variabilidade da rede da VM durante o build.

### E. Monitorar `alembic current` como parte da validação pós-deploy
O `validate_deploy.sh` deveria incluir:
```bash
docker exec finup_backend_prod alembic -c /app/alembic.ini current 2>&1 | grep "(head)"
# Deve retornar exatamente 1 linha com (head)
```

---

## Arquivos modificados nesta sessão

| Arquivo | Modificação |
|---------|-------------|
| `docker-compose.prod.yml` | `network: host` em todas as seções `build:` |
| `app_dev/frontend/Dockerfile` | Sintaxe `ENV key=value` (legacy → correto) |
| `app_admin/frontend/Dockerfile` | Idem |
| `app_dev/backend/Dockerfile` | `pip install --retries 5 --timeout 120` |
| `app_dev/backend/.dockerignore` | Padrão `migrations/versions/* 2.py` adicionado |
| `app_dev/backend/migrations/versions/` | Arquivos ` 2.py` removidos (não eram git-tracked) |

---

## Commits desta sessão

```
14f83f2f  fix(deploy): exclui duplicatas macOS ' 2.py' das migrations no build Docker
ea990996  fix(deploy): pip install com --retries 5 --timeout 120 no backend
dbd9c5c4  fix(deploy): corrige build Docker na VM com iptables:false
```
