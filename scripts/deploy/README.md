# Scripts de Deploy

## Deploy padrão

```bash
./scripts/deploy/deploy.sh
```

Build na VM, restart frontend na porta 3003. Use quando a VM tiver RAM suficiente (8GB+).

## Deploy com build local (alternativa OOM)

```bash
./scripts/deploy/deploy_build_local.sh
```

Build local + envio do `.next` via tar. Use quando `deploy.sh` falhar por OOM.

## Pré-requisitos

1. `git status -uno` limpo
2. `git push origin <branch>` feito
3. Não existe `app_dev/frontend/src/middleware.ts` (apenas `proxy.ts`)
4. SSH `minha-vps-hostinger` configurado

## Documentação

- [DEPLOY_PROCESSO_CONSOLIDADO.md](../../docs/deploy/DEPLOY_PROCESSO_CONSOLIDADO.md) – Processo completo e erros comuns
