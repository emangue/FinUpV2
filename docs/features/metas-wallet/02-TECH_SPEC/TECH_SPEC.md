# 🔧 TECH SPEC - Sistema de Metas Financeiras (Wallet)

**Status:** 🟡 Em Revisão  
**Versão:** 1.0  
**Data:** 02/02/2026  
**Autor:** Tech Lead  
**PRD:** [Link para PRD.md](./01-PRD/PRD.md)

---

## 📊 Sumário Técnico

**Arquitetura:** Cliente-Servidor (Next.js + FastAPI)  
**Stack:** TypeScript + Python + PostgreSQL  
**Esforço:** 148h total (4 semanas-homem)  
**Sprints:** 3 sprints de 2 semanas

---

## 🏗️ 1. Arquitetura

### 1.1 Diagrama Geral

```
┌─────────────────┐      HTTPS/JSON      ┌──────────────────┐
│   Frontend      │ ──────────────────> │   Backend         │
│   (Next.js 14)  │ <────────────────── │   (FastAPI)       │
│   - Wallet Page │                      │   - Metas API     │
│   - Donut Chart │                      │   - Budgets API   │
│   - Categories  │                      │   - Wallet API    │
└─────────────────┘                      └─────────┬─────────┘
                                                   │
                                                   v
                                         ┌──────────────────┐
                                         │   PostgreSQL 16  │
                                         │   - metas        │
                                         │   - budgets      │
                                         │   - notifications│
                                         └──────────────────┘
```

### 1.2 Decisões Arquiteturais

**DA-01: Recharts para Gráfico Donut**
- **Contexto:** Gráfico circular com fatias coloridas
- **Decisão:** Recharts 2.x (PieChart component)
- **Razão:** Suporte nativo a donut, responsivo, performático
- **Alternativas:** Chart.js (mais pesado), D3.js (muito baixo nível)

**DA-02: Dados Calculados em Runtime vs Cached**
- **Contexto:** Progresso de meta precisa ser atualizado em tempo real
- **Decisão:** Calcular no backend a cada request (sem cache)
- **Razão:** Dados mudam frequentemente (nova transação)
- **Consequências:** ✅ Sempre atualizado, ⚠️ Query adicional

**DA-03: Segmented Control com Estado Local**
- **Contexto:** Alternar entre "Savings" e "Expenses"
- **Decisão:** useState local, não persistir no servidor
- **Razão:** Preferência de visualização, não é estado crítico
- **Alternativas:** URL search params (overkill para este caso)

---

## 🗄️ 2. Database Schema

### 2.1 Tabelas Novas

#### **Tabela: `metas`**

```sql
CREATE TABLE metas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    ano INTEGER NOT NULL CHECK (ano >= 2026),
    valor_meta DECIMAL(15, 2) NOT NULL CHECK (valor_meta > 0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, mes, ano)
);

CREATE INDEX idx_metas_user_periodo ON metas(user_id, ano DESC, mes DESC);
```

---

#### **Tabela: `category_budgets`**

```sql
CREATE TABLE category_budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,
    mes INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    ano INTEGER NOT NULL CHECK (ano >= 2026),
    budget DECIMAL(15, 2) NOT NULL CHECK (budget > 0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, categoria_geral, mes, ano)
);

CREATE INDEX idx_budgets_user_periodo ON category_budgets(user_id, ano DESC, mes DESC);
CREATE INDEX idx_budgets_categoria ON category_budgets(categoria_geral);
```

---

#### **Tabela: `budget_notifications`**

```sql
CREATE TABLE budget_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,
    mensagem TEXT NOT NULL,
    percentual_gasto INTEGER CHECK (percentual_gasto BETWEEN 0 AND 200),
    lida BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_lida ON budget_notifications(user_id, lida);
CREATE INDEX idx_notifications_created ON budget_notifications(created_at DESC);
```

---

### 2.2 Migrations Alembic

**Arquivo:** `app_dev/backend/migrations/versions/20260202_add_wallet_tables.py`

```python
"""add wallet tables (metas, category_budgets, budget_notifications)

Revision ID: wallet_v1_tables
Revises: previous_revision
Create Date: 2026-02-02 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'wallet_v1_tables'
down_revision = 'previous_revision'  # Ajustar para última revision
branch_labels = None
depends_on = None

def upgrade():
    # Tabela metas
    op.create_table(
        'metas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('valor_meta', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('mes BETWEEN 1 AND 12', name='check_mes_valido'),
        sa.CheckConstraint('ano >= 2026', name='check_ano_valido'),
        sa.CheckConstraint('valor_meta > 0', name='check_valor_positivo'),
        sa.UniqueConstraint('user_id', 'mes', 'ano', name='unique_meta_periodo')
    )
    op.create_index('idx_metas_user_periodo', 'metas', ['user_id', 'ano', 'mes'])
    
    # Tabela category_budgets
    op.create_table(
        'category_budgets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('categoria_geral', sa.String(50), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('budget', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('mes BETWEEN 1 AND 12', name='check_budget_mes'),
        sa.CheckConstraint('ano >= 2026', name='check_budget_ano'),
        sa.CheckConstraint('budget > 0', name='check_budget_positivo'),
        sa.UniqueConstraint('user_id', 'categoria_geral', 'mes', 'ano', name='unique_budget_categoria')
    )
    op.create_index('idx_budgets_user_periodo', 'category_budgets', ['user_id', 'ano', 'mes'])
    op.create_index('idx_budgets_categoria', 'category_budgets', ['categoria_geral'])
    
    # Tabela budget_notifications
    op.create_table(
        'budget_notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('categoria_geral', sa.String(50), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('percentual_gasto', sa.Integer()),
        sa.Column('lida', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint('percentual_gasto BETWEEN 0 AND 200', name='check_percentual')
    )
    op.create_index('idx_notifications_user_lida', 'budget_notifications', ['user_id', 'lida'])
    op.create_index('idx_notifications_created', 'budget_notifications', ['created_at'])

def downgrade():
    op.drop_index('idx_notifications_created')
    op.drop_index('idx_notifications_user_lida')
    op.drop_table('budget_notifications')
    
    op.drop_index('idx_budgets_categoria')
    op.drop_index('idx_budgets_user_periodo')
    op.drop_table('category_budgets')
    
    op.drop_index('idx_metas_user_periodo')
    op.drop_table('metas')
```

---

## 🐍 3. Backend - Models (SQLAlchemy)

### 3.1 Models

**Arquivo:** `app_dev/backend/app/domains/wallet/models.py`

```python
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, CheckConstraint, UniqueConstraint, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Meta(Base):
    """Modelo de Meta de Economia Mensal"""
    __tablename__ = "metas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    valor_meta = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=datetime.now)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('mes BETWEEN 1 AND 12', name='check_mes_valido'),
        CheckConstraint('ano >= 2026', name='check_ano_valido'),
        CheckConstraint('valor_meta > 0', name='check_valor_positivo'),
        UniqueConstraint('user_id', 'mes', 'ano', name='unique_meta_periodo'),
    )
    
    # Relationships
    user = relationship("User", back_populates="metas")


class CategoryBudget(Base):
    """Modelo de Budget por Categoria"""
    __tablename__ = "category_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    categoria_geral = Column(String(50), nullable=False)
    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    budget = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP, server_default=text("NOW()"), onupdate=datetime.now)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('mes BETWEEN 1 AND 12', name='check_budget_mes'),
        CheckConstraint('ano >= 2026', name='check_budget_ano'),
        CheckConstraint('budget > 0', name='check_budget_positivo'),
        UniqueConstraint('user_id', 'categoria_geral', 'mes', 'ano', name='unique_budget_categoria'),
    )
    
    # Relationships
    user = relationship("User", back_populates="budgets")


class BudgetNotification(Base):
    """Modelo de Notificação de Budget"""
    __tablename__ = "budget_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    categoria_geral = Column(String(50), nullable=False)
    mensagem = Column(String, nullable=False)
    percentual_gasto = Column(Integer)
    lida = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))
    
    # Constraints
    __table_args__ = (
        CheckConstraint('percentual_gasto BETWEEN 0 AND 200', name='check_percentual'),
    )
    
    # Relationships
    user = relationship("User", back_populates="budget_notifications")
```

---

## 📝 4. Backend - Schemas (Pydantic)

**Arquivo:** `app_dev/backend/app/domains/wallet/schemas.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

# === META SCHEMAS ===

class MetaCreate(BaseModel):
    """Schema para criar meta"""
    mes: int = Field(..., ge=1, le=12, description="Mês da meta (1-12)")
    ano: int = Field(..., ge=2026, description="Ano da meta")
    valor_meta: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, description="Valor da meta em R$")
    
    @field_validator('mes')
    def validate_mes(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Mês deve estar entre 1 e 12')
        return v


class MetaUpdate(BaseModel):
    """Schema para atualizar meta"""
    valor_meta: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)


class MetaResponse(BaseModel):
    """Schema de resposta de meta"""
    id: int
    user_id: int
    mes: int
    ano: int
    valor_meta: Decimal
    progresso_percentual: Optional[float] = None  # Calculado
    valor_economizado: Optional[Decimal] = None   # Calculado
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# === BUDGET SCHEMAS ===

class CategoryBudgetCreate(BaseModel):
    """Schema para criar budget de categoria"""
    categoria_geral: str = Field(..., min_length=1, max_length=50)
    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2026)
    budget: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)


class CategoryBudgetUpdate(BaseModel):
    """Schema para atualizar budget"""
    budget: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)


class CategoryBudgetResponse(BaseModel):
    """Schema de resposta de budget"""
    id: int
    user_id: int
    categoria_geral: str
    mes: int
    ano: int
    budget: Decimal
    gasto_atual: Optional[Decimal] = None      # Calculado
    progresso_percentual: Optional[float] = None  # Calculado
    status: Optional[str] = None  # "ok", "warning", "danger"
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# === WALLET SUMMARY SCHEMAS ===

class WalletChartData(BaseModel):
    """Schema para dados do gráfico donut"""
    name: str
    value: float
    color: str


class WalletSummaryResponse(BaseModel):
    """Schema de resposta do summary da wallet"""
    mes: int
    ano: int
    meta_valor: Optional[Decimal] = None
    economia_atual: Decimal
    progresso_percentual: float
    receitas_mes: Decimal
    gastos_mes: Decimal
    chart_data: list[WalletChartData]


class WalletCategoryProgress(BaseModel):
    """Schema de progresso de categoria"""
    categoria: str
    icon: str  # Nome do ícone Lucide
    budget: Optional[Decimal] = None
    gasto: Decimal
    percentual: float
    status: str  # "ok", "warning", "danger"
    color: str  # Classe Tailwind (ex: "blue-500")


class WalletCategoriesResponse(BaseModel):
    """Schema de resposta das categorias"""
    categories: list[WalletCategoryProgress]


# === NOTIFICATION SCHEMAS ===

class BudgetNotificationResponse(BaseModel):
    """Schema de resposta de notificação"""
    id: int
    categoria_geral: str
    mensagem: str
    percentual_gasto: Optional[int]
    lida: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
```

---

## 🔌 5. Backend - API Endpoints

### 5.1 Router Principal

**Arquivo:** `app_dev/backend/app/domains/wallet/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from app.domains.wallet.service import WalletService
from app.domains.wallet.schemas import (
    MetaCreate, MetaUpdate, MetaResponse,
    CategoryBudgetCreate, CategoryBudgetUpdate, CategoryBudgetResponse,
    WalletSummaryResponse, WalletCategoriesResponse,
    BudgetNotificationResponse
)
from typing import List

router = APIRouter(prefix="/api/v1/wallet", tags=["Wallet"])


# === METAS ENDPOINTS ===

@router.post("/metas", response_model=MetaResponse, status_code=201)
def create_meta(
    data: MetaCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Criar nova meta de economia mensal"""
    service = WalletService(db)
    return service.create_meta(user_id, data)


@router.get("/metas", response_model=List[MetaResponse])
def list_metas(
    mes: int = Query(None, ge=1, le=12),
    ano: int = Query(None, ge=2026),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Listar metas do usuário (filtro opcional por mês/ano)"""
    service = WalletService(db)
    return service.list_metas(user_id, mes, ano)


@router.get("/metas/{meta_id}", response_model=MetaResponse)
def get_meta(
    meta_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obter meta específica"""
    service = WalletService(db)
    meta = service.get_meta(user_id, meta_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return meta


@router.patch("/metas/{meta_id}", response_model=MetaResponse)
def update_meta(
    meta_id: int,
    data: MetaUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Atualizar meta existente"""
    service = WalletService(db)
    return service.update_meta(user_id, meta_id, data)


@router.delete("/metas/{meta_id}", status_code=204)
def delete_meta(
    meta_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deletar meta"""
    service = WalletService(db)
    service.delete_meta(user_id, meta_id)
    return None


# === BUDGETS ENDPOINTS ===

@router.post("/budgets", response_model=CategoryBudgetResponse, status_code=201)
def create_budget(
    data: CategoryBudgetCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Criar budget para categoria"""
    service = WalletService(db)
    return service.create_budget(user_id, data)


@router.get("/budgets", response_model=List[CategoryBudgetResponse])
def list_budgets(
    mes: int = Query(None, ge=1, le=12),
    ano: int = Query(None, ge=2026),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Listar budgets (filtro opcional por mês/ano)"""
    service = WalletService(db)
    return service.list_budgets(user_id, mes, ano)


@router.patch("/budgets/{budget_id}", response_model=CategoryBudgetResponse)
def update_budget(
    budget_id: int,
    data: CategoryBudgetUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Atualizar budget de categoria"""
    service = WalletService(db)
    return service.update_budget(user_id, budget_id, data)


# === WALLET SUMMARY ENDPOINTS ===

@router.get("/summary", response_model=WalletSummaryResponse)
def get_wallet_summary(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2026),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obter summary da wallet (dados para gráfico donut)"""
    service = WalletService(db)
    return service.get_wallet_summary(user_id, mes, ano)


@router.get("/categories", response_model=WalletCategoriesResponse)
def get_wallet_categories(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2026),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obter progresso de categorias (lista abaixo do gráfico)"""
    service = WalletService(db)
    return service.get_wallet_categories(user_id, mes, ano)


# === NOTIFICATIONS ENDPOINTS ===

@router.get("/notifications", response_model=List[BudgetNotificationResponse])
def get_budget_notifications(
    apenas_nao_lidas: bool = Query(True),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Listar notificações de budget"""
    service = WalletService(db)
    return service.get_notifications(user_id, apenas_nao_lidas)


@router.patch("/notifications/{notification_id}/read", status_code=204)
def mark_notification_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Marcar notificação como lida"""
    service = WalletService(db)
    service.mark_notification_read(user_id, notification_id)
    return None
```

---

### 5.2 Service Layer (Lógica de Negócio)

**Arquivo:** `app_dev/backend/app/domains/wallet/service.py`

```python
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.domains.wallet.models import Meta, CategoryBudget, BudgetNotification
from app.domains.wallet.schemas import *
from app.domains.transactions.models import JournalEntry
from fastapi import HTTPException
from datetime import datetime
from decimal import Decimal


class WalletService:
    """Serviço de lógica de negócio para Wallet"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === METAS ===
    
    def create_meta(self, user_id: int, data: MetaCreate) -> MetaResponse:
        """Criar nova meta"""
        # Validar se já existe meta para o período
        existing = self.db.query(Meta).filter(
            Meta.user_id == user_id,
            Meta.mes == data.mes,
            Meta.ano == data.ano
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma meta para {data.mes}/{data.ano}"
            )
        
        # Criar meta
        meta = Meta(
            user_id=user_id,
            mes=data.mes,
            ano=data.ano,
            valor_meta=data.valor_meta
        )
        self.db.add(meta)
        self.db.commit()
        self.db.refresh(meta)
        
        # Calcular progresso
        return self._enrich_meta_response(meta)
    
    def get_meta(self, user_id: int, meta_id: int) -> Optional[MetaResponse]:
        """Obter meta específica"""
        meta = self.db.query(Meta).filter(
            Meta.id == meta_id,
            Meta.user_id == user_id
        ).first()
        
        if not meta:
            return None
        
        return self._enrich_meta_response(meta)
    
    def list_metas(self, user_id: int, mes: Optional[int] = None, ano: Optional[int] = None) -> List[MetaResponse]:
        """Listar metas do usuário"""
        query = self.db.query(Meta).filter(Meta.user_id == user_id)
        
        if mes:
            query = query.filter(Meta.mes == mes)
        if ano:
            query = query.filter(Meta.ano == ano)
        
        metas = query.order_by(Meta.ano.desc(), Meta.mes.desc()).all()
        return [self._enrich_meta_response(m) for m in metas]
    
    def update_meta(self, user_id: int, meta_id: int, data: MetaUpdate) -> MetaResponse:
        """Atualizar meta"""
        meta = self.db.query(Meta).filter(
            Meta.id == meta_id,
            Meta.user_id == user_id
        ).first()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        if data.valor_meta is not None:
            meta.valor_meta = data.valor_meta
            meta.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(meta)
        
        return self._enrich_meta_response(meta)
    
    def delete_meta(self, user_id: int, meta_id: int):
        """Deletar meta"""
        meta = self.db.query(Meta).filter(
            Meta.id == meta_id,
            Meta.user_id == user_id
        ).first()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        self.db.delete(meta)
        self.db.commit()
    
    def _enrich_meta_response(self, meta: Meta) -> MetaResponse:
        """Enriquecer meta com dados calculados"""
        # Calcular economia do mês
        economia = self._calcular_economia_mes(meta.user_id, meta.mes, meta.ano)
        progresso = (float(economia) / float(meta.valor_meta)) * 100 if meta.valor_meta > 0 else 0
        
        return MetaResponse(
            id=meta.id,
            user_id=meta.user_id,
            mes=meta.mes,
            ano=meta.ano,
            valor_meta=meta.valor_meta,
            valor_economizado=economia,
            progresso_percentual=round(progresso, 1),
            created_at=meta.created_at,
            updated_at=meta.updated_at
        )
    
    # === BUDGETS ===
    
    def create_budget(self, user_id: int, data: CategoryBudgetCreate) -> CategoryBudgetResponse:
        """Criar budget de categoria"""
        # Validar se já existe
        existing = self.db.query(CategoryBudget).filter(
            CategoryBudget.user_id == user_id,
            CategoryBudget.categoria_geral == data.categoria_geral,
            CategoryBudget.mes == data.mes,
            CategoryBudget.ano == data.ano
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Budget para {data.categoria_geral} em {data.mes}/{data.ano} já existe"
            )
        
        budget = CategoryBudget(
            user_id=user_id,
            categoria_geral=data.categoria_geral,
            mes=data.mes,
            ano=data.ano,
            budget=data.budget
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        return self._enrich_budget_response(budget)
    
    def list_budgets(self, user_id: int, mes: Optional[int] = None, ano: Optional[int] = None) -> List[CategoryBudgetResponse]:
        """Listar budgets"""
        query = self.db.query(CategoryBudget).filter(CategoryBudget.user_id == user_id)
        
        if mes:
            query = query.filter(CategoryBudget.mes == mes)
        if ano:
            query = query.filter(CategoryBudget.ano == ano)
        
        budgets = query.all()
        return [self._enrich_budget_response(b) for b in budgets]
    
    def update_budget(self, user_id: int, budget_id: int, data: CategoryBudgetUpdate) -> CategoryBudgetResponse:
        """Atualizar budget"""
        budget = self.db.query(CategoryBudget).filter(
            CategoryBudget.id == budget_id,
            CategoryBudget.user_id == user_id
        ).first()
        
        if not budget:
            raise HTTPException(status_code=404, detail="Budget não encontrado")
        
        if data.budget is not None:
            budget.budget = data.budget
            budget.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(budget)
        
        return self._enrich_budget_response(budget)
    
    def _enrich_budget_response(self, budget: CategoryBudget) -> CategoryBudgetResponse:
        """Enriquecer budget com dados calculados"""
        # Calcular gasto da categoria no período
        gasto = self._calcular_gasto_categoria(
            budget.user_id,
            budget.categoria_geral,
            budget.mes,
            budget.ano
        )
        
        percentual = (float(gasto) / float(budget.budget)) * 100 if budget.budget > 0 else 0
        
        # Definir status
        if percentual < 70:
            status = "ok"
        elif percentual < 90:
            status = "warning"
        else:
            status = "danger"
        
        return CategoryBudgetResponse(
            id=budget.id,
            user_id=budget.user_id,
            categoria_geral=budget.categoria_geral,
            mes=budget.mes,
            ano=budget.ano,
            budget=budget.budget,
            gasto_atual=gasto,
            progresso_percentual=round(percentual, 1),
            status=status,
            created_at=budget.created_at,
            updated_at=budget.updated_at
        )
    
    # === WALLET SUMMARY ===
    
    def get_wallet_summary(self, user_id: int, mes: int, ano: int) -> WalletSummaryResponse:
        """Obter summary da wallet (dados do gráfico)"""
        # Buscar meta do período
        meta = self.db.query(Meta).filter(
            Meta.user_id == user_id,
            Meta.mes == mes,
            Meta.ano == ano
        ).first()
        
        # Calcular receitas e gastos
        receitas = self._calcular_receitas_mes(user_id, mes, ano)
        gastos_total = self._calcular_gastos_mes(user_id, mes, ano)
        economia = receitas - gastos_total
        
        # Gastos por categoria (para gráfico)
        gastos_por_categoria = self._calcular_gastos_por_categoria(user_id, mes, ano)
        
        # Montar chart_data
        chart_data = []
        
        # Fatia de economia (verde)
        if economia > 0:
            chart_data.append(WalletChartData(
                name="Economia",
                value=float(economia),
                color="#10B981"  # emerald-500
            ))
        
        # Fatias de categorias (cores variadas)
        colors = {
            "Alimentação": "#3B82F6",  # blue-500
            "Transporte": "#F97316",   # orange-500
            "Saúde": "#A855F7",        # purple-500
            "Moradia": "#EF4444",      # red-500
            "Outros": "#6B7280"        # gray-500
        }
        
        for cat, valor in gastos_por_categoria.items():
            chart_data.append(WalletChartData(
                name=cat,
                value=float(valor),
                color=colors.get(cat, "#9CA3AF")
            ))
        
        # Calcular progresso
        meta_valor = meta.valor_meta if meta else None
        progresso = (float(economia) / float(meta_valor)) * 100 if meta_valor and meta_valor > 0 else 0
        
        return WalletSummaryResponse(
            mes=mes,
            ano=ano,
            meta_valor=meta_valor,
            economia_atual=economia,
            progresso_percentual=round(progresso, 1),
            receitas_mes=receitas,
            gastos_mes=gastos_total,
            chart_data=chart_data
        )
    
    def get_wallet_categories(self, user_id: int, mes: int, ano: int) -> WalletCategoriesResponse:
        """Obter progresso de categorias (lista)"""
        # Buscar budgets do período
        budgets = self.db.query(CategoryBudget).filter(
            CategoryBudget.user_id == user_id,
            CategoryBudget.mes == mes,
            CategoryBudget.ano == ano
        ).all()
        
        # Calcular gastos por categoria
        gastos_por_categoria = self._calcular_gastos_por_categoria(user_id, mes, ano)
        
        categories_progress = []
        
        # Mapear ícones e cores
        icon_map = {
            "Alimentação": "UtensilsCrossed",
            "Transporte": "Car",
            "Saúde": "HeartPulse",
            "Moradia": "Home",
            "Lazer": "Gamepad2",
            "Educação": "GraduationCap",
            "Outros": "MoreHorizontal"
        }
        
        color_map = {
            "Alimentação": "blue",
            "Transporte": "orange",
            "Saúde": "purple",
            "Moradia": "red",
            "Lazer": "emerald",
            "Educação": "indigo",
            "Outros": "gray"
        }
        
        for budget in budgets:
            gasto = gastos_por_categoria.get(budget.categoria_geral, Decimal(0))
            percentual = (float(gasto) / float(budget.budget)) * 100 if budget.budget > 0 else 0
            
            # Definir status
            if percentual < 70:
                status = "ok"
            elif percentual < 90:
                status = "warning"
            else:
                status = "danger"
            
            categories_progress.append(WalletCategoryProgress(
                categoria=budget.categoria_geral,
                icon=icon_map.get(budget.categoria_geral, "Circle"),
                budget=budget.budget,
                gasto=gasto,
                percentual=round(percentual, 1),
                status=status,
                color=color_map.get(budget.categoria_geral, "gray")
            ))
        
        return WalletCategoriesResponse(categories=categories_progress)
    
    # === NOTIFICATIONS ===
    
    def get_notifications(self, user_id: int, apenas_nao_lidas: bool = True) -> List[BudgetNotificationResponse]:
        """Listar notificações"""
        query = self.db.query(BudgetNotification).filter(BudgetNotification.user_id == user_id)
        
        if apenas_nao_lidas:
            query = query.filter(BudgetNotification.lida == False)
        
        notifications = query.order_by(BudgetNotification.created_at.desc()).limit(50).all()
        return [BudgetNotificationResponse.from_orm(n) for n in notifications]
    
    def mark_notification_read(self, user_id: int, notification_id: int):
        """Marcar notificação como lida"""
        notification = self.db.query(BudgetNotification).filter(
            BudgetNotification.id == notification_id,
            BudgetNotification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        
        notification.lida = True
        self.db.commit()
    
    # === HELPERS ===
    
    def _calcular_economia_mes(self, user_id: int, mes: int, ano: int) -> Decimal:
        """Calcular economia do mês (receitas - gastos)"""
        receitas = self._calcular_receitas_mes(user_id, mes, ano)
        gastos = self._calcular_gastos_mes(user_id, mes, ano)
        return receitas - gastos
    
    def _calcular_receitas_mes(self, user_id: int, mes: int, ano: int) -> Decimal:
        """Calcular total de receitas do mês"""
        result = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Mes == mes,
            JournalEntry.Ano == ano,
            JournalEntry.CategoriaGeral == "Receita",
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        return Decimal(result or 0)
    
    def _calcular_gastos_mes(self, user_id: int, mes: int, ano: int) -> Decimal:
        """Calcular total de gastos do mês"""
        result = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Mes == mes,
            JournalEntry.Ano == ano,
            JournalEntry.CategoriaGeral == "Despesa",
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        return Decimal(result or 0)
    
    def _calcular_gasto_categoria(self, user_id: int, categoria: str, mes: int, ano: int) -> Decimal:
        """Calcular gasto de uma categoria específica"""
        result = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Grupo == categoria,  # Ajustar campo conforme schema
            JournalEntry.Mes == mes,
            JournalEntry.Ano == ano,
            JournalEntry.CategoriaGeral == "Despesa",
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        return Decimal(result or 0)
    
    def _calcular_gastos_por_categoria(self, user_id: int, mes: int, ano: int) -> dict[str, Decimal]:
        """Calcular gastos agrupados por categoria"""
        results = self.db.query(
            JournalEntry.Grupo,
            func.sum(JournalEntry.Valor).label("total")
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Mes == mes,
            JournalEntry.Ano == ano,
            JournalEntry.CategoriaGeral == "Despesa",
            JournalEntry.IgnorarDashboard == 0
        ).group_by(JournalEntry.Grupo).all()
        
        return {grupo: Decimal(total) for grupo, total in results if grupo}
```

---

## ⚛️ 6. Frontend - Componente Principal

**Arquivo:** `app_dev/frontend/src/app/wallet/page.tsx`

```tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Search, Calendar, ChevronDown, Home, UtensilsCrossed, Car, HeartPulse } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { apiClient } from '@/core/utils/api-client';

// Types
interface ChartData {
  name: string;
  value: number;
  color: string;
}

interface Category {
  categoria: string;
  icon: string;
  budget: number | null;
  gasto: number;
  percentual: number;
  status: 'ok' | 'warning' | 'danger';
  color: string;
}

interface WalletSummary {
  mes: int;
  ano: number;
  meta_valor: number | null;
  economia_atual: number;
  progresso_percentual: number;
  receitas_mes: number;
  gastos_mes: number;
  chart_data: ChartData[];
}

// Icon mapping
const ICON_MAP: Record<string, any> = {
  'Home': Home,
  'UtensilsCrossed': UtensilsCrossed,
  'Car': Car,
  'HeartPulse': HeartPulse,
};

export default function WalletPage() {
  const [activeTab, setActiveTab] = useState<'Savings' | 'Expenses'>('Savings');
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  
  const [summary, setSummary] = useState<WalletSummary | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Fetch data
  useEffect(() => {
    fetchWalletData();
  }, [selectedMonth, selectedYear]);
  
  const fetchWalletData = async () => {
    try {
      setLoading(true);
      
      // Fetch summary
      const summaryRes = await apiClient.get<WalletSummary>(
        `/api/v1/wallet/summary?mes=${selectedMonth}&ano=${selectedYear}`
      );
      setSummary(summaryRes);
      
      // Fetch categories
      const categoriesRes = await apiClient.get<{ categories: Category[] }>(
        `/api/v1/wallet/categories?mes=${selectedMonth}&ano=${selectedYear}`
      );
      setCategories(categoriesRes.categories);
    } catch (error) {
      console.error('Erro ao carregar wallet:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading || !summary) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Carregando...</p>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center p-4 md:p-8">
      {/* Mobile Container */}
      <div className="w-full max-w-[390px] h-[844px] bg-white rounded-[40px] shadow-xl overflow-hidden relative flex flex-col border-[6px] border-slate-900">
        
        {/* Notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[120px] h-[30px] bg-slate-900 rounded-b-2xl z-50" />
        
        {/* Status Bar */}
        <div className="w-full h-12 bg-white shrink-0" />
        
        {/* Header */}
        <header className="px-6 pb-2 flex justify-between items-start bg-white z-10">
          <div className="flex gap-3 items-center">
            <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden border border-gray-100">
              <img src="https://i.pravatar.cc/150?u=user" alt="User" className="w-full h-full object-cover" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-gray-400 font-medium">Metas</span>
              <span className="text-sm font-bold text-slate-800">Wallet</span>
            </div>
          </div>
          <div className="flex gap-4 text-gray-400">
            <Search size={22} strokeWidth={2} />
            <Calendar size={22} strokeWidth={2} />
          </div>
        </header>
        
        {/* Main Content */}
        <main className="flex-1 overflow-y-auto pb-32 px-5 pt-4">
          <h1 className="text-2xl font-bold mb-4 ml-1">Wallet</h1>
          
          {/* Card Principal */}
          <div className="bg-white rounded-[32px] p-1">
            
            {/* Dropdown Período */}
            <div className="flex justify-end mb-2">
              <button className="flex items-center gap-1 text-xs font-semibold bg-gray-50 text-gray-600 px-3 py-1.5 rounded-full border border-gray-100">
                Month <ChevronDown size={14} />
              </button>
            </div>
            
            {/* Gráfico Donut */}
            <div className="h-64 w-full relative flex justify-center items-center -mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={summary.chart_data}
                    cx="50%"
                    cy="50%"
                    innerRadius={75}
                    outerRadius={95}
                    paddingAngle={4}
                    dataKey="value"
                    startAngle={90}
                    endAngle={-270}
                    cornerRadius={8}
                    stroke="none"
                  >
                    {summary.chart_data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              
              {/* Centro do Gráfico */}
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pt-2">
                <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mb-1">
                  {new Date(0, selectedMonth - 1).toLocaleString('pt-BR', { month: 'long' })} {selectedYear}
                </span>
                <div className="flex items-baseline">
                  <span className="text-3xl font-bold text-slate-800">
                    R$ {summary.economia_atual.toFixed(0)}
                  </span>
                  <span className="text-xl font-bold text-gray-400">
                    .{summary.economia_atual.toFixed(2).split('.')[1]}
                  </span>
                </div>
                <span className="text-[10px] text-gray-400 mt-1">
                  economizado de R$ {summary.meta_valor?.toFixed(0) || '---'}
                </span>
              </div>
            </div>
            
            {/* Segmented Control */}
            <div className="bg-gray-100 p-1.5 rounded-2xl flex mb-8">
              <button
                onClick={() => setActiveTab('Savings')}
                className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  activeTab === 'Savings'
                    ? 'bg-white text-slate-800 shadow-[0_2px_8px_rgba(0,0,0,0.08)]'
                    : 'text-gray-500 hover:text-gray-600'
                }`}
              >
                Savings
              </button>
              <button
                onClick={() => setActiveTab('Expenses')}
                className={`flex-1 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  activeTab === 'Expenses'
                    ? 'bg-white text-slate-800 shadow-[0_2px_8px_rgba(0,0,0,0.08)]'
                    : 'text-gray-500 hover:text-gray-600'
                }`}
              >
                Expenses
              </button>
            </div>
            
            {/* Lista de Categorias */}
            <div className="space-y-6">
              {categories.map((item, idx) => {
                const Icon = ICON_MAP[item.icon] || Home;
                const bgColor = `bg-${item.color}-100`;
                const textColor = `text-${item.color}-500`;
                const barColor = `bg-${item.color}-500`;
                const trackColor = `bg-${item.color}-100`;
                
                return (
                  <div key={idx} className="flex flex-col gap-2">
                    <div className="flex items-center gap-4">
                      {/* Ícone */}
                      <div className={`w-10 h-10 rounded-[14px] flex items-center justify-center ${bgColor} ${textColor}`}>
                        <Icon size={20} strokeWidth={2.5} />
                      </div>
                      
                      {/* Texto e Barra */}
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-semibold text-slate-700">{item.categoria}</span>
                          <span className="text-xs text-gray-500">
                            R$ {item.gasto.toFixed(0)} / R$ {item.budget?.toFixed(0) || '---'}
                          </span>
                        </div>
                        
                        {/* Barra de Progresso */}
                        <div className={`w-full h-1.5 rounded-full ${trackColor}`}>
                          <div
                            className={`h-full rounded-full ${barColor} transition-all duration-500`}
                            style={{ width: `${Math.min(item.percentual, 100)}%` }}
                          />
                        </div>
                        
                        <div className="flex justify-end mt-1">
                          <span className={`text-xs font-semibold ${item.status === 'danger' ? 'text-red-500' : item.status === 'warning' ? 'text-orange-500' : 'text-gray-400'}`}>
                            {item.percentual.toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
```

---

## 📊 7. DEPENDENCY GRAPH (DAG)

Ordem de implementação para evitar bloqueios:

```
1️⃣ Database (2-3h)
   ├─ Criar migrations Alembic
   ├─ Aplicar migrations em dev
   └─ Testar constraints

2️⃣ Backend - Models (2h)
   ├─ Meta, CategoryBudget, BudgetNotification
   └─ Relationships com User

3️⃣ Backend - Schemas (2h)
   ├─ Create/Update/Response schemas
   └─ Validações Pydantic

4️⃣ Backend - Service (8h)
   ├─ CRUD metas
   ├─ CRUD budgets
   ├─ Cálculo de progresso
   ├─ Wallet summary
   └─ Notificações

5️⃣ Backend - Router (4h)
   ├─ Endpoints /metas
   ├─ Endpoints /budgets
   ├─ Endpoints /wallet/summary
   └─ Endpoints /notifications

6️⃣ Frontend - API Client (2h)
   ├─ Funções de fetch
   └─ Error handling

7️⃣ Frontend - Componentes (16h)
   ├─ WalletPage (estrutura)
   ├─ Gráfico Donut (Recharts)
   ├─ Segmented Control
   ├─ Lista de Categorias
   └─ Modais (criar/editar meta)

8️⃣ Testes (8h)
   ├─ Testes unitários backend (pytest)
   ├─ Testes E2E (Playwright)
   └─ Validação manual

9️⃣ Deploy (4h)
   ├─ Migrations produção
   ├─ Build frontend
   ├─ Smoke tests
   └─ Monitoring
```

---

## ✅ 8. TESTING STRATEGY

### 8.1 Testes Unitários (Backend)

**Arquivo:** `app_dev/backend/tests/test_wallet_service.py`

```python
import pytest
from app.domains.wallet.service import WalletService
from app.domains.wallet.schemas import MetaCreate

def test_create_meta(db_session, test_user):
    """Testar criação de meta"""
    service = WalletService(db_session)
    
    data = MetaCreate(mes=2, ano=2026, valor_meta=1000.00)
    meta = service.create_meta(test_user.id, data)
    
    assert meta.valor_meta == 1000.00
    assert meta.mes == 2
    assert meta.ano == 2026

def test_create_meta_duplicada(db_session, test_user):
    """Testar erro ao criar meta duplicada"""
    service = WalletService(db_session)
    
    data = MetaCreate(mes=2, ano=2026, valor_meta=1000.00)
    service.create_meta(test_user.id, data)
    
    with pytest.raises(HTTPException) as exc_info:
        service.create_meta(test_user.id, data)
    
    assert exc_info.value.status_code == 400
    assert "Já existe uma meta" in exc_info.value.detail
```

### 8.2 Testes E2E (Playwright)

**Arquivo:** `app_dev/frontend/tests/e2e/wallet.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Wallet - Metas', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'teste@email.com');
    await page.fill('[name="password"]', 'teste123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });
  
  test('deve exibir gráfico donut com dados', async ({ page }) => {
    await page.goto('/wallet');
    
    // Verificar título
    await expect(page.locator('h1')).toContainText('Wallet');
    
    // Verificar gráfico renderizado
    const chart = page.locator('.recharts-wrapper');
    await expect(chart).toBeVisible();
    
    // Verificar valor no centro do gráfico
    const valorEconomizado = page.locator('text=/R\\$ \\d+/');
    await expect(valorEconomizado).toBeVisible();
  });
  
  test('deve alternar entre abas Savings e Expenses', async ({ page }) => {
    await page.goto('/wallet');
    
    // Verificar aba Savings ativa
    const savingsTab = page.locator('button:has-text("Savings")');
    await expect(savingsTab).toHaveClass(/bg-white/);
    
    // Clicar em Expenses
    await page.click('button:has-text("Expenses")');
    
    // Verificar mudança de aba
    const expensesTab = page.locator('button:has-text("Expenses")');
    await expect(expensesTab).toHaveClass(/bg-white/);
  });
  
  test('deve exibir lista de categorias com barras de progresso', async ({ page }) => {
    await page.goto('/wallet');
    
    // Verificar pelo menos 1 categoria
    const categorias = page.locator('[data-testid="categoria-item"]');
    await expect(categorias).toHaveCountGreaterThan(0);
    
    // Verificar primeira categoria tem barra de progresso
    const primeiraBarra = page.locator('.bg-blue-500').first();
    await expect(primeiraBarra).toBeVisible();
  });
});
```

---

## 📱 9. RESPONSIVIDADE E ACESSIBILIDADE

### 9.1 Breakpoints

```css
/* Mobile-first (default) */
.wallet-container { width: 100%; }

/* Tablet (768px+) */
@media (min-width: 768px) {
  .wallet-container { max-width: 390px; }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .wallet-container { max-width: 420px; }
}
```

### 9.2 ARIA Labels

```tsx
// Segmented Control
<button
  role="tab"
  aria-selected={activeTab === 'Savings'}
  aria-controls="wallet-content"
>
  Savings
</button>

// Gráfico
<PieChart aria-label="Distribuição de gastos por categoria">
  ...
</PieChart>

// Barra de Progresso
<div
  role="progressbar"
  aria-valuenow={item.percentual}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`${item.categoria}: ${item.percentual}% gasto`}
>
  ...
</div>
```

---

## 🚀 10. DEPLOY CHECKLIST (Resumo)

- [ ] Migrations aplicadas em produção
- [ ] APIs testadas (curl/Postman)
- [ ] Frontend build sem erros
- [ ] Lighthouse ≥90
- [ ] axe DevTools 0 erros
- [ ] Smoke tests passando
- [ ] Backup do banco criado
- [ ] Monitoring ativo (logs)
- [ ] POST_MORTEM agendado (48h)

---

**Status:** 🟡 **EM REVISÃO** (Aguardando aprovação para começar Sprint 1)

**Próximo Passo:** Aprovação + Início do Sprint 1 (Database + Backend Models)

---

**Histórico:**
| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | 02/02/2026 | Tech Lead | Criação inicial |
