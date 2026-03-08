# Skill: Novo Domínio FastAPI

## Contexto
Backend DDD com 5 arquivos por domínio. Path: `app_dev/backend/app/domains/{nome}/`

## Antes de criar, pergunte
1. Nome do domínio (snake_case)
2. Nome da tabela SQL
3. Campos principais (nome, tipo, nullable?)
4. Endpoints desejados (CRUD completo ou subset?)

## Estrutura a criar
```
app/domains/{nome}/
├── __init__.py
├── models.py        (SQLAlchemy)
├── schemas.py       (Pydantic)
├── repository.py    (queries)
├── service.py       (regras de negócio)
└── router.py        (endpoints HTTP)
```

## Regras obrigatórias
- `user_id = Column(Integer, ForeignKey("users.id"), nullable=False)` em todo model
- Todo repository filtra por `user_id` em todo WHERE
- Todo endpoint usa `Depends(get_current_user_id)`
- Dependências: `from app.core.database import get_db` e `from app.shared.dependencies import get_current_user_id`
- Registrar em `app/main.py`: `app.include_router({nome}_router, prefix="/api/v1")`

## Após criar os arquivos
Gerar migration:
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Add {nome} table"
docker exec finup_backend_dev alembic upgrade head
```
