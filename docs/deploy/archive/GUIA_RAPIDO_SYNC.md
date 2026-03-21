# 🚀 Guia Rápido: Sincronização Local → VM

**Criado em:** 06/03/2026  
**Objetivo:** Alinhar VM (produção) com versão local (verdade)

---

## ⚡ EXECUÇÃO RÁPIDA

### Opção 1: Script Automatizado (RECOMENDADO)

```bash
# P0 - Crítico (executar AGORA)
./scripts/deploy/sync_vm_with_local.sh

# P1 - Limpeza (executar em até 24h)
./scripts/deploy/cleanup_vm_tables.sh
```

### Opção 2: Comandos Manuais

```bash
# 1. Backup
ssh minha-vps-hostinger "mkdir -p /tmp/backups_finup"
ssh minha-vps-hostinger "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db > /tmp/backups_finup/backup_$(date +%Y%m%d_%H%M%S).sql"

# 2. Aplicar migrations
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"

# 3. Restart containers (ordem)
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart postgres redis backend frontend-app nginx"

# 4. Validar
ssh minha-vps-hostinger "docker ps"
ssh minha-vps-hostinger "curl -s http://localhost/api/health"

# 5. Matar processos Ateliê
ssh minha-vps-hostinger "pkill -f '/var/www/atelie'"
```

---

## 📊 DIVERGÊNCIAS DETECTADAS

| Item | Local | VM | Ação |
|------|-------|-----|------|
| **Alembic** | f1200dd073a8 | 833cabc081aa | ⚠️ Aplicar 11 migrations |
| **Tabelas** | 28 | 40+ | ⚠️ Remover 12+ órfãs |
| **Containers** | 1 healthy | 3 unhealthy | ⚠️ Restart |
| **Processos Ateliê** | 0 | 5+ | ⚠️ Matar |

---

## 🚨 CHECKLIST PRÉ-EXECUÇÃO

- [ ] Git local limpo (`git status`)
- [ ] Backup criado antes de aplicar
- [ ] Downtime comunicado (2-5 min)
- [ ] SSH conectando (`ssh minha-vps-hostinger "echo OK"`)

---

## ✅ VALIDAÇÃO PÓS-EXECUÇÃO

```bash
# 1. Verificar versão Alembic
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic current"
# Esperado: f1200dd073a8

# 2. Verificar containers
ssh minha-vps-hostinger "docker ps"
# Esperado: todos "healthy" ou "Up" (sem unhealthy)

# 3. Verificar health
ssh minha-vps-hostinger "curl -s http://localhost/api/health"
# Esperado: {"status":"healthy","database":"connected"}

# 4. Verificar processos Ateliê
ssh minha-vps-hostinger "ps aux | grep -E '/var/www/atelie' | grep -v grep"
# Esperado: vazio (nenhum processo)

# 5. Verificar tabelas
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = '"'"'public'"'"'"'
# Esperado: 28 (após limpeza P1) ou 40 (antes)
```

---

## 🔄 ROLLBACK (se necessário)

```bash
# 1. Restaurar backup
ssh minha-vps-hostinger "docker exec -i finup_postgres_prod psql -U finup_user -d finup_db < /tmp/backups_finup/backup_YYYYMMDD_HHMMSS.sql"

# 2. Downgrade alembic
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic downgrade 833cabc081aa"

# 3. Restart
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart backend"
```

---

## 📝 LOGS E DEBUG

```bash
# Ver logs backend
ssh minha-vps-hostinger "docker logs finup_backend_prod --tail 100 --follow"

# Ver logs postgres
ssh minha-vps-hostinger "docker logs finup_postgres_prod --tail 50"

# Ver logs nginx
ssh minha-vps-hostinger "docker logs finup_nginx_prod --tail 50"

# Stats de recursos
ssh minha-vps-hostinger "docker stats --no-stream"
```

---

## 🎯 MÉTRICAS DE SUCESSO

### P0 (Imediato)
- [x] Versão Alembic: f1200dd073a8 ✅
- [ ] Containers: 6/6 healthy ⏳
- [ ] /api/health: 200 OK ⏳
- [ ] Processos Ateliê: 0 ⏳

### P1 (24h)
- [ ] Tabelas: 28 ⏳
- [ ] Backups antigos: removidos ⏳
- [ ] Git status: limpo ⏳

### P2 (Manutenção)
- [ ] validate_parity.py: 100% OK ⏳
- [ ] Documentação: atualizada ⏳
- [ ] Monitoramento: ativo ⏳

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **Mapeamento Detalhado:** [docs/deploy/MAPEAMENTO_LOCAL_VS_VM.md](./MAPEAMENTO_LOCAL_VS_VM.md)
- **Script P0:** [scripts/deploy/sync_vm_with_local.sh](../../scripts/deploy/sync_vm_with_local.sh)
- **Script P1:** [scripts/deploy/cleanup_vm_tables.sh](../../scripts/deploy/cleanup_vm_tables.sh)
- **Processo Deploy:** [docs/deploy/DEPLOY_PROCESSO_CONSOLIDADO.md](./DEPLOY_PROCESSO_CONSOLIDADO.md)

---

## ⏱️ ESTIMATIVA DE TEMPO

| Fase | Tempo | Downtime |
|------|-------|----------|
| P0 (Crítico) | 20-30 min | 2-5 min |
| P1 (Limpeza) | 10-15 min | 0 min |
| P2 (Validação) | 15-20 min | 0 min |
| **Total** | **~1h** | **2-5 min** |

---

## 🆘 SUPORTE

**Se algo der errado:**

1. **PARAR imediatamente** a execução
2. **NÃO fazer** mais mudanças
3. **Restaurar** backup (ver seção Rollback acima)
4. **Verificar logs** (ver seção Logs e Debug)
5. **Documentar** erro encontrado
6. **Consultar** [docs/deploy/MAPEAMENTO_LOCAL_VS_VM.md](./MAPEAMENTO_LOCAL_VS_VM.md)

**Comandos de emergência:**
```bash
# Parar tudo
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml down"

# Restaurar backup
ssh minha-vps-hostinger "docker exec -i finup_postgres_prod psql -U finup_user -d finup_db < /tmp/backups_finup/backup_ULTIMO.sql"

# Subir novamente
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml up -d"
```

---

**Última atualização:** 06/03/2026 05:50 UTC  
**Próxima revisão:** Após execução P0
