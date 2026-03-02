# TECH SPEC — Admin: Gestão Completa de Usuários + Grupos por Usuário

**Sub-projeto:** 01 | **Sprint:** 0

---

## 0. Base template (fonte para novos usuários)

Tabelas globais (sem user_id) que servem de base para copiar ao criar novo usuário. Fonte: `generic_classification_rules` + complementos.

### 0.1. base_grupos_template

```python
# Migration
def upgrade():
    op.create_table('base_grupos_template',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nome_grupo', sa.String(100), nullable=False),
        sa.Column('tipo_gasto_padrao', sa.String(50), nullable=False),
        sa.Column('categoria_geral', sa.String(50), nullable=False),
        sa.Column('cor', sa.String(7), nullable=True),
    )
    op.create_unique_constraint('uq_base_grupos_template_nome', 'base_grupos_template', ['nome_grupo'])
    
    # Popular: generic_classification_rules (DISTINCT grupo) + base_grupos_config atual
    # Grupos nas regras: Alimentação, Carro, Compras, Educação, Investimentos, Lazer, Moradia, Saúde, Transporte, Viagens, Assinaturas
    # Complementar: Salário (Receita), Transferência Entre Contas (Transferência), Outros (Despesa), Doações (Despesa)
```

### 0.2. base_marcacoes_template

```python
def upgrade():
    op.create_table('base_marcacoes_template',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('GRUPO', sa.String(100), nullable=False),
        sa.Column('SUBGRUPO', sa.String(100), nullable=False),
    )
    op.create_unique_constraint('uq_base_marcacoes_template_grupo_sub', 'base_marcacoes_template', ['GRUPO', 'SUBGRUPO'])
    
    # Popular: SELECT DISTINCT grupo, subgrupo FROM generic_classification_rules WHERE ativo=1
    # + subgrupos padrão para Salário, Transferência, Outros
```

### 0.3. Models template

```python
# app/domains/grupos/models.py
class BaseGruposTemplate(Base):
    __tablename__ = "base_grupos_template"
    id = Column(Integer, primary_key=True)
    nome_grupo = Column(String(100), nullable=False, unique=True)
    tipo_gasto_padrao = Column(String(50), nullable=False)
    categoria_geral = Column(String(50), nullable=False)
    cor = Column(String(7), nullable=True)

# app/domains/categories/models.py (ou novo arquivo)
class BaseMarcacaoTemplate(Base):
    __tablename__ = "base_marcacoes_template"
    id = Column(Integer, primary_key=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint('GRUPO', 'SUBGRUPO', name='uq_base_marcacoes_template_grupo_sub'),)
```

---

## 1. Migrations

### 1.1. base_grupos_config — user_id + is_padrao

```python
# alembic revision -m "add_user_id_is_padrao_base_grupos_config"
def upgrade():
    # 1. Adicionar colunas (nullable para permitir migração)
    op.add_column('base_grupos_config', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('base_grupos_config', sa.Column('is_padrao', sa.Boolean(), nullable=False, server_default='false'))
    
    # 2. Atribuir user_id=1 aos existentes
    op.execute(sa.text("UPDATE base_grupos_config SET user_id = 1 WHERE user_id IS NULL"))
    op.execute(sa.text("UPDATE base_grupos_config SET is_padrao = true WHERE user_id = 1"))
    
    # 3. Tornar user_id NOT NULL
    op.alter_column('base_grupos_config', 'user_id', nullable=False)
    
    # 4. FK (opcional)
    op.create_foreign_key('fk_base_grupos_config_user_id', 'base_grupos_config', 'users', ['user_id'], ['id'])
    
    # 5. Trocar UNIQUE: drop (nome_grupo) → create (user_id, nome_grupo)
    op.drop_index('ix_base_grupos_config_nome_grupo', table_name='base_grupos_config')
    op.create_unique_constraint('uq_base_grupos_config_user_nome', 'base_grupos_config', ['user_id', 'nome_grupo'])
    op.create_index('ix_base_grupos_config_user_id', 'base_grupos_config', ['user_id'], unique=False)
    op.create_index('ix_base_grupos_config_is_padrao', 'base_grupos_config', ['is_padrao'], unique=False)

def downgrade():
    op.drop_index('ix_base_grupos_config_is_padrao', table_name='base_grupos_config')
    op.drop_index('ix_base_grupos_config_user_id', table_name='base_grupos_config')
    op.drop_constraint('uq_base_grupos_config_user_nome', 'base_grupos_config', type_='unique')
    op.create_index('ix_base_grupos_config_nome_grupo', 'base_grupos_config', ['nome_grupo'], unique=True)
    op.drop_constraint('fk_base_grupos_config_user_id', 'base_grupos_config', type_='foreignkey')
    op.drop_column('base_grupos_config', 'is_padrao')
    op.drop_column('base_grupos_config', 'user_id')
```

### 1.2. base_marcacoes — user_id

```python
# alembic revision -m "add_user_id_base_marcacoes"
def upgrade():
    op.add_column('base_marcacoes', sa.Column('user_id', sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE base_marcacoes SET user_id = 1 WHERE user_id IS NULL"))
    op.alter_column('base_marcacoes', 'user_id', nullable=False)
    op.create_foreign_key('fk_base_marcacoes_user_id', 'base_marcacoes', 'users', ['user_id'], ['id'])
    op.create_unique_constraint('uq_base_marcacoes_user_grupo_subgrupo', 'base_marcacoes', ['user_id', 'GRUPO', 'SUBGRUPO'])
    op.create_index('ix_base_marcacoes_user_id', 'base_marcacoes', ['user_id'], unique=False)

def downgrade():
    op.drop_index('ix_base_marcacoes_user_id', table_name='base_marcacoes')
    op.drop_constraint('uq_base_marcacoes_user_grupo_subgrupo', 'base_marcacoes', type_='unique')
    op.drop_constraint('fk_base_marcacoes_user_id', 'base_marcacoes', type_='foreignkey')
    op.drop_column('base_marcacoes', 'user_id')
```

### 1.3. Script de migração de dados (para usuários existentes)

Após as migrations, executar script que copia grupos e marcações do user_id=1 para cada usuário 2, 3, 4...:

```python
# scripts/migration/copiar_template_para_usuarios_existentes.py
# Para cada user_id em (2, 3, 4, ...):
#   INSERT INTO base_grupos_config (...) SELECT user_id_destino, ... FROM base_grupos_template
#   INSERT INTO base_marcacoes (...) SELECT user_id_destino, ... FROM base_marcacoes_template
```

---

## 2. Models

### 2.1. BaseGruposConfig

```python
# app/domains/grupos/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint

class BaseGruposConfig(Base):
    __tablename__ = "base_grupos_config"
    __table_args__ = (UniqueConstraint('user_id', 'nome_grupo', name='uq_base_grupos_config_user_nome'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    nome_grupo = Column(String, nullable=False, index=True)  # removido unique=True
    tipo_gasto_padrao = Column(String, nullable=False)
    categoria_geral = Column(String, nullable=False)
    cor = Column(String(7), nullable=True)
    is_padrao = Column(Boolean, default=False, nullable=False)
```

### 2.2. BaseMarcacao

```python
# app/domains/categories/models.py
class BaseMarcacao(Base):
    __tablename__ = "base_marcacoes"
    __table_args__ = (UniqueConstraint('user_id', 'GRUPO', 'SUBGRUPO', name='uq_base_marcacoes_user_grupo_subgrupo'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)
```

---

## 3. Backend — Users

### 3.1. Constante grupos padrão

```python
# app/domains/users/service.py
GRUPOS_PADRAO = [
    {"nome_grupo": "Alimentação",   "categoria_geral": "Despesa",       "cor": "#E74C3C"},
    {"nome_grupo": "Moradia",       "categoria_geral": "Despesa",       "cor": "#E67E22"},
    {"nome_grupo": "Transporte",    "categoria_geral": "Despesa",       "cor": "#F1C40F"},
    {"nome_grupo": "Saúde",         "categoria_geral": "Despesa",       "cor": "#27AE60"},
    {"nome_grupo": "Educação",      "categoria_geral": "Despesa",       "cor": "#2980B9"},
    {"nome_grupo": "Lazer",         "categoria_geral": "Despesa",       "cor": "#8E44AD"},
    {"nome_grupo": "Roupas",        "categoria_geral": "Despesa",       "cor": "#16A085"},
    {"nome_grupo": "Outros",        "categoria_geral": "Despesa",       "cor": "#B0B0B0"},
    {"nome_grupo": "Investimentos", "categoria_geral": "Investimento",  "cor": "#2ECC71"},
    {"nome_grupo": "Receita",       "categoria_geral": "Receita",       "cor": "#F7DC6F"},
    {"nome_grupo": "Transferência", "categoria_geral": "Transferência", "cor": "#AEB6BF"},
]
```

### 3.2. _inicializar_grupos_usuario

```python
def _inicializar_grupos_usuario(self, user_id: int) -> None:
    """Idempotente — copia do TEMPLATE (base_grupos_template, base_marcacoes_template)."""
    from app.domains.grupos.models import BaseGruposConfig, BaseGruposTemplate
    from app.domains.categories.models import BaseMarcacao, BaseMarcacaoTemplate

    db = self.repository.db
    if db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_id).count() > 0:
        return

    for t in db.query(BaseGruposTemplate).all():
        db.add(BaseGruposConfig(
            user_id=user_id,
            nome_grupo=t.nome_grupo,
            tipo_gasto_padrao=t.tipo_gasto_padrao,
            categoria_geral=t.categoria_geral,
            cor=t.cor,
            is_padrao=True
        ))
    db.flush()

    for t in db.query(BaseMarcacaoTemplate).all():
        db.add(BaseMarcacao(user_id=user_id, GRUPO=t.GRUPO, SUBGRUPO=t.SUBGRUPO))
    db.flush()
```

### 3.3. create_user + purge_user

```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    # ... criação do user ...
    created = self.repository.create(user)
    self._inicializar_grupos_usuario(created.id)
    return UserResponse.from_orm(created)

def purge_user(self, user_id: int, executado_por: int) -> dict:
    # ... antes de delete User ...
    db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user_id).delete()
    db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_id).delete()
    db.query(User).filter(User.id == user_id).delete()
    # ...
```

---

## 4. Backend — Grupos e Marcações (filtrar por user_id)

### 4.1. GrupoRepository

```python
def get_all(self, user_id: int) -> List[BaseGruposConfig]:
    return self.db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id
    ).order_by(BaseGruposConfig.nome_grupo).all()

def get_by_nome(self, user_id: int, nome_grupo: str) -> Optional[BaseGruposConfig]:
    return self.db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id,
        BaseGruposConfig.nome_grupo == nome_grupo
    ).first()
```

### 4.2. MarcacaoRepository

```python
def get_all(self, user_id: int) -> List[dict]:
    return self.db.query(...).join(BaseGruposConfig, ...).filter(
        BaseMarcacao.user_id == user_id,
        BaseGruposConfig.user_id == user_id
    ).all()

def get_grupo_config(self, user_id: int, nome_grupo: str) -> Optional[BaseGruposConfig]:
    return self.db.query(BaseGruposConfig).filter(
        BaseGruposConfig.user_id == user_id,
        BaseGruposConfig.nome_grupo == nome_grupo
    ).first()

def create_marcacao(self, user_id: int, grupo: str, subgrupo: str) -> BaseMarcacao:
    marcacao = BaseMarcacao(user_id=user_id, GRUPO=grupo, SUBGRUPO=subgrupo)
    # ...
```

### 4.3. MarcacaoService.create_grupo_com_subgrupo

```python
def create_grupo_com_subgrupo(self, user_id: int, grupo: str, subgrupo: str, ...) -> dict:
    existing_grupo = self.repository.get_grupo_config(user_id, grupo)
    if existing_grupo:
        raise HTTPException(409, f"Grupo '{grupo}' já existe")
    novo_grupo = BaseGruposConfig(user_id=user_id, nome_grupo=grupo, ...)
    marcacao = self.repository.create_marcacao(user_id, grupo, subgrupo)
    # ...
```

### 4.4. Routers — passar user_id

Os routers já têm `user_id: int = Depends(get_current_user_id)`. Passar para os services.

---

## 5. Backend — outros domínios (padrão de alteração)

Em **todos** os pontos que usam `base_grupos_config` ou `base_marcacoes`:

```python
# ANTES
db.query(BaseGruposConfig).filter(BaseGruposConfig.nome_grupo == grupo).first()

# DEPOIS
db.query(BaseGruposConfig).filter(
    BaseGruposConfig.user_id == user_id,
    BaseGruposConfig.nome_grupo == grupo
).first()
```

**Arquivos a alterar:**
- `app/domains/budget/service.py` — get_budget_planning, list_grupos
- `app/domains/budget/router.py` — list_grupos_disponiveis, list_grupos_com_categoria
- `app/domains/upload/service.py` — _ensure_marcacao_exists, queries de tipo_gasto
- `app/domains/upload/processors/pattern_generator.py` — query base_grupos_config
- `app/domains/transactions/service.py` — validar grupo, _ensure_marcacao_exists
- `app/domains/dashboard/repository.py` — grupos_inv
- `app/domains/classification/service.py` — get_grupos_com_tipos

---

## 6. Frontend — app_admin (~2h)

Já implementado: UserStatsCell, PurgeUserModal, toggle inativos, reativar/desativar.

---

## 7. Checklist

### Banco
- [ ] Migration: base_grupos_template + base_marcacoes_template (tabelas globais)
- [ ] Seed: popular template de generic_classification_rules + complementos
- [ ] Migration: base_grupos_config (user_id, is_padrao, UNIQUE user_id+nome_grupo)
- [ ] Migration: base_marcacoes (user_id, UNIQUE user_id+GRUPO+SUBGRUPO)
- [ ] Script: copiar do template para usuários existentes (2, 3, 4...)

### Backend
- [ ] Models: BaseGruposConfig, BaseMarcacao com user_id
- [ ] _inicializar_grupos_usuario() idempotente
- [ ] create_user() chama _inicializar_grupos_usuario()
- [ ] purge_user() deleta base_grupos_config e base_marcacoes
- [ ] grupos/repository, service: filtrar por user_id
- [ ] marcacoes/repository, service: filtrar por user_id; create com user_id
- [ ] budget, upload, transactions, dashboard, classification: filtrar por user_id

### Testes
- [ ] Criar usuário → 11 grupos em base_grupos_config WHERE user_id=X
- [ ] User A cria grupo → User B não vê
- [ ] Purge → base_grupos_config e base_marcacoes zerados para user_id
