# Scripts de Deploy

## Deploy padrão (build local)

```bash
./scripts/deploy/deploy_docker_build_local.sh
```

Build das imagens **localmente** (evita OOM na VM), envia via SCP, sobe os containers. É o fluxo recomendado.

## Deploy alternativo (build na VM)

```bash
./scripts/deploy/deploy_docker_vm.sh
# Com rebuild completo:
./scripts/deploy/deploy_docker_vm.sh --no-cache
# Sem rebuild (só restart):
./scripts/deploy/deploy_docker_vm.sh --skip-build
```

Use quando a VM tiver RAM disponível (15 GB). Inclui rollback automático se o deploy falhar.

## Validação pós-deploy

```bash
./scripts/deploy/validate_deploy.sh
```

## Pré-requisitos

1. `git status -uno` limpo
2. `git push origin <branch>` feito
3. SSH `minha-vps-hostinger` configurado

## Documentação

- [GUIA_DEPLOY.md](../../docs/deploy/GUIA_DEPLOY.md) — Fluxo completo, containers em produção, migrations, rollback
- [TROUBLESHOOTING.md](../../docs/deploy/TROUBLESHOOTING.md) — Erros comuns e soluções
