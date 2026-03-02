# Performance — Oportunidades de Melhoria

**Data:** 01/03/2026
**Contexto:** App na VM apresentando lentidão. Auditoria identificou 15 gargalos no backend distribuídos por todos os domínios.
**Status:** Em discussão — pronto para priorização e implementação.

---

## 1. Visão Geral

O problema central é um **padrão repetido em vários domínios**: loops que fazem queries dentro de loops (N+1), ou queries sequenciais por mês que poderiam ser 1 query única com agregação. Isso multiplica o número de roundtrips ao banco e é a principal causa de lentidão.

### Resumo por severidade

| Severidade | Qtd | Descrição |
|------------|-----|-----------|
| Crítico | 2 | Queries sem `user_id` — dados entre usuários |
| Alto | 4 | Padrão "N queries por request" (loop × query) |
| Médio | 7 | N+1, filtros em Python, queries duplicadas |
| Baixo | 2 | Pequenas ineficiências |

---

## 2. Crítico — Risco de Dados Entre Usuários

Além de performance, esses dois são **bugs de integridade**: buscam dados sem filtrar por `user_id`, o que significa que se dois usuários tiverem grupos/marcações com o mesmo nome, os dados se misturam.

### 2.1 `grupos/repository.py` — `count_transacoes_by_grupo()`

```python
# PROBLEMA: sem filtro user_id
SELECT count(*) FROM journal_entries WHERE "GRUPO" = :grupo
```

**Fix:** adicionar `JournalEntry.user_id == user_id` no WHERE.

---

### 2.2 `marcacoes/service.py` — `count_transacoes_by_marcacao()`

Mesmo padrão — conta transações por marcação sem filtrar pelo usuário.

**Fix:** passar `user_id` como parâmetro e adicionar ao filtro da query.

---

## 3. Alto — Padrão "Loop × Query" (N queries por request)

O padrão problemático: um loop sobre N itens (meses, grupos) fazendo 1 ou mais queries por iteração. O total de queries por request cresce linearmente com N.

### 3.1 `plano/service.py` — `get_cashflow()` ← já em andamento

**Antes:** 4-5 queries por mês × 12 meses = **~60 queries por request**.

**Depois (em andamento):** `get_planejado_por_grupo_mes` centralizado + `expectativas_mes` materializada reduz para 2 queries + merge em memória.

**Padrão do fix:** pré-buscar todos os dados do ano em 1-2 queries, montar dict por `mes_referencia`, acessar em O(1) dentro do loop.

```python
# PATTERN (aplicar em todos os casos semelhantes)
# 1. Busca fora do loop — 1 query para o ano todo
dados_ano = {r.mes_referencia: r for r in query.filter(ano=ano).all()}
# 2. Acessa dentro do loop — O(1)
for mes in range(1, 13):
    dado = dados_ano.get(f"{ano}-{str(mes).zfill(2)}", default)
```

---

### 3.2 `dashboard/repository.py` — `get_chart_data()`

**Antes:** loop 12 meses com 1 query SQL por mês = **12 queries** para renderizar o gráfico.

```python
# PROBLEMA atual (pseudocódigo)
for mes in range(1, 13):
    resultado = db.query(sum(Valor)).filter(MesFatura=mes).scalar()  # query por mês
```

**Fix:** 1 query com `GROUP BY MesFatura` para o ano inteiro.

```python
# FIX
rows = db.query(
    JournalEntry.MesFatura,
    func.sum(JournalEntry.Valor)
).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.MesFatura.like(f"{ano}%"),
    JournalEntry.CategoriaGeral == "Despesa",
    JournalEntry.IgnorarDashboard == 0
).group_by(JournalEntry.MesFatura).all()

por_mes = {r.MesFatura: float(r[1]) for r in rows}
```

**Redução:** 12 queries → 1 query.

---

### 3.3 `dashboard/repository.py` — `get_metrics()`

**Problema:** Executa 6-8 queries separadas (receitas, despesas, cartões, transações, mês anterior, etc.) para montar o resumo do dashboard — endpoint chamado com alta frequência.

**Fix:** consolidar em 1-2 queries com `CASE WHEN CategoriaGeral = 'Receita' THEN Valor END` (conditional aggregation), reduzindo para 1 query que retorna todos os totais de uma vez.

**Redução estimada:** 6-8 queries → 1-2 queries.

---

### 3.4 `transactions/service.py` — `_propagate_to_padrao()`

**Problema:** Busca **todas as transações do usuário** com `.all()` (~milhares de registros), depois itera em Python checando estabelecimento e valor.

```python
# PROBLEMA: carrega tudo na memória
todas = db.query(JournalEntry).filter(user_id == user_id).all()
for t in todas:
    if t.Estabelecimento == target and t.Valor == valor: ...
```

**Fix:** mover o filtro para o SQL.

```python
# FIX: filtra no banco
matches = db.query(JournalEntry).filter(
    JournalEntry.user_id == user_id,
    JournalEntry.Estabelecimento == target,
    JournalEntry.Valor == valor
).all()
```

**Impacto:** para usuários com muitas transações, isso pode estar carregando dezenas de milhares de registros na memória a cada propagação.

---

## 4. Médio — N+1 e Filtros em Python

### 4.1 `marcacoes/service.py` — `get_grupos_com_subgrupos()`

**Problema (N+1 clássico):** para cada grupo único, faz 1 query buscando os subgrupos daquele grupo.

```python
# N+1: 1 query por grupo
for grupo in grupos_unicos:
    subgrupos = get_subgrupos_by_grupo(grupo)  # query aqui
```

**Fix:** 1 query com todos os grupos+subgrupos, agrupar em Python.

```python
# FIX: 1 query total
rows = db.query(JournalEntry.GRUPO, JournalEntry.SubGrupo).distinct().filter(...).all()
resultado = {}
for grupo, sub in rows:
    resultado.setdefault(grupo, []).append(sub)
```

---

### 4.2 `budget/service.py` — `calcular_media_3_meses()`

**Problema:** busca todas as transações dos 3 meses com `.all()`, soma em Python.

**Fix:** `func.sum()` + `GROUP BY GRUPO` no banco — retorna apenas os totais por grupo, sem carregar transações individuais na memória.

---

### 4.3 `budget/service.py` — `bulk_upsert_budget_planning()`

**Problema:** para cada budget na lista, faz 1 query de busca + 1 insert/update = 2N queries para upsert de N registros.

**Fix:** buscar todos os registros existentes em 1 query, fazer o diff em memória, depois 1 bulk insert + 1 bulk update.

---

### 4.4 `dashboard/repository.py` — `get_category_expenses()`

**Problema:** 2 queries separadas — uma para o total de despesas, outra para o breakdown por categoria.

**Fix:** 1 query com `GROUP BY` retorna o breakdown; o total é `sum()` do resultado em Python. Zero roundtrip extra.

---

### 4.5 `transactions/repository.py` — filtros duplicados

**Problema:** a lógica de filtro base (user_id, período, categoria) é repetida em `list_with_filters()`, `count_with_filters()`, `get_total_by_filters()` e `get_resumo()` — 4× o mesmo código.

**Fix:** método privado `_build_base_query(user_id, filtros)` reutilizado pelas 4 funções.

---

## 5. Baixo — Pequenas Ineficiências

### 5.1 `classification/service.py` — `import_hardcoded_rules()`

1 query por regra para verificar se já existe → substituir por 1 query trazendo todas as regras existentes, fazer o diff em Python, inserir apenas as novas.

### 5.2 `transactions/service.py` — `get_grupos_subgrupos_disponiveis()`

Busca todos os grupos/subgrupos e filtra `if r.GRUPO` em Python. Mover o `WHERE GRUPO IS NOT NULL AND GRUPO != ''` para o SQL.

---

## 6. Índices — O que Verificar

Queries que rodam em todo request e se beneficiam de índices compostos:

| Tabela | Índice recomendado | Usado em |
|--------|-------------------|----------|
| `journal_entries` | `(user_id, MesFatura)` | dashboard, cashflow, orcamento |
| `journal_entries` | `(user_id, CategoriaGeral, MesFatura)` | get_metrics, get_chart_data |
| `budget_planning` | `(user_id, mes_referencia, ativo)` | get_cashflow, get_orcamento |
| `expectativas_mes` | `(user_id, mes_referencia)` | get_expectativas_por_mes |
| `base_expectativas` | `(user_id, mes_referencia, status)` | fallback expectativas |

Se esses índices não existirem nas migrations, cada query faz full scan na tabela.

---

## 7. O Que Já Foi Corrigido

| Fix | Status | Impacto |
|-----|--------|---------|
| `get_planejado_por_grupo_mes` centralizado | ✅ Implementado | Elimina duplicação |
| `get_resumo` usa função central | ✅ Implementado | Budget + extras correto |
| `get_orcamento` usa função central | ✅ Implementado | Budget + extras correto |
| `get_expectativas_por_mes` lê de `expectativas_mes` | ✅ Implementado (com fallback) | Hot path O(1) |

---

## 8. Plano de Ataque Priorizado

| Prioridade | Fix | Esforço | Impacto |
|------------|-----|---------|---------|
| 1 | `grupos` e `marcacoes`: adicionar `user_id` nos filtros | 30min | Crítico — integridade |
| 2 | `dashboard.get_chart_data()`: 12 queries → 1 GROUP BY | 1h | Alto — dashboard é a home |
| 3 | `dashboard.get_metrics()`: consolidar em 1-2 queries | 1h | Alto — chamado frequentemente |
| 4 | `transactions._propagate_to_padrao()`: filtrar no banco | 1h | Alto — carrega tudo na memória |
| 5 | `marcacoes.get_grupos_com_subgrupos()`: N+1 → 1 query | 30min | Médio |
| 6 | `budget.calcular_media_3_meses()`: aggregate no banco | 30min | Médio |
| 7 | `budget.bulk_upsert_budget_planning()`: bulk operations | 1h | Médio |
| 8 | Verificar/criar índices compostos em `journal_entries` | 30min | Alto (custo baixo) |
| 9 | `transactions.repository`: extrair `_build_base_query` | 1h | Baixo (qualidade) |

**Total estimado:** ~7h para resolver todos os gargalos de médio a crítico.

---

## 9. Padrão a Evitar no Futuro

```python
# ❌ NUNCA: query dentro de loop
for mes in range(1, 13):
    valor = db.query(func.sum(...)).filter(mes=mes).scalar()

# ✅ SEMPRE: 1 query fora do loop, dict lookup dentro
por_mes = {r.mes: r.valor for r in db.query(...).group_by(mes).all()}
for mes in range(1, 13):
    valor = por_mes.get(mes, 0)

# ❌ NUNCA: carregar tudo e filtrar em Python
todos = db.query(Model).filter(user_id=uid).all()
resultado = [r for r in todos if r.campo == valor]

# ✅ SEMPRE: filtrar no banco
resultado = db.query(Model).filter(user_id=uid, campo=valor).all()

# ❌ NUNCA: query sem user_id em tabelas compartilhadas
db.query(JournalEntry).filter(GRUPO=grupo).count()

# ✅ SEMPRE: user_id obrigatório
db.query(JournalEntry).filter(user_id=uid, GRUPO=grupo).count()
```
