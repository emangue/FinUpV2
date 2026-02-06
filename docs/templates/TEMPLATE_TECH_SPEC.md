# 🔧 TECH SPEC - [Nome da Feature]

**Status:** 🟡 Em Revisão  
**Versão:** 1.0  
**Data:** DD/MM/YYYY  
**Autor:** [Nome]  
**PRD:** [Link para PRD.md]

---

## 📊 Sumário Técnico

**Arquitetura:** [Ex: Cliente-Servidor, Microserviços]  
**Stack:** [Ex: FastAPI + Next.js + PostgreSQL]  
**Esforço:** [Ex: 40h total]  
**Sprints:** [Ex: 3 sprints de 2 semanas]

---

## 🏗️ 1. Arquitetura

### 1.1 Diagrama Geral

```
┌──────────────┐      HTTP/JSON      ┌──────────────┐
│   Frontend   │ ───────────────────> │   Backend    │
│  (Next.js)   │ <─────────────────── │  (FastAPI)   │
└──────────────┘                      └───────┬──────┘
                                              │
                                              v
                                      ┌──────────────┐
                                      │  PostgreSQL  │
                                      │  (Database)  │
                                      └──────────────┘
```

### 1.2 Decisões Arquiteturais

**DA-01: Usar PostgreSQL em vez de SQLite**
- **Contexto:** Produção precisa de concorrência
- **Decisão:** PostgreSQL + Alembic migrations
- **Consequências:** ✅ Robusto, ❌ Mais complexo
- **Alternativas:** SQLite (não escala), MongoDB (schema flexível demais)

**DA-02: [Outra Decisão]**
[Mesma estrutura]

---

## 🗄️ 2. Database Schema

### 2.1 Tabelas Novas

#### **Tabela: `feature_table`**

```sql
CREATE TABLE feature_table (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    nome VARCHAR(255) NOT NULL,
    valor DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_feature_user ON feature_table(user_id);
CREATE INDEX idx_feature_created ON feature_table(created_at DESC);
```

### 2.2 Migrations Alembic

**Arquivo:** `migrations/versions/XXXX_add_feature_table.py`

```python
"""add feature table

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-01-15 10:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'feature_table',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('valor', sa.DECIMAL(15, 2)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
    )
    
    op.create_index('idx_feature_user', 'feature_table', ['user_id'])
    op.create_foreign_key(
        'fk_feature_user', 'feature_table', 'users', 
        ['user_id'], ['id'], ondelete='CASCADE'
    )

def downgrade():
    op.drop_table('feature_table')
```

### 2.3 Modelos SQLAlchemy

**Arquivo:** `app/domains/feature/models.py`

```python
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base

class FeatureModel(Base):
    __tablename__ = "feature_table"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(255), nullable=False)
    valor = Column(DECIMAL(15, 2))
    created_at = Column(TIMESTAMP, server_default="NOW()")
    updated_at = Column(TIMESTAMP, server_default="NOW()", onupdate="NOW()")
    
    # Relationships
    user = relationship("User", back_populates="features")
```

---

## 🔌 3. API Specification

### 3.1 Endpoints

#### **GET /api/v1/feature/list**

**Descrição:** Lista todos os itens da feature do usuário

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Params:**
```
?mes_referencia=2026-01  (opcional)
?limit=50                 (opcional, default: 100)
```

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 42,
      "nome": "Item A",
      "valor": 1000.50,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "mes_referencia": "2026-01"
}
```

**Response 401:**
```json
{
  "detail": "Not authenticated"
}
```

**Curl Example:**
```bash
curl -H "Authorization: Bearer eyJ..." \
     http://localhost:8000/api/v1/feature/list?mes_referencia=2026-01
```

---

#### **POST /api/v1/feature/create**

**Descrição:** Cria novo item

**Request:**
```json
{
  "nome": "Item Novo",
  "valor": 500.00
}
```

**Response 201:**
```json
{
  "id": 123,
  "nome": "Item Novo",
  "valor": 500.00,
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Curl Example:**
```bash
curl -X POST -H "Authorization: Bearer eyJ..." \
     -H "Content-Type: application/json" \
     -d '{"nome":"Item Novo","valor":500.00}' \
     http://localhost:8000/api/v1/feature/create
```

---

### 3.2 Backend Implementation

**Arquivo:** `app/domains/feature/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from . import schemas, service

router = APIRouter(prefix="/feature", tags=["Feature"])

@router.get("/list", response_model=schemas.FeatureListResponse)
def list_features(
    mes_referencia: str = None,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Lista features do usuário"""
    feature_service = service.FeatureService(db)
    return feature_service.list_features(user_id, mes_referencia, limit)

@router.post("/create", response_model=schemas.FeatureResponse, status_code=201)
def create_feature(
    data: schemas.FeatureCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cria nova feature"""
    feature_service = service.FeatureService(db)
    return feature_service.create_feature(user_id, data)
```

**Arquivo:** `app/domains/feature/service.py`

```python
from sqlalchemy.orm import Session
from . import models, schemas, repository

class FeatureService:
    def __init__(self, db: Session):
        self.repository = repository.FeatureRepository(db)
    
    def list_features(self, user_id: int, mes_referencia: str, limit: int):
        items = self.repository.get_by_user(user_id, mes_referencia, limit)
        return {
            "items": items,
            "total": len(items),
            "mes_referencia": mes_referencia
        }
    
    def create_feature(self, user_id: int, data: schemas.FeatureCreate):
        # Validações de negócio
        if data.valor and data.valor < 0:
            raise ValueError("Valor não pode ser negativo")
        
        # Criar no banco
        return self.repository.create(user_id, data)
```

---

## 🎨 4. Frontend Components

### 4.1 Componente Principal

**Arquivo:** `app/mobile/feature/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { MobileHeader } from '@/components/mobile/mobile-header';
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';

interface FeatureItem {
  id: number;
  nome: string;
  valor: number;
  created_at: string;
}

export default function FeaturePage() {
  const [items, setItems] = useState<FeatureItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchItems();
  }, []);
  
  const fetchItems = async () => {
    try {
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`;
      const response = await fetchWithAuth(`${BASE_URL}/feature/list`);
      
      if (!response.ok) throw new Error('Erro ao buscar dados');
      
      const data = await response.json();
      setItems(data.items);
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <MobileHeader title="Feature" showBackButton />
      
      <div className="flex-1 overflow-y-auto p-5">
        {loading ? (
          <div className="text-gray-500">Carregando...</div>
        ) : (
          <div className="space-y-3">
            {items.map(item => (
              <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900">{item.nome}</h3>
                <p className="text-lg text-blue-600">
                  R$ {item.valor.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### 4.2 Schemas Pydantic

**Arquivo:** `app/domains/feature/schemas.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class FeatureCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., ge=0, decimal_places=2)

class FeatureResponse(BaseModel):
    id: int
    user_id: int
    nome: str
    valor: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class FeatureListResponse(BaseModel):
    items: list[FeatureResponse]
    total: int
    mes_referencia: str | None
```

---

## 📊 5. Dependency Graph (DAG)

### 5.1 Ordem de Implementação

```
1. Database
   ├── 1.1 Migration (add_feature_table.py)
   └── 1.2 Model (models.py)

2. Backend
   ├── 2.1 Schemas (schemas.py)
   ├── 2.2 Repository (repository.py)
   ├── 2.3 Service (service.py)
   └── 2.4 Router (router.py)

3. Frontend
   ├── 3.1 API client (já existe)
   ├── 3.2 Types (types.ts)
   ├── 3.3 Component (page.tsx)
   └── 3.4 Styles (já existem via Tailwind)

4. Tests
   ├── 4.1 Unit tests backend
   ├── 4.2 Integration tests API
   └── 4.3 E2E tests frontend

5. Deploy
   ├── 5.1 Aplicar migration
   ├── 5.2 Deploy backend
   ├── 5.3 Deploy frontend
   └── 5.4 Smoke tests
```

### 5.2 Sprint Breakdown

**Sprint 1 (8-12h):**
- [ ] Database: Migration + Model
- [ ] Backend: Schemas + Repository
- [ ] Backend: Service + Router
- [ ] Registrar router em main.py

**Sprint 2 (6-10h):**
- [ ] Frontend: Types
- [ ] Frontend: Component principal
- [ ] Frontend: Lista de items
- [ ] Frontend: Loading states

**Sprint 3 (4-6h):**
- [ ] Tests: Unit + Integration
- [ ] Tests: E2E Playwright
- [ ] Deploy: Staging
- [ ] Deploy: Produção

---

## 🧪 6. Testing Strategy

### 6.1 Unit Tests

**Arquivo:** `tests/unit/test_feature_service.py`

```python
import pytest
from app.domains.feature.service import FeatureService
from app.domains.feature.schemas import FeatureCreate

def test_create_feature_valid(db_session, mock_user):
    service = FeatureService(db_session)
    data = FeatureCreate(nome="Test", valor=100.00)
    
    result = service.create_feature(mock_user.id, data)
    
    assert result.id is not None
    assert result.nome == "Test"
    assert result.valor == 100.00

def test_create_feature_negative_valor(db_session, mock_user):
    service = FeatureService(db_session)
    data = FeatureCreate(nome="Test", valor=-50.00)
    
    with pytest.raises(ValueError, match="negativo"):
        service.create_feature(mock_user.id, data)
```

### 6.2 E2E Tests

**Arquivo:** `tests/e2e/feature.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import { loginAsAdmin } from './helpers';

test.describe('Feature Page', () => {
  test('should display feature list', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/mobile/feature');
    
    // Aguardar carregar
    await expect(page.locator('text=Carregando')).toBeVisible();
    await expect(page.locator('text=Carregando')).not.toBeVisible({ timeout: 5000 });
    
    // Validar items aparecem
    const items = page.locator('[data-testid="feature-item"]');
    await expect(items).toHaveCount(await items.count());
  });
});
```

### 6.3 Cobertura Alvo

| Tipo | Cobertura Mínima | Como Medir |
|------|------------------|------------|
| Unit Tests | 80% | `pytest --cov=app/domains/feature` |
| Integration | 70% | `pytest tests/integration/` |
| E2E | Key flows | Playwright test count |

---

## ⚙️ 7. Environment Configuration

### 7.1 Variáveis .env

**Desenvolvimento:**
```bash
DATABASE_URL=sqlite:///./financas_dev.db
DEBUG=true
```

**Produção:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/finup_db
DEBUG=false
JWT_SECRET_KEY=<secret_64_chars>
```

### 7.2 Secrets Obrigatórios

| Variável | Onde | Como Gerar |
|----------|------|------------|
| JWT_SECRET_KEY | Prod | `python -c "import secrets; print(secrets.token_hex(32))"` |
| DATABASE_URL | Prod | Configurado no servidor |

---

## 📊 8. Performance Budget

| Métrica | Alvo | Como Medir |
|---------|------|------------|
| Lighthouse Performance | ≥85 | Chrome DevTools |
| TTI (Time to Interactive) | ≤3s | Lighthouse |
| FCP (First Contentful Paint) | ≤1.5s | Lighthouse |
| API Response Time | ≤500ms | Backend logs |
| Bundle Size (JS) | ≤300KB | `npm run build --analyze` |

---

## 🔒 9. Security Checklist

- [ ] **Autenticação:** JWT obrigatório em rotas protegidas
- [ ] **Autorização:** Usuário só acessa próprios dados
- [ ] **Validação:** Pydantic valida inputs
- [ ] **SQL Injection:** SQLAlchemy ORM (não raw SQL)
- [ ] **XSS:** React escapa strings automaticamente
- [ ] **CORS:** Origins específicas (não "*")
- [ ] **Rate Limiting:** 200 req/min global, 5/min login
- [ ] **HTTPS:** Obrigatório em produção
- [ ] **Secrets:** Nunca commitados no git

---

## 📂 10. File Structure

```
app_dev/
├── backend/
│   └── app/
│       └── domains/
│           └── feature/
│               ├── __init__.py
│               ├── models.py          # ✅ CRIAR
│               ├── schemas.py         # ✅ CRIAR
│               ├── repository.py      # ✅ CRIAR
│               ├── service.py         # ✅ CRIAR
│               └── router.py          # ✅ CRIAR
│
└── frontend/
    └── src/
        └── app/
            └── mobile/
                └── feature/
                    ├── page.tsx       # ✅ CRIAR
                    └── types.ts       # ✅ CRIAR (opcional)
```

---

## ✅ 11. Checklist de Implementação

### Backend
- [ ] Migration criada (`alembic revision`)
- [ ] Model SQLAlchemy completo
- [ ] Schemas Pydantic validam inputs
- [ ] Repository com queries SQL
- [ ] Service com lógica de negócio
- [ ] Router com endpoints
- [ ] Router registrado em `main.py`
- [ ] Unit tests (cobertura ≥80%)

### Frontend
- [ ] Types TypeScript definidos
- [ ] Component principal criado
- [ ] fetchWithAuth integrado
- [ ] Loading states
- [ ] Error handling
- [ ] E2E tests (key flows)

### Deploy
- [ ] Migration aplicada em staging
- [ ] Smoke tests passando
- [ ] Lighthouse ≥85
- [ ] WCAG ≥90%
- [ ] Backup criado
- [ ] Deploy em produção

---

## 📖 12. Referências

**Documentação:**
- PRD: `/docs/features/[nome]/01-PRD/PRD.md`
- API Docs: `http://localhost:8000/docs`
- Style Guide: `/docs/features/mobile-v1/01-PRD/STYLE_GUIDE.md`

**Código de Referência:**
- Backend: `/app/domains/transactions/`
- Frontend: `/app/mobile/dashboard/page.tsx`

---

**Próximo Passo:** Iniciar Sprint 1 (criar SPRINT1_WIP.md)
