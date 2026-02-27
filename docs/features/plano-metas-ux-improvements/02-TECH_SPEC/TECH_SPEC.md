# TECH SPEC — Plano Financeiro Integrado

**Feature:** `plano-metas-ux-improvements`  
**Branch:** `feature/plano-metas-ux-improvements`  
**Data:** 26/02/2026  
**Status:** 🟡 Pronto para implementação  
**Referência UX:** `../UX_PLANO_FINANCEIRO_INTEGRADO.md`  
**Referência PRD:** `../PRD.md`

---

## 0. Visão geral

Esta feature entrega três camadas interligadas:

1. **Construtor de Plano** — wizard 4 etapas que substitui o fluxo de metas atual e unifica gastos + aposentadoria
2. **Cashflow engine** — motor de projeção que une realizado (`journal_entries`) + expectativas (`base_expectativas`) + plano base (`budget_planning`) em uma visão única por mês
3. **Nudge de aposentadoria** — para cada desvio do plano, calcula o impacto composto na data de aposentadoria

---

## 1. DAG — Ordem de implementação

```
NÍVEL 0 — Bugs (sem dependências, começar aqui)
├── B1: fix updateGoal replicarParaAnoTodo        ~3h
├── B2: fix router.back loop em [goalId]           ~1h
├── B3: fix scroll em /mobile/budget               ~1h
└── B4: fix formatação de /mobile/budget/edit      ~1h

NÍVEL 1 — Backend: banco (base para tudo)
├── M1: migration user_financial_profile           ~1h
└── M2: migration base_expectativas                ~2h

NÍVEL 2 — Backend: domínio plano (depende M1, M2)
├── P1: UserFinancialProfile CRUD                  ~2h
├── P2: BaseExpectativas CRUD                      ~2h
└── P3: Fase 6 no upload confirm                   ~3h

NÍVEL 3 — Backend: cashflow engine (depende P1, P2, P3)
└── C1: GET /budget/cashflow endpoint              ~4h
    ├── realizado: journal_entries agrupados
    ├── expectativas: base_expectativas pendentes
    ├── plano: budget_planning + inflação
    ├── budget-at-risk por grupo
    └── nudge aposentadoria (usa InvestimentoCenario)

NÍVEL 4 — Frontend: novo domínio (depende C1)
├── F1: bottom nav "Plano" + roteamento            ~2h
├── F2: /mobile/plano — Acompanhamento             ~4h
├── F3: /mobile/construir-plano — wizard etapa 1   ~3h
├── F4: /mobile/construir-plano — wizard etapa 2   ~3h
├── F5: /mobile/construir-plano — wizard etapa 3   ~3h
└── F6: /mobile/construir-plano — wizard etapa 4   ~3h

NÍVEL 5 — Integração (depende F1–F6)
├── I1: atualizar CTAs existentes (carteira, plano-aposentadoria-tab)
└── I2: smoke tests E2E do fluxo completo
```

**Estimativa total:** ~40h  
**Caminho crítico:** M2 → P3 → C1 → F2

---

## 2. Banco de dados — migrations

### 2.1 `user_financial_profile` (nova tabela)

Armazena a renda mensal e parâmetros globais do plano do usuário.

```python
# alembic: migration — add_user_financial_profile
class UserFinancialProfile(Base):
    __tablename__ = "user_financial_profile"

    id             = Column(Integer, primary_key=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Renda
    renda_mensal   = Column(Numeric(15, 2), nullable=False)    # renda líquida mensal recorrente
    inflacao_pct   = Column(Numeric(5, 2), default=5.0)        # % a.a. para correção dos gastos

    # Controle
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_financial_profile_user", "user_id"),
    )
```

```bash
# gerar migration
docker exec finup_backend_dev alembic revision --autogenerate \
  -m "add_user_financial_profile"
docker exec finup_backend_dev alembic upgrade head
```

---

### 2.2 `base_expectativas` (nova tabela)

Camada de projeção — tudo que é esperado para meses futuros, sem sujar `base_parcelas` (realizado).

```python
# alembic: migration — add_base_expectativas
class BaseExpectativas(Base):
    __tablename__ = "base_expectativas"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # O quê
    descricao        = Column(String(200))               # "IPVA 2026" | "LOJA AMERICANAS 5/12"
    valor            = Column(Numeric(15, 2), nullable=False)
    grupo            = Column(String(100))               # espelha budget_planning.grupo
    tipo_lancamento  = Column(String(10), default="debito")  # 'debito' | 'credito'

    # Quando
    mes_referencia   = Column(String(7), nullable=False, index=True)  # "2026-05"

    # Origem
    tipo_expectativa = Column(String(30), nullable=False)
    # 'sazonal_plano'  → usuário declarou no Construtor
    # 'renda_plano'    → renda extraordinária declarada
    # 'parcela_futura' → derivada automaticamente de base_parcelas

    origem           = Column(String(20), nullable=False)
    # 'usuario' | 'sistema'

    # Link para base_parcelas (preenchido quando tipo='parcela_futura')
    id_parcela       = Column(String(64), index=True)    # FK lógica → base_parcelas.id_parcela
    parcela_seq      = Column(Integer)                   # seq desta parcela (ex: 5)
    parcela_total    = Column(Integer)                   # total da série (ex: 12)

    # Conciliação
    status           = Column(String(20), default="pendente", index=True)
    # 'pendente' | 'realizado' | 'divergente' | 'cancelado'

    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    valor_realizado  = Column(Numeric(15, 2))             # valor efetivo (pode diferir)
    realizado_em     = Column(DateTime)

    # Temporal
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        # Evita duplicar parcelas futuras geradas pelo sistema
        UniqueConstraint("user_id", "id_parcela", "parcela_seq",
                         name="uq_expectativa_parcela"),
        Index("idx_expectativas_user_mes", "user_id", "mes_referencia"),
        Index("idx_expectativas_status", "status"),
    )
```

```bash
docker exec finup_backend_dev alembic revision --autogenerate \
  -m "add_base_expectativas"
docker exec finup_backend_dev alembic upgrade head
```

---

### 2.3 Sem alterações em `budget_planning`

A decisão do UX doc de adicionar campos de parcela em `budget_planning` foi **revisada** — parcelas do plano entram em `base_expectativas` (com `tipo='sazonal_plano'` e os campos `parcela_seq`/`parcela_total`). `budget_planning` fica apenas com metas recorrentes mensais por grupo. Isso mantém o modelo mais limpo.

---

## 3. Backend — novos domínios e serviços

### 3.1 Domínio: `plano`

Novo domínio em `app_dev/backend/app/domains/plano/`. Não estender `budget` — responsabilidades diferentes.

```
app/domains/plano/
├── __init__.py
├── models.py       → UserFinancialProfile, BaseExpectativas (imports dos modelos)
├── schemas.py      → schemas Pydantic
├── repository.py   → queries SQL isoladas
├── service.py      → lógica de negócio + cashflow engine + nudge
└── router.py       → endpoints FastAPI
```

---

### 3.2 Schemas (`schemas.py`)

```python
# --- Financial Profile ---
class FinancialProfileUpsert(BaseModel):
    renda_mensal: Decimal
    inflacao_pct: Decimal = 5.0

class FinancialProfileResponse(FinancialProfileUpsert):
    id: int
    user_id: int
    updated_at: datetime

# --- Expectativas ---
class ExpectativaCreate(BaseModel):
    descricao: str
    valor: Decimal
    grupo: str
    tipo_lancamento: Literal["debito", "credito"] = "debito"
    mes_referencia: str                            # "YYYY-MM"
    tipo_expectativa: Literal[
        "sazonal_plano", "renda_plano", "parcela_futura"
    ]
    # Parcelamento (opcional)
    parcela_seq:   Optional[int] = None
    parcela_total: Optional[int] = None
    # Evolução anual (opcional, só para tipo != 'parcela_futura')
    evolucao_pct:  Optional[Decimal] = None        # % a.a. ex: 7.0

class ExpectativaResponse(ExpectativaCreate):
    id: int
    origem: str
    status: str
    valor_realizado: Optional[Decimal] = None
    realizado_em:    Optional[datetime] = None

# --- Cashflow ---
class GrupoStatus(BaseModel):
    grupo: str
    orcamento: Decimal                    # budget_planning.valor_planejado
    realizado: Decimal                    # journal_entries somados
    esperado_extra: Decimal               # base_expectativas pendentes do mês
    total_projetado: Decimal              # realizado + esperado_extra
    pct_orcamento: float                  # total_projetado / orcamento * 100
    status_previsao: Literal["ok", "atencao", "estouro"]
    # 'ok' ≤ 100%  |  'atencao' ≤ 120%  |  'estouro' > 120%
    nudge_aposentadoria: Optional[Decimal] = None  # impacto composto no patrimônio

class MesCashflow(BaseModel):
    mes_referencia: str                   # "2026-03"
    renda_esperada: Decimal               # financial_profile.renda_mensal + expectativas crédito
    gastos_recorrentes: Decimal           # sum(budget_planning)
    gastos_extras_esperados: Decimal      # sum(base_expectativas debito pendentes)
    gastos_realizados: Decimal            # sum(journal_entries) — apenas meses passados/atual
    aporte_planejado: Decimal             # do cenário de aposentadoria
    saldo_projetado: Decimal              # renda - gastos - aporte
    status_mes: Literal["ok", "atencao", "estouro", "realizado", "parcial"]
    grupos: List[GrupoStatus]
    expectativas: List[ExpectativaResponse]
    nudge_aposentadoria_mes: Optional[Decimal] = None  # impacto composto deste mês

class CashflowResponse(BaseModel):
    ano: int
    nudge_acumulado: Optional[Decimal] = None  # soma ponderada Jan–hoje
    meses: List[MesCashflow]
```

---

### 3.3 Repository (`repository.py`)

```python
class PlanoRepository:
    def __init__(self, db: Session): self.db = db

    # Financial Profile
    def get_profile(self, user_id: int) -> Optional[UserFinancialProfile]: ...
    def upsert_profile(self, user_id: int, data: FinancialProfileUpsert) -> UserFinancialProfile: ...

    # Expectativas
    def list_expectativas(self, user_id: int, mes: str) -> List[BaseExpectativas]: ...
    def create_expectativa(self, user_id: int, data: dict) -> BaseExpectativas: ...
    def upsert_expectativa_parcela(self, user_id: int, data: dict) -> None:
        # ON CONFLICT (user_id, id_parcela, parcela_seq) DO NOTHING
        ...
    def marcar_realizado(self, expectativa_id: int,
                          journal_entry_id: int, valor_realizado: Decimal) -> None: ...

    # Cashflow queries
    def get_realizado_por_grupo(self, user_id: int, mes: str) -> Dict[str, Decimal]:
        # SUM(ValorPositivo) GROUP BY GRUPO de journal_entries
        # filtro: Ano+Mes do MesFatura, CategoriaGeral='Despesa', IgnorarDashboard=0
        ...

    def get_budget_planning(self, user_id: int, mes: str) -> Dict[str, Decimal]:
        # SELECT grupo, valor_planejado FROM budget_planning
        # WHERE user_id=X AND mes_referencia=Y AND ativo=1
        ...

    def get_expectativas_mes(self, user_id: int, mes: str) -> List[BaseExpectativas]:
        # WHERE user_id=X AND mes_referencia=Y AND status IN ('pendente','divergente')
        ...

    def get_cenario_principal(self, user_id: int) -> Optional[InvestimentoCenario]:
        # WHERE user_id=X AND principal=True AND ativo=True
        ...
```

---

### 3.4 Service — Cashflow Engine (`service.py`)

```python
class PlanoService:
    def __init__(self, db: Session):
        self.repo = PlanoRepository(db)

    def get_cashflow(self, user_id: int, ano: int) -> CashflowResponse:
        profile  = self.repo.get_profile(user_id)
        cenario  = self.repo.get_cenario_principal(user_id)
        hoje     = date.today()

        nudge_acumulado = Decimal(0)
        meses_response  = []

        for mes_num in range(1, 13):
            mes_ref = f"{ano}-{mes_num:02d}"
            anomes  = ano * 100 + mes_num

            # 1. Dados do mês
            budget   = self.repo.get_budget_planning(user_id, mes_ref)
            extras   = self.repo.get_expectativas_mes(user_id, mes_ref)
            realizado = (
                self.repo.get_realizado_por_grupo(user_id, mes_ref)
                if anomes <= hoje.year * 100 + hoje.month
                else {}
            )

            # 2. Renda esperada = perfil + expectativas crédito do mês
            creditos_mes = sum(e.valor for e in extras if e.tipo_lancamento == "credito")
            renda_mes    = (profile.renda_mensal if profile else Decimal(0)) + creditos_mes

            # 3. Gastos extras (débito) do mês
            debitos_mes = sum(e.valor for e in extras if e.tipo_lancamento == "debito")

            # 4. Aporte planejado do cenário
            aporte_plan = cenario.aporte_mensal if cenario else Decimal(0)

            # 5. Grupos com budget-at-risk
            grupos = self._build_grupos(budget, realizado, extras, cenario, anomes)

            # 6. Saldo projetado
            gastos_rec     = sum(budget.values())
            gastos_real    = sum(realizado.values())
            gastos_plan    = gastos_real if realizado else gastos_rec
            saldo_projetado = renda_mes - gastos_plan - debitos_mes - aporte_plan

            # 7. Status do mês
            status_mes = self._mes_status(anomes, hoje, saldo_projetado)

            # 8. Nudge do mês (apenas se cenário configurado)
            nudge_mes = None
            if cenario and realizado:
                nudge_mes = self._calc_nudge_mes(
                    delta_aporte = aporte_plan - gastos_real,  # simplificado
                    cenario      = cenario,
                    anomes_mes   = anomes
                )
                nudge_acumulado += nudge_mes

            meses_response.append(MesCashflow(
                mes_referencia        = mes_ref,
                renda_esperada        = renda_mes,
                gastos_recorrentes    = gastos_rec,
                gastos_extras_esperados = debitos_mes,
                gastos_realizados     = gastos_real,
                aporte_planejado      = aporte_plan,
                saldo_projetado       = saldo_projetado,
                status_mes            = status_mes,
                grupos                = grupos,
                expectativas          = [ExpectativaResponse.from_orm(e) for e in extras],
                nudge_aposentadoria_mes = nudge_mes
            ))

        return CashflowResponse(
            ano             = ano,
            nudge_acumulado = nudge_acumulado if nudge_acumulado != 0 else None,
            meses           = meses_response
        )

    def _build_grupos(self, budget, realizado, extras, cenario, anomes) -> List[GrupoStatus]:
        """Une budget_planning + base_expectativas + realizado por grupo."""
        todos_grupos = set(budget.keys()) | set(realizado.keys())
        resultado = []
        for grupo in todos_grupos:
            orcamento      = budget.get(grupo, Decimal(0))
            real           = realizado.get(grupo, Decimal(0))
            esperado_extra = sum(
                e.valor for e in extras
                if e.grupo == grupo and e.tipo_lancamento == "debito"
            )
            total          = real + esperado_extra
            pct            = float(total / orcamento * 100) if orcamento else 0
            status         = "ok" if pct <= 100 else ("atencao" if pct <= 120 else "estouro")

            nudge = None
            if cenario and real > 0:
                delta = real - float(orcamento)
                if abs(delta) >= 50:  # threshold mínimo
                    nudge = self._calc_nudge_mes(
                        delta_aporte=-delta,  # estouro = menos aporte
                        cenario=cenario,
                        anomes_mes=anomes
                    )

            resultado.append(GrupoStatus(
                grupo=grupo, orcamento=orcamento, realizado=real,
                esperado_extra=esperado_extra, total_projetado=total,
                pct_orcamento=pct, status_previsao=status,
                nudge_aposentadoria=nudge
            ))
        return resultado

    def _calc_nudge_mes(self, delta_aporte: float,
                         cenario: InvestimentoCenario,
                         anomes_mes: int) -> Decimal:
        """
        Calcula o impacto composto de um desvio no patrimônio da aposentadoria.

        nudge = Δaporte × (1 + taxa_mensal)^meses_restantes

        Campos do InvestimentoCenario usados:
          - rendimento_mensal_pct: taxa mensal (ex: 0.0080)
          - idade_atual, idade_aposentadoria: calcula meses restantes
          - anomes_inicio: YYYYMM do início da projeção (fallback)
        """
        taxa = float(cenario.rendimento_mensal_pct or 0.008)

        # Calcular meses restantes até aposentadoria
        if cenario.idade_atual and cenario.idade_aposentadoria:
            anos_faltantes    = (cenario.idade_aposentadoria - cenario.idade_atual)
            ano_aposentadoria = (anomes_mes // 100) + anos_faltantes
            anomes_apos       = ano_aposentadoria * 100 + (anomes_mes % 100)
        elif cenario.anomes_inicio and cenario.periodo_meses:
            anomes_apos = cenario.anomes_inicio + cenario.periodo_meses  # aproximado
        else:
            return Decimal(0)

        # Converter YYYYMM em meses para calcular diferença
        def anomes_to_months(ym): return (ym // 100) * 12 + (ym % 100)
        meses_restantes = anomes_to_months(anomes_apos) - anomes_to_months(anomes_mes)

        if meses_restantes <= 12:  # irrelevante perto da aposentadoria
            return Decimal(0)

        fator = (1 + taxa) ** meses_restantes
        nudge = delta_aporte * fator
        return Decimal(str(round(nudge, 2)))

    def _mes_status(self, anomes, hoje, saldo) -> str:
        hoje_anomes = hoje.year * 100 + hoje.month
        if anomes < hoje_anomes:
            return "realizado"
        if anomes == hoje_anomes:
            return "parcial"
        return "ok" if saldo >= 0 else ("atencao" if saldo > -500 else "estouro")
```

---

### 3.5 Fase 6 — Upload confirm (`upload/service.py`)

Adicionar após `_fase5_update_base_parcelas()`:

```python
def _fase6_conciliar_expectativas(self, user_id: int, upload_history_id: int) -> dict:
    """
    Fase 6: Concilia expectativas com transações confirmadas e cria expectativas futuras.

    PARTE A — marcar realizados:
      Para cada transação parcelada do upload:
        → busca base_expectativas pendente com mesmo id_parcela+parcela_seq
        → marca 'realizado' ou 'divergente' (threshold ±5%)

    PARTE B — criar expectativas futuras (todas as parcelas até o fim da série):
      Para cada base_parcelas WHERE status='ativa':
        → cria uma BaseExpectativas por parcela ainda não realizada
        → ON CONFLICT DO NOTHING (idempotente)
    """
    from app.domains.plano.models import BaseExpectativas
    from app.domains.transactions.models import JournalEntry, BaseParcelas

    THRESHOLD_DIVERGENCIA = 0.05  # 5%
    realizados = divergentes = criadas = 0

    # ── PARTE A ──────────────────────────────────────────────────────────────
    transacoes = self.db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.upload_history_id == upload_history_id,
        JournalEntry.IdParcela.isnot(None),
        JournalEntry.TotalParcelas > 1
    ).all()

    for t in transacoes:
        exp = self.db.query(BaseExpectativas).filter(
            BaseExpectativas.user_id == user_id,
            BaseExpectativas.id_parcela == t.IdParcela,
            BaseExpectativas.parcela_seq == t.parcela_atual,
            BaseExpectativas.status == "pendente"
        ).first()

        if exp:
            diff = abs(float(t.ValorPositivo) - float(exp.valor))
            ok   = diff / float(exp.valor) <= THRESHOLD_DIVERGENCIA
            exp.status           = "realizado" if ok else "divergente"
            exp.journal_entry_id = t.id
            exp.valor_realizado  = t.ValorPositivo
            exp.realizado_em     = datetime.now()
            realizados += 1 if ok else 0
            divergentes += 0 if ok else 1

    # ── PARTE B ──────────────────────────────────────────────────────────────
    parcelas_ativas = self.db.query(BaseParcelas).filter(
        BaseParcelas.user_id == user_id,
        BaseParcelas.status == "ativa"
    ).all()

    for p in parcelas_ativas:
        # data_inicio: "DD/MM/YYYY" → parse
        try:
            d0 = datetime.strptime(p.data_inicio, "%d/%m/%Y")
        except (ValueError, TypeError):
            continue

        for seq in range((p.qtd_pagas or 0) + 1, (p.qtd_parcelas or 1) + 1):
            # Calcular mês desta parcela
            mes_offset = seq - 1
            ano_p  = d0.year  + (d0.month - 1 + mes_offset) // 12
            mes_p  = (d0.month - 1 + mes_offset) % 12 + 1
            mes_ref = f"{ano_p}-{mes_p:02d}"

            nova = BaseExpectativas(
                user_id          = user_id,
                descricao        = f"{p.estabelecimento_base} {seq}/{p.qtd_parcelas}",
                valor            = p.valor_parcela,
                grupo            = p.grupo_sugerido,
                tipo_lancamento  = "debito",
                mes_referencia   = mes_ref,
                tipo_expectativa = "parcela_futura",
                origem           = "sistema",
                id_parcela       = p.id_parcela,
                parcela_seq      = seq,
                parcela_total    = p.qtd_parcelas,
                status           = "pendente",
                created_at       = datetime.now(),
                updated_at       = datetime.now(),
            )
            # ON CONFLICT (user_id, id_parcela, parcela_seq) → skip silencioso
            try:
                self.db.add(nova)
                self.db.flush()
                criadas += 1
            except Exception:
                self.db.rollback()  # ignorar conflito

    self.db.commit()
    return {"realizados": realizados, "divergentes": divergentes, "criadas": criadas}
```

**Onde chamar:** em `confirmar_upload()`, logo após `_fase5_update_base_parcelas()`:

```python
fase5 = self._fase5_update_base_parcelas(user_id, upload_history_id)
fase6 = self._fase6_conciliar_expectativas(user_id, upload_history_id)
```

---

### 3.6 Conciliação de sazonais (match automático)

Roda em `_fase6`, PARTE A extendida — depois de processar parcelas, tenta match de sazonais:

```python
# Para transações NÃO parceladas do upload:
transacoes_normais = [t for t in todas_transacoes if not t.IdParcela]

for t in transacoes_normais:
    mes_ref = f"{t.MesFatura[:4]}-{t.MesFatura[4:]}"  # "202604"→"2026-04"
    candidatas = self.db.query(BaseExpectativas).filter(
        BaseExpectativas.user_id       == user_id,
        BaseExpectativas.mes_referencia == mes_ref,
        BaseExpectativas.tipo_expectativa == "sazonal_plano",
        BaseExpectativas.status        == "pendente",
        BaseExpectativas.grupo         == t.GRUPO,
    ).all()

    for cand in candidatas:
        diff = abs(float(t.ValorPositivo) - float(cand.valor))
        if diff / float(cand.valor) <= 0.10:  # ±10% para sazonais
            ok = diff / float(cand.valor) <= 0.05
            cand.status           = "realizado" if ok else "divergente"
            cand.journal_entry_id = t.id
            cand.valor_realizado  = t.ValorPositivo
            cand.realizado_em     = datetime.now()
            break  # um match por transação
```

---

### 3.7 Router (`router.py`)

```python
router = APIRouter(tags=["Plano"])

# Financial Profile
@router.get("/plano/profile", response_model=FinancialProfileResponse)
def get_profile(user_id=Depends(get_current_user_id), db=Depends(get_db)):
    return PlanoService(db).get_profile(user_id)

@router.post("/plano/profile", response_model=FinancialProfileResponse)
def upsert_profile(data: FinancialProfileUpsert,
                   user_id=Depends(get_current_user_id), db=Depends(get_db)):
    return PlanoService(db).upsert_profile(user_id, data)

# Expectativas
@router.get("/plano/expectativas", response_model=List[ExpectativaResponse])
def list_expectativas(mes: str = Query(..., regex=r"^\d{4}-\d{2}$"),
                      user_id=Depends(get_current_user_id), db=Depends(get_db)):
    return PlanoService(db).list_expectativas(user_id, mes)

@router.post("/plano/expectativas", response_model=ExpectativaResponse, status_code=201)
def create_expectativa(data: ExpectativaCreate,
                       user_id=Depends(get_current_user_id), db=Depends(get_db)):
    return PlanoService(db).create_expectativa(user_id, data)

@router.delete("/plano/expectativas/{id}", status_code=204)
def delete_expectativa(id: int,
                       user_id=Depends(get_current_user_id), db=Depends(get_db)):
    PlanoService(db).delete_expectativa(user_id, id)

# Cashflow
@router.get("/plano/cashflow", response_model=CashflowResponse)
def get_cashflow(ano: int = Query(default=None),
                 user_id=Depends(get_current_user_id), db=Depends(get_db)):
    ano = ano or date.today().year
    return PlanoService(db).get_cashflow(user_id, ano)
```

**Registrar em `main.py`:**
```python
from app.domains.plano.router import router as plano_router
app.include_router(plano_router, prefix="/api/v1")
```

---

## 4. Frontend — rotas e componentes

### 4.1 Bottom nav (`bottom-navigation.tsx`)

**Mudança:** index 2 de `Metas` → `Plano`, path `/mobile/plano`, ícone `LineChart`.

```tsx
// src/components/mobile/bottom-navigation.tsx
// Linha atual (approx):
{ label: "Metas", icon: Target, path: "/mobile/budget" }
// → substituir por:
{ label: "Plano", icon: LineChart, path: "/mobile/plano" }
```

---

### 4.2 Nova rota: `/mobile/plano` (Acompanhamento)

**Arquivo:** `src/app/mobile/plano/page.tsx`

Lógica de navegação:
```tsx
// Se o usuário nunca configurou o plano financeiro → redirecionar para /mobile/construir-plano
// Senão → mostrar AcompanhamentoPlano
const { data: profile } = useSWR("/api/v1/plano/profile")
if (!profile) return <router.push("/mobile/construir-plano") />
```

**Componente principal:** `src/features/plano/components/acompanhamento-plano.tsx`

Props: recebe `CashflowResponse` do endpoint `GET /api/v1/plano/cashflow?ano=2026`.

Seções:
1. **Header nudge** — nudge acumulado (verde se positivo, vermelho se negativo)
2. **Mês atual** — saldo projetado + status
3. **Gastos vs plano por grupo** — barras com badge budget-at-risk
4. **Próximos meses com alertas** — lista de meses futuros com status de estouro
5. **CTA** — [Ver recibo do ano] [Editar plano]

---

### 4.3 Nova rota: `/mobile/construir-plano` (Wizard)

**Arquivo:** `src/app/mobile/construir-plano/page.tsx`

Wizard com estado local (4 etapas). Não usa URL para cada etapa — `step` é estado React.

```tsx
type WizardState = {
  step: 1 | 2 | 3 | 4
  // Etapa 1
  renda_mensal: number
  inflacao_pct: number
  ganhos_extras: ExpectativaCreate[]
  // Etapa 2
  budget_por_grupo: { grupo: string; valor: number }[]
  // Etapa 3
  sazonais: ExpectativaCreate[]
  // Etapa 4
  aporte_mensal: number
}
```

**Persistência:** ao avançar etapa, fazer `POST /api/v1/plano/profile` e `POST /api/v1/plano/expectativas` progressivamente — não aguardar o final do wizard para salvar (UX mais resiliente).

---

### 4.4 Componentes novos

| Componente | Path | Reutiliza |
|-----------|------|-----------|
| `AcompanhamentoPlano` | `features/plano/components/acompanhamento-plano.tsx` | `OrcamentoTab` como base |
| `CashflowRecibo` | `features/plano/components/cashflow-recibo.tsx` | `plano-chart.tsx` como base |
| `NudgeAposentadoriaCard` | `features/plano/components/nudge-card.tsx` | novo |
| `BudgetAtRiskBadge` | `features/plano/components/budget-at-risk-badge.tsx` | novo |
| `GrupoGastoEditor` | `features/plano/components/grupo-gasto-editor.tsx` | novo |
| `GastosExtraordinariosEditor` | `features/plano/components/gastos-extraordinarios-editor.tsx` | espelho de `AportesExtraordinarios` existente |
| `InflacaoSlider` | `features/plano/components/inflacao-slider.tsx` | novo (simples) |

**Componentes reutilizados sem modificação:**
- `GanhosExtraordinariosEditor` — mesmo componente de `PersonalizarPlanoLayout.tsx`
- `ReciboPorMes` — extrair de `plano-chart.tsx` (linhas 406+) como componente independente

---

### 4.5 CTAs a atualizar

| Arquivo | Mudança |
|---------|---------|
| `src/app/mobile/carteira/page.tsx` | `router.push('/mobile/dashboard?tab=patrimonio')` → `router.push('/mobile/plano')` |
| `src/features/dashboard/components/plano-aposentadoria-tab.tsx` | CTA "Personalizar plano" → `/mobile/construir-plano` |
| `src/app/mobile/budget/new/page.tsx` | Redirecionar para `/mobile/construir-plano` |
| `src/app/mobile/budget/edit/page.tsx` | Redirecionar para `/mobile/construir-plano` |

---

## 5. Bug fixes (nível 0 do DAG)

### B1 — `updateGoal` sem `replicarParaAnoTodo`

**Arquivo:** `src/features/goals/services/goals-api.ts`

`createGoal` já tem o loop de meses. `updateGoal` chama `bulk-upsert` diretamente sem replicar.

```typescript
// Adicionar em updateGoal(), antes de chamar bulk-upsert:
if (goalData.replicarParaAnoTodo) {
  const meses = Array.from({ length: 12 }, (_, i) => {
    const mes = String(i + 1).padStart(2, "0")
    return { ...goalData, mes_referencia: `${ano}-${mes}` }
  })
  // chamar bulk-upsert para cada mês
  for (const m of meses) {
    await fetch(`/api/v1/budget/planning/bulk-upsert`, { method: "POST", body: JSON.stringify(m) })
  }
  return
}
// fallback: atualização normal do mês específico
```

### B2 — Loop `router.back()` em `[goalId]/page.tsx`

**Arquivo:** `src/app/mobile/budget/[goalId]/page.tsx`

```typescript
// ❌ Atual
router.back()

// ✅ Correto — navegar para a lista de metas (futuro: /mobile/plano)
router.push("/mobile/budget")
// após renomeação:
// router.push("/mobile/plano")
```

### B3 — Scroll em `/mobile/budget`

**Arquivo:** `src/app/mobile/budget/page.tsx` (ou layout wrapper)

Adicionar `overflow-y-auto` e `h-full` no container da lista, garantir `pb-24` para não esconder atrás do bottom nav.

### B4 — Formatação de `/mobile/budget/edit`

**Arquivo:** `src/app/mobile/budget/edit/page.tsx`

Adicionar `max-w-md mx-auto` no wrapper + padding lateral `px-4`.

---

## 6. Fluxo de dados — diagrama

```
Upload confirm
  └── Fase 5: base_parcelas.qtd_pagas++
  └── Fase 6: base_expectativas (parcelas futuras criadas / sazonais conciliados)

Usuário configura plano (Construtor)
  └── POST /plano/profile         → user_financial_profile
  └── POST /plano/expectativas    → base_expectativas (tipo='sazonal_plano' | 'renda_plano')

GET /plano/cashflow?ano=2026
  ├── user_financial_profile      → renda_mensal, inflacao_pct
  ├── budget_planning             → orçamento recorrente por grupo
  ├── base_expectativas           → sazonais + parcelas futuras (status pendente)
  ├── journal_entries             → realizado (meses passados e atual)
  └── investimentos_cenarios      → taxa + prazo para nudge de aposentadoria
      │
      ▼
  CashflowResponse (12 meses)
      ├── Por mês: saldo, status, grupos, expectativas
      ├── Por grupo: orcamento, real, esperado_extra, status_previsao, nudge
      └── Topo: nudge_acumulado Jan–hoje
```

---

## 7. Responses de exemplo

### `GET /api/v1/plano/cashflow?ano=2026` (trecho)

```json
{
  "ano": 2026,
  "nudge_acumulado": -333.40,
  "meses": [
    {
      "mes_referencia": "2026-03",
      "renda_esperada": 15000.00,
      "gastos_recorrentes": 10700.00,
      "gastos_extras_esperados": 1267.00,
      "gastos_realizados": 650.00,
      "aporte_planejado": 2500.00,
      "saldo_projetado": -2000.00,
      "status_mes": "parcial",
      "nudge_aposentadoria_mes": -828.00,
      "grupos": [
        {
          "grupo": "Carro",
          "orcamento": 1000.00,
          "realizado": 650.00,
          "esperado_extra": 1267.00,
          "total_projetado": 1917.00,
          "pct_orcamento": 191.7,
          "status_previsao": "estouro",
          "nudge_aposentadoria": -2842.00
        }
      ],
      "expectativas": [
        {
          "id": 42,
          "descricao": "IPVA 2026 1/3",
          "valor": 1267.00,
          "grupo": "Carro",
          "tipo_lancamento": "debito",
          "mes_referencia": "2026-03",
          "tipo_expectativa": "parcela_futura",
          "origem": "sistema",
          "id_parcela": "abc123",
          "parcela_seq": 1,
          "parcela_total": 3,
          "status": "pendente"
        }
      ]
    }
  ]
}
```

---

## 8. Checklist de implementação

### Banco
- [ ] Migration `user_financial_profile` criada e aplicada
- [ ] Migration `base_expectativas` criada e aplicada
- [ ] Índices criados: `(user_id, mes_referencia)`, `(status)`, `(user_id, id_parcela, parcela_seq)`
- [ ] UNIQUE constraint `(user_id, id_parcela, parcela_seq)` funcionando

### Backend
- [ ] `app/domains/plano/` criado com models, schemas, repository, service, router
- [ ] Router registrado em `main.py`
- [ ] `_fase6_conciliar_expectativas()` adicionada em `upload/service.py`
- [ ] `_fase6_*` chamada após `_fase5_*` em `confirmar_upload()`
- [ ] `GET /plano/cashflow` retorna 12 meses com todos os campos
- [ ] Nudge calcula corretamente com `InvestimentoCenario.principal=True`
- [ ] Threshold de nudge: não mostrar se desvio < R$50 ou meses_restantes < 12

### Frontend
- [ ] Bottom nav: "Metas" → "Plano", path `/mobile/plano`
- [ ] `/mobile/plano`: redirect para construtor se sem perfil, senão acompanhamento
- [ ] `/mobile/construir-plano`: wizard 4 etapas funcional com estado local
- [ ] `AcompanhamentoPlano`: nudge no topo, gastos vs plano, alertas futuros
- [ ] `NudgeAposentadoriaCard`: mostra impacto por mês e running
- [ ] `BudgetAtRiskBadge`: ✅/⚠️/❌ baseado em `status_previsao`
- [ ] CTAs atualizados em carteira, plano-aposentadoria-tab, budget/new, budget/edit

### Bugs
- [ ] B1: `updateGoal` com `replicarParaAnoTodo`
- [ ] B2: `router.back()` → `router.push("/mobile/plano")`
- [ ] B3: scroll em `/mobile/budget` (ou `/mobile/plano`)
- [ ] B4: formatação de `/mobile/budget/edit`

### Testes
- [ ] Upload confirm com parcela 4/12 → cria expectativas 5..12 corretamente
- [ ] Upload seguinte com parcela 5/12 → marca expectativa 5 como `realizado`
- [ ] Sazonal IPVA declarado → match automático com ±10%
- [ ] Cashflow: mês passado usa `gastos_realizados`, mês futuro usa `gastos_recorrentes + extras`
- [ ] Nudge: sinal correto (estouro = negativo, economia = positivo)
- [ ] Nudge: não aparece se sem cenário de aposentadoria configurado

---

## Módulo 2 — Budget ↔ Patrimônio (conexão de aportes)

### 9. DAG incremental (depende do Módulo 1 estar concluído)

```
NÍVEL 0 — Banco (sem dependências)
├── N1: migration market_data_cache                ~30min
├── N2: migration investimentos_transacoes (+campos) ~30min
└── N3: migration investimentos_portfolio (+campos)  ~30min

NÍVEL 1 — Backend: jobs e dados externos (depende N1)
└── J1: job diário market_data_sync                ~3h
    ├── CDI/IPCA/SELIC via BCB (gratuito)
    └── cotações via brapi (token em .env)

NÍVEL 2 — Backend: domínio investimentos estendido (depende N2, N3)
├── V1: endpoint vínculo POST /investimentos/vincular-aporte  ~2h
├── V2: lógica de match automático (texto_match)              ~1h
├── V3: cálculo custo médio (track='variavel')                ~2h
├── V4: cálculo CDI acumulado (track='fixo')                  ~2h
└── V5: IR estimado sobre ganho de capital                    ~1h

NÍVEL 3 — Backend: upload Fase 7 (depende V1, V2)
└── U1: Fase 7 — detecta GRUPO='Investimentos' → fila de vínculo ~2h

NÍVEL 4 — Frontend: carteira enriquecida (depende J1, V3, V4, V5)
├── F1: badge "N aportes aguardando vínculo" na tela carteira  ~1h
├── F2: modal de match automático                              ~2h
├── F3: modal de vínculo manual (com sub-forms por track)      ~4h
├── F4: detalhe do produto com rentabilidade calculada         ~3h
└── F5: IR estimado no resumo do portfólio                     ~2h
```

**Estimativa total Módulo 2:** ~23h  
**Caminho crítico:** N1–N3 → J1 + V3/V4 → F3

---

### 10. Banco de dados — migrations do Módulo 2

#### 10.1 `market_data_cache` (nova tabela)

```python
class MarketDataCache(Base):
    __tablename__ = "market_data_cache"

    id              = Column(Integer, primary_key=True)
    tipo            = Column(String(20), nullable=False)
    # "acao" | "cdi" | "selic" | "ipca" | "igpm" | "incc"
    codigo          = Column(String(20), nullable=False)
    # "PETR4" | "MXRF11" | "CDI" | "SELIC" | "IPCA" | "IGPM" | "INCC"
    data_referencia = Column(Date, nullable=False)
    valor           = Column(Numeric(20, 8), nullable=False)
    # ação: preço em R$  |  CDI/SELIC: % ao dia  |  IPCA: % ao mês
    fonte           = Column(String(30), nullable=False)
    # "brapi" | "bcb"
    created_at      = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tipo", "codigo", "data_referencia",
                         name="uq_market_data_dia"),
        Index("idx_market_data_tipo_codigo", "tipo", "codigo"),
        Index("idx_market_data_data", "data_referencia"),
    )
```

```bash
docker exec finup_backend_dev alembic revision --autogenerate \
  -m "add_market_data_cache"
docker exec finup_backend_dev alembic upgrade head
```

---

#### 10.2 `investimentos_transacoes` — novos campos (nullable, zero impacto em prod)

```python
# alembic: migration — extend_investimentos_transacoes_v2

# Vínculo com budget
journal_entry_id = Column(Integer,
    ForeignKey("journal_entries.id", ondelete="SET NULL"),
    nullable=True, index=True)

# Track variavel — ações, FIIs, ETFs
codigo_ativo     = Column(String(20))        # "PETR4", "MXRF11"
quantidade       = Column(Numeric(15, 6))    # cotas (pode ser fracionária)
preco_unitario   = Column(Numeric(15, 6))    # preço por cota na data

# Track fixo — renda fixa
indexador        = Column(String(20))
# "CDI" | "SELIC" | "IPCA" | "IGPM" | "INCC" | "IPCA+X" | "PREFIXADO"
taxa_pct         = Column(Numeric(8, 4))
# Pós-fixado: 112.0 = 112% CDI  |  6.5 = IPCA + 6,5% a.a.
# Prefixado:  13.5  = 13,5% a.a. nominal (sem indexador externo)
regime           = Column(String(12))
# "prefixado"  — taxa fixa, capitalização diária pela taxa a.a.
# "pos_fixado" — indexado ao indicador (CDI, SELIC, IPCA, IGPM, INCC, IPCA+X)
# NULL         — não se aplica (variavel, snapshot, saldo_corretora)
data_vencimento  = Column(Date, nullable=True)
# NULL = liquidez diária (nunca vence)

# Proventos (preenchido quando tipo='rendimento')
tipo_proventos   = Column(String(30))
# "dividendo" | "jcp" | "rendimento_fii" | "juros_rf"
ir_retido        = Column(Numeric(15, 2))    # IR já retido na fonte (renda fixa)

# Operação e destino
tipo_operacao    = Column(String(10), default="aporte")
# "aporte" — compra / aplicação / depósito na corretora
# "venda"  — resgate / desinvestimento / retirada da posição
destino_resgate  = Column(String(20))
# "conta_bancaria"  → volta ao extrato bancário (conciliável com journal_entry)
# "saldo_corretora" → fica na corretora aguardando nova aplicação
# NULL              → não se aplica (tipo_operacao='aporte')
```

```bash
docker exec finup_backend_dev alembic revision --autogenerate \
  -m "extend_investimentos_transacoes_v2"
docker exec finup_backend_dev alembic upgrade head
```

---

#### 10.3 `investimentos_portfolio` — novos campos

```python
# alembic: migration — extend_investimentos_portfolio_v2

track        = Column(String(15), default="snapshot")
# "snapshot"         — Imóvel, FGTS, Previdência, Conta corrente pessoal
# "fixo"             — CDB, LCI, LCA, Tesouro Direto, Debêntures, Poupança
# "variavel"         — Ações, FIIs, ETFs, BDRs
# "saldo_corretora"  — Caixa na corretora aguardando nova aplicação

subtipo_ativo = Column(String(15))
# Para track='variavel': "acao" | "fii" | "etf" | "bdr"
# Determina a regra de IR: acao=15%+isenção R$20k; fii=20%; etf/bdr=15% sem isenção

regime       = Column(String(12))
# "prefixado" | "pos_fixado" | NULL (variavel, snapshot, saldo_corretora)

codigo_ativo = Column(String(20))
# "PETR4", "MXRF11" — usado para busca diária no brapi e custo médio

texto_match  = Column(String(200))
# Substring detectada no Estabelecimento do journal_entry
# Ex: "XP RENDA FIXA", "NUBANK CDB", "BTG PACTUAL"
# Match case-insensitive, partial
```

```bash
docker exec finup_backend_dev alembic revision --autogenerate \
  -m "extend_investimentos_portfolio_v2"
docker exec finup_backend_dev alembic upgrade head
```

---

#### 10.4 Regras de IR por tipo de ativo (tabela de referência)

| Tipo | `subtipo_ativo` | Alíquota | Isenção | Base legal |
|------|----------------|---------|---------|------------|
| Ações (swing trade) | `acao` | **15%** | ✅ Vendas brutas ≤ R$ 20.000/mês → IR = 0 | Art. 22, Lei 9.250/95 |
| FIIs (cotas) | `fii` | **20%** | ❌ Nenhuma — sem isenção de R$ 20k | Art. 3º, Lei 11.033/2004 |
| ETFs renda variável | `etf` | **15%** | ❌ Sem isenção | IN RFB 1.585/2015 |
| BDRs | `bdr` | **15%** | ❌ Sem isenção | IN RFB 1.585/2015 |
| Day trade | — | 20% | ❌ | App não rastreia intraday |

**Renda fixa — IR retido na fonte (tabela regressiva):**

| Prazo da aplicação | Alíquota |
|--------------------|----------|
| Até 180 dias | 22,5% |
| 181 a 360 dias | 20,0% |
| 361 a 720 dias | 17,5% |
| Acima de 720 dias | 15,0% |

> IR de renda fixa é sempre retido na fonte pela corretora/banco. O app exibe a alíquota estimada **para fins informativos** com base no prazo — **não entra no "IR estimado" do portfólio**.

**Isenção de R$ 20.000 para ações — detalhes de implementação:**
- Isenção é por CPF e por mês calendário (não por produto)
- O app agrega `SUM(valor_total)` de todas as transações `tipo_operacao='venda'` com `subtipo_ativo='acao'` no mês corrente para o user_id
- Se `total_vendas_mes ≤ R$20.000`: `ir_estimado = 0` e `ir_isento_este_mes = True`
- Limitação documentada: vendas em outras corretoras não capturadas pelo app reduzem o "espaço de isenção" real mas não são rastreadas

---

### 11. Job diário de cotações (`market_data_sync.py`)

**Path:** `scripts/jobs/market_data_sync.py`  
**Trigger:** APScheduler dentro do FastAPI — `cron` às 18h (após fechamento B3)  
**Registro em `main.py`:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(sync_market_data, "cron", hour=18, minute=0)
scheduler.start()
```

#### Implementação

```python
import requests
from datetime import date, timedelta
from sqlalchemy.dialects.postgresql import insert as pg_insert

BCB_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
BRAPI_BASE = "https://brapi.dev/api"

# Séries diárias — acumulação dia a dia útil
SERIES_BCB_DIARIOS = {
    "CDI":   4389,  # % ao dia — base dos pós-fixados CDI
    "SELIC": 11,    # % ao dia — meta SELIC over
}

# Séries mensais — variação mensal do índice de preços
SERIES_BCB_MENSAIS = {
    "IPCA":  433,   # % ao mês — IBGE via BCB
    "IGPM":  189,   # % ao mês — FGV via BCB (Índice Geral de Preços — Mercado)
    "INCC":  192,   # % ao mês — FGV via BCB (Índice Nac. de Custo da Construção)
}

def upsert_cache(db, tipo, codigo, data_ref, valor, fonte):
    stmt = pg_insert(MarketDataCache).values(
        tipo=tipo, codigo=codigo,
        data_referencia=data_ref, valor=valor, fonte=fonte
    ).on_conflict_do_nothing(
        constraint="uq_market_data_dia"
    )
    db.execute(stmt)

def sync_market_data(db: Session):
    hoje = date.today()
    ontem = hoje - timedelta(days=1)

    inicio_mes = hoje.replace(day=1)

    # ── BCB: séries DIÁRIAS (CDI, SELIC) ─────────────────────────────────
    for codigo, serie in SERIES_BCB_DIARIOS.items():
        ini = ontem.strftime("%d/%m/%Y")
        fim = hoje.strftime("%d/%m/%Y")
        r = requests.get(
            f"{BCB_BASE}.{serie}/dados"
            f"?formato=json&dataInicial={ini}&dataFinal={fim}",
            timeout=10
        )
        for item in r.json():
            dt = datetime.strptime(item["data"], "%d/%m/%Y").date()
            upsert_cache(db, codigo.lower(), codigo, dt, float(item["valor"]), "bcb")

    # ── BCB: séries MENSAIS (IPCA, IGPM, INCC) ───────────────────────────
    for codigo, serie in SERIES_BCB_MENSAIS.items():
        ini = inicio_mes.strftime("%d/%m/%Y")
        fim = hoje.strftime("%d/%m/%Y")
        r = requests.get(
            f"{BCB_BASE}.{serie}/dados"
            f"?formato=json&dataInicial={ini}&dataFinal={fim}",
            timeout=10
        )
        for item in r.json():
            # Data de referência: primeiro dia do mês publicado
            dt = datetime.strptime(item["data"], "%d/%m/%Y").date().replace(day=1)
            upsert_cache(db, codigo.lower(), codigo, dt, float(item["valor"]), "bcb")

    # ── brapi: ações, FIIs, ETFs ─────────────────────────────────────────
    codigos = db.execute(
        "SELECT DISTINCT codigo_ativo FROM investimentos_portfolio "
        "WHERE track = 'variavel' AND codigo_ativo IS NOT NULL AND ativo = TRUE"
    ).fetchall()
    codigos = [row[0] for row in codigos]

    token = settings.BRAPI_TOKEN  # variável de ambiente BRAPI_TOKEN
    for codigo in codigos:
        try:
            r = requests.get(
                f"{BRAPI_BASE}/quote/{codigo}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            preco = r.json()["results"][0]["regularMarketPrice"]
            upsert_cache(db, "acao", codigo, hoje, preco, "brapi")
        except Exception as e:
            # log e continua — não falha o job inteiro por uma ação
            logger.warning(f"brapi error for {codigo}: {e}")

    db.commit()
```

**Variável de ambiente a adicionar em `.env`:**
```bash
BRAPI_TOKEN=seu_token_aqui   # gratuito: 15.000 req/mês
```

---

### 12. Lógica de cálculo por track

#### 12.1 Track `variavel` — Custo médio e rentabilidade

```python
def calc_posicao_variavel(investimento_id: int, user_id: int,
                          db: Session) -> dict:
    """
    Calcula posição atual, custo médio ponderado e rentabilidade de ativo variável.
    Usa FIFO implícito via média ponderada.
    """
    transacoes = db.query(InvestimentoTransacao).filter(
        InvestimentoTransacao.investimento_id == investimento_id,
        InvestimentoTransacao.user_id == user_id,
        InvestimentoTransacao.quantidade.isnot(None),
    ).order_by(InvestimentoTransacao.data).all()

    qtd_total = Decimal(0)
    custo_total = Decimal(0)

    for t in transacoes:
        qtd = Decimal(str(t.quantidade))
        preco = Decimal(str(t.preco_unitario or 0))
        if t.tipo == "aporte":    # compra
            custo_total += qtd * preco
            qtd_total   += qtd
        elif t.tipo == "resgate": # venda
            # Reduz posição pro-rata (média ponderada)
            if qtd_total > 0:
                custo_total -= (qtd / qtd_total) * custo_total
            qtd_total -= qtd

    custo_medio = custo_total / qtd_total if qtd_total > 0 else Decimal(0)

    # Preço atual do cache
    portfolio = db.query(InvestimentoPortfolio).get(investimento_id)
    cache = db.query(MarketDataCache).filter(
        MarketDataCache.tipo == "acao",
        MarketDataCache.codigo == portfolio.codigo_ativo,
    ).order_by(MarketDataCache.data_referencia.desc()).first()

    preco_atual = Decimal(str(cache.valor)) if cache else Decimal(0)
    valor_atual = qtd_total * preco_atual
    ganho       = valor_atual - custo_total

    # IR diferenciado por subtipo de ativo (regras: seção 10.4)
    subtipo = portfolio.subtipo_ativo or "acao"  # default: ação

    # Vendas brutas de ações no mês corrente (para verificar isenção R$20k)
    vendas_mes = Decimal(0)
    if subtipo == "acao":
        mes_ini   = date.today().replace(day=1)
        ids_acoes = db.query(InvestimentoPortfolio.id).filter(
            InvestimentoPortfolio.user_id       == user_id,
            InvestimentoPortfolio.subtipo_ativo == "acao",
        )
        vendas_mes = db.query(func.coalesce(func.sum(InvestimentoTransacao.valor), 0)).filter(
            InvestimentoTransacao.user_id        == user_id,
            InvestimentoTransacao.tipo_operacao  == "venda",
            InvestimentoTransacao.data           >= mes_ini,
            InvestimentoTransacao.investimento_id.in_(ids_acoes),
        ).scalar() or Decimal(0)

    ir_info     = calcular_ir_variavel(ganho, subtipo, vendas_mes)
    ir_estimado = Decimal(str(ir_info["ir_estimado"]))

    return {
        "posicao_atual":           float(qtd_total),
        "custo_medio":             float(custo_medio),
        "custo_total":             float(custo_total),
        "preco_atual":             float(preco_atual),
        "valor_atual":             float(valor_atual),
        "ganho_capital":           float(ganho),
        "ir_estimado":             float(ir_estimado),
        "ir_aliquota_pct":         ir_info["aliquota"],
        "ir_regra":                ir_info["ir_regra"],
        "ir_isento_este_mes":      ir_info.get("isento", False),
        "vendas_brutas_mes":       float(ir_info.get("vendas_brutas_mes", 0)),
        "valor_liquido_estimado":  float(valor_atual - ir_estimado),
        "rentabilidade_pct":       float(ganho / custo_total * 100) if custo_total > 0 else 0,
        "cache_data":              cache.data_referencia.isoformat() if cache else None,
        "subtipo_ativo":           subtipo,
    }


def calcular_ir_variavel(ganho: Decimal, subtipo: str,
                          vendas_brutas_mes: Decimal) -> dict:
    """
    Calcula IR estimado sobre ganho de capital de ativos variáveis.

    Regras (art. 22 Lei 9.250/95 e IN RFB 1.585/2015):
    ┌──────────────┬──────────┬─────────────────────────────────────┐
    │ acao         │ 15%      │ ISENTO se vendas_brutas_mes ≤ R$20k │
    │ fii          │ 20%      │ SEM isenção (Lei 11.033/2004)        │
    │ etf / bdr    │ 15%      │ SEM isenção (IN RFB 1585/2015)      │
    └──────────────┴──────────┴─────────────────────────────────────┘
    """
    if ganho <= 0:
        return {"ir_estimado": Decimal(0), "aliquota": 0,
                "isento": False, "ir_regra": "sem_ganho"}

    if subtipo == "acao":
        isento = vendas_brutas_mes <= Decimal("20000")
        return {
            "ir_estimado": Decimal(0) if isento else ganho * Decimal("0.15"),
            "aliquota": 15,
            "isento": isento,
            "ir_regra": "isento_20k" if isento else "acao_15pct",
            "vendas_brutas_mes": float(vendas_brutas_mes),
        }

    if subtipo == "fii":
        return {"ir_estimado": ganho * Decimal("0.20"), "aliquota": 20,
                "isento": False, "ir_regra": "fii_sem_isencao_20pct"}

    # etf, bdr: 15% sem isenção
    return {"ir_estimado": ganho * Decimal("0.15"), "aliquota": 15,
            "isento": False, "ir_regra": "etf_bdr_15pct"}
```

#### 12.2 Track `fixo` — CDI acumulado

```python
def calc_valor_fixo(transacao_aplicacao: InvestimentoTransacao,
                    db: Session) -> dict:
    """
    Calcula valor atual de renda fixa para qualquer indexador/regime.

    Suportados:
    ┌─────────────────────┬────────────────────────────────────────────────┐
    │ PREFIXADO           │ capital × (1 + taxa_aa/100)^(du/252)           │
    │ PÓS CDI / SELIC     │ capital × Π(1 + taxa_dia × mult)  — diário     │
    │ PÓS IPCA/IGPM/INCC  │ capital × Π(1 + variacao_mensal)  — mensal     │
    │ PÓS IPCA+X          │ IPCA acumulado × (1 + spread/100)^(du/252)    │
    └─────────────────────┴────────────────────────────────────────────────┘
    """
    capital     = Decimal(str(transacao_aplicacao.valor))
    taxa_pct    = Decimal(str(transacao_aplicacao.taxa_pct or 100))
    regime      = transacao_aplicacao.regime or "pos_fixado"
    indexador   = (transacao_aplicacao.indexador or "CDI").upper()
    data_inicio = transacao_aplicacao.data
    data_fim    = transacao_aplicacao.data_vencimento or date.today()
    dias_prazo  = (date.today() - data_inicio).days

    # ── PREFIXADO ─────────────────────────────────────────────────────────
    if regime == "prefixado":
        dias_corridos   = (data_fim - data_inicio).days
        du              = max(1, int(dias_corridos / 1.4))
        taxa_dia        = (1 + taxa_pct / 100) ** (Decimal(1) / 252) - 1
        fator           = (1 + taxa_dia) ** du
        valor_atual     = capital * fator
        rentabilidade   = (fator - 1) * 100
        valor_projetado = None
        if transacao_aplicacao.data_vencimento:
            du_total = max(1, int((transacao_aplicacao.data_vencimento - data_inicio).days / 1.4))
            valor_projetado = float(capital * (1 + taxa_dia) ** du_total)
        return {
            "capital_inicial": float(capital), "valor_atual": float(valor_atual),
            "rentabilidade_pct": float(rentabilidade), "regime": "prefixado",
            "indexador": "PREFIXADO", "taxa_pct": float(taxa_pct),
            "valor_projetado_vencimento": valor_projetado,
            "n_periodos_calculados": du,
            **_ir_renda_fixa_info(dias_prazo),
        }

    # ── PÓS CDI / SELIC (séries diárias) ─────────────────────────────────
    if indexador in ("CDI", "SELIC"):
        dados = db.query(MarketDataCache).filter(
            MarketDataCache.tipo == indexador.lower(),
            MarketDataCache.data_referencia.between(data_inicio, data_fim),
        ).order_by(MarketDataCache.data_referencia).all()
        if not dados:
            return {"valor_atual": float(capital), "rentabilidade_pct": 0,
                    "aviso": f"sem_dados_{indexador.lower()}_cache"}
        mult  = taxa_pct / 100  # 112% CDI → mult=1.12
        fator = Decimal(1)
        for d in dados:
            fator *= (1 + Decimal(str(d.valor)) / 100 * mult)
        valor_atual   = capital * fator
        rentabilidade = (fator - 1) * 100
        return {**_base_fixo(capital, valor_atual, rentabilidade, indexador,
                              taxa_pct, dados, transacao_aplicacao, regime),
                **_ir_renda_fixa_info(dias_prazo)}

    # ── PÓS IPCA / IGPM / INCC (séries mensais) ──────────────────────────
    if indexador in ("IPCA", "IGPM", "INCC"):
        dados = db.query(MarketDataCache).filter(
            MarketDataCache.tipo == indexador.lower(),
            MarketDataCache.data_referencia >= data_inicio.replace(day=1),
            MarketDataCache.data_referencia <= data_fim,
        ).order_by(MarketDataCache.data_referencia).all()
        if not dados:
            return {"valor_atual": float(capital), "rentabilidade_pct": 0,
                    "aviso": f"sem_dados_{indexador.lower()}_cache"}
        fator = Decimal(1)
        for m in dados:
            fator *= (1 + Decimal(str(m.valor)) / 100)
        valor_atual   = capital * fator
        rentabilidade = (fator - 1) * 100
        return {**_base_fixo(capital, valor_atual, rentabilidade, indexador,
                              taxa_pct, dados, transacao_aplicacao, regime),
                **_ir_renda_fixa_info(dias_prazo)}

    # ── IPCA + spread fixo (IPCA+X) ───────────────────────────────────────
    if indexador == "IPCA+X":
        meses = db.query(MarketDataCache).filter(
            MarketDataCache.tipo == "ipca",
            MarketDataCache.data_referencia >= data_inicio.replace(day=1),
        ).order_by(MarketDataCache.data_referencia).all()
        fator_ipca = Decimal(1)
        for m in meses:
            fator_ipca *= (1 + Decimal(str(m.valor)) / 100)
        du            = max(1, int((data_fim - data_inicio).days / 1.4))
        taxa_dia_fixa = (1 + taxa_pct / 100) ** (Decimal(1) / 252) - 1
        fator_fixo    = (1 + taxa_dia_fixa) ** du
        valor_atual   = capital * fator_ipca * fator_fixo
        rentabilidade = (valor_atual / capital - 1) * 100
        return {**_base_fixo(capital, valor_atual, rentabilidade, "IPCA+X",
                              taxa_pct, meses, transacao_aplicacao, regime),
                **_ir_renda_fixa_info(dias_prazo)}

    return {"erro": f"indexador_nao_suportado: {indexador}",
            "capital_inicial": float(capital), "valor_atual": float(capital),
            "rentabilidade_pct": 0}


def _ir_renda_fixa_info(dias_prazo: int) -> dict:
    """Tabela regressiva de IR — renda fixa (art. 206 CTN). IR retido na fonte."""
    aliquota = (22.5 if dias_prazo <= 180 else
                20.0 if dias_prazo <= 360 else
                17.5 if dias_prazo <= 720 else 15.0)
    return {
        "ir_aliquota_estimada_pct": aliquota,
        "nota_ir": "IR retido na fonte pela corretora. Alíquota estimada pelo prazo da aplicação.",
    }


def _base_fixo(capital, valor_atual, rentabilidade, indexador,
               taxa_pct, dados, transacao, regime) -> dict:
    """Monta response padrão para renda fixa pós-fixada."""
    valor_projetado = None
    if transacao.data_vencimento and dados:
        ultimos      = dados[-6:]
        media_var    = sum(Decimal(str(d.valor)) for d in ultimos) / len(ultimos) / 100
        dias_rest    = (transacao.data_vencimento - date.today()).days
        periodos     = (max(1, int(dias_rest / 1.4))
                        if indexador in ("CDI", "SELIC")
                        else max(1, round(dias_rest / 30)))
        valor_projetado = float(valor_atual * (1 + media_var) ** periodos)
    return {
        "capital_inicial": float(capital),
        "valor_atual": float(valor_atual),
        "rentabilidade_pct": float(rentabilidade),
        "regime": regime,
        "indexador": indexador,
        "taxa_pct": float(taxa_pct),
        "valor_projetado_vencimento": valor_projetado,
        "n_periodos_calculados": len(dados),
    }
```

---

### 13. Endpoints novos do Módulo 2

```python
# Adicionar em investimentos/router.py

@router.post("/vincular-aporte", status_code=201)
def vincular_aporte(
    data: VincularAporteRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Vincula um journal_entry de investimento a um ou mais produtos do portfólio.

    Cria N linhas em investimentos_transacoes (uma por produto),
    atualiza investimentos_historico.aporte_mes do mês correspondente.
    """
    return InvestimentoService(db).vincular_aporte(user_id, data)

@router.get("/pendentes-vinculo")
def aportes_pendentes(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista journal_entries com GRUPO='Investimentos' sem investimentos_transacoes vinculado.
    Retorna também sugestão de match automático se texto_match detectado.
    """
    return InvestimentoService(db).get_aportes_pendentes(user_id)

@router.get("/{investimento_id}/posicao")
def get_posicao(
    investimento_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Posição atual, custo médio, rentabilidade e IR estimado (variável) ou CDI acumulado (fixo)."""
    return InvestimentoService(db).get_posicao(investimento_id, user_id)

@router.get("/resumo-ir")
def get_resumo_ir(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna IR estimado consolidado sobre ganho de capital (apenas track='variavel').
    Usado no card do portfólio: patrimônio bruto - IR estimado = patrimônio líquido.
    """
    return InvestimentoService(db).get_resumo_ir(user_id)

@router.post("/registrar-venda", status_code=201)
def registrar_venda(
    data: RegistrarVendaRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Registra venda/resgate de ativo (variável ou fixo).

    Pergunta obrigatória: destino do valor recebido.
    - "conta_bancaria"  → volta ao extrato bancário; pode ser conciliado via journal_entry_id
    - "saldo_corretora" → cria automaticamente produto track='saldo_corretora' na corretora
                          (ou incrementa o saldo existente) — fica visível no portfólio

    Para ações/FIIs: valida que posição não fica negativa após a venda.
    Recalcula aporte_mes do InvestimentoHistorico se destino='conta_bancaria'.
    """
    return InvestimentoService(db).registrar_venda(user_id, data)
```

---

### 14. Schemas do Módulo 2

```python
class IndexadorEnum(str, Enum):
    CDI       = "CDI"
    SELIC     = "SELIC"
    IPCA      = "IPCA"
    IGPM      = "IGPM"
    INCC      = "INCC"
    IPCA_X    = "IPCA+X"
    PREFIXADO = "PREFIXADO"

class RegimeEnum(str, Enum):
    PREFIXADO  = "prefixado"
    POS_FIXADO = "pos_fixado"

class SubtipoAtivoEnum(str, Enum):
    ACAO = "acao"  # ações: 15% + isenção R$20k
    FII  = "fii"   # fundos imobiliários: 20%, sem isenção
    ETF  = "etf"   # ETFs renda variável: 15%, sem isenção
    BDR  = "bdr"   # BDRs: 15%, sem isenção


class AporteParcial(BaseModel):
    """Um produto + valor dentro de um vínculo (aporte ou venda)"""
    investimento_id: int                 # portfólio existente (ou None para criar novo)
    valor: Decimal                       # valor destinado a este produto
    tipo_operacao: str = "aporte"        # "aporte" | "venda"

    # Track variavel — ações, FIIs, ETFs, BDRs
    codigo_ativo:   Optional[str] = None
    subtipo_ativo:  Optional[SubtipoAtivoEnum] = None  # determina a regra de IR
    quantidade:     Optional[Decimal] = None
    preco_unitario: Optional[Decimal] = None

    # Track fixo — renda fixa
    indexador:       Optional[IndexadorEnum] = None
    regime:          Optional[RegimeEnum] = None    # obrigatório se track='fixo'
    taxa_pct:        Optional[Decimal] = None
    data_vencimento: Optional[date] = None          # None = liquidez diária

    # Venda/resgate (preenchido quando tipo_operacao='venda')
    destino_resgate: Optional[str] = None  # "conta_bancaria" | "saldo_corretora"

class VincularAporteRequest(BaseModel):
    journal_entry_id: int
    aportes: List[AporteParcial]
    # Validação: sum(aportes.valor) deve igualar journal_entry.ValorPositivo ± R$0,01

class AportePendenteResponse(BaseModel):
    journal_entry_id: int
    estabelecimento: str
    valor: Decimal
    data: date
    match_automatico: Optional[dict] = None  # {investimento_id, nome, score}

class PosicaoVariavelResponse(BaseModel):
    track: str                      # "variavel"
    subtipo_ativo: str              # "acao" | "fii" | "etf" | "bdr"
    posicao_atual: float
    custo_medio: float
    custo_total: float
    preco_atual: float
    valor_atual: float
    ganho_capital: float
    ir_estimado: float              # R$ 0 se isento; 15% ou 20% conforme subtipo
    ir_aliquota_pct: int            # 15 ou 20
    ir_regra: str                   # "isento_20k" | "acao_15pct" | "fii_sem_isencao_20pct" | ...
    ir_isento_este_mes: bool        # True = vendas totais de ações no mês < R$ 20k
    vendas_brutas_mes: float        # soma de todas as vendas de ações no mês corrente
    valor_liquido_estimado: float
    rentabilidade_pct: float
    cache_data: Optional[str]       # data da última cotação ("YYYY-MM-DD")

class PosicaoFixoResponse(BaseModel):
    track: str                              # "fixo"
    regime: str                             # "prefixado" | "pos_fixado"
    indexador: str                          # "CDI" | "SELIC" | "IPCA" | "IGPM" | "INCC" | "IPCA+X" | "PREFIXADO"
    capital_inicial: float
    valor_atual: float
    rentabilidade_pct: float
    taxa_pct: float                         # % do indexador (pós) ou taxa a.a. (pré)
    valor_projetado_vencimento: Optional[float]
    n_periodos_calculados: int              # dias úteis (CDI/SELIC) ou meses (IPCA/IGPM/INCC)
    ir_aliquota_estimada_pct: float         # 22.5 / 20 / 17.5 / 15 conforme tabela regressiva
    nota_ir: str                            # "IR retido na fonte..."

class ResumoIRResponse(BaseModel):
    total_ativos_bruto: Decimal
    ir_estimado_total: Decimal
    patrimonio_liquido_estimado: Decimal
    produtos_com_ganho: int
    nota: str  # "Estimativa sobre ações/FIIs. Não considera isenção ou day trade."

class RegistrarVendaRequest(BaseModel):
    """Registra venda ou resgate de ativo diretamente no portfólio."""
    investimento_id: int
    valor_total: Decimal              # valor bruto recebido (pré-IR para renda fixa)
    data: date
    destino_resgate: str              # "conta_bancaria" | "saldo_corretora"

    # Para track='variavel' (ações, FIIs)
    quantidade:     Optional[Decimal] = None
    preco_unitario: Optional[Decimal] = None
    subtipo_ativo:  Optional[SubtipoAtivoEnum] = None

    # Para track='fixo' (renda fixa)
    ir_retido: Optional[Decimal] = None   # IR já descontado pela corretora/banco

    # Vínculo opcional com o extrato bancário
    journal_entry_id: Optional[int] = None  # crédito correspondente no extrato
```

---

### 15. Fase 7 do upload — detectar GRUPO='Investimentos'

Adicionar em `upload/service.py` após `_fase6_conciliar_expectativas()`:

```python
def _fase7_fila_vinculo_investimentos(self,
                                      user_id: int,
                                      upload_history_id: int) -> dict:
    """
    Fase 7: Detecta transações GRUPO='Investimentos' sem vínculo e marca para vinculação.

    Não cria vínculos — apenas retorna as transações pendentes.
    O usuário vincula manualmente (ou auto se texto_match detectado) na tela de Carteira.
    """
    pendentes = self.db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.upload_history_id == upload_history_id,
        JournalEntry.GRUPO == "Investimentos",
    ).filter(
        ~JournalEntry.id.in_(
            self.db.query(InvestimentoTransacao.journal_entry_id).filter(
                InvestimentoTransacao.journal_entry_id.isnot(None)
            )
        )
    ).all()

    return {"pendentes_vinculo": len(pendentes)}
```

Chamar em `confirmar_upload()`:
```python
fase6 = self._fase6_conciliar_expectativas(user_id, upload_history_id)
fase7 = self._fase7_fila_vinculo_investimentos(user_id, upload_history_id)
```

O response do confirm passa a incluir:
```json
{
  "fase7": { "pendentes_vinculo": 2 }
}
```
O frontend usa esse número para exibir o badge na tela de Carteira.

---

### 16. Frontend — Módulo 2

#### Componentes novos

| Componente | Path | Responsabilidade |
|-----------|------|-----------------|
| `AportesPendentesBar` | `features/investimentos/components/aportes-pendentes-bar.tsx` | Badge amarelo com contador + botão "Vincular" |
| `VincularAporteModal` | `features/investimentos/components/vincular-aporte-modal.tsx` | Modal completo de vínculo (match + manual + sub-forms por track) |
| `MatchAutomaticoCard` | `features/investimentos/components/match-automatico-card.tsx` | Card de sugestão automática com 1 clique |
| `AporteTrackVariavelForm` | `features/investimentos/components/aporte-track-variavel-form.tsx` | Sub-form: ticker, qtd, preço |
| `AporteTrackFixoForm` | `features/investimentos/components/aporte-track-fixo-form.tsx` | Sub-form: indexador, taxa%, vencimento |
| `PosicaoVariavelCard` | `features/investimentos/components/posicao-variavel-card.tsx` | Custo médio, rentabilidade, IR estimado |
| `PosicaoFixoCard` | `features/investimentos/components/posicao-fixo-card.tsx` | CDI acumulado, valor atual estimado, projeção |
| `ResumoIRPatrimonio` | `features/investimentos/components/resumo-ir-patrimonio.tsx` | Linha IR estimado no topo da Carteira |

#### Integração na tela `/mobile/carteira`

```tsx
// Adicionar logo abaixo do header, antes do donut:
const { data: pendentes } = useSWR("/api/v1/investimentos/pendentes-vinculo")

{pendentes?.length > 0 && (
  <AportesPendentesBar
    count={pendentes.length}
    onPress={() => setVincularOpen(true)}
  />
)}

<VincularAporteModal
  open={vincularOpen}
  pendentes={pendentes}
  onClose={() => setVincularOpen(false)}
  onConfirm={() => { mutate("/api/v1/investimentos/pendentes-vinculo"); setVincularOpen(false) }}
/>

// Após o patrimônio líquido atual, antes das barras de tipo:
<ResumoIRPatrimonio />
```

---

### 17. Checklist — Módulo 2

### Banco
- [ ] Migration `market_data_cache` com constraint `uq_market_data_dia`
- [ ] Migration `investimentos_transacoes`: campos `regime`, `tipo_operacao`, `destino_resgate` adicionados (nullable)
- [ ] Migration `investimentos_portfolio`: `track` (add 'saldo_corretora'), `subtipo_ativo`, `regime`, `codigo_ativo`, `texto_match`

### Backend
- [ ] Job `sync_market_data` rodando às 18h via APScheduler
- [ ] `BRAPI_TOKEN` no `.env` local e no servidor
- [ ] CDI / SELIC (BCB séries 4389/11) inseridos diáriamente via `SERIES_BCB_DIARIOS`
- [ ] IPCA / IGPM / INCC (BCB séries 433/189/192) inseridos mensalmente via `SERIES_BCB_MENSAIS`
- [ ] Ações/FIIs: brapi inserindo preços no cache
- [ ] `InvestimentoService.vincular_aporte()` cria transações e atualiza `aporte_mes`
- [ ] `InvestimentoService.get_aportes_pendentes()` com sugestão de match
- [ ] `InvestimentoService.get_posicao()`: despacha por track (`calc_posicao_variavel` / `calc_valor_fixo`)
- [ ] `calc_posicao_variavel()`: IR por subtipo (`calcular_ir_variavel`), isenção R$20k para ações
- [ ] `calc_valor_fixo()`: suporte a PREFIXADO, CDI, SELIC, IPCA, IGPM, INCC, IPCA+X
- [ ] `InvestimentoService.registrar_venda()`: deducts posição, cria produto `saldo_corretora` se destino='saldo_corretora'
- [ ] `InvestimentoService.get_resumo_ir()`: soma IR estimado de todos variáveis
- [ ] Fase 7 em `upload/service.py` integrada ao confirm
- [ ] Endpoints registrados: vincular-aporte, pendentes-vinculo, posicao, resumo-ir, registrar-venda

### Frontend
- [ ] Badge `AportesPendentesBar` aparece e some corretamente
- [ ] Match automático: sugere com 1 clique quando `texto_match` detecta 1 produto
- [ ] Modal manual: validação de soma = valor total da transação
- [ ] Sub-form variável: ticker, subtipo (ação/FII/ETF/BDR), qtd, preço
- [ ] Sub-form fixo: toggle Pré-fixado / Pós-fixado; dropdown de indexador (CDI/SELIC/IPCA/IGPM/INCC/IPCA+X); taxa%; vencimento opcional
- [ ] Venda/resgate: pergunta destino (conta bancária / saldo corretora)
- [ ] `PosicaoVariavelCard`: custo médio, preço atual, ganho, IR por subtipo, badge "Isento" quando aplicável
- [ ] `PosicaoFixoCard`: regime, indexador, capital, valor atual, alíquota IR estimada pelo prazo
- [ ] `SaldoCorretoraCard`: exibido quando track='saldo_corretora' (valor + corretora)
- [ ] `ResumoIRPatrimonio`: bruto − IR = líquido estimado com tooltip explicativo
