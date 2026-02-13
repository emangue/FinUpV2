# 🔄 Migração: Adicionar user_id nas Bases de Classificação

**Data:** 12/02/2026  
**Decisão:** Permitir que cada usuário tenha seus próprios grupos e subgrupos personalizados

---

## 🎯 Objetivo

Migrar **base_grupos_config** e **base_marcacoes** de tabelas globais para **por usuário**, adicionando coluna `user_id`.

**Benefícios:**
- ✅ Cada usuário cria seus próprios grupos e subgrupos
- ✅ Total flexibilidade e personalização
- ✅ Não interfere em outros usuários
- ✅ Usuário organiza como quiser

---

## 📊 Estado Atual vs Desejado

### Estado Atual (GLOBAL)
```sql
-- base_grupos_config (21 registros compartilhados)
CREATE TABLE base_grupos_config (
    id INTEGER PRIMARY KEY,
    nome_grupo TEXT NOT NULL,
    tipo_gasto_padrao TEXT NOT NULL,
    categoria_geral TEXT NOT NULL
);

-- base_marcacoes (405 registros compartilhados)
CREATE TABLE base_marcacoes (
    id INTEGER PRIMARY KEY,
    GRUPO VARCHAR(100) NOT NULL,
    SUBGRUPO VARCHAR(100) NOT NULL,
    TipoGasto VARCHAR(100) NOT NULL,
    CategoriaGeral VARCHAR(100)
);
```

### Estado Desejado (POR USUÁRIO)
```sql
-- base_grupos_config (21 registros × N usuários)
CREATE TABLE base_grupos_config (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,  -- ✅ ADICIONAR
    nome_grupo TEXT NOT NULL,
    tipo_gasto_padrao TEXT NOT NULL,
    categoria_geral TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- base_marcacoes (405 registros × N usuários)
CREATE TABLE base_marcacoes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,  -- ✅ ADICIONAR
    GRUPO VARCHAR(100) NOT NULL,
    SUBGRUPO VARCHAR(100) NOT NULL,
    TipoGasto VARCHAR(100) NOT NULL,
    CategoriaGeral VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 🚀 Plano de Migração

### Fase 1: Criar Templates (Backup dos Dados Atuais)

**Criar tabelas temporárias com dados atuais:**
```sql
-- Template de grupos (21 registros)
CREATE TABLE base_grupos_config_template AS 
SELECT * FROM base_grupos_config;

-- Template de marcações (405 registros)
CREATE TABLE base_marcacoes_template AS 
SELECT * FROM base_marcacoes;
```

**Validação:**
```sql
SELECT COUNT(*) FROM base_grupos_config_template;  -- Esperado: 21
SELECT COUNT(*) FROM base_marcacoes_template;      -- Esperado: 405
```

---

### Fase 2: Adicionar user_id nas Tabelas Originais

**Opção A: Via Alembic (Recomendado)**

**File:** `app_dev/backend/migrations/versions/XXXX_add_user_id_bases.py`

```python
"""add user_id to base_grupos_config and base_marcacoes

Revision ID: xxxx
Revises: yyyy
Create Date: 2026-02-12

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Adicionar user_id em base_grupos_config
    op.add_column('base_grupos_config', 
        sa.Column('user_id', sa.Integer(), nullable=True))
    
    # 2. Adicionar user_id em base_marcacoes
    op.add_column('base_marcacoes', 
        sa.Column('user_id', sa.Integer(), nullable=True))
    
    # 3. Criar foreign keys
    op.create_foreign_key(
        'fk_base_grupos_config_user_id',
        'base_grupos_config', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_base_marcacoes_user_id',
        'base_marcacoes', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Remover foreign keys
    op.drop_constraint('fk_base_grupos_config_user_id', 'base_grupos_config')
    op.drop_constraint('fk_base_marcacoes_user_id', 'base_marcacoes')
    
    # Remover colunas
    op.drop_column('base_grupos_config', 'user_id')
    op.drop_column('base_marcacoes', 'user_id')
```

**Executar:**
```bash
cd app_dev/backend
alembic upgrade head
```

---

**Opção B: Via Script SQL Direto (Alternativa)**

**File:** `scripts/database/migrate_add_user_id_bases.py`

```python
#!/usr/bin/env python3
"""
Adiciona user_id em base_grupos_config e base_marcacoes
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "app_dev/backend/database/financas_dev.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔄 Iniciando migração...")
        
        # 1. Adicionar user_id em base_grupos_config
        print("1. Adicionando user_id em base_grupos_config...")
        cursor.execute("ALTER TABLE base_grupos_config ADD COLUMN user_id INTEGER")
        
        # 2. Adicionar user_id em base_marcacoes
        print("2. Adicionando user_id em base_marcacoes...")
        cursor.execute("ALTER TABLE base_marcacoes ADD COLUMN user_id INTEGER")
        
        conn.commit()
        print("✅ Migração concluída!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
```

---

### Fase 3: Popular Dados para Usuários Existentes

**Script:** `scripts/database/populate_bases_for_existing_users.py`

```python
#!/usr/bin/env python3
"""
Popula base_grupos_config e base_marcacoes para todos os usuários existentes
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "app_dev/backend/database/financas_dev.db"

def populate_existing_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔄 Populando bases para usuários existentes...")
        
        # 1. Buscar todos os usuários
        cursor.execute("SELECT id FROM users")
        users = cursor.fetchall()
        
        print(f"📊 Encontrados {len(users)} usuários")
        
        for (user_id,) in users:
            print(f"\n👤 Processando user_id={user_id}...")
            
            # 2. Copiar grupos do template
            cursor.execute("""
                INSERT INTO base_grupos_config (user_id, nome_grupo, tipo_gasto_padrao, categoria_geral)
                SELECT ?, nome_grupo, tipo_gasto_padrao, categoria_geral
                FROM base_grupos_config_template
            """, (user_id,))
            
            grupos_count = cursor.rowcount
            print(f"   ✅ {grupos_count} grupos copiados")
            
            # 3. Copiar marcações do template
            cursor.execute("""
                INSERT INTO base_marcacoes (user_id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral)
                SELECT ?, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
                FROM base_marcacoes_template
            """, (user_id,))
            
            marcacoes_count = cursor.rowcount
            print(f"   ✅ {marcacoes_count} marcações copiadas")
        
        conn.commit()
        print("\n🎉 População concluída!")
        
        # 4. Validar
        print("\n📊 Validação:")
        cursor.execute("SELECT COUNT(*) FROM base_grupos_config WHERE user_id IS NOT NULL")
        total_grupos = cursor.fetchone()[0]
        print(f"   base_grupos_config: {total_grupos} registros com user_id")
        
        cursor.execute("SELECT COUNT(*) FROM base_marcacoes WHERE user_id IS NOT NULL")
        total_marcacoes = cursor.fetchone()[0]
        print(f"   base_marcacoes: {total_marcacoes} registros com user_id")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    populate_existing_users()
```

**Executar:**
```bash
python scripts/database/populate_bases_for_existing_users.py
```

---

### Fase 4: Limpar Dados Globais Antigos

**Após validar que todos os usuários têm dados:**

```python
# scripts/database/cleanup_old_global_bases.py
def cleanup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Deletar registros sem user_id (dados globais antigos)
        cursor.execute("DELETE FROM base_grupos_config WHERE user_id IS NULL")
        grupos_deletados = cursor.rowcount
        
        cursor.execute("DELETE FROM base_marcacoes WHERE user_id IS NULL")
        marcacoes_deletados = cursor.rowcount
        
        conn.commit()
        print(f"✅ Limpeza concluída!")
        print(f"   base_grupos_config: {grupos_deletados} registros globais removidos")
        print(f"   base_marcacoes: {marcacoes_deletados} registros globais removidos")
        
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
```

---

### Fase 5: Atualizar Modelos SQLAlchemy

**File:** `app_dev/backend/app/domains/grupos/models.py`

```python
class BaseGruposConfig(Base):
    __tablename__ = "base_grupos_config"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ✅ ADICIONAR
    nome_grupo = Column(Text, nullable=False)
    tipo_gasto_padrao = Column(Text, nullable=False)
    categoria_geral = Column(Text, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="grupos_config")  # ✅ ADICIONAR
```

**File:** `app_dev/backend/app/domains/categories/models.py`

```python
class BaseMarcacao(Base):
    __tablename__ = "base_marcacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ✅ ADICIONAR
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)
    TipoGasto = Column(String(100), nullable=False)
    CategoriaGeral = Column(String(100))
    
    # Relationship
    user = relationship("User", back_populates="marcacoes")  # ✅ ADICIONAR
```

**File:** `app_dev/backend/app/domains/users/models.py`

```python
class User(Base):
    __tablename__ = "users"
    
    # ... campos existentes ...
    
    # Relationships
    grupos_config = relationship("BaseGruposConfig", back_populates="user", cascade="all, delete-orphan")  # ✅ ADICIONAR
    marcacoes = relationship("BaseMarcacao", back_populates="user", cascade="all, delete-orphan")  # ✅ ADICIONAR
```

---

### Fase 6: Atualizar Queries (Adicionar Filtro user_id)

**Todas as queries devem filtrar por user_id:**

```python
# ❌ ANTES (buscava global)
grupos = db.query(BaseGruposConfig).all()

# ✅ DEPOIS (filtra por usuário)
grupos = db.query(BaseGruposConfig).filter_by(user_id=user_id).all()
```

**Arquivos a atualizar:**
- `app/domains/grupos/repository.py` - Adicionar filtro user_id
- `app/domains/categories/repository.py` - Adicionar filtro user_id
- `app/domains/transactions/service.py` - Queries de TipoGasto/CategoriaGeral
- `app/domains/upload/service.py` - Classificação durante upload
- `app/domains/classification/service.py` - Auto-classificação

---

### Fase 7: Atualizar `_populate_user_defaults()`

**Novo comportamento: Copiar do template ao criar usuário**

```python
def _populate_user_defaults(self, user_id: int):
    """
    Popula bases auxiliares para novo usuário
    
    1. base_grupos_config (copiar 21 grupos do template)
    2. base_marcacoes (copiar 405 marcações do template)
    3. budget_geral (metas template para próximos 3 meses)
    4. cartoes (cartão genérico)
    """
    try:
        # 1. Copiar grupos do template
        cursor.execute("""
            INSERT INTO base_grupos_config (user_id, nome_grupo, tipo_gasto_padrao, categoria_geral)
            SELECT ?, nome_grupo, tipo_gasto_padrao, categoria_geral
            FROM base_grupos_config_template
        """, (user_id,))
        
        # 2. Copiar marcações do template
        cursor.execute("""
            INSERT INTO base_marcacoes (user_id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral)
            SELECT ?, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
            FROM base_marcacoes_template
        """, (user_id,))
        
        # 3. Budget geral (código existente)
        # ...
        
        # 4. Cartão genérico (código existente)
        # ...
        
        db.commit()
        logger.info(f"✅ Bases populadas: 21 grupos + 405 marcações + metas + cartão")
        
    except Exception as e:
        db.rollback()
        raise
```

---

## 📋 Checklist de Migração

### Preparação
- [ ] Criar backup completo do banco (`backup_daily.sh`)
- [ ] Criar tabelas template (base_grupos_config_template, base_marcacoes_template)
- [ ] Validar templates (21 grupos, 405 marcações)

### Migração
- [ ] Executar migration Alembic (adicionar user_id)
- [ ] Popular dados para usuários existentes
- [ ] Validar que todos os usuários têm dados
- [ ] Limpar registros globais antigos (user_id IS NULL)

### Código
- [ ] Atualizar modelos SQLAlchemy (adicionar user_id, relationships)
- [ ] Atualizar repositories (adicionar filtro user_id)
- [ ] Atualizar services (adicionar filtro user_id)
- [ ] Atualizar `_populate_user_defaults()` (copiar templates)

### Validação
- [ ] Criar usuário de teste
- [ ] Verificar que tem 21 grupos próprios
- [ ] Verificar que tem 405 marcações próprias
- [ ] Fazer upload e validar classificação
- [ ] Verificar que usuários não veem dados uns dos outros

### Limpeza
- [ ] Remover templates (ou manter para referência futura)
- [ ] Atualizar documentação (VALIDACOES_COMPLETAS.md)
- [ ] Commitar mudanças no git

---

## 🎯 Resultado Esperado

### Antes (Global)
```sql
SELECT COUNT(*) FROM base_grupos_config;
-- Resultado: 21 (compartilhado por todos)

SELECT COUNT(*) FROM base_marcacoes;
-- Resultado: 405 (compartilhado por todos)
```

### Depois (Por Usuário)
```sql
-- Usuário 1
SELECT COUNT(*) FROM base_grupos_config WHERE user_id = 1;
-- Resultado: 21 (só dele)

SELECT COUNT(*) FROM base_marcacoes WHERE user_id = 1;
-- Resultado: 405 (só dele)

-- Usuário 2
SELECT COUNT(*) FROM base_grupos_config WHERE user_id = 2;
-- Resultado: 21 (só dele)

SELECT COUNT(*) FROM base_marcacoes WHERE user_id = 2;
-- Resultado: 405 (só dele)
```

**Benefício:** Cada usuário pode adicionar, editar, remover grupos e subgrupos sem afetar outros! ✅

---

## 📊 Impacto no Banco de Dados

### Antes
```
base_grupos_config: 21 registros (global)
base_marcacoes: 405 registros (global)
Total: 426 registros
```

### Depois (com 4 usuários ativos)
```
base_grupos_config: 21 × 4 = 84 registros
base_marcacoes: 405 × 4 = 1.620 registros
Total: 1.704 registros (+300% espaço)
```

**Trade-off:** Mais espaço no banco, mas **total flexibilidade** para usuários ✅

---

## ⚡ Execução Rápida

```bash
# 1. Backup
./scripts/deploy/backup_daily.sh

# 2. Criar templates
python scripts/database/create_templates.py

# 3. Migration
cd app_dev/backend && alembic upgrade head

# 4. Popular usuários existentes
python scripts/database/populate_bases_for_existing_users.py

# 5. Validar
python scripts/database/validate_migration.py

# 6. Limpar globais
python scripts/database/cleanup_old_global_bases.py

# 7. Reiniciar servidores
./scripts/deploy/quick_stop.sh && ./scripts/deploy/quick_start.sh
```

---

**Status:** 🟡 Plano pronto, aguardando execução  
**Próximo passo:** Executar Fase 1 (criar templates)
