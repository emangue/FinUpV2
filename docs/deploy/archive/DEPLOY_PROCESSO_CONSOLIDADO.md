# Processo de Deploy Consolidado

**Data:** 21/02/2026  
**Objetivo:** Deploy direto e eficiente, com correções para os erros recorrentes.

---

## Erros encontrados (e correções)

| Erro | Causa | Correção |
|------|-------|----------|
| **OOM no build** | VM com pouca RAM | Aumentar RAM ou usar build local |
| **rsync falha** | Conexão cai durante transferência | Usar tar+ssh (mais leve) |
| **systemctl Permission denied** | Provedor restringe systemctl | Usar pkill + nohup para restart |
| **Porta 3000 ocupada** | Easypanel usa 3000 | FinUp na porta 3003 |
| **Git: bad object refs/heads/main 2** | Refs corrompidos (arquivos com espaço) | Remover `.git/refs/heads/main 2` etc. |
| **Git: HEAD não existe** | Arquivo HEAD ausente | Restaurar de `HEAD 2` ou criar |
| **Git: origin não configurado** | Remote perdido | `git remote add origin https://github.com/emangue/FinUpV2.git` |
| **Build: middleware e proxy** | Ambos presentes | Manter só `proxy.ts`, remover `middleware.ts` |

---

## Configuração atual do servidor (VPS)

| Porta | Serviço | Domínio |
|-------|---------|---------|
| 3000 | Easypanel | - |
| 3001 | Ateliê frontend | - |
| 3002 | FinUp app_admin | admin.meufinup.com.br |
| **3003** | **FinUp app_dev** | **meufinup.com.br** |
| 8000 | FinUp backend | /api/ |

**Nginx:** `/etc/nginx/sites-enabled/finup` → `proxy_pass http://127.0.0.1:3003` para meufinup.com.br

**Restart:** systemctl não funciona. Usar `pkill` + `nohup` para reiniciar processos.

---

## Fluxo de deploy (único)

```
1. Pré-requisitos (local)
   ├── Git limpo (commit + push)
   ├── Sem middleware.ts (só proxy.ts)
   └── Build local passa (opcional, validação)

2. Na VM (via SSH)
   ├── Backup PostgreSQL (opcional)
   ├── git pull
   ├── alembic upgrade head
   ├── npm ci + npm run build (ou receber .next via tar)
   └── Restart frontend (pkill + nohup na 3003)

3. Validação
   └── curl https://meufinup.com.br (ou /api/health)
```

---

## Scripts de deploy

| Script | Quando usar |
|--------|-------------|
| **`deploy.sh`** | Padrão – build na VM (requer RAM suficiente) |
| **`deploy_build_local.sh`** | Quando OOM no build – build local + tar para VM |
| **`deploy_branch_vm.sh`** | Legado – mesmo que deploy.sh |

O `deploy.sh`:
- Valida git (com fallback se remote/refs tiverem problema)
- Tenta build na VM; se OOM, sugere build local
- Restart via pkill+nohup (não systemctl)
- Usa porta 3003 para frontend

---

## Checklist pré-deploy (evitar erros)

- [ ] `git status -uno` limpo
- [ ] `git push origin <branch>` feito
- [ ] Não existe `src/middleware.ts` (apenas `src/proxy.ts`)
- [ ] `npm run build` passa localmente (opcional)
- [ ] SSH `minha-vps-hostinger` funciona
- [ ] Backup do banco (se migrations novas)

---

## Correções rápidas (Git)

```bash
# HEAD ausente
echo "ref: refs/heads/feature/revisao-completa-do-app" > .git/HEAD

# Refs corrompidos (main 2, main 3)
rm -f ".git/refs/heads/main 2" ".git/refs/heads/main 3"

# Remote origin ausente
git remote add origin https://github.com/emangue/FinUpV2.git
```

## Comandos manuais (se o script falhar)

```bash
# Restart frontend na 3003
ssh minha-vps-hostinger "pkill -f 'next start -p 3003' 2>/dev/null; sleep 2; cd /var/www/finup/app_dev/frontend && sudo -u deploy nohup npm run start -- -p 3003 > /tmp/finup-frontend.log 2>&1 &"

# Verificar se subiu
ssh minha-vps-hostinger "tail -5 /tmp/finup-frontend.log; ss -tlnp | grep 3003"
```

---

## Referências

- [ANALISE_FALHA_DEPLOY_21FEV2026.md](ANALISE_FALHA_DEPLOY_21FEV2026.md) – OOM e diagnóstico
- [DIAGNOSTICO_BLANK_PAGE_21FEV2026.md](DIAGNOSTICO_BLANK_PAGE_21FEV2026.md) – Porta 3003
- [OPORTUNIDADES_OTIMIZACAO_MEMORIA.md](OPORTUNIDADES_OTIMIZACAO_MEMORIA.md) – Otimizações
