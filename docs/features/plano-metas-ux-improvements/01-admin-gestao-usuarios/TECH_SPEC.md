# TECH SPEC — Admin: Gestão Completa de Usuários

**Sub-projeto:** 01 | **Sprint:** 0

---

## Migrations

### 1. `base_grupos_config.is_padrao`

```python
# alembic revision --autogenerate -m "add_is_padrao_base_grupos_config"
def upgrade():
    op.add_column('base_grupos_config',
        sa.Column('is_padrao', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('ix_base_grupos_config_is_padrao', 'base_grupos_config', ['is_padrao'])

def downgrade():
    op.drop_index('ix_base_grupos_config_is_padrao', 'base_grupos_config')
    op.drop_column('base_grupos_config', 'is_padrao')
```

---

## Backend — `app/domains/users/`

### Constante: grupos padrão

```python
# app/domains/users/service.py
GRUPOS_PADRAO = [
    {"nome": "Alimentação",   "categoria_geral": "Despesa",       "cor": "#E74C3C"},
    {"nome": "Moradia",       "categoria_geral": "Despesa",       "cor": "#E67E22"},
    {"nome": "Transporte",    "categoria_geral": "Despesa",       "cor": "#F1C40F"},
    {"nome": "Saúde",         "categoria_geral": "Despesa",       "cor": "#27AE60"},
    {"nome": "Educação",      "categoria_geral": "Despesa",       "cor": "#2980B9"},
    {"nome": "Lazer",         "categoria_geral": "Despesa",       "cor": "#8E44AD"},
    {"nome": "Roupas",        "categoria_geral": "Despesa",       "cor": "#16A085"},
    {"nome": "Outros",        "categoria_geral": "Despesa",       "cor": "#B0B0B0"},
    {"nome": "Investimentos", "categoria_geral": "Investimento",  "cor": "#2ECC71"},
    {"nome": "Receita",       "categoria_geral": "Receita",       "cor": "#F7DC6F"},
    {"nome": "Transferência", "categoria_geral": "Transferência", "cor": "#AEB6BF"},
]
```

### Trigger de inicialização (SA4)

```python
class UserService:
    def _inicializar_usuario(self, user_id: int) -> None:
        """Idempotente — não duplica se já inicializado."""
        existentes = self.db.query(BaseGruposConfig).filter_by(
            user_id=user_id, is_padrao=True
        ).count()
        if existentes > 0:
            return

        for g in GRUPOS_PADRAO:
            self.db.add(BaseGruposConfig(
                user_id=user_id, is_padrao=True, **g
            ))

        if not self.db.query(UserFinancialProfile).filter_by(user_id=user_id).first():
            self.db.add(UserFinancialProfile(user_id=user_id))
        self.db.flush()

    def create_user(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        self.db.flush()            # garante user.id antes do trigger
        self._inicializar_usuario(user.id)
        self.db.commit()
        return user
```

### Stats de conta (SA2)

```python
# router
@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(user_id: int, db=Depends(get_db), _=Depends(require_admin)):
    return UserService(db).get_stats(user_id)

# service
def get_stats(self, user_id: int) -> dict:
    total_tx      = self.db.query(func.count(JournalEntry.id)).filter_by(user_id=user_id).scalar() or 0
    total_uploads = self.db.query(func.count(UploadHistory.id)).filter_by(user_id=user_id).scalar() or 0
    ultimo_upload = self.db.query(func.max(UploadHistory.criado_em)).filter_by(user_id=user_id).scalar()
    total_grupos  = self.db.query(func.count(BaseGruposConfig.id)).filter_by(user_id=user_id).scalar() or 0
    tem_plano     = self.db.query(BudgetPlanning).filter_by(user_id=user_id).first() is not None
    tem_invest    = self.db.query(InvestimentosPortfolio).filter_by(user_id=user_id).first() is not None
    return dict(total_transacoes=total_tx, total_uploads=total_uploads,
                ultimo_upload_em=ultimo_upload, total_grupos=total_grupos,
                tem_plano=tem_plano, tem_investimentos=tem_invest)
```

### Reativar conta (SA1)

```python
@router.post("/{user_id}/reativar")
def reativar(user_id: int, db=Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user: raise HTTPException(404, "Usuário não encontrado")
    user.ativo = True
    db.commit()
    return {"message": "Usuário reativado"}
```

### Purge total (SA3)

```python
# schemas
class PurgeConfirmacao(BaseModel):
    confirmacao: str   # deve ser "EXCLUIR PERMANENTEMENTE"
    email_usuario: str  # deve bater com user.email

# router
@router.delete("/{user_id}/purge")
def purge(user_id: int, body: PurgeConfirmacao, db=Depends(get_db), admin=Depends(require_admin)):
    if user_id == 1:
        raise HTTPException(403, "Admin principal não pode ser purgado")
    if body.confirmacao != "EXCLUIR PERMANENTEMENTE":
        raise HTTPException(400, "Confirmação inválida")
    user = db.query(User).filter_by(id=user_id).first()
    if not user: raise HTTPException(404, "Usuário não encontrado")
    if body.email_usuario.lower() != user.email.lower():
        raise HTTPException(400, "E-mail não confere")
    return UserService(db).purge_user(user_id, executado_por=admin.id)

# service — ordem de deleção respeita FKs
def purge_user(self, user_id: int, executado_por: int) -> dict:
    db = self.db
    db.query(InvestimentosTransacoes).filter_by(user_id=user_id).delete()
    db.query(InvestimentosHistorico).filter_by(user_id=user_id).delete()
    db.query(InvestimentosPortfolio).filter_by(user_id=user_id).delete()
    db.query(BudgetPlanning).filter_by(user_id=user_id).delete()
    db.query(BaseExpectativas).filter_by(user_id=user_id).delete()
    db.query(UserFinancialProfile).filter_by(user_id=user_id).delete()
    db.query(UploadHistory).filter_by(user_id=user_id).delete()  # cascade → journal_entries
    db.query(BaseMarcacoes).filter_by(user_id=user_id).delete()
    db.query(BaseParcelas).filter_by(user_id=user_id).delete()
    db.query(BaseGruposConfig).filter_by(user_id=user_id).delete()
    db.query(User).filter_by(id=user_id).delete()
    db.commit()
    logger.warning(f"PURGE user_id={user_id} por admin_id={executado_por}")
    return {"message": f"Usuário {user_id} removido permanentemente"}
```

### Listar com filtro de inativos (SA5)

```python
@router.get("/", response_model=list[UserResponse])
def list_users(apenas_ativos: bool = True, db=Depends(get_db), _=Depends(require_admin)):
    q = db.query(User)
    if apenas_ativos:
        q = q.filter(User.ativo == True)
    return q.order_by(User.nome).all()
```

---

## Frontend — `app_admin/frontend/`

### `UserStatsCell` — coluna com lazy load e tooltip

```tsx
// src/components/user-stats-cell.tsx
"use client"
import useSWR from "swr"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

export function UserStatsCell({ userId }: { userId: number }) {
  const { data, isLoading } = useSWR(`/api/v1/users/${userId}/stats`)
  if (isLoading) return <span className="text-muted-foreground text-sm">…</span>
  if (!data) return <span className="text-muted-foreground text-sm">Sem dados</span>
  const ultimo = data.ultimo_upload_em
    ? new Date(data.ultimo_upload_em).toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" })
    : "nunca"
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="text-sm cursor-help">
          {data.total_transacoes.toLocaleString()} tx · últ. {ultimo}
        </span>
      </TooltipTrigger>
      <TooltipContent>
        <p>{data.total_uploads} uploads · {data.total_grupos} grupos</p>
        <p>{data.tem_plano ? "✅ Tem plano" : "❌ Sem plano"}</p>
        <p>{data.tem_investimentos ? "✅ Tem investimentos" : "❌ Sem investimentos"}</p>
      </TooltipContent>
    </Tooltip>
  )
}
```

### `PurgeUserModal` — 2 etapas

```tsx
// src/components/purge-user-modal.tsx
"use client"
import { useState } from "react"
import { Dialog, DialogContent, DialogHeader } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function PurgeUserModal({ user, stats, open, onClose, onConfirm }) {
  const [step, setStep] = useState<1|2>(1)
  const [emailInput, setEmailInput] = useState("")
  const emailOk = emailInput.trim().toLowerCase() === user.email.toLowerCase()

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        {step === 1 ? (
          <>
            <DialogHeader>⚠️ Excluir permanentemente: {user.nome}</DialogHeader>
            <ul className="text-sm mt-2 space-y-1">
              <li>🗂 {stats.total_transacoes.toLocaleString()} transações</li>
              <li>📤 {stats.total_uploads} uploads</li>
              <li>📋 {stats.total_grupos} grupos</li>
              {stats.tem_investimentos && (
                <li className="text-amber-600">⚠️ Investimentos vinculados — também removidos</li>
              )}
            </ul>
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={onClose}>Cancelar</Button>
              <Button variant="destructive" onClick={() => setStep(2)}>Continuar →</Button>
            </div>
          </>
        ) : (
          <>
            <DialogHeader>⚠️ Confirmar exclusão permanente</DialogHeader>
            <p className="text-sm">Digite o e-mail do usuário:</p>
            <Input value={emailInput} onChange={e => setEmailInput(e.target.value)}
              placeholder={user.email} className="mt-2" />
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={() => setStep(1)}>← Voltar</Button>
              <Button variant="destructive" disabled={!emailOk}
                onClick={() => onConfirm(user.id, emailInput)}>
                🗑 Excluir Permanentemente
              </Button>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
```

### Toggle de inativos na listagem

```tsx
// src/app/usuarios/page.tsx (trecho)
const [verInativos, setVerInativos] = useState(false)
const { data } = useSWR(`/api/v1/users?apenas_ativos=${!verInativos}`)

// No header:
<label className="flex items-center gap-2 text-sm cursor-pointer">
  <input type="checkbox" checked={verInativos} onChange={e => setVerInativos(e.target.checked)} />
  Ver inativos
</label>

// Na linha:
<tr className={!user.ativo ? "opacity-50 bg-gray-50" : ""}>
  <td>{user.nome} {!user.ativo && <Badge variant="outline">INATIVA</Badge>}</td>
```

---

## Checklist

### Banco
- [ ] Migration: `base_grupos_config.is_padrao` boolean default false

### Backend
- [ ] `_inicializar_usuario()` idempotente: 11 grupos + perfil financeiro
- [ ] `create_user()` chama `_inicializar_usuario()` após flush
- [ ] `GET /users/{id}/stats` — sem bloquear listagem principal
- [ ] `POST /users/{id}/reativar` — seta `ativo=True`
- [ ] `DELETE /users/{id}/purge` — body `PurgeConfirmacao`, user_id=1 protegido
- [ ] `GET /users/?apenas_ativos=false` — inclui inativos
- [ ] Teste: criar usuário → confirmar 11 grupos em `base_grupos_config`
- [ ] Teste: purge → `SELECT COUNT(*) WHERE user_id=X` = 0 em todas as tabelas

### Frontend (app_admin)
- [ ] `UserStatsCell` com skeleton + tooltip
- [ ] Toggle "Ver inativos" + badge INATIVA + opacidade 50%
- [ ] Botão "Reativar" apenas em inativos; "Desativar" apenas em ativos
- [ ] `PurgeUserModal` em 2 etapas; confirmar desabilitado até e-mail bater
- [ ] user_id=1: sem botão Purge
