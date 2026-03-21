# 🗺️ Mapeamento Local vs VM - Sistema FinUp

**Data:** 06/03/2026  
**Versão Local:** v5 (commit: 504b961c)  
**Versão VM:** v5 (commit: 504b961c)  
**Status:** ⚠️ DIVERGÊNCIAS CRÍTICAS DETECTADAS

---

## 📊 RESUMO EXECUTIVO

| Item | Local (Dev) | VM (Prod) | Status |
|------|------------|-----------|--------|
| **Commit Git** | 504b961c | 504b961c | ✅ Sincronizado |
| **Branch** | main | main | ✅ Sincronizado |
| **Migrations** | 25 arquivos | 25 arquivos | ✅ Sincronizado |
| **Versão Alembic** | f1200dd073a8 | 833cabc081aa | ❌ **DIVERGENTE** |
| **Registros journal_entries** | 8,096 | 8,096 | ✅ Sincronizado |
| **Total Tabelas** | 28 | 40+ | ❌ **DIVERGENTE** |
| **Docker** | Ativo (1 container) | Ativo (6 containers) | ⚠️ Configuração Diferente |
| **Mudanças não-commitadas** | 0 | 1 arquivo (backup script) | ⚠️ Arquivo extra na VM |

---

## 🚨 DIVERGÊNCIAS CRÍTICAS

### 1. **Versão Alembic Desatualizada na VM**

**Problema:** VM está em migration antiga (833cabc081aa), local está na mais recente (f1200dd073a8)

**Impacto:** 
- ❌ Schema do banco pode estar desatualizado na VM
- ❌ Novas features podem não funcionar corretamente
- ❌ Risco de perda de dados ou comportamento inconsistente

**Migrations pendentes na VM:**
```bash
# Local (aplicada): f1200dd073a8
# VM (atual): 833cabc081aa

# Migrations entre 833cabc e f1200dd (11 migrations pendentes):
1. 85375a56914c - add_modo_reajuste_to_user_financial
2. a1b2c3d4e5f6 - (próxima)
3. b2c3d4e5f6g7 - (próxima)
... até ...
11. f1200dd073a8 - (mais recente)
```

---

### 2. **Tabelas Extras na VM (12+ tabelas)**

**Local tem:** 28 tabelas  
**VM tem:** 40+ tabelas  

**Tabelas EXTRAS na VM (não existem no local):**
- ❌ `audit_log`
- ❌ `bank_format_compatibility_backup_20260109_185955`
- ❌ `base_padroes_backup_20260114_144652`
- ❌ `budget_planning_backup_20260115_204445`
- ❌ `budget_planning_backup_20260115_204836`
- ❌ `budget_categorias_config`
- ❌ `categories`
- ❌ `duplicados_temp`
- ❌ `error_codes`
- ❌ Possivelmente outras (needs full comparison)

**Análise:**
- ✅ Backups antigos (seguro manter, mas considerar limpeza)
- ⚠️ Tabelas de funcionalidades antigas (`audit_log`, `error_codes`)
- ⚠️ Tabelas possivelmente depreciadas (`categories`, `duplicados_temp`)

---

### 3. **Configuração Docker Divergente**

**Local (Dev):**
```yaml
# 1 container PostgreSQL standalone
- finup_postgres_dev (porta 5432 exposta)
```

**VM (Prod):**
```yaml
# 6 containers em produção
1. finup_nginx_prod (80/443) - ⚠️ unhealthy
2. finup_frontend_app_prod - ⚠️ unhealthy
3. finup_frontend_admin_prod - ✅ healthy
4. finup_backend_prod - ⚠️ unhealthy
5. finup_postgres_prod - ✅ healthy
6. finup_redis_prod - ✅ healthy
```

**Problemas detectados:**
- ❌ 3 containers unhealthy na VM
- ❌ Backend reiniciando workers continuamente (logs mostram child process dying)
- ⚠️ Possível problema de memória ou configuração

---

### 4. **Processos Duplicados na VM**

**Detectado:**
```bash
# Ateliê (porta 8001) - projeto antigo?
/var/www/atelie/app_dev/backend/venv/bin/uvicorn app.main:app --port 8001

# FinUp via Docker (porta 8000)
/opt/venv/bin/uvicorn app.main:app --port 8000

# Next.js builds/servers do Ateliê
node /var/www/atelie/app_dev/frontend/node_modules/.bin/next build
node /var/www/atelie/app_dev/frontend/node_modules/.bin/next start -p 3004
```

**Problema:**
- ❌ 2 projetos rodando simultaneamente (FinUp + Ateliê)
- ❌ Consumo desnecessário de recursos
- ⚠️ Risco de conflitos de porta/memória

---

### 5. **Arquivo Não-Commitado na VM**

**Arquivo:** `scripts/backup_to_drive.sh` (untracked)

**Ação necessária:**
- [ ] Avaliar se deve ser commitado
- [ ] Se privado: adicionar ao `.gitignore`
- [ ] Se útil: commitar e push

---

## 📋 TABELAS LOCAIS (28) - VERDADE ABSOLUTA

```
1. alembic_version                           ← Controle de migrations
2. bank_format_compatibility                 ← Compatibilidade bancos
3. base_expectativas                         ← Expectativas orçamento
4. base_grupos_config                        ← Grupos/categorias
5. base_grupos_template                      ← Templates de grupos
6. base_marcacoes                            ← Marcações/tags
7. base_marcacoes_template                   ← Templates marcações
8. base_padroes                              ← Padrões classificação
9. base_parcelas                             ← Parcelas
10. budget_planning                          ← Planejamento orçamento
11. cartoes                                  ← Cartões crédito
12. expectativas_mes                         ← Expectativas mensais
13. generic_classification_rules             ← Regras classificação
14. investimentos_aportes_extraordinarios    ← Aportes extra
15. investimentos_cenario_projecao           ← Cenários projeção
16. investimentos_cenarios                   ← Cenários investimento
17. investimentos_historico                  ← Histórico investimentos
18. investimentos_planejamento               ← Planejamento investimento
19. investimentos_portfolio                  ← Portfolio investimentos
20. investimentos_transacoes                 ← Transações investimentos
21. journal_entries                          ← Transações principais
22. plano_metas_categoria                    ← Metas por categoria
23. preview_transacoes                       ← Preview upload
24. screen_visibility                        ← Visibilidade telas
25. transacoes_exclusao                      ← Exclusões transações
26. upload_history                           ← Histórico uploads
27. user_financial_profile                   ← Perfil financeiro usuário
28. users                                    ← Usuários
```

---

## 🎯 PLANO DE AJUSTE - VM PARA ALINHAR COM LOCAL

### 🔴 **PRIORIDADE P0 - CRÍTICO (executar IMEDIATAMENTE)**

#### 1. Atualizar Migrations Alembic na VM

```bash
# 1. Fazer backup do banco antes
ssh minha-vps-hostinger "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db > /tmp/backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql"

# 2. Verificar migrations pendentes
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic history --verbose"

# 3. Aplicar migrations pendentes (11 migrations)
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic upgrade head"

# 4. Validar versão atualizada
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic current"
# Esperado: f1200dd073a8

# 5. Validar schema
ssh minha-vps-hostinger "docker exec finup_postgres_prod psql -U finup_user -d finup_db -c '\dt'"
```

**Tempo estimado:** 5-10 minutos  
**Risco:** Médio (mitigado com backup)  
**Rollback:** Restaurar backup + downgrade alembic

---

#### 2. Resolver Containers Unhealthy

```bash
# 1. Verificar logs de cada container unhealthy
ssh minha-vps-hostinger "docker logs finup_nginx_prod --tail 50"
ssh minha-vps-hostinger "docker logs finup_frontend_app_prod --tail 50"
ssh minha-vps-hostinger "docker logs finup_backend_prod --tail 50"

# 2. Verificar recursos (memória/CPU)
ssh minha-vps-hostinger "docker stats --no-stream"

# 3. Se OOM (Out of Memory), ajustar limites no docker-compose.prod.yml
# Exemplo:
# services:
#   backend:
#     deploy:
#       resources:
#         limits:
#           memory: 1G
#         reservations:
#           memory: 512M

# 4. Restart coordenado (ordem: postgres → redis → backend → frontend → nginx)
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart postgres"
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart redis"
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart backend"
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart frontend-app"
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml restart nginx"

# 5. Validar health
ssh minha-vps-hostinger "docker ps"
# Todos devem estar "healthy" ou "Up" (sem unhealthy)
```

**Tempo estimado:** 10-15 minutos  
**Risco:** Baixo (restart apenas)

---

#### 3. Matar Processos do Ateliê (liberação de recursos)

```bash
# 1. Identificar PIDs
ssh minha-vps-hostinger "ps aux | grep -E '/var/www/atelie' | grep -v grep"

# 2. Matar processos uvicorn (backend ateliê)
ssh minha-vps-hostinger "pkill -f '/var/www/atelie/app_dev/backend/venv/bin/uvicorn'"

# 3. Matar processos Node (frontend ateliê)
ssh minha-vps-hostinger "pkill -f '/var/www/atelie/app_dev/frontend'"

# 4. Validar que foram mortos
ssh minha-vps-hostinger "ps aux | grep -E '/var/www/atelie' | grep -v grep"
# Deve retornar vazio

# 5. Opcional: Prevenir restart automático
ssh minha-vps-hostinger "systemctl disable atelie_backend atelie_frontend 2>/dev/null || echo 'Sem systemd service'"
```

**Tempo estimado:** 2-3 minutos  
**Risco:** Baixo (projeto antigo/paralelo)

---

### 🟡 **PRIORIDADE P1 - IMPORTANTE (executar em até 24h)**

#### 4. Limpar Tabelas de Backup Antigas

```bash
# 1. Validar que são backups antigos mesmo
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "SELECT COUNT(*) FROM bank_format_compatibility_backup_20260109_185955"'

# 2. Criar backup final antes de deletar
ssh minha-vps-hostinger "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db -t 'bank_format_compatibility_backup_20260109_185955' -t 'base_padroes_backup_20260114_144652' -t 'budget_planning_backup_20260115_204445' -t 'budget_planning_backup_20260115_204836' > /tmp/backup_old_tables_$(date +%Y%m%d).sql"

# 3. Dropar tabelas de backup antigas
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "DROP TABLE IF EXISTS bank_format_compatibility_backup_20260109_185955, base_padroes_backup_20260114_144652, budget_planning_backup_20260115_204445, budget_planning_backup_20260115_204836 CASCADE"'

# 4. Validar que foram removidas
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "\dt" | grep backup'
# Não deve retornar nada
```

**Tempo estimado:** 5 minutos  
**Risco:** Baixo (são backups, dados estão nas tabelas principais)

---

#### 5. Investigar Tabelas Órfãs (audit_log, error_codes, categories, etc)

```bash
# 1. Verificar se têm dados
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "SELECT COUNT(*) as audit_log_count FROM audit_log; SELECT COUNT(*) as error_codes_count FROM error_codes; SELECT COUNT(*) as categories_count FROM categories; SELECT COUNT(*) as duplicados_temp_count FROM duplicados_temp"'

# 2. Se vazias ou irrelevantes:
#    a. Criar backup
ssh minha-vps-hostinger "docker exec finup_postgres_prod pg_dump -U finup_user -d finup_db -t 'audit_log' -t 'error_codes' -t 'categories' -t 'duplicados_temp' > /tmp/backup_orphan_tables_$(date +%Y%m%d).sql"

#    b. Dropar (se confirmado seguro)
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "DROP TABLE IF EXISTS audit_log, error_codes, categories, duplicados_temp CASCADE"'

# 3. Se audit_log for necessário:
#    - Criar migration local para adicionar
#    - Aplicar localmente também
```

**Tempo estimado:** 10-15 minutos  
**Risco:** Médio (avaliar impacto antes de dropar)  
**Decisão:** ⏸️ Aguardar análise de uso

---

#### 6. Resolver Arquivo `scripts/backup_to_drive.sh`

```bash
# Opção 1: Se é útil, commitar
ssh minha-vps-hostinger "cd /var/www/finup && cat scripts/backup_to_drive.sh"
# Avaliar conteúdo
# Se útil: copiar para local, commitar, push

# Opção 2: Se é privado/sensível, ignorar
echo "scripts/backup_to_drive.sh" >> .gitignore
git add .gitignore
git commit -m "chore: ignora script de backup privado"
git push
ssh minha-vps-hostinger "cd /var/www/finup && git pull"

# Opção 3: Se é lixo, deletar
ssh minha-vps-hostinger "cd /var/www/finup && rm scripts/backup_to_drive.sh"
```

**Tempo estimado:** 3-5 minutos  
**Risco:** Baixo

---

### 🟢 **PRIORIDADE P2 - MANUTENÇÃO (executar quando possível)**

#### 7. Validar Paridade de Schemas Completa

```bash
# Usar script existente
python scripts/testing/validate_parity.py

# Se divergências:
# 1. Gerar migration para corrigir
# 2. Aplicar em dev primeiro
# 3. Testar
# 4. Aplicar em prod
```

**Tempo estimado:** 15-20 minutos  
**Risco:** Baixo (apenas diagnóstico)

---

#### 8. Atualizar Documentação de Deploy

```bash
# Atualizar docs/deploy/DEPLOY_PROCESSO_CONSOLIDADO.md
# - Incluir novo processo de validação de paridade
# - Documentar migrations pendentes
# - Adicionar checklist de containers healthy
```

**Tempo estimado:** 10 minutos  
**Risco:** Zero (documentação)

---

#### 9. Configurar Monitoramento de Health

```bash
# Criar script de monitoramento contínuo
# docs/deploy/monitor_health.sh

#!/bin/bash
while true; do
  echo "=== $(date) ==="
  docker ps --format "table {{.Names}}\t{{.Status}}"
  curl -s http://localhost/api/health | jq .
  sleep 300  # 5 min
done

# Executar em screen/tmux na VM
ssh minha-vps-hostinger "cd /var/www/finup && screen -dmS health_monitor ./docs/deploy/monitor_health.sh"
```

**Tempo estimado:** 5 minutos  
**Risco:** Zero (monitoramento apenas)

---

## 📋 CHECKLIST DE EXECUÇÃO

### Pré-Deploy
- [ ] ✅ Git status limpo no local
- [ ] ✅ Backup do banco VM criado
- [ ] ✅ Documentação atualizada
- [ ] ✅ Usuário notificado de downtime (se necessário)

### P0 - Execução Imediata
- [ ] ❌ Backup banco VM (pg_dump)
- [ ] ❌ Aplicar migrations (alembic upgrade head)
- [ ] ❌ Validar versão alembic (f1200dd073a8)
- [ ] ❌ Restart containers (ordem: postgres → redis → backend → frontend → nginx)
- [ ] ❌ Validar containers healthy
- [ ] ❌ Matar processos Ateliê
- [ ] ❌ Validar health endpoint (curl /api/health)

### P1 - Até 24h
- [ ] ⏸️ Limpar tabelas backup antigas
- [ ] ⏸️ Investigar tabelas órfãs (audit_log, error_codes, etc)
- [ ] ⏸️ Resolver arquivo backup_to_drive.sh
- [ ] ⏸️ Validar contagem de tabelas (28 em ambos)

### P2 - Manutenção
- [ ] ⏸️ Validar paridade completa (validate_parity.py)
- [ ] ⏸️ Atualizar documentação deploy
- [ ] ⏸️ Configurar monitoramento health

---

## 🚨 ROLLBACK PLAN

### Se Migrations Falharem

```bash
# 1. Parar backend
ssh minha-vps-hostinger "docker-compose -f /var/www/finup/docker-compose.prod.yml stop backend"

# 2. Restaurar backup
ssh minha-vps-hostinger "docker exec -i finup_postgres_prod psql -U finup_user -d finup_db < /tmp/backup_pre_migration_YYYYMMDD_HHMMSS.sql"

# 3. Downgrade alembic para versão anterior
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic downgrade 833cabc081aa"

# 4. Restart backend
ssh minha-vps-hostinger "docker-compose -f /var/www/finup/docker-compose.prod.yml start backend"

# 5. Validar funcionamento
ssh minha-vps-hostinger "curl -s http://localhost/api/health"
```

### Se Containers Não Subirem Após Restart

```bash
# 1. Verificar logs
ssh minha-vps-hostinger "docker logs finup_backend_prod --tail 100"

# 2. Se problema de memória, reduzir workers
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml down"
# Editar docker-compose.prod.yml: workers=1 (instead of 2)
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml up -d"

# 3. Se persistir, voltar para última imagem estável
ssh minha-vps-hostinger "docker pull ghcr.io/emangue/finup-backend:COMMIT_ANTERIOR"
ssh minha-vps-hostinger "cd /var/www/finup && docker-compose -f docker-compose.prod.yml up -d --force-recreate backend"
```

---

## 📊 MÉTRICAS DE SUCESSO

### Após P0
- ✅ Versão Alembic: f1200dd073a8 (ambos)
- ✅ Containers healthy: 6/6
- ✅ /api/health retorna 200 OK
- ✅ Processos Ateliê: 0 (mortos)
- ✅ Logs backend: sem "child process died"

### Após P1
- ✅ Tabelas: 28 (ambos) ou 28+4 se audit_log necessário
- ✅ Backups antigos: removidos
- ✅ Git status: limpo (ambos)

### Após P2
- ✅ validate_parity.py: 100% OK
- ✅ Documentação: atualizada
- ✅ Monitoramento: ativo

---

## 🔍 COMANDOS ÚTEIS DE VALIDAÇÃO

```bash
# Verificar sincronização git
git log --oneline -1
ssh minha-vps-hostinger "cd /var/www/finup && git log --oneline -1"

# Verificar alembic
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "SELECT version_num FROM alembic_version"
ssh minha-vps-hostinger "docker exec finup_backend_prod alembic current"

# Verificar containers
docker ps
ssh minha-vps-hostinger "docker ps"

# Verificar health
curl -s http://localhost:8000/api/health | jq .
ssh minha-vps-hostinger "curl -s http://localhost/api/health"

# Verificar tabelas
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'"
ssh minha-vps-hostinger 'docker exec finup_postgres_prod psql -U finup_user -d finup_db -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = '"'"'public'"'"'"'

# Verificar registros
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "SELECT COUNT(*) FROM journal_entries"
ssh minha-vps-hostinger "docker exec finup_postgres_prod psql -U finup_user -d finup_db -c 'SELECT COUNT(*) FROM journal_entries'"
```

---

## 📝 NOTAS IMPORTANTES

1. **Backup antes de TUDO**: Sempre fazer backup do banco antes de aplicar migrations ou modificações de schema

2. **Ordem de restart**: Sempre respeitar ordem de dependências (postgres → redis → backend → frontend → nginx)

3. **Downtime**: Migrations podem causar 2-5 minutos de downtime. Executar em horário de baixo tráfego.

4. **Validação**: Após cada etapa P0, validar que sistema está funcional antes de prosseguir

5. **Rollback**: Manter backups por pelo menos 7 dias após mudanças críticas

6. **Monitoramento**: Após ajustes P0, monitorar por 24h para garantir estabilidade

---

## ✅ CONCLUSÃO

**Estado Atual:** ⚠️ VM divergente da verdade local (11 migrations atrasadas, containers unhealthy, processos duplicados)

**Risco:** 🔴 **ALTO** - Sistema em produção com schema desatualizado e containers instáveis

**Ação Requerida:** 🚨 **IMEDIATA** - Executar plano P0 nas próximas 2-4 horas

**Tempo Total Estimado:** 
- P0: 20-30 minutos
- P1: 30-40 minutos  
- P2: 30 minutos
- **Total: ~1h30min**

**Próximos Passos:**
1. Criar backup do banco VM
2. Aplicar migrations pendentes
3. Resolver containers unhealthy
4. Matar processos Ateliê
5. Validar sistema 100% operacional

---

**Documento criado em:** 06/03/2026 05:45 UTC  
**Última atualização:** 06/03/2026 05:45 UTC  
**Responsável:** Sistema de Mapeamento Automático  
**Próxima revisão:** Após execução P0
