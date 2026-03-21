# Deploy & Performance Evaluation — 07/03/2026

Avaliação completa realizada em sessão interativa com acesso direto à VM.

## Documentos

| Arquivo | Conteúdo |
|---------|----------|
| [01_AVALIACAO_DEPLOY.md](./01_AVALIACAO_DEPLOY.md) | Por que o deploy não avançava, estado atual, plano de ação |
| [02_VM_ARCHITECTURE_MAP.md](./02_VM_ARCHITECTURE_MAP.md) | Mapeamento completo da VM: 3 apps, containers, portas, imagens |
| [03_PERFORMANCE_SLOWNESS_ANALYSIS.md](./03_PERFORMANCE_SLOWNESS_ANALYSIS.md) | Causa raiz da lentidão no app (cache stampede + N3 pendente) |

## Principais descobertas

### Deploy
- Script ativo: `deploy_docker_build_local.sh` com `docker-compose.prod.yml`
- 46 scripts de deploy → manter apenas 3
- `docker-compose.vm.yml` obsoleto (remover)

### VM
- 3 apps na mesma VM: FinUp (Docker), Ateliê Gestão (host process), Infra Nginx (Docker)
- `infra_nginx` é o único nginx ativo (portas 80/443)
- 2 instâncias de Postgres: uma em container (FinUp), uma no host (Ateliê)
- ~3 GB de imagens Docker ociosas (GHCR + Easypanel + Traefik)

### Performance
- **Causa confirmada:** cache stampede em `dashboard-api.ts` — requests duplicados provados pelos logs nginx
- **Causa adicional:** N3 não implementado (auth e lastMonth em sequência)
- A VM estar em São Paulo elimina RTT como hipótese — o problema é código

## Status de implementação

| Doc | Conteúdo |
|-----|----------|
| [06_STATUS_IMPLEMENTACAO.md](./06_STATUS_IMPLEMENTACAO.md) | Status N1–N4, latências medidas, análise de prefetch dos outros dados |

## Próximas ações

- [x] Fix cache stampede + _inflight (N1/N2)
- [x] N3: prefetch lastMonth antes do auth
- [x] N4: sliding window + prefetch de vizinhos — commit `4db0ca5a`
- [ ] Adicionar cache a `fetchOrcamentoInvestimentos` (único sem cache)
- [ ] Investigar `goals-api` (404 em produção, sem cache)
- [ ] Deploy N4 na VM
