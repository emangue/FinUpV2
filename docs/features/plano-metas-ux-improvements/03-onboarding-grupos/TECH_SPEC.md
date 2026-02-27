# TECH SPEC — Onboarding + Grupos Padrão

**Sub-projeto:** 03 | **Sprint:** 2

---

## Migration

### `journal_entries.fonte` e `journal_entries.is_demo`

```python
# alembic revision --autogenerate -m "add_fonte_is_demo_journal_entries"
def upgrade():
    op.add_column('journal_entries',
        sa.Column('fonte', sa.String(20), nullable=True,
                  comment="'upload'|'planilha'|'demo'|'manual'"))
    op.add_column('journal_entries',
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('ix_journal_entries_fonte', 'journal_entries', ['fonte'])
    op.create_index('ix_journal_entries_is_demo', 'journal_entries', ['is_demo'])
```

---

## Backend

### Progresso do onboarding

```python
# app/domains/onboarding/router.py
@router.get("/progress")
def get_progress(user_id=Depends(get_current_user_id), db=Depends(get_db)):
    has_upload = db.query(UploadHistory).filter_by(
        user_id=user_id, status="sucesso"
    ).first() is not None
    has_plano = db.query(BudgetPlanning).filter_by(user_id=user_id).first() is not None
    has_invest = db.query(InvestimentosPortfolio).filter_by(user_id=user_id).first() is not None
    return {
        "conta_criada": True,        # sempre True se chegou aqui
        "primeiro_upload": has_upload,
        "plano_criado": has_plano,
        "investimento_adicionado": has_invest,
        "onboarding_completo": all([has_upload, has_plano, has_invest]),
    }
```

### Modo demo

```python
# Seed de dados demo (executado uma vez por usuário)
@router.post("/modo-demo")
def ativar_modo_demo(user_id=Depends(get_current_user_id), db=Depends(get_db)):
    # Verificar se já tem dados demo
    if db.query(JournalEntry).filter_by(user_id=user_id, fonte="demo").count() > 0:
        return {"message": "Modo demo já ativo"}
    OnboardingService(db).criar_dados_demo(user_id)
    return {"message": "Dados de demonstração criados"}

@router.delete("/modo-demo")
def desativar_modo_demo(user_id=Depends(get_current_user_id), db=Depends(get_db)):
    deleted = db.query(JournalEntry).filter_by(
        user_id=user_id, fonte="demo"
    ).delete()
    db.commit()
    return {"message": f"{deleted} registros demo removidos"}

# OnboardingService.criar_dados_demo — 90 transações ~3 meses
DEMO_TRANSACTIONS = [
    {"Lancamento": "Supermercado Extra",  "Valor": -450.00, "Grupo": "Alimentação",  "Mes": 1},
    {"Lancamento": "Netflix",             "Valor": -55.90,  "Grupo": "Lazer",         "Mes": 1},
    {"Lancamento": "Salário",             "Valor": 5000.00, "Grupo": "Receita",       "Mes": 1},
    # ... ~87 mais cobrindo os 3 meses e todos os grupos
]
```

---

## Frontend

### Middleware de onboarding

```ts
// src/middleware.ts (ou src/app/mobile/middleware.ts se por segmento)
import { NextRequest, NextResponse } from "next/server"

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Não interceptar paths de sistema
  const BYPASS = ["/mobile/onboarding", "/mobile/upload", "/api/", "/_next/"]
  if (BYPASS.some(p => pathname.startsWith(p))) return NextResponse.next()

  // Verificar cookie/header de onboarding completo
  const onboardingCompleto = request.cookies.get("onboarding_completo")?.value === "true"
  if (!onboardingCompleto && pathname.startsWith("/mobile")) {
    return NextResponse.redirect(new URL("/mobile/onboarding/welcome", request.url))
  }
  return NextResponse.next()
}
```

### Telas de onboarding

```
src/app/mobile/onboarding/
├── welcome/page.tsx         # Tela de boas-vindas
├── choose-path/page.tsx     # Escolher: meus dados ou explorar
└── layout.tsx               # Layout sem bottom nav (onboarding é linear)
```

```tsx
// welcome/page.tsx
export default function WelcomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-dvh p-8 text-center">
      <Logo className="mb-8" />
      <h1 className="text-2xl font-bold mb-4">Bem-vindo ao FinUp</h1>
      <ul className="text-sm text-muted-foreground space-y-2 mb-10 text-left max-w-xs">
        <li>✅ Veja para onde vai seu dinheiro todo mês</li>
        <li>✅ Planeje sua aposentadoria e metas</li>
        <li>✅ Acompanhe seus investimentos em um lugar só</li>
      </ul>
      <Link href="/mobile/onboarding/choose-path">
        <Button size="lg" className="w-full mb-3">Começar →</Button>
      </Link>
      <Button variant="ghost" size="sm" onClick={markOnboardingComplete}>
        Pular por agora
      </Button>
    </div>
  )
}
```

### Checklist de progresso

```tsx
// src/features/onboarding/components/onboarding-checklist.tsx
"use client"
import useSWR from "swr"

const ITEMS = [
  { key: "conta_criada",              label: "Criou sua conta",             href: null },
  { key: "primeiro_upload",           label: "Suba seu primeiro extrato",   href: "/mobile/upload" },
  { key: "plano_criado",              label: "Crie seu Plano Financeiro",   href: "/mobile/plano" },
  { key: "investimento_adicionado",   label: "Adicione um investimento",    href: "/mobile/carteira" },
]

export function OnboardingChecklist() {
  const { data } = useSWR("/api/v1/onboarding/progress")
  if (!data) return null
  if (data.onboarding_completo) return null  // some quando tudo feito

  const done = Object.values(data).filter(Boolean).length - 1  // -1 para onboarding_completo

  return (
    <div className="rounded-xl border p-4 mb-4">
      <p className="text-sm font-medium mb-3">
        Seus primeiros passos · {done}/4 concluídos
      </p>
      {ITEMS.map(item => (
        <div key={item.key} className="flex items-center gap-3 py-2">
          <span>{data[item.key] ? "✅" : "⬜"}</span>
          <span className={cn("text-sm flex-1", data[item.key] && "text-muted-foreground line-through")}>
            {item.label}
          </span>
          {!data[item.key] && item.href && (
            <Link href={item.href}>
              <Button size="sm" variant="outline">→ Fazer</Button>
            </Link>
          )}
        </div>
      ))}
    </div>
  )
}
```

### Banner demo

```tsx
// src/features/onboarding/components/demo-mode-banner.tsx
"use client"
export function DemoModeBanner() {
  const { data } = useSWR("/api/v1/onboarding/progress")
  // Mostrar apenas se há dados demo (verificar via flag no progress ou header)
  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 flex items-center justify-between text-sm">
      <span className="text-amber-800">📊 Modo de Exploração — dados fictícios</span>
      <Link href="/mobile/upload">
        <Button size="sm" variant="outline" className="text-amber-800 border-amber-300">
          Usar meus dados →
        </Button>
      </Link>
    </div>
  )
}
```

---

## Checklist

### Banco
- [ ] Migration: `journal_entries.fonte` (string) + `is_demo` (boolean)

### Backend
- [ ] `GET /onboarding/progress` — 4 booleans + `onboarding_completo`
- [ ] `POST /onboarding/modo-demo` — seed ~90 transações com `fonte='demo'`
- [ ] `DELETE /onboarding/modo-demo` — limpar `WHERE fonte='demo'`
- [ ] Registrar em `docs/features/03-onboarding-grupos/DEMO_SEED.md` quais transações compõem o dataset

### Frontend
- [ ] Middleware: redirect para `/mobile/onboarding/welcome` no primeiro acesso
- [ ] Tela `/mobile/onboarding/welcome` com 2 CTAs
- [ ] Tela `/mobile/onboarding/choose-path` (upload vs. demo)
- [ ] `OnboardingChecklist` no `/mobile/inicio` (some quando completo)
- [ ] `DemoModeBanner` quando `fonte='demo'` existe
- [ ] `DemoModeBanner`: "Usar meus dados →" chama DELETE + vai para upload
- [ ] Banners S29 (nudges): implementar 4 triggers com `[X] Fechar` + localStorage
