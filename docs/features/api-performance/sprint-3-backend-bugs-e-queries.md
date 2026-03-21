# Sprint 3 — Backend: Bugs e Otimizações de Query

> **Escopo:** Backend only. Sem novos endpoints, sem mudanças no frontend.
> **Itens:** I1 (novo) · E1 · F1 · F6
> **Arquivos:** `transactions/models.py` · migration · `plano/service.py` · `dashboard/repository.py` · `investimentos/repository.py`
> **Pré-requisito:** Nenhum (pode iniciar em paralelo com Sprint 1 e 2)
> **Ordem obrigatória dentro do sprint:** I1 primeiro (os outros ficam mais rápidos depois dos índices)

---

## Índice

- [I1 — Índices compostos em journal\_entries](#i1--índices-compostos-em-journal_entries)
- [E1 — Fix projeção de economia (tela Plano)](#e1--fix-projeção-de-economia-tela-plano)
- [F1 — chart-data: 12 queries → 1](#f1--chart-data-12-queries--1)
- [F6 — Renomear campos confusos em get\_portfolio\_resumo](#f6--renomear-campos-confusos-em-get_portfolio_resumo)

---

## I1 — Índices compostos em journal_entries

**Problema:** `MesFatura` não tem índice algum na tabela `journal_entries`. Toda query de dashboard que filtra `WHERE user_id = ? AND MesFatura IN (...)` faz sequential scan dentro das linhas do usuário.
**Impacto:** 5–20× speedup em todas as queries de dashboard e plano. Efeito cumulativo com F1.
**Escopo:** Backend only — 1 migration, 1 alteração no model.
**Risco:** Baixo. `CREATE INDEX CONCURRENTLY` não bloqueia escritas em PostgreSQL.

---

### Estado atual (verificado nas migrations e no model)

```
Indexes existentes em journal_entries:
✅ ix_journal_entries_id           (id)
✅ ix_journal_entries_user_id      (user_id)   ← simples, não composto
✅ ix_journal_entries_IdTransacao  (IdTransacao, unique)
✅ ix_journal_entries_session_id   (session_id)
✅ ix_journal_entries_upload_history_id
✅ ix_journal_entries_fonte

❌ MesFatura        — sem índice algum
❌ (user_id, MesFatura)           — sem índice composto
❌ (user_id, MesFatura, CategoriaGeral) — sem índice composto
```

---

### Microação 1 — Adicionar índices compostos no model SQLAlchemy

**Arquivo:** `app_dev/backend/app/domains/transactions/models.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    # ... colunas existentes (não alterar) ...

    __table_args__ = (
        # Cobre: WHERE user_id = ? AND MesFatura = ?  (dashboard por mês)
        # Cobre: WHERE user_id = ? AND MesFatura IN (...)  (chart-data, F1)
        Index("idx_je_user_mesfatura", "user_id", "MesFatura"),

        # Cobre: GROUP BY MesFatura, CategoriaGeral com filtro user_id
        # Permite index-only scan no F1 (chart-data)
        Index("idx_je_user_mesfatura_cat_valor", "user_id", "MesFatura", "CategoriaGeral", "Valor"),

        # Cobre: WHERE user_id = ? AND IgnorarDashboard = 0 AND MesFatura = ?
        Index("idx_je_user_ignorar_mesfatura", "user_id", "IgnorarDashboard", "MesFatura"),
    )
```

> **Nota:** Se `JournalEntry` já tiver `__table_args__`, adicionar as entradas dentro da tupla existente, não criar outra.

---

### Microação 2 — Gerar e aplicar migration

```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add composite indexes to journal_entries"
```

Revisar o arquivo gerado — deve conter apenas `op.create_index(...)` sem nenhum `op.alter_column` (índices novos não mudam colunas).

```bash
docker exec finup_backend_dev alembic upgrade head
```

---

### Microação 3 — Verificar índices criados no banco

```bash
docker exec finup_backend_dev python -c "
from app.core.database import engine
from sqlalchemy import inspect
indexes = inspect(engine).get_indexes('journal_entries')
for idx in indexes:
    print(idx['name'], idx['column_names'])
"
```

Saída esperada incluir:
```
idx_je_user_mesfatura ['user_id', 'MesFatura']
idx_je_user_mesfatura_cat_valor ['user_id', 'MesFatura', 'CategoriaGeral', 'Valor']
idx_je_user_ignorar_mesfatura ['user_id', 'IgnorarDashboard', 'MesFatura']
```

---

### Microação 4 — Medir impacto com EXPLAIN ANALYZE

```bash
docker exec finup_backend_dev python -c "
from app.core.database import SessionLocal
db = SessionLocal()

# Simular a query do F1 (chart-data)
result = db.execute('''
    EXPLAIN ANALYZE
    SELECT \"MesFatura\",
           SUM(CASE WHEN \"CategoriaGeral\" = 'Receita' THEN \"Valor\" ELSE 0 END) AS receitas,
           SUM(CASE WHEN \"CategoriaGeral\" = 'Despesa' THEN \"Valor\" ELSE 0 END) AS despesas
    FROM journal_entries
    WHERE user_id = 1
      AND \"MesFatura\" IN ('202501','202502','202503','202504','202505','202506',
                            '202507','202508','202509','202510','202511','202512')
      AND \"IgnorarDashboard\" = 0
    GROUP BY \"MesFatura\"
''')
for row in result:
    print(row[0])
db.close()
"
```

Antes dos índices: `Seq Scan` ou `Bitmap Heap Scan` com custo alto.
Depois dos índices: `Index Scan` ou `Index Only Scan` com custo ~10× menor.

---

### Checklist I1

- [ ] Model atualizado com `__table_args__` contendo os 3 índices
- [ ] Migration gerada e aplicada (`alembic upgrade head`)
- [ ] `alembic downgrade -1` funciona (índices removidos)
- [ ] EXPLAIN ANALYZE mostra `Index Scan` (não `Seq Scan`) nas queries de dashboard
- [ ] Latência de `GET /dashboard/chart-data` medida antes e depois

---

## E1 — Fix projeção de economia (tela Plano)

**Problema:** A curva laranja ("Real + Economia") ignora os valores extraordinários. A fórmula atual cancela créditos e débitos extraordinários algebricamente, resultando em linha suavizada sem sazonalidade.
**Impacto:** Bug de lógica — curva mostra valores incorretos para meses com IPVA, 13º, bônus.
**Escopo:** Backend only — 1 função, ~15 linhas.
**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

---

### Fórmula correta

```
saldo_mes = renda - gastos_rec × (1 - %economia) + creditos_extras - debitos_extras
```

Mapeado para campos do cashflow (todos já existem):
```
m["renda_esperada"] - m["gastos_recorrentes"] × fator + m["extras_creditos"] - m["extras_debitos"]
```

O slider de economia só reduz os `gastos_recorrentes`. Créditos e débitos extraordinários passam integralmente.

---

### Microação 1 — Localizar o branch 2 de `get_projecao()`

**Arquivo:** `app_dev/backend/app/domains/plano/service.py` — buscar por `else:` dentro de `get_projecao`, aproximadamente nas linhas 511–528.

Identificar o bloco que calcula `saldo_mes` para meses futuros (o `else` do `if m.get("use_realizado")`).

---

### Microação 2 — Substituir o bloco else pelo código correto

```python
# Substituir o bloco else (branch 2) por:
else:
    # Curva laranja — fórmula: renda - gastos_rec*(1-%eco) + Ce - De
    for i, m in enumerate(cashflow["meses"][:meses]):
        if m.get("use_realizado"):
            # Meses passados: usar valores realizados diretamente
            renda_real  = m.get("renda_realizada") or 0.0
            gastos_real = m.get("gastos_realizados") or 0.0
            invest_real = m.get("investimentos_realizados") or 0.0
            saldo_mes   = renda_real - gastos_real - invest_real
        else:
            # Meses futuros: slider reduz APENAS gastos recorrentes
            renda_base      = m.get("renda_esperada") or 0.0
            gastos_rec      = m.get("gastos_recorrentes") or 0.0
            creditos_extras = m.get("extras_creditos") or 0.0
            debitos_extras  = m.get("extras_debitos") or 0.0
            saldo_mes = (
                renda_base
                - gastos_rec * fator
                + creditos_extras
                - debitos_extras
            )
        acumulado += saldo_mes
        serie.append({
            "mes": i + 1,
            "mes_referencia": m["mes_referencia"],
            "saldo_mes": round(saldo_mes, 2),
            "acumulado": round(acumulado, 2),
        })
```

---

### Checklist E1

- [ ] Curva laranja mostra dip nos meses com débitos extraordinários (IPVA, seguros)
- [ ] Curva laranja mostra spike nos meses com créditos extraordinários (13º, bônus)
- [ ] Slider em 0%: curva laranja = curva azul (meses futuros sem redução)
- [ ] Débitos extras NÃO são reduzidos pelo slider
- [ ] Meses passados (`use_realizado=True`) não são afetados pela mudança

---

## F1 — chart-data: 12 queries → 1

**Problema:** `GET /dashboard/chart-data` executa 12 queries SQL em loop (1 por mês). Mesmo com cache N4a, o cold start sempre executa 12 queries.
**Impacto:** Cold start do chart: ~600ms (12×50ms) → ~50ms (1 query).
**Escopo:** Backend only — 1 função, mesma interface de retorno.
**Arquivo:** `app_dev/backend/app/domains/dashboard/repository.py` — função `get_chart_data()` (~linha 299)

---

### Microação 1 — Reescrever `get_chart_data()` com 1 query usando IN + GROUP BY

```python
def get_chart_data(self, user_id: int, year: int, month: int) -> List[Dict]:
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    reference_date = datetime(year, month if month > 0 else 12, 1)

    # Montar lista dos 12 mes_fatura na ordem correta (mais antigo → mais novo)
    meses_fatura = []
    meses_meta = []  # para reconstruir date/year/month depois
    for i in range(11, -1, -1):
        d = reference_date - relativedelta(months=i)
        meses_fatura.append(f"{d.year}{d.month:02d}")
        meses_meta.append((d.year, d.month))

    # 1 query com IN + GROUP BY em vez de 12 queries separadas
    rows = self.db.query(
        JournalEntry.MesFatura,
        func.sum(case(
            (JournalEntry.CategoriaGeral == 'Receita', JournalEntry.Valor), else_=0
        )).label('receitas'),
        func.abs(func.sum(case(
            (JournalEntry.CategoriaGeral == 'Despesa', JournalEntry.Valor), else_=0
        ))).label('despesas')
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.MesFatura.in_(meses_fatura),
        JournalEntry.IgnorarDashboard == 0
    ).group_by(JournalEntry.MesFatura).all()

    by_mes = {r.MesFatura: r for r in rows}

    return [
        {
            "date": f"{ano}-{mes:02d}-01",
            "receitas": float(by_mes[mf].receitas or 0) if mf in by_mes else 0.0,
            "despesas": float(by_mes[mf].despesas or 0) if mf in by_mes else 0.0,
            "year": ano,
            "month": mes,
        }
        for mf, (ano, mes) in zip(meses_fatura, meses_meta)
    ]
```

---

### Verificar imports necessários

Confirmar que os seguintes imports já estão no arquivo (adicionar se faltar):

```python
from sqlalchemy import func, case
```

---

### Checklist F1

- [ ] Shape idêntico: cada item tem `date`, `receitas`, `despesas`, `year`, `month`
- [ ] Meses sem transações retornam `receitas: 0.0, despesas: 0.0` (não ficam ausentes)
- [ ] Cache N4a continua funcionando (usa `date` como key — não muda)
- [ ] Resultado numérico idêntico ao original para meses com dados
- [ ] DevTools: apenas 1 query no banco ao chamar `GET /dashboard/chart-data`

---

## F6 — Renomear campos confusos em `get_portfolio_resumo`

**Problema:** Os campos `total_investido`, `valor_atual` e `rendimento_total` têm nomes que não correspondem ao conteúdo real. São respectivamente `total_ativos`, `total_passivos` e `patrimonio_liquido`. Armadilha para manutenção futura.
**Impacto:** Clareza de código — sem impacto em performance. Risco baixo com backward-compat.
**Escopo:** Backend — 2 arquivos (repository de investimentos + repository de dashboard).

---

### Microação 1 — Renomear no retorno de `get_portfolio_resumo()`

**Arquivo:** `app_dev/backend/app/domains/investimentos/repository.py` (~linha 462)

```python
# Antes (nomes confusos)
return {
    'total_investido': total_ativos,
    'valor_atual': total_passivos,
    'rendimento_total': patrimonio_liquido,
    ...
}

# Depois (nomes descritivos + backward-compat por 1 ciclo)
return {
    'total_ativos': total_ativos,
    'total_passivos': total_passivos,
    'patrimonio_liquido': patrimonio_liquido,
    # deprecated — remover após atualizar todos os consumers
    'total_investido': total_ativos,
    'valor_atual': total_passivos,
    'rendimento_total': patrimonio_liquido,
    ...
}
```

---

### Microação 2 — Atualizar consumer em `dashboard/repository.py`

**Arquivo:** `app_dev/backend/app/domains/dashboard/repository.py` (~linhas 230–232)

```python
# Antes
ativos_mes             = float(resumo.get("total_investido") or 0)
passivos_mes           = float(resumo.get("valor_atual") or 0)
patrimonio_liquido_mes = float(resumo.get("rendimento_total") or 0)

# Depois
ativos_mes             = float(resumo.get("total_ativos") or 0)
passivos_mes           = float(resumo.get("total_passivos") or 0)
patrimonio_liquido_mes = float(resumo.get("patrimonio_liquido") or 0)
```

---

### Microação 3 — Verificar consumers no frontend

Buscar no frontend por `total_investido`, `valor_atual`, `rendimento_total` e atualizar se existirem:

```bash
grep -r "total_investido\|valor_atual\|rendimento_total" app_dev/frontend/src/features/investimentos/
```

Atualizar os arquivos encontrados para usar os novos nomes.

---

### Checklist F6

- [ ] `get_portfolio_resumo()` retorna os 3 novos campos + os 3 deprecated
- [ ] `dashboard/repository.py` usa os novos nomes
- [ ] Frontend (se existir) atualizado para novos nomes
- [ ] Nenhum 500 ou KeyError em produção após o deploy

---

## Resumo do Sprint 3

| Item | Arquivo(s) | Risco | Impacto |
|------|-----------|-------|---------|
| **I1 — Índices compostos** | `transactions/models.py` + migration | Muito baixo | ⭐⭐⭐ todas as queries |
| E1 — Fix projeção economia | `plano/service.py` (~511-528) | Baixo | Bug corrigido |
| F1 — chart-data 1 query | `dashboard/repository.py` (~299) | Médio (verificar shape) | ⭐⭐ cold start chart |
| F6 — Renomear campos | `investimentos/repository.py`, `dashboard/repository.py` | Baixo (backward-compat) | Clareza código |

**Ordem obrigatória:** I1 → E1 → F6 → F1

I1 deve vir primeiro: os índices reduzem o custo base de todas as queries. F1 fica mais rápido ainda depois de I1 (1 query com índice vs 12 queries sem índice).
