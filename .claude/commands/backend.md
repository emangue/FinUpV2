# Skill: Backend — Guia de Desenvolvimento FastAPI

Você é um assistente especialista no backend do FinUpV2. Antes de sugerir qualquer mudança,
verifique se o padrão abaixo está sendo seguido. Esse guia é a fonte da verdade para
decisões de arquitetura, segurança e eficiência no backend.

---

## Estrutura do Projeto

```
app_dev/backend/app/
├── core/
│   ├── config.py           # Settings via pydantic-settings (env vars)
│   └── database.py         # SQLAlchemy engine + session + Base
├── shared/
│   ├── dependencies.py     # get_current_user_id, get_db, require_admin
│   └── utils/
│       ├── hasher.py       # FNV-1a para IdTransacao
│       └── normalizer.py   # Normalização de texto (nomes de banco, etc.)
├── domains/                # 17 domínios DDD
│   ├── auth/
│   ├── users/
│   ├── transactions/
│   ├── categories/
│   ├── upload/
│   ├── dashboard/
│   └── ...
└── main.py                 # App FastAPI, middleware, registro de routers
```

### Estrutura padrão de cada domínio

```
domains/{nome}/
├── __init__.py
├── models.py       # SQLAlchemy ORM — colunas, FKs, índices
├── schemas.py      # Pydantic — validação de entrada e formato de saída
├── router.py       # FastAPI — endpoints HTTP (só orquestra, sem lógica)
├── service.py      # Regras de negócio (instancia repository)
└── repository.py   # Todas as queries SQL isoladas aqui
```

---

## Regras de Segurança — NUNCA IGNORE

### 1. Isolamento por user_id (mais crítico)
Todo model que pertence a um usuário DEVE ter `user_id`:
```python
user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
```

Todo repository DEVE filtrar por `user_id` em TODAS as queries:
```python
# ✅ CORRETO
db.query(Model).filter(Model.user_id == user_id, Model.id == id).first()

# ❌ ERRADO — expõe dados de outros usuários
db.query(Model).filter(Model.id == id).first()
```

### 2. Dependências obrigatórias nos endpoints
```python
from app.shared.dependencies import get_current_user_id, get_db

@router.get("/")
def list_items(
    user_id: int = Depends(get_current_user_id),  # SEMPRE
    db: Session = Depends(get_db),                 # SEMPRE
):
```

### 3. Nunca hardcode user_id
O bug histórico (user_id=1 hardcoded) foi corrigido em 23/01/2026. Não reintroduza.

### 4. Admin check
```python
from app.shared.dependencies import require_admin

@router.delete("/admin/resource/{id}")
def delete_resource(
    _: None = Depends(require_admin),  # 403 se não for admin
    db: Session = Depends(get_db),
):
```

---

## Padrão de Código por Camada

### models.py
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class MeuModel(Base):
    __tablename__ = "meus_itens"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    nome    = Column(String(200), nullable=False)
    valor   = Column(Float, default=0.0)
    criado_em = Column(DateTime, server_default=func.now())
```

### schemas.py
```python
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class MeuItemCreate(BaseModel):
    nome: str
    valor: float

class MeuItemUpdate(BaseModel):
    nome: Optional[str] = None
    valor: Optional[float] = None

class MeuItemResponse(BaseModel):
    id: int
    nome: str
    valor: float
    model_config = ConfigDict(from_attributes=True)

class MeuItemListResponse(BaseModel):
    items: List[MeuItemResponse]
    total: int
```

### repository.py
```python
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import MeuModel
from .schemas import MeuItemCreate, MeuItemUpdate

class MeuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> List[MeuModel]:
        return self.db.query(MeuModel).filter(MeuModel.user_id == user_id).all()

    def get_by_id(self, user_id: int, id: int) -> Optional[MeuModel]:
        return self.db.query(MeuModel).filter(
            MeuModel.user_id == user_id,
            MeuModel.id == id
        ).first()

    def create(self, user_id: int, data: MeuItemCreate) -> MeuModel:
        obj = MeuModel(user_id=user_id, **data.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: MeuModel, data: MeuItemUpdate) -> MeuModel:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: MeuModel) -> None:
        self.db.delete(obj)
        self.db.commit()
```

### service.py
```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import MeuRepository
from .schemas import MeuItemCreate, MeuItemUpdate, MeuItemResponse, MeuItemListResponse

class MeuService:
    def __init__(self, db: Session):
        self.repo = MeuRepository(db)

    def list(self, user_id: int) -> MeuItemListResponse:
        items = self.repo.get_all_by_user(user_id)
        return MeuItemListResponse(items=items, total=len(items))

    def get_or_404(self, user_id: int, id: int):
        obj = self.repo.get_by_id(user_id, id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
        return obj

    def create(self, user_id: int, data: MeuItemCreate) -> MeuItemResponse:
        return self.repo.create(user_id, data)

    def update(self, user_id: int, id: int, data: MeuItemUpdate) -> MeuItemResponse:
        obj = self.get_or_404(user_id, id)
        return self.repo.update(obj, data)

    def delete(self, user_id: int, id: int) -> None:
        obj = self.get_or_404(user_id, id)
        self.repo.delete(obj)
```

### router.py
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.shared.dependencies import get_current_user_id, get_db
from .service import MeuService
from .schemas import MeuItemCreate, MeuItemUpdate, MeuItemResponse, MeuItemListResponse

router = APIRouter(prefix="/meus-itens", tags=["meus-itens"])

@router.get("/", response_model=MeuItemListResponse)
def list_items(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return MeuService(db).list(user_id)

@router.get("/{id}", response_model=MeuItemResponse)
def get_item(id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return MeuService(db).get_or_404(user_id, id)

@router.post("/", response_model=MeuItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(data: MeuItemCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return MeuService(db).create(user_id, data)

@router.patch("/{id}", response_model=MeuItemResponse)
def update_item(id: int, data: MeuItemUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return MeuService(db).update(user_id, id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    MeuService(db).delete(user_id, id)
```

### Registrar o router em main.py
```python
# app/main.py — adicionar no bloco de imports e includes:
from app.domains.meus_itens.router import router as meus_itens_router
app.include_router(meus_itens_router, prefix="/api/v1")
```

---

## O Que É OK Fazer

- ✅ Adicionar novos domínios seguindo o padrão de 5 arquivos acima
- ✅ Adicionar campos opcionais a modelos existentes (migration necessária)
- ✅ Criar schemas adicionais (filtros, paginação, bulk operations)
- ✅ Adicionar índices em colunas frequentemente filtradas
- ✅ Usar `model_dump(exclude_unset=True)` em updates (PATCH parcial)
- ✅ Usar `func.sum()`, `func.count()`, `.group_by()` para agregações no repository
- ✅ Criar routers aninhados (ex: `/upload/preview/{session_id}`)
- ✅ Adicionar rate limiting com slowapi em endpoints sensíveis
- ✅ Usar `Optional[str] = None` em schemas de update (PATCH)
- ✅ Pre-carregar dados em memória para processamento em bulk (ver classifier.py)

## O Que NÃO Fazer

- ❌ Colocar queries SQL no router ou no service — só no repository
- ❌ Colocar regras de negócio no router — só no service
- ❌ Esquecer `user_id` no filter das queries — vazamento de dados
- ❌ Usar `db.query(Model).all()` sem filtro por user_id
- ❌ Criar endpoints async sem necessidade real (o projeto é síncrono)
- ❌ Rodar `alembic upgrade head` fora do container Docker
- ❌ Usar SQLite — o guard em `migrations/env.py` bloqueia, mas não tente
- ❌ Retornar objetos ORM direto sem passar por schema `Response`
- ❌ Duplicar lógica de extração de JWT — use sempre `get_current_user_id`
- ❌ Expor `/docs` em produção — controlado por `DEBUG=False`
- ❌ Fazer queries N+1 — pre-carregar ou usar joins quando processar listas grandes

---

## Migrations Alembic

```bash
# 1. Modificar models.py com as novas colunas/tabelas
# 2. Gerar migration dentro do container dev:
docker exec finup_backend_dev alembic revision --autogenerate -m "Add campo_x to meus_itens"

# 3. Revisar o arquivo gerado em migrations/versions/
# 4. Testar em dev:
docker exec finup_backend_dev alembic upgrade head

# 5. Em produção: migration roda automaticamente no deploy
# 6. Rollback emergencial:
docker exec finup_backend_prod alembic downgrade -1
```

**Atenção com campos NOT NULL sem default em tabelas com dados:**
Sempre usar `server_default` ou migração em dois passos (adicionar nullable → popular → adicionar constraint).

---

## Checklist Antes de Abrir PR

- [ ] Todos os queries no repository filtram por `user_id`
- [ ] Router tem `Depends(get_current_user_id)` em todos os endpoints
- [ ] Schemas `Response` usam `model_config = ConfigDict(from_attributes=True)`
- [ ] Erros retornam `HTTPException` com status code correto (404, 400, 403)
- [ ] Novo domínio registrado em `main.py`
- [ ] Migration gerada e testada em dev
- [ ] Nenhuma lógica de negócio no router
- [ ] Nenhuma query SQL no service
