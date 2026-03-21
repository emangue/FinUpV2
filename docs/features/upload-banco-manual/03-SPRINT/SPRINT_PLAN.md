# 🏃 SPRINT PLAN — IdTransacao v5

**Feature:** Upload com Seleção Manual + IdTransacao v5  
**PRD:** `../01-PRD/PRD.md`  
**Tech Spec:** `../02-TECH_SPEC/TECH_SPEC.md`  
**Versão:** 1.0  
**Data:** 21/03/2026  
**Branch:** `investigate/server-vs-local-dedup`  
**Estimativa total:** ~5h

---

## 📊 Status das Fases

| Fase | Nome | Horas | Status |
|------|------|-------|--------|
| Fase 1 | Seleção manual de banco no upload | — | ✅ Concluída (commit `27ea995d`) |
| Fase 2a | service.py — injeção banco/tipo do form | 0.5h | ✅ Concluída |
| Sprint 1 | Implementar hasher.py v5 + marker.py + router.py | 2h | 🔵 Próximo |
| Sprint 2 | Migração histórica + teste E2E dedup | 2h | 🟡 Aguardando S1 |
| Sprint 3 | Deploy + migração em produção + monitoring | 1h | 🟡 Aguardando S2 |

---

## 🔵 SPRINT 1 — Implementar Algoritmo v5

**Duração estimada:** 2h  
**Objetivo:** Atualizar hasher.py, marker.py e router.py para usar o novo algoritmo

### DAG do Sprint 1

```
T1 [hasher.py v5]
    ↓
T2 [marker.py — nova chamada]
T3 [router.py — validação banco]
    ↓ (ambos dependem de T1)
T4 [testes unitários]
    ↓
T5 [restart Docker + smoke test]
    ↓
T6 [commit]
```

---

### T1 — Atualizar `hasher.py` para v5

**Arquivo:** `app_dev/backend/app/shared/utils/hasher.py`  
**Tempo:** ~40min  
**Risco:** ALTO — arquivo crítico, BREAKING CHANGE na assinatura

**Pré-condição:**
```bash
# Verificar que não há outras chamadas com assinatura antiga que possam ser esquecidas
grep -rn "generate_id_transacao" app_dev/backend/ --include="*.py" | grep -v "__pycache__"
```

**Mudanças:**
1. Adicionar `import unicodedata` e `import re` no topo
2. Adicionar `_BANCO_CANONICAL` dict
3. Adicionar `_normalize_str()` função privada
4. Adicionar `get_canonical_banco()` função pública
5. Substituir `generate_id_transacao` pela v5 (nova assinatura: `data, banco, tipo_documento, valor, user_id, sequencia=1`)
6. Manter `fnv1a_64_hash` e `generate_id_simples` **inalterados**

**Referência:** Seção 3.2 do TECH_SPEC.md

**Validação:**
```bash
# Rodar testes unitários (devem passar 23/23)
python3 scripts/testing/test_idtransacao_v5.py
```

---

### T2 — Atualizar `marker.py`

**Arquivo:** `app_dev/backend/app/domains/upload/processors/marker.py`  
**Tempo:** ~20min  
**Risco:** MÉDIO — mudança localizada no bloco de cálculo de IdTransacao

**Mudança:** Substituir bloco que calcula `chave_unica` e chama `generate_id_transacao`

**Antes:**
```python
estab_normalizado = re.sub(r'[^A-Z0-9]', '', raw.lancamento.upper())
chave_unica = f"{raw.data}|{estab_hash}|{valor_hash:.2f}"
sequencia = self._get_sequence_for_duplicate(chave_unica)
id_transacao = generate_id_transacao(
    data=raw.data,
    estabelecimento=estab_normalizado,
    valor=raw.valor,
    user_id=self.user_id,
    sequencia=sequencia
)
```

**Depois:**
```python
# v5 — banco+tipo+data+valor (sem nome da transação)
valor_hash  = arredondar_2_decimais(raw.valor)
chave_unica = f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}"
sequencia   = self._get_sequence_for_duplicate(chave_unica)
id_transacao = generate_id_transacao(
    data=raw.data,
    banco=raw.banco,
    tipo_documento=raw.tipo_documento,
    valor=raw.valor,
    user_id=self.user_id,
    sequencia=sequencia
)
```

**Referência:** Seção 4.3 do TECH_SPEC.md

---

### T3 — Adicionar validação de banco em `router.py`

**Arquivo:** `app_dev/backend/app/domains/upload/router.py`  
**Tempo:** ~10min  
**Risco:** BAIXO — adicionar validação antes da chamada ao service

**Mudança:** Bloco de validação no início do endpoint `/upload/preview`

**Referência:** Seção 5.2 do TECH_SPEC.md

---

### T4 — Executar testes unitários

**Tempo:** ~10min

```bash
# Testes devem passar 23/23 após T1
python3 scripts/testing/test_idtransacao_v5.py

# Esperado:
# ✅ Grupo 1: Prova do bug v4.2.1 (2/2)
# ✅ Grupo 2: Fix v5 — mesmo banco+tipo+data+valor (3/3)
# ✅ Grupo 3: Sequência diferencia transações (2/2)
# ✅ Grupo 4: Isolamento por user_id (2/2)
# ✅ Grupo 5: extrato vs fatura → IDs diferentes (2/2)
# ✅ Grupo 6: Normalização (4/4)
# ✅ Grupo 7: Anti-colisão entre bancos (3/3)
# ✅ Grupo 8: Cross-format PDF vs XLSX (5/5)
# ─────────────────────────────────────────────────
# Total: 23/23 ✅
```

---

### T5 — Restart Docker + smoke test

**Tempo:** ~5min

```bash
# Restart backend (hot reload não é suficiente para mudanças de módulo crítico)
docker-compose restart backend
sleep 8

# Smoke test
curl -s http://localhost:8000/api/health | python3 -m json.tool
# Esperado: { "status": "ok" }
```

---

### T6 — Commit Sprint 1

```bash
git add app_dev/backend/app/shared/utils/hasher.py
git add app_dev/backend/app/domains/upload/processors/marker.py
git add app_dev/backend/app/domains/upload/router.py

git commit -m "feat(dedup): IdTransacao v5 — banco+tipo+data+valor sem nome

- hasher.py v3.0.0: nova assinatura generate_id_transacao(data, banco, tipo, valor, user_id, seq)
  Adiciona _BANCO_CANONICAL, _normalize_str, get_canonical_banco
  Remove dependência de lancamento/estabelecimento no hash
- marker.py: atualiza chamada — chave_unica usa banco+tipo em vez de estab_normalizado
- router.py: valida banco obrigatório (rejeita vazio/generico com 422)

BREAKING CHANGE: Todos os IdTransacao existentes requerem recálculo (Sprint 2)

Testes: 23/23 passando em scripts/testing/test_idtransacao_v5.py
Refs: PRD v0.3 RF-10, TECH_SPEC.md seção 3-5

Co-authored-by: GitHub Copilot"
```

---

## 🟡 SPRINT 2 — Migração Histórica + Teste E2E

**Duração estimada:** 2h  
**Pré-condição:** Sprint 1 concluído (código em Docker funcionando)  
**Objetivo:** Recalcular todos os IdTransacao no banco para v5; provar dedup funcionando

### DAG do Sprint 2

```
T7 [criar script recalculate_id_transacao_v5.py]
    ↓
T8 [dry-run — verificar preview]
    ↓
T9 [backup obrigatório]
    ↓
T10 [executar migração]
    ↓
T11 [validar contagens]
    ↓
T12 [teste E2E dedup BTG XLS]
    ↓
T13 [commit]
```

---

### T7 — Criar script de migração

**Arquivo:** `scripts/database/recalculate_id_transacao_v5.py`  
**Tempo:** ~30min

**Referência:** Seção 6.2 do TECH_SPEC.md — código completo pronto para copy/paste

**Ponto de atenção:** Mapa `BANCO_ORIGEM_CLEANUP` deve cobrir os 2 filenames sujos conhecidos:
```python
BANCO_ORIGEM_CLEANUP = {
    'BTG202601.xls':                                      'BTG Pactual',
    'Extrato_2025-11-20_a_2026-01-18_11259347605.xls':    'BTG Pactual',
}
```

Confirmar os filenames exatos antes de rodar:
```bash
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT DISTINCT banco_origem FROM journal_entries WHERE banco_origem LIKE '%.xls%';"
```

---

### T8 — Dry-run de migração

**Tempo:** ~10min

```bash
# Copiar script para container
docker cp scripts/database/recalculate_id_transacao_v5.py \
  finup_backend_dev:/app/scripts/recalculate_id_transacao_v5.py

# Dry-run
docker exec finup_backend_dev python3 \
  /app/scripts/recalculate_id_transacao_v5.py --dry-run

# Output esperado:
# INFO: Total de registros a migrar: 4048
# INFO: Bancos já limpos: 4019
# INFO: Bancos corrigidos: 29
# INFO: Erros: 0
# INFO: ⚠  DRY RUN — nenhuma alteração salva
```

---

### T9 — Backup obrigatório

**Tempo:** ~5min

```bash
./scripts/deploy/backup_daily.sh

# Verificar que backup existe
ls -lh app_dev/backend/database/backups_daily/
# Deve mostrar backup de hoje com tamanho não-zero
```

> ⚠️ **BLOQUEANTE:** Não prosseguir para T10 sem backup confirmado

---

### T10 — Executar migração (apenas user_id=1 primeiro)

**Tempo:** ~5min

```bash
# Migrar user_id=1 primeiro para validar
docker exec finup_backend_dev python3 \
  /app/scripts/recalculate_id_transacao_v5.py --user-id 1

# Output esperado:
# INFO: Total de registros a migrar: 4048
# INFO: Bancos corrigidos: 29
# INFO: Erros: 0
# INFO: Atualizados: 4048
# INFO: ✅ Commit realizado com sucesso

# Se houver mais usuários, migrar todos:
docker exec finup_backend_dev python3 \
  /app/scripts/recalculate_id_transacao_v5.py
```

---

### T11 — Validar contagens pós-migração

**Tempo:** ~5min

```bash
# 1. Total não mudou
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM journal_entries;"
# Esperado: 4048

# 2. Nenhum IdTransacao nulo
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT COUNT(*) FROM journal_entries WHERE \"IdTransacao\" IS NULL;"
# Esperado: 0

# 3. Nenhum banco_origem sujo (filenames)
docker exec finup_postgres_dev psql -U finup_user -d finup_db \
  -c "SELECT banco_origem, COUNT(*) FROM journal_entries GROUP BY banco_origem ORDER BY count DESC;"
# Esperado: apenas bancos canônicos (Itaú, Mercado Pago, XP, BTG Pactual, Santander, Nubank)
```

---

### T12 — Teste E2E: dedup BTG XLS

**Tempo:** ~15min  
**Objetivo:** Provar que re-upload do mesmo arquivo BTG detecta 100% como duplicadas

```
Passo 1: Abrir http://localhost:3000
Passo 2: Ir para Upload
Passo 3: Selecionar arquivo: Extrato_2025-12-10_a_2026-03-09_11259347605.xls
         (ou qualquer XLS BTG que já foi importado com o novo algoritmo)
Passo 4: Banco = BTG Pactual
Passo 5: Tipo = Extrato
Passo 6: Confirmar upload

Resultado esperado:
  ✅ Preview mostra aba "Já Importadas" com as transações do upload anterior
  ✅ 0 transações novas (todas são duplicatas)
  ✅ Nenhuma transação duplicada inserida no banco
```

> **Se o arquivo original foi importado com v4.2.1 (antes da migração):**  
> Os IDs v4.2.1 estão no DB e foram recalculados para v5 na migração.  
> O novo upload gera IDs v5. Se os hashes baterem → dedup funciona ✅  
> Se não baterem → investigar discrepância nas chaves.

---

### T13 — Commit Sprint 2

```bash
git add scripts/database/recalculate_id_transacao_v5.py

git commit -m "feat(dedup): migração histórica IdTransacao v4.2.1 → v5

- scripts/database/recalculate_id_transacao_v5.py
  Recalcula 4048 registros, limpa 29 banco_origem com filenames (todos BTG)
  Suporte a --dry-run e --user-id para execução segura
  BANCO_ORIGEM_CLEANUP: BTG202601.xls e Extrato_..._11259347605.xls → BTG Pactual

- E2E confirmado: re-upload BTG XLS detecta 100% como duplicatas

Refs: PRD v0.3 seção 4.3, TECH_SPEC.md seção 6"
```

---

## 🟡 SPRINT 3 — Deploy + Produção

**Duração estimada:** 1h  
**Pré-condição:** Sprint 2 concluído, E2E passando  
**Objetivo:** Subir para produção e migrar dados reais

### DAG do Sprint 3

```
T14 [merge branch → main]
T15 [pré-deploy checklist]
T16 [deploy prod]
T17 [migração dados prod]
T18 [smoke test prod]
T19 [post-mortem — doc]
```

---

### T14 — Merge para main

```bash
# Na branch investigate/server-vs-local-dedup
git push origin investigate/server-vs-local-dedup

# Criar PR ou merge direto (depende do fluxo):
git checkout main
git merge investigate/server-vs-local-dedup
git push origin main
```

---

### T15 — Pré-deploy checklist

```bash
./deploy/scripts/predeploy.sh
```

**Critério de passagem:** 0 falhas bloqueantes

---

### T16 — Deploy em produção

```bash
./deploy/scripts/deploy_docker_build_local.sh
# Se OOM na VM:
./deploy/scripts/deploy_docker_vm.sh
```

---

### T17 — Migração de dados em produção

```bash
# SSH na VPS
ssh minha-vps-hostinger

# Backup antes de migrar
cd /var/www/finup
./scripts/deploy/backup_daily.sh

# Copiar script
# (ou usar git pull que já traz o script via volume mount)

# Dry-run em prod
docker exec finup_backend_prod python3 \
  /app/scripts/recalculate_id_transacao_v5.py --dry-run

# Executar migração
docker exec finup_backend_prod python3 \
  /app/scripts/recalculate_id_transacao_v5.py

# Validar
docker exec finup_postgres_prod psql -U finup_user -d finup_db \
  -c "SELECT banco_origem, COUNT(*) FROM journal_entries GROUP BY banco_origem ORDER BY count DESC;"
```

---

### T18 — Smoke test em produção

```bash
# Da máquina local:
curl -s https://[dominio_prod]/api/health | python3 -m json.tool

# Login + upload de teste via navegador
# Conferir aba "Já Importadas" em re-upload
```

---

### T19 — Documentar post-mortem

**Arquivo:** `docs/features/upload-banco-manual/POST_MORTEM.md`  
**Template:** `docs/templates/TEMPLATE_POST_MORTEM.md`

Pontos obrigatórios:
1. Root cause do bug de dedup (descrição variável no hash)
2. Impacto: N registros duplicados já existentes no DB (quantificar)
3. Solução: hash independente de descrição
4. Lição aprendida: nunca usar campo mutável/variável em chave de dedup
5. Ações preventivas: testes de dedup cross-format no CI

---

## 📋 Checklist Final

### Sprint 1
- [ ] `hasher.py` atualizado para v3.0.0
- [ ] `marker.py` chamando nova assinatura
- [ ] `router.py` validando banco obrigatório
- [ ] 23/23 testes unitários passando
- [ ] Backend reiniciado sem erros
- [ ] Commit `feat(dedup): IdTransacao v5...`

### Sprint 2
- [ ] `recalculate_id_transacao_v5.py` criado
- [ ] Dry-run executado sem erros
- [ ] Backup criado
- [ ] Migração executada (4048 records, 0 erros)
- [ ] Bancos sujos corrigidos (0 filenames no banco_origem)
- [ ] E2E dedup BTG XLS: 100% detectado como duplicata
- [ ] Commit `feat(dedup): migração histórica...`

### Sprint 3
- [ ] Merge para main
- [ ] `predeploy.sh` passando (0 falhas)
- [ ] Deploy em produção
- [ ] Backup em produção
- [ ] Migração em produção (dry-run primeiro)
- [ ] Smoke test em produção
- [ ] Post-mortem documentado

---

## 🔙 Plano de Rollback

### Sprint 1 (código)
```bash
# Reverter commit do Sprint 1
git revert HEAD
docker-compose restart backend
```

### Sprint 2 (dados)
```bash
# Restaurar backup criado em T9
docker exec -i finup_postgres_dev psql -U finup_user -d finup_db \
  < app_dev/backend/database/backups_daily/backup_YYYY-MM-DD.sql
```

### Sprint 3 (prod)
```bash
# SSH prod + restaurar backup
ssh minha-vps-hostinger
docker exec -i finup_postgres_prod psql -U finup_user -d finup_db \
  < /var/www/finup/backups/backup_YYYY-MM-DD.sql
```

---

## 📚 Referências

| Documento | Path |
|-----------|------|
| PRD v0.3 | `../01-PRD/PRD.md` |
| TECH_SPEC | `../02-TECH_SPEC/TECH_SPEC.md` |
| Testes unitários | `scripts/testing/test_idtransacao_v5.py` |
| Guia de deploy | `deploy/README.md` |
| SSH access | `docs/deploy/SSH_ACCESS.md` |
| Backup daily | `scripts/deploy/backup_daily.sh` |
