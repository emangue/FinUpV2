# Skill: Migration Alembic

## Contexto do projeto
- Container dev: `finup_backend_dev`
- Migrations: `app_dev/backend/migrations/versions/`
- Guard: `migrations/env.py` bloqueia SQLite (PostgreSQL only)

## Antes de executar, pergunte
1. Descrição da mudança (ex: "Add plano_cashflow_mes table")
2. Tabelas/campos afetados
3. Os models.py foram atualizados?

## Passos

### 1. Verificar models atualizados
Ler o `models.py` do domínio afetado e confirmar que a mudança está refletida.

### 2. Gerar migration
```bash
docker exec finup_backend_dev alembic revision --autogenerate -m "Descrição da mudança"
```

### 3. Revisar o arquivo gerado
Abrir o arquivo em `migrations/versions/`. Verificar:
- `upgrade()` contém a mudança esperada
- `downgrade()` reverte corretamente
- Campos NOT NULL sem default em tabelas com dados existentes têm `server_default`

### 4. Testar em dev
```bash
docker exec finup_backend_dev alembic upgrade head
docker exec finup_backend_dev alembic current
```

### 5. Testar rollback
```bash
docker exec finup_backend_dev alembic downgrade -1
docker exec finup_backend_dev alembic upgrade head
```

## Armadilhas
- Campo NOT NULL sem server_default em tabela com dados = falha em prod
- `alembic upgrade` fora do container pode rodar contra banco errado
- Nunca commitar migrations sem testar upgrade + downgrade em dev
