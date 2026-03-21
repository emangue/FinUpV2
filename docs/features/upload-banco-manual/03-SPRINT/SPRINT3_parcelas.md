# 🏃 SPRINT 3 — Fix Dedup Parcelas v5.1

**Feature:** Fix falso-positivo dedup em compras parceladas  
**PRD:** `../01-PRD/PRD_parcelas_v5_1.md`  
**Tech Spec:** `../02-TECH_SPEC/TECH_SPEC_parcelas_v5_1.md`  
**Versão:** 1.0  
**Data:** 23/03/2026  
**Branch:** `fix/dedup-parcelas-v5-1`  
**Estimativa total:** ~4.5h

---

## 📊 Visão Geral das Tarefas

| # | Tarefa | Arquivo | Estimativa | Dependência |
|---|---|---|---|---|
| T1 | Atualizar `hasher.py` | `app/shared/utils/hasher.py` | 20min | — |
| T2 | Corrigir `marker.py` (3 bugs) | `app/domains/upload/processors/marker.py` | 40min | T1 |
| T3 | Criar `test_hasher_parcelas.py` | `tests/test_hasher_parcelas.py` | 30min | T1 |
| T4 | Criar `test_marker_parcelas.py` | `tests/test_marker_parcelas.py` | 40min | T2 |
| T5 | Atualizar `test_hash_user_id.py` | `tests/test_hash_user_id.py` | 20min | T1, T2 |
| T6 | Criar migration script v5.1 | `scripts/database/recalculate_id_transacao_v5_1.py` | 30min | T1 |
| T7 | Executar migration (dry-run + real) | DB Docker | 15min | T6 |
| T8 | Validação E2E (re-upload fatura-202602) | Browser + DB | 30min | T7 |
| T9 | Commit final | git | 15min | T1..T8 |

---

## 🔵 T1 — Atualizar `hasher.py`

**Estimativa:** 20min  
**Arquivo:** `app_dev/backend/app/shared/utils/hasher.py`

### Checklist T1
- [ ] Adicionar parâmetro `parcela: str | None = None` na assinatura de `generate_id_transacao`
- [ ] Adicionar condicional: se `parcela`: `chave = f"...|{parcela}"`, senão: chave atual (sem mudança)
- [ ] Atualizar docstring da função
- [ ] Verificar que `sequencia` continua funcionando com e sem parcela

### Diff esperado

```python
# ANTES
def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1) -> str:
    ...
    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"

# DEPOIS
def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1,
                          parcela: str | None = None) -> str:
    ...
    if parcela:
        chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}|{parcela}"
    else:
        chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"
```

### Teste rápido T1
```bash
docker exec finup_backend_dev python3 -c "
from app.shared.utils.hasher import generate_id_transacao
id1 = generate_id_transacao('19/01/2026','itau','fatura',-1011.21,1,parcela='1/6')
id2 = generate_id_transacao('19/01/2026','itau','fatura',-1011.21,1,parcela='2/6')
id0 = generate_id_transacao('19/01/2026','itau','fatura',-1011.21,1)
print('p1:', id1)
print('p2:', id2)
print('sem parcela:', id0)
assert id1 != id2, 'FALHOU: 1/6 == 2/6'
assert id0 != id1, 'FALHOU: sem parcela == 1/6'
print('✅ T1 OK')
"
```

---

## 🔵 T2 — Corrigir `marker.py`

**Estimativa:** 40min  
**Arquivo:** `app_dev/backend/app/domains/upload/processors/marker.py`  
**Depende de:** T1

### Checklist T2
- [ ] **BUG-1:** `chave_unica` inclui `parcela_param` quando `info_parcela` presente
- [ ] **BUG-2:** `generate_id_transacao()` recebe `parcela=parcela_param`
- [ ] **BUG-3:** Fórmula `IdParcela` substituída por `banco|tipo|data|valor|total|user_id`
- [ ] Branch `else` (sem parcela) mantida idêntica ao v5 (zero mudança na lógica)
- [ ] Importação de `hashlib` já presente (não precisa adicionar)
- [ ] Verificar que `info_parcela["parcela"]` é int e `info_parcela["total"]` é int

### Localização no arquivo

Buscar pela string `chave_unica` — o bloco está dentro do método `_mark_row()` ou equivalente.

### Teste rápido T2
```bash
docker exec finup_backend_dev python3 -c "
import sys; sys.path.insert(0, '/app')
# Verificar que bloco if info_parcela usa parcela na chave_unica
import inspect
from app.domains.upload.processors.marker import TransactionMarker
src = inspect.getsource(TransactionMarker)
assert 'parcela_param' in src, 'FALHOU: parcela_param não encontrado'
assert 'parcela=parcela_param' in src, 'FALHOU: parcela não passado para generate_id_transacao'
print('✅ T2 código verificado')
"
```

---

## 🔵 T3 — Criar `test_hasher_parcelas.py`

**Estimativa:** 30min  
**Arquivo:** `app_dev/backend/tests/test_hasher_parcelas.py`  
**Depende de:** T1

### Testes a implementar

| Teste | Descrição | Tipo |
|---|---|---|
| `test_parcela_1_difere_de_parcela_2` | 1/6 ≠ 2/6 mesma compra | Happy path |
| `test_todas_parcelas_diferentes` | Parcelas 1..6 todas únicas | Happy path |
| `test_sem_parcela_backward_compat` | `parcela=None` → hash v5 idêntico | Backward compat |
| `test_parcela_none_nao_colapsa_com_1_1` | `None` ≠ `"1/1"` | Edge case |
| `test_mesma_parcela_idempotente` | Mesmo call → mesmo hash | Determinismo |
| `test_parcela_formato_variado` | `"1/12"` ≠ `"01/12"` | Edge case |
| `test_user_id_isolamento_com_parcela` | user_id=1 ≠ user_id=2 mesmo parcela | Segurança |
| `test_hash_e_inteiro` | Resultado é inteiro numérico | Tipo |

### Executar testes T3
```bash
docker exec finup_backend_dev python3 -m pytest tests/test_hasher_parcelas.py -v
```

**Meta:** 8/8 testes passando ✅

---

## 🔵 T4 — Criar `test_marker_parcelas.py`

**Estimativa:** 40min  
**Arquivo:** `app_dev/backend/tests/test_marker_parcelas.py`  
**Depende de:** T2

### Testes a implementar

| Teste | Classe | Descrição |
|---|---|---|
| `test_chave_diferentes_para_parcelas_diferentes` | `TestChaueUnicaBug1` | BUG-1: parcelas 1/6 ≠ 2/6 na chave_unica |
| `test_chave_igual_mesma_parcela` | `TestChaueUnicaBug1` | Mesma parcela → mesma chave (idempotente) |
| `test_sem_parcela_backward_compat` | `TestChaueUnicaBug1` | BUG-1: sem parcela = v5 |
| `test_formato_nao_afeta_id_parcela` | `TestIdParcelaBug3` | BUG-3: mesmos dados = mesmo IdParcela |
| `test_id_parcela_diferente_por_user` | `TestIdParcelaBug3` | BUG-3: user isolamento |
| `test_id_parcela_formato_16_chars` | `TestIdParcelaBug3` | BUG-3: formato correto |
| `test_anuidade_parcelas_data_diferente` | `TestIdParcelaBug3` | Edge: cobrança mensal (data muda) |
| `test_airbnb_parcelas_mesma_data` | `TestIdParcelaBug3` | Happy: mesma data = mesmo IdParcela |
| `test_assinatura_v5_requer_banco_e_tipo` | `TestAtualizacaoTestHashUserId` | Documentar assinatura v5.1 |

### Executar testes T4
```bash
docker exec finup_backend_dev python3 -m pytest tests/test_marker_parcelas.py -v
```

**Meta:** 9/9 testes passando ✅

---

## 🔵 T5 — Atualizar `test_hash_user_id.py`

**Estimativa:** 20min  
**Arquivo:** `app_dev/backend/tests/test_hash_user_id.py`  
**Depende de:** T1, T2

### O que atualizar

1. **Chamadas a `generate_id_transacao`:** adicionar `banco` e `tipo_documento` à chamada (assinatura v5.1)

```python
# ANTES (quebrado)
id_user1 = generate_id_transacao(data, estab, valor, user_id=1)

# DEPOIS (v5.1)
id_user1 = generate_id_transacao(data, "itau", "fatura", valor, user_id=1)
```

2. **Função `_gerar_id_parcela_esperado`:** atualizar para nova fórmula banco|tipo|data|valor|total

```python
# ANTES
def _gerar_id_parcela_esperado(estab_base: str, valor: float, total: int, user_id: int) -> str:
    estab_norm = normalizar_estabelecimento(estab_base)
    chave = f"{estab_norm}|{round(float(valor), 2):.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]

# DEPOIS
def _gerar_id_parcela_esperado(banco: str, tipo: str, data: str,
                                valor: float, total: int, user_id: int) -> str:
    chave = f"{banco}|{tipo}|{data}|{round(float(valor), 2):.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]
```

3. **Atualizar chamadas** a `_gerar_id_parcela_esperado` nos testes com os novos parâmetros

### Executar testes T5
```bash
docker exec finup_backend_dev python3 -m pytest tests/test_hash_user_id.py -v
```

**Meta:** Todos os testes existentes passando com assinatura atualizada ✅

---

## 🔵 T6 — Criar Migration Script v5.1

**Estimativa:** 30min  
**Arquivo:** `scripts/database/recalculate_id_transacao_v5_1.py`  
**Depende de:** T1

### Checklist T6
- [ ] Copiar estrutura do script v5 como referência
- [ ] WHERE clause: `"TotalParcelas" IS NOT NULL` — APENAS parcelados
- [ ] Usar nova assinatura `generate_id_transacao(..., parcela=parcela_param)`
- [ ] Usar nova fórmula `IdParcela` (banco|tipo|data|valor|total|user_id)
- [ ] Modo `--dry-run` funcional (sem `--dry-run` executa)
- [ ] Log de cada registro atualizado
- [ ] Diagnóstico de unicidade (deve ser 0 colisões após)
- [ ] `sys.exit(1)` se colisão detectada no dry-run

### Teste manual T6
```bash
# Dry-run (deve mostrar ~42 registros, 0 colisões)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
source app_dev/venv/bin/activate
python scripts/database/recalculate_id_transacao_v5_1.py --dry-run
```

**Meta:** `[DRY-RUN] 42 registros seriam atualizados. IDs únicos DEPOIS: 42. ✅ Nenhuma colisão.`

---

## 🔵 T7 — Executar Migration

**Estimativa:** 15min  
**Depende de:** T6 dry-run OK

### Passos obrigatórios

```bash
# 1. Backup antes (obrigatório)
ls app_dev/backend/database/backups_daily/   # Verificar backup de hoje existe

# 2. Dry-run para confirmar
python scripts/database/recalculate_id_transacao_v5_1.py --dry-run

# 3. Executar (sem --dry-run)
python scripts/database/recalculate_id_transacao_v5_1.py

# 4. Validação SQL
docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "
  SELECT COUNT(*) FROM journal_entries WHERE \"TotalParcelas\" IS NOT NULL;
  -- Esperado: ~42
"

docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "
  SELECT \"IdTransacao\", COUNT(*) as cnt
  FROM journal_entries
  WHERE \"TotalParcelas\" IS NOT NULL
  GROUP BY \"IdTransacao\" HAVING COUNT(*) > 1;
  -- Esperado: 0 linhas (sem colisões)
"

docker exec finup_postgres_dev psql -U finup_user -d finup_db -c "
  SELECT COUNT(*) FROM journal_entries WHERE \"TotalParcelas\" IS NULL;
  -- Esperado: 4207 (inalterado)
"
```

### Checklist T7
- [ ] ✅ Backup diário existe para hoje
- [ ] ✅ Dry-run passou sem erros
- [ ] ✅ Migration executada com sucesso (~42 updates)
- [ ] ✅ `SELECT ... HAVING COUNT(*) > 1` retorna 0 linhas
- [ ] ✅ Não-parcelados = 4207 (inalterado)

---

## 🔵 T8 — Validação E2E

**Estimativa:** 30min  
**Depende de:** T7 completo

### Cenário 1: Upload fatura-202602 (o arquivo original do bug)

```
Arquivo: fatura_azul_202602.csv (45 lançamentos, Itaú cartão Azul)
Usuário: admin@financas.com

Resultado ANTES do fix:
  ❌ Já Importadas: 45
  ❌ Novas: 0

Resultado ESPERADO após fix + migração:
  ✅ Já Importadas: 31
  ✅ Novas: 14
```

### Cenário 2: Re-upload (idempotência)

```
Após importar as 14 novas do Cenário 1, re-fazer upload do mesmo arquivo.

Resultado ESPERADO:
  ✅ Já Importadas: 45
  ✅ Novas: 0
  (todas 45 agora estão no banco)
```

### Cenário 3: Upload fatura-202601 (regressão)

```
Arquivo: fatura que já foi importada corretamente (31 lançamentos sem parcelas)
Resultado ESPERADO:
  ✅ Já Importadas: 31
  ✅ Novas: 0
  (não regrediu)
```

### Checklist T8
- [ ] ✅ Cenário 1: 14 novas importadas, 31 bloqueadas
- [ ] ✅ Cenário 1: Verificar no DB que 14 novas têm `MesFatura=202602` correto
- [ ] ✅ Cenário 2: Re-upload resulta em 45 já importadas
- [ ] ✅ Cenário 3: Fatura anterior não regrediu
- [ ] ✅ DB: `SELECT COUNT(*) WHERE MesFatura=202602 AND TipoDocumento='fatura'` = 45

---

## 🔵 T9 — Commit Final

**Estimativa:** 15min  
**Depende de:** T1..T8 todos OK

### Arquivos do commit

```bash
git add \
  app_dev/backend/app/shared/utils/hasher.py \
  app_dev/backend/app/domains/upload/processors/marker.py \
  app_dev/backend/tests/test_hasher_parcelas.py \
  app_dev/backend/tests/test_marker_parcelas.py \
  app_dev/backend/tests/test_hash_user_id.py \
  scripts/database/recalculate_id_transacao_v5_1.py \
  docs/features/upload-banco-manual/
```

### Mensagem de commit

```
fix(dedup): corrige falso-positivo em compras parceladas (IdTransacao v5.1)

Problema: parcelas 2/N, 3/N da mesma compra geravam IdTransacao idêntico
ao da parcela 1/N (mesma data original + mesmo valor → colisão de hash).
Resultado: fatura-202602 bloqueada como "Já Importadas (45)" com apenas
31 registros no banco.

Correções:
- hasher.py: adiciona param `parcela: str | None` à generate_id_transacao
- marker.py: BUG-1 chave_unica inclui parcela; BUG-2 passa parcela ao hasher;
  BUG-3 IdParcela usa banco|tipo|data|valor|total (não mais nome de estab.)
- migration v5.1: recalcula IdTransacao+IdParcela WHERE TotalParcelas IS NOT NULL

Backward compat: parcela=None → hash idêntico ao v5 (4207 registros intactos)
Migração: ~42 registros parcelados atualizados, 0 colisões após

Testes:
- test_hasher_parcelas.py: 8 testes novos (todos passando)
- test_marker_parcelas.py: 9 testes novos (todos passando)
- test_hash_user_id.py: atualizado para assinatura v5.1

Closes: bug "Já Importadas (45)" fatura-202602
```

---

## 📊 Sumário de Testes

### Suite completa

```bash
docker exec finup_backend_dev python3 -m pytest tests/ -v --tb=short
```

### Testes por arquivo após Sprint 3

| Arquivo | Testes | Status Meta |
|---|---|---|
| `tests/test_hasher_parcelas.py` | 8 novos | ✅ 8/8 |
| `tests/test_marker_parcelas.py` | 9 novos | ✅ 9/9 |
| `tests/test_hash_user_id.py` | 5 existentes atualizados | ✅ 5/5 |
| `tests/test_hash_pit_stop.py` | Verificar compat | ✅ Passando |
| `tests/test_grupos_por_usuario.py` | Sem mudança | ✅ Passando |
| **Total** | **~27 testes** | **✅ 100%** |

---

## 🚨 Critérios de Aceite

| Critério | Verificação | Obrigatório |
|---|---|---|
| `pytest tests/` passa 100% | `docker exec finup_backend_dev python3 -m pytest tests/` | ✅ SIM |
| Fatura-202602 importa 14 novas | Upload E2E + SELECT COUNT | ✅ SIM |
| Não-parcelados inalterados (4207) | `SELECT COUNT WHERE TotalParcelas IS NULL` | ✅ SIM |
| Idempotência: re-upload = 0 novas | Upload E2E segunda vez | ✅ SIM |
| 0 colisões em IdTransacao parcelados | `GROUP BY HAVING COUNT(*) > 1` | ✅ SIM |

---

## 📝 Post-Sprint Notes

Após concluir o Sprint 3, criar `SPRINT3_COMPLETE.md` com:
- Hashes antes/depois dos 21 registros parcelados
- Output do `--dry-run`
- Screenshot do upload E2E (14 novas importadas)
- Tempo real vs estimado
