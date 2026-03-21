# 📋 PRD — Fix Falso-Positivo Dedup em Compras Parceladas (IdTransacao v5.1)

**Feature:** Fix dedup parcelas  
**Versão:** 1.0  
**Data:** 23/03/2026  
**Status:** ✅ Aprovado para implementação  
**Branch:** `fix/dedup-parcelas-v5-1`  
**PRD anterior:** `PRD.md` (upload-banco-manual, base deste fix)

---

## 1. Problema

### 1.1 Descrição do Problema

Ao tentar importar a fatura do cartão Azul (Itaú) referente a **Fevereiro/2026**, o sistema retornou:

> **"Já Importadas (45)"** — bloqueando a importação completa do arquivo.

No entanto, o banco de dados continha apenas **31 transações** para esse período (Itaú/fatura/202602). Ou seja, **14 transações legítimas foram falsamente identificadas como duplicatas**.

### 1.2 Root Cause Confirmado

O `IdTransacao v5` é gerado com a seguinte chave:

```
chave = f"{user_id}|{banco}|{tipo}|{data}|{valor}"
```

**Problema:** em compras parceladas no cartão de crédito, todas as parcelas de uma mesma compra **compartilham a data original da compra** (não a data de cobrança do mês). O valor por parcela também é fixo.

**Consequência:** Parcela 1/6 (fatura-202601) e Parcela 2/6 (fatura-202602) da mesma compra geram **IdTransacao idêntico** → a parcela 2/6 é falsamente classificada como "já importada".

### 1.3 Exemplo Real (DB user_id=1)

| Estabelecimento | MesFatura | Parcela | Data | Valor | IdTransacao |
|---|---|---|---|---|---|
| AIRBNB * HMHMZAQ | 202601 | 1/6 | 19/01/2026 | -1011.21 | `12041517302535481192` |
| AIRBNB * HMHMZAQ | 202602 | 2/6 | **19/01/2026** | **-1011.21** | `12041517302535481192` ← **COLISÃO** |
| AIRBNB * HMYX3X9 | 202601 | 1/6 | 19/01/2026 | -769.86 | `9064568136652700650` |
| AIRBNB * HMYX3X9 | 202602 | 2/6 | **19/01/2026** | **-769.86** | `9064568136652700650` ← **COLISÃO** |

### 1.4 Exceção: Parceladas por Data de Cobrança

Algumas faturas (ex: `ANUIDADE DIFERENCI`) geram parcelas com **data de cobrança diferente a cada mês**:

| Estabelecimento | MesFatura | Parcela | Data | Valor |
|---|---|---|---|---|
| ANUIDADE DIFERENCI | 202601 | 5/10 | **26/12/2025** | -73.50 |
| ANUIDADE DIFERENCI | 202602 | 6/10 | **26/01/2026** | -73.50 |

→ Datas diferentes → IdTransacao diferentes → **sem colisão** (funciona corretamente).

### 1.5 Escopo do Problema

- **Registros afetados:** ~21 (user_id=1), ~42 total (ambos os usuários)  
- **Falsos positivos confirmados em fatura-202602:** 14 transações bloqueadas  
- **Registros não parcelados (4207):** corretos, **não serão tocados**

---

## 2. Objetivo

Corrigir o algoritmo de deduplicação para que **cada parcela de uma compra parcelada gere um IdTransacao único e distinto**, eliminando os falsos positivos sem quebrar a lógica para transações não-parceladas.

### 2.1 Objetivos Específicos

1. **IdTransacao:** incluir `parcela_atual/total` na chave quando a transação for parcelada
2. **IdParcela:** substituir fórmula baseada em nome de estabelecimento por fórmula baseada em `banco|tipo|data|valor|total` (mais robusta, sem variações de texto PDF/CSV)
3. **Migração v5.1:** recalcular apenas os ~42 registros parcelados no banco atual
4. **Backward compatibility:** transações não-parceladas continuam gerando exatamente o mesmo hash da v5

---

## 3. User Stories

### US-01: Upload sem falso-positivo
> **Como** usuário importando a fatura de fevereiro/2026,  
> **Quero** que as 14 compras parceladas (parcela 2/N, 3/N, etc.) sejam reconhecidas como **novas** transações,  
> **Para que** o sistema as importe corretamente em vez de bloqueá-las.

**Acceptance Criteria:**
- [ ] Ao re-importar fatura-202602 após fix + migração: resultado deve ser `Já Importadas (31)` + `Novas (14)` — nunca mais `Já Importadas (45)`
- [ ] As 14 novas transações são inseridas corretamente no banco com os campos `parcela_atual`, `TotalParcelas`, `MesFatura` corretos

### US-02: Idempotência mantida
> **Como** usuário que acidentalmente re-faz upload do mesmo arquivo,  
> **Quero** que o sistema continue detectando duplicatas corretamente,  
> **Para que** transações não sejam inseridas em dobro.

**Acceptance Criteria:**
- [ ] Re-upload da mesma fatura (mesmo arquivo) → `Já Importadas (45)` (todas bloqueadas, incluindo as parceladas)
- [ ] Parceladas do mesmo MesFatura não são duplicadas mesmo com o fix

### US-03: Dados históricos preservados
> **Como** usuário com histórico importado nos sprints anteriores,  
> **Quero** que meu histórico (4207 transações não-parceladas) permaneça intacto,  
> **Para** que o fix não introduza regressões.

**Acceptance Criteria:**
- [ ] Todos os 4207 registros não-parcelados mantêm exatamente o mesmo `IdTransacao` após a migração
- [ ] Apenas os ~42 registros com `TotalParcelas IS NOT NULL` são atualizados

### US-04: IdParcela consistente entre formatos
> **Como** sistema de agrupamento de parcelas,  
> **Quero** que `LOJA (1/12)` (formato CSV antigo) e `LOJA 01/12` (formato PDF) gerem o mesmo `IdParcela`,  
> **Para** que relatórios de parcelas agrupem corretamente independente do formato de origem.

**Acceptance Criteria:**
- [ ] `IdParcela` baseado em `banco|tipo|data|valor|total|user_id` é consistente entre formatos
- [ ] Parcelas do mesmo MesFatura geram mesmo `IdParcela` se mesmos dados

---

## 4. Escopo

### 4.1 Incluído

- ✅ Alterar assinatura de `generate_id_transacao` em `hasher.py` (adicionar param `parcela`)
- ✅ Corrigir `chave_unica` em `marker.py` para incluir parcela no hash local
- ✅ Corrigir chamada a `generate_id_transacao` em `marker.py` passando `parcela`
- ✅ Substituir fórmula de `IdParcela` em `marker.py`
- ✅ Script de migração `recalculate_id_transacao_v5_1.py` com dry-run
- ✅ Testes unitários: `test_hasher_parcelas.py` + `test_marker_parcelas.py`
- ✅ Atualizar `test_hash_user_id.py` (assinatura quebrada com nova versão)

### 4.2 Excluído

- ❌ Mudanças na UI (nenhuma necessária — erro era silencioso)
- ❌ Migração de produção (fica para Sprint 4 / próximo deploy)
- ❌ Processadores de outros bancos (BTG, MercadoPago) — mesma lógica, mesma correção automática via `marker.py`
- ❌ Mudança no schema da tabela `journal_entries` (campos já existem: `parcela_atual`, `TotalParcelas`)

---

## 5. Métricas de Sucesso

| Métrica | Antes do Fix | Meta Após Fix |
|---|---|---|
| Falsos positivos em fatura-202602 | 14 | 0 |
| Importados na fatura-202602 (novos) | 0 | 14 |
| Registros não-parcelados afetados | — | 0 |
| Testes unitários passando | — | 100% |
| Colisões de IdTransacao entre parcelas | ~14+ | 0 |

---

## 6. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Migração altera IDs de transações não-parceladas | Baixo | Alto | WHERE clause explícita: `TotalParcelas IS NOT NULL` |
| Usuário fez dedup manual das 14 parcelas | Médio | Baixo | Dry-run mostra registros antes de executar |
| IdParcela nova fórmula quebra agrupamentos existentes | Baixo | Médio | ~42 registros apenas; agrupamento por IdParcela ainda não é feature ativa na UI |
| Backward compat hasher.py quebrada | Baixo | Alto | Teste explícito `test_sem_parcela_backward_compat` |

---

## 7. Dependências

- Sprint 1 ✅ concluído (hasher.py v3.0.0, marker.py, router.py — commit `eda4ef12`)
- Sprint 2 ✅ concluído (migração v5 — commit `5fa5601f`, 8096 registros migrados)
- Fatura-202602 disponível para E2E test (arquivo CSV Itaú, 45 lançamentos)

---

## 8. Não Objetivos

- **Não** mudar a UI de upload (o problema era silencioso para o usuário)
- **Não** modificar como `MesFatura` é calculado (campo `YYYYmm`, correto)
- **Não** tratar parcelas de outros bancos separadamente (lógica unificada em `marker.py`)

---

## ✅ Stakeholder Aprovado

> Feature de correção crítica. Impede importação de compras parceladas após o primeiro mês. Prioridade máxima. — **Aprovado em 23/03/2026**
