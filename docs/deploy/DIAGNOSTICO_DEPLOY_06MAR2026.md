# Diagnóstico: Falha no Deploy Docker (06/03/2026)

## O que estamos tentando fazer

**Deploy completo** da branch `perf/performance-v2-n0-n4` via `deploy_docker_vm.sh`:
1. Git pull na VM
2. **Rebuild** das imagens Docker (backend, frontend-app, frontend-admin)
3. `docker compose up -d`
4. Migrations Alembic

---

## Por que funcionou "hoje cedo"?

**Não foi deploy — foi restauração.** O documento `STATUS_RESTAURACAO_VM.md` descreve:

- **Ação:** Matar processos do Ateliê + `docker restart` dos containers
- **Resultado:** "Restart simples resolveu"
- **Nenhum rebuild** foi feito

Os containers estavam rodando desde **26/02/2026** (imagem `b07fee3eb873`). A restauração apenas reiniciou containers já construídos.

---

## Por que falha agora?

Ao fazer **deploy com código novo**, o script tenta **rebuild** das imagens. O build do `frontend-app` falha na etapa de build do Next.js.

### Erros observados (em sequência de tentativas)

| Tentativa | Comando                    | Erro |
|-----------|----------------------------|------|
| 1         | `npm run build`            | `sh: next: not found` |
| 2         | `npx next build`          | `EAI_AGAIN` (npx tenta baixar do registry, rede falha) |
| 3         | `./node_modules/.bin/next build` | `./node_modules/.bin/next: not found` |

### Causa raiz

1. **Cache Docker corrompido ou incompleto**  
   A camada `RUN npm install --frozen-lockfile` pode estar em cache de um build anterior onde a instalação falhou ou ficou incompleta. O `node_modules/.bin/next` não existe nessa camada.

2. **Diferença entre app_dev e app_admin**  
   O `app_admin/frontend/Dockerfile` usa:
   - `npm ci` (instalação limpa, mais previsível)
   - `npm run build` (usa PATH do npm com `node_modules/.bin`)

   O `app_dev/frontend/Dockerfile` usava:
   - `npm install --frozen-lockfile` (comportamento diferente do `npm ci`)
   - Caminhos diretos para o binário (que não existiam no cache)

3. **Rede instável na VM**  
   O `EAI_AGAIN` indica falha de DNS/rede ao acessar `registry.npmjs.org`. O build deve funcionar sem rede após o `npm install`/`npm ci`.

---

## Solução aplicada

Alinhar `app_dev/frontend/Dockerfile` com `app_admin/frontend/Dockerfile`:

- Trocar `npm install --frozen-lockfile` por `npm ci`
- Usar `npm run build` (padrão, confiável)

O `npm ci`:
- Remove `node_modules` antes de instalar
- Usa exatamente o `package-lock.json`
- É o comando recomendado para CI/Docker

---

## Validação

Após a correção:

```bash
# Build local (teste)
cd app_dev/frontend && docker build -t test-frontend .

# Deploy na VM
./scripts/deploy/deploy_docker_vm.sh
```

Se ainda falhar por cache, forçar rebuild sem cache:

```bash
ssh minha-vps-hostinger "cd /var/www/finup && docker compose -f docker-compose.prod.yml build --no-cache frontend-app"
```
