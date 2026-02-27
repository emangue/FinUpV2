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
