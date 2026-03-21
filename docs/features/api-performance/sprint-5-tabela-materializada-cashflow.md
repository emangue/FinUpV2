# Sprint 5 — Backend: Tabela Materializada Cashflow (A1)

> **Escopo:** Backend only. Frontend zero mudanças.
> **Itens:** A1 (único item, mas com 7 microações)
> **Pré-requisito:** Nenhum sprint anterior obrigatório. (Sprint 4/A2 pode usar a função nova se disponível)
> **Impacto:** `GET /plano/cashflow/mes`: 300-800ms → 20-50ms por request.

---

## Contexto

O endpoint `GET /plano/cashflow/mes?ano=Y&mes=M` atualmente chama `get_cashflow(db, user_id, ano)`, que computa os 12 meses do ano e descarta 11. Isso gera 48-60 queries SQL por requisição.

A solução é uma **tabela materializada** que persiste o resultado computado por mês. O endpoint passa a ler da tabela (leitura simples) e só recomputa quando os dados estão invalidados ou expirados.

---

## Microação 1 — Criar o model SQLAlchemy

**Arquivo:** `app_dev/backend/app/domains/plano/models.py`

Adicionar ao final do arquivo, após os models existentes:

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

class PlanoCashflowMes(Base):
    __tablename__ = "plano_cashflow_mes"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ano             = Column(Integer, nullable=False)
    mes             = Column(Integer, nullable=False)        # 1 a 12
    mes_referencia  = Column(String(7), nullable=False)     # 'YYYY-MM'

    # Realizados (de journal_entries)
    renda_realizada           = Column(Float, nullable=True)
    gastos_realizados         = Column(Float, nullable=True)
    investimentos_realizados  = Column(Float, nullable=True)

    # Planejados (de budget_planning + expectativas)
    renda_esperada     = Column(Float, nullable=True)
    gastos_recorrentes = Column(Float, nullable=True)
    extras_creditos    = Column(Float, nullable=True)
    extras_debitos     = Column(Float, nullable=True)

    # Computados (resultado final da lógica de negócio)
    renda_usada      = Column(Float, nullable=True)
    total_gastos     = Column(Float, nullable=True)
    aporte_planejado = Column(Float, nullable=True)
    aporte_usado     = Column(Float, nullable=True)

    # Flags
    use_realizado = Column(Boolean, nullable=True)
    status_mes    = Column(String(20), nullable=True)   # 'ok', 'atencao', 'critico'

    # Controle
    computed_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())
    invalidated  = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "ano", "mes", name="uq_plano_cashflow_mes"),
        Index("idx_plano_cashflow_mes_user_ano", "user_id", "ano"),
    )
```

---

## Microação 2 — Gerar a migration Alembic

```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add plano_cashflow_mes table"
```

Revisar o arquivo gerado em `app_dev/backend/migrations/versions/`. Verificar:
- `upgrade()` contém: `op.create_table("plano_cashflow_mes", ...)` com todos os campos, constraints e índices.
- `downgrade()` contém: `op.drop_table("plano_cashflow_mes")`.

---

## Microação 3 — Aplicar em dev e verificar

```bash
docker exec finup_backend_dev alembic upgrade head

# Verificar que a tabela foi criada corretamente
docker exec finup_backend_dev python -c "
from app.core.database import engine
from sqlalchemy import inspect
cols = inspect(engine).get_columns('plano_cashflow_mes')
print([c['name'] for c in cols])
"
```

Saída esperada: lista com todos os campos definidos no model.

---

## Microação 4 — Criar função de invalidação no service

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

Adicionar a função utilitária de invalidação. Ela será chamada por outros domínios após mutações:

```python
from app.domains.plano.models import PlanoCashflowMes

def invalidate_cashflow_cache(
    db: Session,
    user_id: int,
    mes_referencia: list[str] | None = None,   # ex: ['2026-02', '2026-03']
    ano_partir: int | None = None,              # invalida ano_partir em diante
):
    """
    Invalida entradas da tabela materializada.

    Casos de uso:
    - mes_referencia=['2026-02']: invalida meses específicos (após editar transação)
    - ano_partir=2026: invalida o ano inteiro e futuros (após mudar perfil financeiro)
    - ambos None: invalida tudo do usuário (uso excepcional)
    """
    query = db.query(PlanoCashflowMes).filter(
        PlanoCashflowMes.user_id == user_id
    )

    if mes_referencia:
        query = query.filter(PlanoCashflowMes.mes_referencia.in_(mes_referencia))
    elif ano_partir:
        query = query.filter(PlanoCashflowMes.ano >= ano_partir)

    query.update({"invalidated": True}, synchronize_session=False)
    db.commit()
```

---

## Microação 5 — Criar `get_cashflow_mes_cached` com lazy recompute

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

Adicionar após `invalidate_cashflow_cache`:

```python
from datetime import datetime, timezone, timedelta

CASHFLOW_MES_TTL_HOURS = 6   # recomputa se mais velho que 6h

def get_cashflow_mes_cached(
    db: Session,
    user_id: int,
    ano: int,
    mes: int,
) -> dict:
    cached = db.query(PlanoCashflowMes).filter_by(
        user_id=user_id, ano=ano, mes=mes, invalidated=False
    ).first()

    is_stale = (
        cached is None
        or (datetime.now(timezone.utc) - cached.computed_at) > timedelta(hours=CASHFLOW_MES_TTL_HOURS)
    )

    if not is_stale:
        return _cashflow_mes_to_dict(cached)

    # Recomputar usando a lógica existente
    computed = _compute_cashflow_mes(db, user_id, ano, mes)

    # Upsert na tabela materializada
    if cached:
        for key, value in computed.items():
            setattr(cached, key, value)
        cached.computed_at = datetime.now(timezone.utc)
        cached.invalidated = False
    else:
        db.add(PlanoCashflowMes(
            user_id=user_id, ano=ano, mes=mes,
            mes_referencia=f"{ano}-{mes:02d}",
            **computed,
        ))
    db.commit()

    return computed


def _cashflow_mes_to_dict(row: PlanoCashflowMes) -> dict:
    """Converte ORM para o formato de dict retornado pela função original."""
    return {
        "renda_realizada": row.renda_realizada,
        "gastos_realizados": row.gastos_realizados,
        "investimentos_realizados": row.investimentos_realizados,
        "renda_esperada": row.renda_esperada,
        "gastos_recorrentes": row.gastos_recorrentes,
        "extras_creditos": row.extras_creditos,
        "extras_debitos": row.extras_debitos,
        "renda_usada": row.renda_usada,
        "total_gastos": row.total_gastos,
        "aporte_planejado": row.aporte_planejado,
        "aporte_usado": row.aporte_usado,
        "use_realizado": row.use_realizado,
        "status_mes": row.status_mes,
    }
```

> **Nota:** `_compute_cashflow_mes` deve ser a função atual que já computa 1 mês isolado. Se não existir com esse nome, renomear ou criar um wrapper ao redor da lógica existente.

---

## Microação 6 — Plugar invalidações nos domínios que mutam dados

### `transactions/service.py` — após import de transações

**Arquivo:** `app_dev/backend/app/domains/transactions/service.py`

```python
from app.domains.plano.service import invalidate_cashflow_cache

# Dentro de after_import ou função equivalente, após inserir transações:
meses_afetados = list({
    t.MesFatura[:4] + '-' + t.MesFatura[4:6]   # 'YYYYMM' → 'YYYY-MM'
    for t in transacoes_inseridas
    if t.MesFatura and len(t.MesFatura) >= 6
})
if meses_afetados:
    invalidate_cashflow_cache(db, user_id, mes_referencia=meses_afetados)
```

### `budget/service.py` — após criar/editar/deletar budget_planning

**Arquivo:** `app_dev/backend/app/domains/budget/service.py`

```python
from app.domains.plano.service import invalidate_cashflow_cache

# Após upsert de budget_planning:
invalidate_cashflow_cache(db, user_id, mes_referencia=[item.mes_referencia])
```

### `plano/service.py` — após atualizar perfil financeiro

**Arquivo:** `app_dev/backend/app/domains/plano/service.py`

```python
from datetime import datetime

# Após atualizar user_financial_profile (renda, crescimento %):
ano_atual = datetime.now().year
invalidate_cashflow_cache(db, user_id, ano_partir=ano_atual)
```

---

## Microação 7 — Substituir chamada no router

**Arquivo:** `app_dev/backend/app/domains/plano/router.py`

```python
# Importar a função nova
from app.domains.plano.service import get_cashflow_mes_cached

# Antes (linha ~241-269)
@router.get("/cashflow/mes")
def cashflow_mes(ano: int, mes: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    resultado = get_cashflow(db, user_id, ano)   # computa 12 meses
    return resultado[mes - 1]

# Depois
@router.get("/cashflow/mes")
def cashflow_mes(ano: int, mes: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return get_cashflow_mes_cached(db, user_id, ano, mes)
```

---

## Checklist A1

- [ ] Model `PlanoCashflowMes` criado sem erros de import
- [ ] Migration gerada e aplicada em dev (`alembic upgrade head`)
- [ ] `alembic downgrade -1` funciona (rollback limpo)
- [ ] `get_cashflow_mes_cached` retorna o mesmo shape que a função original
- [ ] Invalidação chamada após:
  - [ ] Import de transações
  - [ ] Edição de transação individual
  - [ ] Criação/edição/deleção em budget_planning
  - [ ] Mudança em expectativas (extras_creditos / extras_debitos)
  - [ ] Atualização de perfil financeiro (renda, crescimento %)
- [ ] Teste manual: fazer upload → verificar cache invalidado → request seguinte recomputa → request posterior usa cache (0 queries SQL extras)
- [ ] Latência antes vs depois: `GET /plano/cashflow/mes` deve cair de ~95ms para < 20ms (cache hit)

---

## Resumo do Sprint 5

| Microação | Arquivo | O que faz |
|-----------|---------|-----------|
| 1 | `plano/models.py` | Cria o model ORM |
| 2 | `migrations/versions/` | Gera migration alembic |
| 3 | Terminal | Aplica migration e verifica |
| 4 | `plano/service.py` | Função de invalidação |
| 5 | `plano/service.py` | Função cached + to_dict |
| 6 | `transactions/service.py`, `budget/service.py`, `plano/service.py` | Plugar invalidações |
| 7 | `plano/router.py` | Substituir chamada no endpoint |

**Ordem obrigatória:** 1 → 2 → 3 → (4 e 5 em paralelo) → 6 → 7
