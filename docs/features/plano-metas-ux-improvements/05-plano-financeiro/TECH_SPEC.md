# TECH SPEC — Plano Financeiro
> Sub-projeto 05 | Sprints 6, 7

---

## 1. Arquitetura

```
Frontend (Next.js)                   Backend (FastAPI)
─────────────────────────────────────────────────────────
RendaDeclaracaoForm              ── POST /plano/renda
CompromissosFixosList            ── GET/POST/DELETE /plano/compromissos
OrcamentoCategorias              ── GET /plano/orcamento?ano=&mes=
ProjecaoChart                    ── GET /plano/projecao?meses=12
TabelaDetalhadaCategorias        ── GET /plano/categorias/detalhado
AnosPerdidasCard                 ── GET /plano/impacto-longo-prazo
BudgetDashboardWidget            └── (combina /plano/* + /transactions/*)
```

---

## 2. Banco de Dados — Migrations

### 2a. `user_financial_profile` — tabela principal (pode já existir parcialmente do onboarding)

```python
# app/domains/plano/models.py
class UserFinancialProfile(Base):
    __tablename__ = "user_financial_profile"

    id                    = Column(Integer, primary_key=True)
    user_id               = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    renda_mensal_liquida  = Column(Numeric(12, 2), nullable=True)
    idade_atual           = Column(Integer, nullable=True)
    idade_aposentadoria   = Column(Integer, nullable=True, default=65)
    patrimonio_atual      = Column(Numeric(14, 2), nullable=True, default=0)
    taxa_retorno_anual    = Column(Numeric(5, 4), nullable=True, default=0.08)  # 8% a.a.
    updated_at            = Column(DateTime, default=func.now(), onupdate=func.now())
```

### 2b. `plano_metas_categoria` — metas por grupo

```python
class PlanoMetaCategoria(Base):
    __tablename__ = "plano_metas_categoria"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    grupo_id    = Column(Integer, ForeignKey("base_grupos_config.id"), nullable=False)
    valor_meta  = Column(Numeric(12, 2), nullable=False)
    ano         = Column(Integer, nullable=False)  # Ano de referência
    mes         = Column(Integer, nullable=True)   # NULL = meta anual/mensal global
    created_at  = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "grupo_id", "ano", "mes"),
    )
```

### 2c. `plano_compromissos` — compromissos fixos mensais

```python
class PlanoCompromisso(Base):
    __tablename__ = "plano_compromissos"

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    nome            = Column(String, nullable=False)        # "Financiamento carro"
    valor_mensal    = Column(Numeric(12, 2), nullable=False)
    meses_restantes = Column(Integer, nullable=True)        # NULL = indefinido
    grupo_id        = Column(Integer, ForeignKey("base_grupos_config.id"), nullable=True)
    data_inicio     = Column(Date, nullable=False)
    ativo           = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=func.now())
```

### Migration Alembic

```python
def upgrade():
    op.create_table("user_financial_profile", ...)
    op.create_table("plano_metas_categoria", ...)
    op.create_table("plano_compromissos", ...)
```

---

## 3. Backend — Serviços

### S5: Declaração de renda

```python
# app/domains/plano/router.py
class RendaUpdate(BaseModel):
    renda_mensal_liquida: Decimal

@router.post("/renda")
def atualizar_renda(data: RendaUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    profile = db.query(UserFinancialProfile).filter(
        UserFinancialProfile.user_id == user_id
    ).first()

    if not profile:
        profile = UserFinancialProfile(user_id=user_id)
        db.add(profile)

    profile.renda_mensal_liquida = data.renda_mensal_liquida
    db.commit()
    return {"success": True, "renda": float(profile.renda_mensal_liquida)}
```

### S6: Compromissos fixos

```python
@router.get("/compromissos")
def listar_compromissos(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    compromissos = db.query(PlanoCompromisso).filter(
        PlanoCompromisso.user_id == user_id,
        PlanoCompromisso.ativo == True
    ).all()
    total = sum(float(c.valor_mensal) for c in compromissos)
    return {"compromissos": [c.__dict__ for c in compromissos], "total_mensal": total}

@router.post("/compromissos")
def criar_compromisso(data: CompromissoCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    c = PlanoCompromisso(user_id=user_id, **data.dict())
    db.add(c)
    db.commit()
    return {"id": c.id}

@router.delete("/compromissos/{id}")
def remover_compromisso(id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    c = db.query(PlanoCompromisso).filter(
        PlanoCompromisso.id == id, PlanoCompromisso.user_id == user_id
    ).first_or_404()
    c.ativo = False
    db.commit()
```

### S7: Orçamento com desvio por categoria

```python
@router.get("/orcamento")
def orcamento_por_categoria(
    ano: int = Query(...), mes: int = Query(...),
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Retorna gasto real vs. meta por grupo para o mês."""
    # Gastos reais
    gastos = db.execute(text("""
        SELECT CategoriaGeral as grupo, SUM(ABS(Valor)) as gasto
        FROM journal_entries
        WHERE user_id = :uid AND Ano = :ano AND Mes = :mes
          AND CategoriaGeral != 'Receita' AND IgnorarDashboard = 0
        GROUP BY CategoriaGeral
    """), {"uid": user_id, "ano": ano, "mes": mes}).fetchall()

    # Metas
    metas = {m.grupo_id: float(m.valor_meta) for m in
             db.query(PlanoMetaCategoria).filter(
                 PlanoMetaCategoria.user_id == user_id,
                 PlanoMetaCategoria.ano == ano,
                 PlanoMetaCategoria.mes == mes
             ).all()}

    resultado = []
    for g in gastos:
        meta = metas.get(g.grupo)
        pct = (float(g.gasto) / meta * 100) if meta else None
        resultado.append({
            "grupo": g.grupo,
            "gasto": float(g.gasto),
            "meta": meta,
            "percentual": pct,
            "status": "ok" if not pct else ("alerta" if pct < 100 else "excedido")
        })

    return resultado
```

### S8: Projeção de 12 meses

```python
@router.get("/projecao")
def projecao_12_meses(
    meses: int = Query(default=12, le=24),
    reducao_pct: float = Query(default=0),
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    """Projeta renda e gastos para os próximos N meses."""
    profile = db.query(UserFinancialProfile).filter(
        UserFinancialProfile.user_id == user_id
    ).first()

    if not profile or not profile.renda_mensal_liquida:
        raise HTTPException(422, "Renda não declarada")

    # Média de gastos dos últimos 3 meses
    tres_meses_atras = date.today() - timedelta(days=90)
    media_gastos = db.execute(text("""
        SELECT AVG(total_mes) FROM (
            SELECT Ano, Mes, SUM(ABS(Valor)) as total_mes
            FROM journal_entries
            WHERE user_id = :uid AND CategoriaGeral != 'Receita'
              AND IgnorarDashboard = 0
              AND Ano >= :ano AND Mes >= :mes
            GROUP BY Ano, Mes
        ) sub
    """), {"uid": user_id, "ano": tres_meses_atras.year, "mes": tres_meses_atras.month}).scalar() or 0

    renda = float(profile.renda_mensal_liquida)
    gasto_base = float(media_gastos) * (1 - reducao_pct / 100)

    projecao = []
    poupanca_acumulada = 0
    for i in range(meses):
        mes_ref = date.today() + timedelta(days=30 * i)
        poupanca_mes = renda - gasto_base
        poupanca_acumulada += poupanca_mes
        projecao.append({
            "mes": mes_ref.strftime("%Y-%m"),
            "renda": renda,
            "gasto_projetado": gasto_base,
            "poupanca_mes": poupanca_mes,
            "poupanca_acumulada": poupanca_acumulada
        })

    return {"projecao": projecao, "media_gastos_historica": float(media_gastos)}
```

### S10: Impacto no longo prazo ("anos perdidos")

```python
@router.get("/impacto-longo-prazo")
def impacto_longo_prazo(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    profile = db.query(UserFinancialProfile).filter(
        UserFinancialProfile.user_id == user_id
    ).first()

    if not profile or not profile.renda_mensal_liquida:
        raise HTTPException(422, "Perfil financeiro incompleto")

    # Gasto do mês atual vs. plano
    hoje = date.today()
    orcamento = orcamento_por_categoria(ano=hoje.year, mes=hoje.month, user_id=user_id, db=db)
    excedentes = [item for item in orcamento if item["status"] == "excedido"]
    deficit_mensal = sum(item["gasto"] - (item["meta"] or 0) for item in excedentes)

    taxa_mensal = (1 + float(profile.taxa_retorno_anual)) ** (1/12) - 1
    anos_restantes = (profile.idade_aposentadoria or 65) - (profile.idade_atual or 30)
    meses = anos_restantes * 12

    # Valor futuro do déficit mensal capitalizado
    custo_oportunidade = deficit_mensal * ((1 + taxa_mensal) ** meses - 1) / taxa_mensal if taxa_mensal > 0 else deficit_mensal * meses

    # "Dias de trabalho" = custo_oportunidade / (renda_mensal / 22 dias úteis)
    renda_diaria = float(profile.renda_mensal_liquida) / 22
    dias_perdidos = custo_oportunidade / renda_diaria if renda_diaria > 0 else 0

    return {
        "deficit_mensal": deficit_mensal,
        "custo_oportunidade_futuro": custo_oportunidade,
        "dias_trabalho_equivalentes": dias_perdidos,
        "anos_restantes_para_aposentadoria": anos_restantes,
        "taxa_retorno_anual": float(profile.taxa_retorno_anual),
        "mensagem": f"Cada R$ 100 economizados hoje = {100 / renda_diaria:.1f} dias a menos de trabalho"
    }
```

---

## 4. Frontend — Componentes

### `RendaDeclaracaoForm` (`features/plano/components/renda-declaracao-form.tsx`)

```tsx
export function RendaDeclaracaoForm({ currentRenda, onSaved }: Props) {
  const [valor, setValor] = useState(currentRenda ? String(currentRenda) : "")
  const [loading, setLoading] = useState(false)

  const handleSave = async () => {
    setLoading(true)
    const v = parseBRLInput(valor)  // Remove formatação
    await fetch("/api/plano/renda", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ renda_mensal_liquida: v })
    })
    setLoading(false)
    onSaved(v)
  }

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Renda mensal líquida</label>
      <div className="flex gap-2">
        <Input
          value={valor}
          onChange={e => setValor(formatBRLInput(e.target.value))}
          placeholder="R$ 0,00"
          className="text-right"
        />
        <Button onClick={handleSave} disabled={loading || !valor}>
          {loading ? <Loader2 className="animate-spin" size={14} /> : "Salvar"}
        </Button>
      </div>
    </div>
  )
}
```

### `OrcamentoCategorias` (`features/plano/components/orcamento-categorias.tsx`)

```tsx
export function OrcamentoCategorias({ ano, mes }: Props) {
  const { data } = useSWR(`/api/plano/orcamento?ano=${ano}&mes=${mes}`, fetcher)

  return (
    <div className="space-y-2">
      {data?.map(item => (
        <div key={item.grupo} className="space-y-1">
          <div className="flex justify-between text-sm">
            <span>{item.grupo}</span>
            <span className="text-muted-foreground">
              {formatBRL(item.gasto)} {item.meta && `/ ${formatBRL(item.meta)}`}
              {item.percentual && <span className={cn("ml-1 font-medium",
                item.status === "excedido" ? "text-red-500" :
                item.status === "alerta" ? "text-yellow-500" : "text-green-500"
              )}>{item.percentual.toFixed(0)}%</span>}
            </span>
          </div>
          {item.meta && (
            <Progress
              value={Math.min(item.percentual ?? 0, 100)}
              className={cn("h-1.5",
                item.status === "excedido" ? "[&>div]:bg-red-500" :
                item.status === "alerta" ? "[&>div]:bg-yellow-500" : "[&>div]:bg-green-500"
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}
```

### `ProjecaoChart` (`features/plano/components/projecao-chart.tsx`)

```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

export function ProjecaoChart() {
  const [reducao, setReducao] = useState(0)
  const { data } = useSWR(`/api/plano/projecao?meses=12&reducao_pct=${reducao}`, fetcher)

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground">Se eu reduzir gastos em</span>
        <Slider value={[reducao]} onValueChange={([v]) => setReducao(v)} min={0} max={30} step={5} className="w-32" />
        <span className="text-sm font-medium">{reducao}%</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data?.projecao}>
          <XAxis dataKey="mes" tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => formatBRL(v, "compact")} />
          <Tooltip formatter={(v: number) => formatBRL(v)} />
          <Line dataKey="poupanca_acumulada" stroke="#22c55e" dot={false} strokeWidth={2} name="Poupança acum." />
          <Line dataKey="gasto_projetado" stroke="#ef4444" dot={false} strokeWidth={1.5} name="Gasto projetado" strokeDasharray="4 2" />
        </LineChart>
      </ResponsiveContainer>
      {data && (
        <p className="text-sm text-center text-muted-foreground">
          Poupança acumulada em 12 meses:{" "}
          <span className="font-semibold text-green-600">
            {formatBRL(data.projecao.at(-1)?.poupanca_acumulada ?? 0)}
          </span>
        </p>
      )}
    </div>
  )
}
```

### `AnosPerdidasCard` (`features/plano/components/anos-perdidas-card.tsx`)

```tsx
export function AnosPerdidasCard() {
  const { data } = useSWR("/api/plano/impacto-longo-prazo", fetcher)

  if (!data || data.deficit_mensal <= 0) return null

  const diasPerdidos = Math.round(data.dias_trabalho_equivalentes)
  const unidade = diasPerdidos < 30 ? `${diasPerdidos} dias` :
                  diasPerdidos < 365 ? `${(diasPerdidos/30).toFixed(1)} meses` :
                  `${(diasPerdidos/365).toFixed(1)} anos`

  return (
    <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20">
      <CardContent className="pt-4 space-y-2">
        <p className="text-sm font-semibold flex items-center gap-2">
          <Hourglass size={16} className="text-orange-500" />
          Impacto no longo prazo
        </p>
        <p className="text-sm text-muted-foreground">
          Gasto além do plano este mês: <strong>{formatBRL(data.deficit_mensal)}</strong>
        </p>
        <p className="text-2xl font-bold text-orange-600">{unidade}</p>
        <p className="text-xs text-muted-foreground">a mais de trabalho necessário para se aposentar</p>
        <p className="text-xs text-green-600 mt-2">{data.mensagem}</p>
      </CardContent>
    </Card>
  )
}
```

---

## 5. Widget no Dashboard

```tsx
// features/dashboard/components/budget-widget.tsx
export function BudgetWidget({ ano, mes }: Props) {
  const { data: profile } = useSWR("/api/plano/renda", fetcher)

  if (!profile?.renda_mensal_liquida) {
    return (
      <Card>
        <CardContent className="pt-4 text-center">
          <p className="text-sm text-muted-foreground">Declare sua renda para ver seu orçamento</p>
          <Button variant="link" size="sm" asChild>
            <Link href="/mobile/perfil/financeiro">Declarar agora →</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Orçamento mensal</CardTitle>
      </CardHeader>
      <CardContent>
        <OrcamentoCategorias ano={ano} mes={mes} />
      </CardContent>
    </Card>
  )
}
```

---

## 6. Checklist de Implementação

### Sprint 6 — Renda + Compromissos + Desvio
- [ ] Migrations: `user_financial_profile`, `plano_metas_categoria`, `plano_compromissos`
- [ ] Endpoints: `POST /plano/renda`, `GET/POST/DELETE /plano/compromissos`, `GET /plano/orcamento`
- [ ] Componentes: `RendaDeclaracaoForm`, `CompromissosFixosList`, `OrcamentoCategorias`
- [ ] Widget de desvio no dashboard
- [ ] Interface de definição de metas por categoria
- [ ] Testar: renda salva → dashboard mostra poupança correta

### Sprint 7 — Projeção + Tabela + Anos perdidos
- [ ] Endpoint `GET /plano/projecao` com parâmetro `reducao_pct`
- [ ] Endpoint `GET /plano/categorias/detalhado` (drill-down)
- [ ] Endpoint `GET /plano/impacto-longo-prazo`
- [ ] Componente `ProjecaoChart` (Recharts, slider de redução)
- [ ] Componente `TabelaDetalhadaCategorias` (ordenável + drill-down)
- [ ] Componente `AnosPerdidasCard`
- [ ] Tela `/mobile/plano` com todos os componentes
- [ ] Configuração de parâmetros de aposentadoria no perfil
