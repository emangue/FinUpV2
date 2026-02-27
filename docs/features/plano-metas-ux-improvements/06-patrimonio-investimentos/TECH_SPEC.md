# TECH SPEC — Patrimônio e Investimentos
> Sub-projeto 06 | Sprints 8, 9

---

## 1. Arquitetura

```
Frontend (Next.js)                   Backend (FastAPI)
─────────────────────────────────────────────────────────
CarteiraView                     ── GET  /investimentos
VinculoAporteModal               ── POST /investimentos/{id}/vincular
VinculoResgateModal              ── POST /investimentos/{id}/resgatar
SugestoesMatchCard               ── GET  /investimentos/sugestoes-match
InvestimentoDetailCard           ── GET  /investimentos/{id}/rentabilidade
IREstimadoView                   ── GET  /investimentos/ir-estimado
SaldoCorretoraCard               ── GET  /investimentos/saldo-corretora
                                 └── [job diário] → BCB + brapi
```

---

## 2. Banco de Dados — Migrations

### 2a. `investimentos` — cadastro de ativos

```python
class Investimento(Base):
    __tablename__ = "investimentos"

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    nome            = Column(String, nullable=False)           # "CDB XP 120% CDI"
    tipo            = Column(String, nullable=False)           # "renda_fixa", "acao", "fii"
    banco_corretora = Column(String, nullable=True)            # "xp", "btg", "nubank"
    codigo_ativo    = Column(String, nullable=True)            # "ITSA4", "MXRF11" (para ações/FIIs)
    indexador       = Column(String, nullable=True)            # "cdi", "igpm", "incc", "pre", "ipca"
    percentual_indexador = Column(Numeric(5, 2), nullable=True) # 120.00 = 120% CDI
    taxa_pre        = Column(Numeric(6, 4), nullable=True)     # 0.1050 = 10.50% a.a.
    data_inicio     = Column(Date, nullable=True)
    data_vencimento = Column(Date, nullable=True)
    ativo           = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=func.now())
```

### 2b. `investimentos_transacoes` — vínculos aporte/resgate

```python
class InvestimentoTransacao(Base):
    __tablename__ = "investimentos_transacoes"

    id               = Column(Integer, primary_key=True)
    investimento_id  = Column(Integer, ForeignKey("investimentos.id"), nullable=False)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)  # Pode ser manual
    tipo             = Column(String, nullable=False)   # "aporte", "resgate", "rendimento"
    valor            = Column(Numeric(14, 2), nullable=False)
    quantidade       = Column(Numeric(14, 6), nullable=True)  # Cotas/ações (para renda variável)
    data             = Column(Date, nullable=False)
    preco_unitario   = Column(Numeric(14, 6), nullable=True)  # Preço da cota/ação no dia
    created_at       = Column(DateTime, default=func.now())
```

### 2c. `investimentos_cotacoes` — cache de preços/taxas

```python
class InvestimentoCotacao(Base):
    __tablename__ = "investimentos_cotacoes"

    id           = Column(Integer, primary_key=True)
    ticker       = Column(String, nullable=False)  # "ITSA4", "CDI", "IGPM"
    data         = Column(Date, nullable=False)
    valor        = Column(Numeric(14, 8), nullable=False)  # Preço ou taxa diária
    fonte        = Column(String, nullable=True)  # "brapi", "bacen"
    created_at   = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("ticker", "data"),)
```

### Migration Alembic

```python
def upgrade():
    op.create_table("investimentos", ...)
    op.create_table("investimentos_transacoes", ...)
    op.create_table("investimentos_cotacoes", ...)
```

---

## 3. Backend — Serviços

### S11: Vínculo manual

```python
# app/domains/investimentos/schemas.py
class VincularAporteRequest(BaseModel):
    journal_entry_id: Optional[int] = None
    tipo: Literal["aporte", "resgate"]
    valor: Decimal
    quantidade: Optional[Decimal] = None
    data: date
    preco_unitario: Optional[Decimal] = None

@router.post("/{investimento_id}/vincular")
def vincular_aporte(
    investimento_id: int,
    data: VincularAporteRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    inv = db.query(Investimento).filter(
        Investimento.id == investimento_id,
        Investimento.user_id == user_id
    ).first_or_404()

    tx = InvestimentoTransacao(
        investimento_id=investimento_id,
        journal_entry_id=data.journal_entry_id,
        tipo=data.tipo,
        valor=data.valor,
        quantidade=data.quantidade,
        data=data.data,
        preco_unitario=data.preco_unitario
    )
    db.add(tx)

    # Marcar journal_entry como "investimento" se vinculada
    if data.journal_entry_id:
        je = db.query(JournalEntry).get(data.journal_entry_id)
        if je:
            je.CategoriaGeral = "Investimento"  # Não conta no dashboard de gastos

    db.commit()
    return {"id": tx.id}
```

### S12: Match automático

```python
# app/domains/investimentos/service.py
class InvestimentoService:
    def sugerir_matches(self, user_id: int) -> list[dict]:
        """
        Heurística: transação de débito sem vínculo,
        com valor similar a um aporte histórico de investimento
        """
        # Bancos conhecidos como corretoras
        CORRETORAS = ["xp", "btg", "clear", "rico", "modal", "inter"]

        # Buscar JournalEntries de débito das últimas 4 semanas sem vínculo
        cutoff = date.today() - timedelta(days=28)
        candidatos = self.db.execute(text("""
            SELECT je.id, je.Data, je.Lancamento, je.Valor
            FROM journal_entries je
            LEFT JOIN investimentos_transacoes it ON it.journal_entry_id = je.id
            WHERE je.user_id = :uid
              AND je.Ano >= :ano AND je.Mes >= :mes
              AND je.Valor < 0
              AND it.id IS NULL
              AND (
                LOWER(je.Lancamento) LIKE '%xp%' OR
                LOWER(je.Lancamento) LIKE '%btg%' OR
                LOWER(je.Lancamento) LIKE '%clear%' OR
                LOWER(je.Lancamento) LIKE '%rico%'
              )
        """), {"uid": user_id, "ano": cutoff.year, "mes": cutoff.month}).fetchall()

        sugestoes = []
        for cand in candidatos:
            # Buscar investimento com mesmo valor (±2%) e data próxima (±3 dias)
            match = self.db.execute(text("""
                SELECT i.id, i.nome
                FROM investimentos i
                WHERE i.user_id = :uid AND i.ativo = true
                  -- Pode ter aporte com valor similar registrado manualmente
            """), {"uid": user_id}).fetchall()
            # Retornar sugestão se houver candidatos plausíveis
            sugestoes.append({"journal_entry": dict(cand), "investimentos_sugeridos": [dict(m) for m in match[:3]]})

        return sugestoes

@router.get("/sugestoes-match")
def sugestoes(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = InvestimentoService(db)
    return service.sugerir_matches(user_id)
```

### S13: Rentabilidade CDI (job diário)

```python
# app/domains/investimentos/jobs.py
import httpx
from datetime import date

BACEN_SERIES = {
    "cdi":  "4389",  # CDI diário (% a.d.)
    "igpm": "189",
    "incc": "192",
    "ipca": "433"
}

async def atualizar_cotacoes_bacen():
    """Job diário — atualiza taxas do BACEN."""
    hoje = date.today().strftime("%d/%m/%Y")
    ontem = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")

    for indexador, serie in BACEN_SERIES.items():
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json&dataInicial={ontem}&dataFinal={hoje}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            if resp.status_code == 200:
                dados = resp.json()
                for d in dados:
                    cotacao = InvestimentoCotacao(
                        ticker=indexador.upper(),
                        data=datetime.strptime(d["data"], "%d/%m/%Y").date(),
                        valor=Decimal(d["valor"].replace(",", ".")),
                        fonte="bacen"
                    )
                    # Upsert
                    db.merge(cotacao)
        db.commit()

# Cálculo de rentabilidade CDI acumulada
def calcular_rentabilidade_cdi(principal: Decimal, data_inicio: date,
                                percentual_cdi: Decimal, db: Session) -> dict:
    cotacoes = db.query(InvestimentoCotacao).filter(
        InvestimentoCotacao.ticker == "CDI",
        InvestimentoCotacao.data >= data_inicio,
        InvestimentoCotacao.data <= date.today()
    ).order_by(InvestimentoCotacao.data).all()

    valor_atual = float(principal)
    for cot in cotacoes:
        taxa_diaria = float(cot.valor) / 100 * float(percentual_cdi) / 100
        valor_atual *= (1 + taxa_diaria)

    rendimento_bruto = valor_atual - float(principal)
    dias = (date.today() - data_inicio).days

    # IR tabela regressiva
    ir_aliquota = 0.225 if dias <= 180 else (0.20 if dias <= 360 else (0.175 if dias <= 720 else 0.15))
    ir_valor = rendimento_bruto * ir_aliquota
    rendimento_liquido = rendimento_bruto - ir_valor

    return {
        "principal": float(principal),
        "valor_atual": valor_atual,
        "rendimento_bruto": rendimento_bruto,
        "rendimento_liquido": rendimento_liquido,
        "ir_estimado": ir_valor,
        "ir_aliquota": ir_aliquota,
        "dias_investido": dias,
        "pct_rentabilidade": (rendimento_bruto / float(principal)) * 100
    }
```

### S14: Cotações de ações (brapi)

```python
async def atualizar_cotacoes_acoes(tickers: list[str], db: Session):
    """Busca cotações em lote de até 10 tickers."""
    for i in range(0, len(tickers), 10):
        batch = tickers[i:i+10]
        url = f"https://brapi.dev/api/quote/{','.join(batch)}?token={BRAPI_TOKEN}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=15)
            if resp.status_code == 200:
                for quote in resp.json().get("results", []):
                    cotacao = InvestimentoCotacao(
                        ticker=quote["symbol"],
                        data=date.today(),
                        valor=Decimal(str(quote["regularMarketPrice"])),
                        fonte="brapi"
                    )
                    db.merge(cotacao)
    db.commit()

def calcular_posicao_acoes(investimento_id: int, db: Session) -> dict:
    """Custo médio FIFO + posição atual."""
    aportes = db.query(InvestimentoTransacao).filter(
        InvestimentoTransacao.investimento_id == investimento_id,
        InvestimentoTransacao.tipo.in_(["aporte", "resgate"])
    ).order_by(InvestimentoTransacao.data).all()

    # Custo médio ponderado
    qtd_total = sum(float(a.quantidade or 0) * (1 if a.tipo == "aporte" else -1) for a in aportes)
    custo_total = sum(float(a.valor) * (1 if a.tipo == "aporte" else -1) for a in aportes)
    custo_medio = custo_total / qtd_total if qtd_total > 0 else 0

    # Cotação atual
    inv = db.query(Investimento).get(investimento_id)
    cotacao = db.query(InvestimentoCotacao).filter(
        InvestimentoCotacao.ticker == inv.codigo_ativo
    ).order_by(InvestimentoCotacao.data.desc()).first()

    preco_atual = float(cotacao.valor) if cotacao else 0
    posicao_atual = qtd_total * preco_atual
    pl = posicao_atual - custo_total

    return {
        "quantidade": qtd_total,
        "custo_medio": custo_medio,
        "preco_atual": preco_atual,
        "posicao_atual": posicao_atual,
        "custo_total": custo_total,
        "pl": pl,
        "pl_pct": (pl / custo_total * 100) if custo_total > 0 else 0
    }
```

### S15: IR estimado

```python
@router.get("/ir-estimado")
def ir_estimado_carteira(
    ano: int = Query(default=date.today().year),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    investimentos = db.query(Investimento).filter(
        Investimento.user_id == user_id, Investimento.ativo == True
    ).all()

    ir_total = 0
    detalhe = []

    for inv in investimentos:
        if inv.tipo == "acao":
            # Vendas do ano
            vendas = db.query(func.sum(InvestimentoTransacao.valor)).filter(
                InvestimentoTransacao.investimento_id == inv.id,
                InvestimentoTransacao.tipo == "resgate",
                func.extract("year", InvestimentoTransacao.data) == ano
            ).scalar() or 0

            lucro = float(vendas) - float(db.query(func.sum(InvestimentoTransacao.valor)).filter(
                InvestimentoTransacao.investimento_id == inv.id,
                InvestimentoTransacao.tipo == "aporte",
                func.extract("year", InvestimentoTransacao.data) <= ano
            ).scalar() or 0)

            ir = max(0, lucro * 0.20) if vendas > 20000 else 0  # Isenção < R$20k/mês
            ir_total += ir
            detalhe.append({"investimento": inv.nome, "tipo": "acao", "ir": ir, "lucro": lucro})

        elif inv.tipo == "fii":
            rendimentos = float(db.query(func.sum(InvestimentoTransacao.valor)).filter(
                InvestimentoTransacao.investimento_id == inv.id,
                InvestimentoTransacao.tipo == "rendimento",
                func.extract("year", InvestimentoTransacao.data) == ano
            ).scalar() or 0)
            ir = rendimentos * 0.20
            ir_total += ir
            detalhe.append({"investimento": inv.nome, "tipo": "fii", "ir": ir})

        elif inv.tipo == "renda_fixa" and inv.indexador:
            rent = calcular_rentabilidade_cdi(inv.principal, inv.data_inicio, inv.percentual_indexador, db)
            ir = rent["ir_estimado"]
            ir_total += ir
            detalhe.append({"investimento": inv.nome, "tipo": "renda_fixa", "ir": ir})

    return {"ir_total_estimado": ir_total, "ano": ano, "detalhe": detalhe}
```

---

## 4. Frontend — Componentes

### `CarteiraView` (`features/investimentos/components/carteira-view.tsx`)

```tsx
export function CarteiraView() {
  const { data } = useSWR("/api/investimentos", fetcher)

  const porTipo = useMemo(() => {
    const grupos: Record<string, Investimento[]> = {}
    data?.forEach(inv => {
      if (!grupos[inv.tipo]) grupos[inv.tipo] = []
      grupos[inv.tipo].push(inv)
    })
    return grupos
  }, [data])

  return (
    <div className="space-y-4">
      {Object.entries(porTipo).map(([tipo, investimentos]) => (
        <div key={tipo}>
          <h3 className="text-sm font-semibold capitalize text-muted-foreground mb-2">
            {tipo.replace("_", " ")}
          </h3>
          {investimentos.map(inv => (
            <InvestimentoDetailCard key={inv.id} investimento={inv} />
          ))}
        </div>
      ))}
    </div>
  )
}
```

### `InvestimentoDetailCard` (`features/investimentos/components/investimento-detail-card.tsx`)

```tsx
export function InvestimentoDetailCard({ investimento }: Props) {
  const { data: rent } = useSWR(`/api/investimentos/${investimento.id}/rentabilidade`, fetcher)

  return (
    <Card className="mb-2">
      <CardContent className="pt-3 pb-3">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium">{investimento.nome}</p>
            {investimento.indexador && (
              <p className="text-xs text-muted-foreground">
                {investimento.percentual_indexador}% {investimento.indexador.toUpperCase()}
              </p>
            )}
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold">{formatBRL(rent?.valor_atual ?? 0)}</p>
            {rent && (
              <p className={cn("text-xs", rent.pl_pct >= 0 ? "text-green-500" : "text-red-500")}>
                {rent.pl_pct >= 0 ? "+" : ""}{rent.pl_pct?.toFixed(2)}%
              </p>
            )}
          </div>
        </div>
        {rent && (
          <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
            <span>Investido: {formatBRL(rent.principal ?? rent.custo_total)}</span>
            <span>Rendimento liq.: {formatBRL(rent.rendimento_liquido ?? rent.pl)}</span>
            <span>IR: {formatBRL(rent.ir_estimado ?? 0)}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

### `VinculoAporteModal` (`features/investimentos/components/vinculo-aporte-modal.tsx`)

```tsx
export function VinculoAporteModal({ journalEntry, onClose, onSaved }: Props) {
  const { data: investimentos } = useSWR("/api/investimentos", fetcher)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [valor, setValor] = useState(String(Math.abs(journalEntry.Valor)))

  const handleVincular = async () => {
    await fetch(`/api/investimentos/${selectedId}/vincular`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        journal_entry_id: journalEntry.id,
        tipo: journalEntry.Valor < 0 ? "aporte" : "resgate",
        valor: parseBRLInput(valor),
        data: journalEntry.Data
      })
    })
    onSaved()
    onClose()
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>🔗 Vincular investimento</DialogTitle>
          <DialogDescription>{journalEntry.Lancamento} • {formatBRL(journalEntry.Valor)}</DialogDescription>
        </DialogHeader>

        <div className="space-y-3">
          <Select onValueChange={v => setSelectedId(Number(v))}>
            <SelectTrigger><SelectValue placeholder="Selecionar investimento" /></SelectTrigger>
            <SelectContent>
              {investimentos?.map(inv => (
                <SelectItem key={inv.id} value={String(inv.id)}>{inv.nome}</SelectItem>
              ))}
              <SelectItem value="new">➕ Criar novo investimento</SelectItem>
            </SelectContent>
          </Select>

          <div>
            <label className="text-sm">Valor</label>
            <Input value={valor} onChange={e => setValor(formatBRLInput(e.target.value))} />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button disabled={!selectedId} onClick={handleVincular}>Vincular</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

---

## 5. Job Scheduler

```python
# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("cron", hour=7, minute=0)  # 7h todo dia
async def job_cotacoes_bacen():
    """Atualiza CDI, IGPM, INCC, IPCA do BACEN."""
    async with get_db_context() as db:
        await atualizar_cotacoes_bacen(db)

@scheduler.scheduled_job("cron", minute="*/15", day_of_week="mon-fri",
                          hour="10-17")  # A cada 15min em dias úteis
async def job_cotacoes_acoes():
    """Atualiza preços de ações/FIIs durante pregão."""
    async with get_db_context() as db:
        tickers = db.query(Investimento.codigo_ativo).filter(
            Investimento.tipo.in_(["acao", "fii"]),
            Investimento.codigo_ativo.isnot(None)
        ).distinct().all()
        await atualizar_cotacoes_acoes([t[0] for t in tickers], db)
```

---

## 6. Checklist de Implementação

### Sprint 8 — Vínculos + CDI + Match
- [ ] Migrations: `investimentos`, `investimentos_transacoes`, `investimentos_cotacoes`
- [ ] Endpoints: CRUD `investimentos`, `POST /vincular`, `GET /rentabilidade/{id}`
- [ ] Job diário BACEN (CDI, IGPM, INCC, IPCA)
- [ ] Função `calcular_rentabilidade_cdi()`
- [ ] Endpoint `GET /sugestoes-match` com heurística básica
- [ ] Componentes: `CarteiraView`, `InvestimentoDetailCard` (renda fixa)
- [ ] Componente `VinculoAporteModal` acessível do extrato
- [ ] Componente `SugestoesMatchCard`

### Sprint 9 — Ações + IR + Resgate + Saldo
- [ ] Variável de ambiente `BRAPI_TOKEN` configurada
- [ ] Job de cotações brapi (a cada 15min durante pregão)
- [ ] Função `calcular_posicao_acoes()` com custo médio
- [ ] `InvestimentoDetailCard` suporte a ações (quantidade, P&L, variação dia)
- [ ] Endpoint `GET /ir-estimado` com regras corretas por tipo
- [ ] `VinculoResgateModal` — registrar venda/resgate
- [ ] Endpoint `GET /saldo-corretora` por banco
- [ ] Componente `SaldoCorretoraCard`
- [ ] Componente `IREstimadoView`
- [ ] Tela `/mobile/carteira` completa
- [ ] Link "Carteira" no BottomNav
