# 🎯 Sprint 2 - Auto-Criação de Grupos/Subgrupos

**Status:** 🟡 Planejamento  
**Dependências:** Sprint 1 (✅ Completo)  
**Estimativa:** 1-2 dias  
**Prioridade:** Alta

---

## 📋 Objetivo

**Permitir criação automática de grupos/subgrupos via API durante upload de arquivos**

### Problema Atual
- ❌ Usuário faz upload de arquivo
- ❌ Sistema detecta grupos inexistentes: `["Novo Grupo", "Outro Grupo"]`
- ❌ Marcação FALHA porque grupos não existem em `base_marcacoes`
- ❌ Usuário precisa criar manualmente via interface web

### Solução Proposta
- ✅ Usuário faz upload de arquivo
- ✅ Sistema detecta grupos inexistentes
- ✅ API cria grupos automaticamente em `base_marcacoes`
- ✅ Marcação prossegue automaticamente
- ✅ (Opcional) Modal UI para confirmar/editar grupos novos

---

## 🎯 Resultados Esperados

### Backend
- ✅ 2 novos endpoints REST:
  - `POST /api/v1/marcacoes/grupos` - Criar grupo
  - `POST /api/v1/marcacoes/grupos/{grupo_id}/subgrupos` - Criar subgrupo
- ✅ Validação de duplicatas (caso já exista)
- ✅ Suporte a criação em lote (batch)
- ✅ Retornar grupos criados com IDs

### Upload Flow
- ✅ Upload processa arquivo normalmente
- ✅ Se grupo não existe → cria automaticamente
- ✅ Log de grupos criados: `"Criados automaticamente: Novo Grupo, Outro Grupo"`
- ✅ Marcação prossegue sem interrupção

### Frontend (Opcional - Sprint 3)
- ⏳ Modal "+ Criar Grupo" durante upload
- ⏳ Permitir editar nome/categoria antes de criar
- ⏳ Preview de grupos que serão criados

---

## 🗂️ Estrutura de Dados

### Tabela: `base_marcacoes`
```sql
CREATE TABLE base_marcacoes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,              -- Nome do grupo/subgrupo
    categoria VARCHAR(255),                  -- Categoria (Despesa, Receita, etc)
    tipo VARCHAR(50),                        -- Tipo (Grupo, Subgrupo)
    grupo_pai_id INTEGER,                    -- FK para grupo pai (se subgrupo)
    user_id INTEGER NOT NULL,                -- FK para users
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, nome, grupo_pai_id)     -- Evitar duplicatas
);
```

### Modelo SQLAlchemy: `BaseMarcacao`
```python
class BaseMarcacao(Base):
    __tablename__ = 'base_marcacoes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    categoria = Column(String(255))                    # Despesa, Receita, etc
    tipo = Column(String(50))                          # Grupo, Subgrupo
    grupo_pai_id = Column(Integer, ForeignKey('base_marcacoes.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    subgrupos = relationship('BaseMarcacao', backref='grupo_pai', remote_side=[id])
```

---

## 🔧 Backend - Endpoints

### 1. `POST /api/v1/marcacoes/grupos` - Criar Grupo

**Request Body:**
```json
{
  "nome": "Novo Grupo",
  "categoria": "Despesa",               // Opcional
  "tipo": "Grupo"                       // Default se não especificado
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "nome": "Novo Grupo",
  "categoria": "Despesa",
  "tipo": "Grupo",
  "grupo_pai_id": null,
  "user_id": 1,
  "created_at": "2026-02-13T10:30:00Z"
}
```

**Response (409 Conflict - já existe):**
```json
{
  "detail": "Grupo 'Novo Grupo' já existe para este usuário",
  "existing_id": 45
}
```

**Validações:**
- ✅ `nome` obrigatório, max 255 chars
- ✅ `categoria` opcional (default: "Despesa")
- ✅ `tipo` opcional (default: "Grupo")
- ✅ Verificar duplicata: `user_id + nome + grupo_pai_id=NULL`
- ✅ Retornar 409 se já existe (com ID do existente)

---

### 2. `POST /api/v1/marcacoes/grupos/{grupo_id}/subgrupos` - Criar Subgrupo

**Request Body:**
```json
{
  "nome": "Novo Subgrupo",
  "categoria": "Despesa"                // Opcional (herda do grupo pai)
}
```

**Response (201 Created):**
```json
{
  "id": 124,
  "nome": "Novo Subgrupo",
  "categoria": "Despesa",
  "tipo": "Subgrupo",
  "grupo_pai_id": 123,
  "user_id": 1,
  "created_at": "2026-02-13T10:35:00Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Grupo pai com ID 123 não encontrado"
}
```

**Response (409 Conflict):**
```json
{
  "detail": "Subgrupo 'Novo Subgrupo' já existe em 'Novo Grupo'",
  "existing_id": 98
}
```

**Validações:**
- ✅ `grupo_id` no path obrigatório
- ✅ Verificar se grupo pai existe
- ✅ `nome` obrigatório, max 255 chars
- ✅ `categoria` opcional (herda do pai se não especificado)
- ✅ `tipo` automático: "Subgrupo"
- ✅ Verificar duplicata: `user_id + nome + grupo_pai_id={grupo_id}`

---

### 3. `POST /api/v1/marcacoes/grupos/batch` - Criar Múltiplos Grupos (Opcional)

**Request Body:**
```json
{
  "grupos": [
    {
      "nome": "Grupo A",
      "categoria": "Despesa",
      "subgrupos": [
        {"nome": "Subgrupo A1"},
        {"nome": "Subgrupo A2"}
      ]
    },
    {
      "nome": "Grupo B",
      "categoria": "Receita"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "created": [
    {"id": 125, "nome": "Grupo A", "tipo": "Grupo"},
    {"id": 126, "nome": "Subgrupo A1", "tipo": "Subgrupo", "grupo_pai_id": 125},
    {"id": 127, "nome": "Subgrupo A2", "tipo": "Subgrupo", "grupo_pai_id": 125},
    {"id": 128, "nome": "Grupo B", "tipo": "Grupo"}
  ],
  "skipped": [
    {"nome": "Grupo C", "reason": "Já existe", "existing_id": 50}
  ]
}
```

**Benefício:** Criar múltiplos grupos/subgrupos em uma chamada (upload processa em batch)

---

## 🔄 Fluxo de Upload com Auto-criação

### Antes (Sprint 1):
```python
# upload/processors/marker.py
def mark_transactions(df, user_id):
    grupos_existentes = get_grupos(user_id)
    
    for row in df.iterrows():
        if row['grupo'] not in grupos_existentes:
            # ❌ FALHA - grupo não existe
            raise ValueError(f"Grupo '{row['grupo']}' não encontrado")
```

### Depois (Sprint 2):
```python
# upload/processors/marker.py
def mark_transactions(df, user_id):
    grupos_existentes = get_grupos(user_id)
    grupos_criados = []
    
    for row in df.iterrows():
        if row['grupo'] not in grupos_existentes:
            # ✅ CRIAR grupo automaticamente
            novo_grupo = create_grupo({
                "nome": row['grupo'],
                "categoria": row['categoria_geral'],
                "tipo": "Grupo"
            }, user_id)
            grupos_existentes.append(novo_grupo['nome'])
            grupos_criados.append(novo_grupo)
    
    # Log de grupos criados
    if grupos_criados:
        logger.info(f"Grupos criados automaticamente: {[g['nome'] for g in grupos_criados]}")
    
    # Marcar transações normalmente
    # ...
```

---

## 🧪 Testes

### Backend - Unit Tests

**Test: Criar grupo novo**
```python
def test_create_grupo_success():
    response = client.post(
        "/api/v1/marcacoes/grupos",
        json={"nome": "Novo Grupo", "categoria": "Despesa"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["nome"] == "Novo Grupo"
    assert response.json()["tipo"] == "Grupo"
```

**Test: Criar grupo duplicado**
```python
def test_create_grupo_duplicate():
    # Criar primeiro
    client.post("/api/v1/marcacoes/grupos", json={"nome": "Grupo Teste"})
    
    # Tentar criar novamente
    response = client.post("/api/v1/marcacoes/grupos", json={"nome": "Grupo Teste"})
    assert response.status_code == 409
    assert "já existe" in response.json()["detail"]
    assert "existing_id" in response.json()
```

**Test: Criar subgrupo**
```python
def test_create_subgrupo_success():
    # Criar grupo pai
    grupo_response = client.post("/api/v1/marcacoes/grupos", json={"nome": "Pai"})
    grupo_id = grupo_response.json()["id"]
    
    # Criar subgrupo
    response = client.post(
        f"/api/v1/marcacoes/grupos/{grupo_id}/subgrupos",
        json={"nome": "Filho"}
    )
    assert response.status_code == 201
    assert response.json()["tipo"] == "Subgrupo"
    assert response.json()["grupo_pai_id"] == grupo_id
```

**Test: Criar subgrupo sem grupo pai**
```python
def test_create_subgrupo_no_parent():
    response = client.post(
        "/api/v1/marcacoes/grupos/99999/subgrupos",
        json={"nome": "Filho"}
    )
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]
```

### Integration Test - Upload com Auto-criação

**Test: Upload cria grupos automaticamente**
```python
def test_upload_creates_missing_grupos():
    # Preparar CSV com grupo inexistente
    csv_content = """
    Data,Lancamento,Valor,Tipo,Grupo,Subgrupo
    01/02/2026,Compra teste,100.00,Débito,Grupo Novo,Subgrupo Novo
    """
    
    # Upload
    response = client.post(
        "/api/v1/upload/classificar",
        files={"file": ("test.csv", csv_content)},
        data={"tipo_documento": "extrato"}
    )
    
    # Verificar grupos criados
    assert response.status_code == 200
    assert "Grupo Novo" in response.json()["grupos_criados"]
    
    # Verificar grupo existe no banco
    grupos = client.get("/api/v1/marcacoes/grupos").json()
    assert any(g["nome"] == "Grupo Novo" for g in grupos)
```

---

## � PROBLEMA ARQUITETURAL IDENTIFICADO

### Redundância de Dados entre Tabelas

**Situação Atual:**
```sql
-- base_grupos_config (fonte oficial)
base_grupos_config:
  - nome_grupo
  - tipo_gasto_padrao       ✅ FONTE OFICIAL
  - categoria_geral         ✅ FONTE OFICIAL

-- base_marcacoes (duplicação!)
base_marcacoes:
  - GRUPO
  - SUBGRUPO
  - TipoGasto              ❌ DUPLICADO (deveria vir de grupos_config)
  - CategoriaGeral         ❌ DUPLICADO (deveria vir de grupos_config)
```

**Problema:**
- Campos `TipoGasto` e `CategoriaGeral` estão **duplicados** em `base_marcacoes`
- Dados oficiais estão em `base_grupos_config`
- Pode causar inconsistências (ex: mudar em um lugar e não atualizar no outro)

**Solução Proposta:**
```sql
-- base_marcacoes LIMPA (apenas relação grupo-subgrupo)
base_marcacoes:
  - GRUPO              ✅ MANTÉM (FK para base_grupos_config.nome_grupo)
  - SUBGRUPO           ✅ MANTÉM (nome do subgrupo)
  
-- Remover campos redundantes:
  - TipoGasto          ❌ DELETAR (vem de JOIN com grupos_config)
  - CategoriaGeral     ❌ DELETAR (vem de JOIN com grupos_config)
```

**Migration Necessária:**
```python
# migrations/versions/XXXX_cleanup_base_marcacoes.py
def upgrade():
    # 1. Validar integridade antes de deletar
    op.execute("""
        SELECT COUNT(*) FROM base_marcacoes m
        LEFT JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo
        WHERE g.nome_grupo IS NULL
    """)
    # Se > 0, há grupos órfãos que precisam ser criados em grupos_config primeiro
    
    # 2. Remover colunas redundantes
    op.drop_column('base_marcacoes', 'TipoGasto')
    op.drop_column('base_marcacoes', 'CategoriaGeral')
    
    # 3. Adicionar FK (opcional)
    op.create_foreign_key(
        'fk_marcacoes_grupos',
        'base_marcacoes', 'base_grupos_config',
        ['GRUPO'], ['nome_grupo']
    )

def downgrade():
    # Restaurar colunas (dados serão NULL após restore)
    op.add_column('base_marcacoes', sa.Column('TipoGasto', sa.String(100)))
    op.add_column('base_marcacoes', sa.Column('CategoriaGeral', sa.String(100)))
    op.drop_constraint('fk_marcacoes_grupos', 'base_marcacoes')
```

**Queries Após Limpeza:**
```python
# ANTES (campos redundantes)
marcacao = db.query(BaseMarcacao).filter(...).first()
tipo_gasto = marcacao.TipoGasto  # Dados duplicados

# DEPOIS (JOIN com grupos_config)
marcacao = db.query(BaseMarcacao, BaseGruposConfig)\
    .join(BaseGruposConfig, BaseMarcacao.GRUPO == BaseGruposConfig.nome_grupo)\
    .filter(...).first()
tipo_gasto = marcacao.BaseGruposConfig.tipo_gasto_padrao  # Fonte oficial
```

**Benefícios:**
- ✅ Elimina duplicação de dados
- ✅ Fonte única de verdade (base_grupos_config)
- ✅ Reduz tamanho do banco
- ✅ Previne inconsistências
- ✅ Facilita manutenção

---

## 📊 Sub-Sprints

### Sprint 2.0 - Análise e Limpeza Arquitetural (2 horas) ⚠️ CRÍTICO
**Atividades:**
- [ ] **Análise:** Avaliar necessidade de manter ambas as tabelas
  - Cenário 1: Manter ambas → Remover campos redundantes
  - Cenário 2: Unificar → Migrar tudo para uma tabela
- [ ] **Auditoria:** Verificar integridade de dados
  - Grupos em base_marcacoes sem correspondente em base_grupos_config
  - Inconsistências entre TipoGasto/CategoriaGeral das duas tabelas
- [ ] **Migration:** Criar migration para limpeza
  - Remover colunas TipoGasto e CategoriaGeral de base_marcacoes
  - Adicionar FK GRUPO → base_grupos_config.nome_grupo
  - Validar integridade referencial
- [ ] **Atualizar Queries:** Refatorar para usar JOIN
  - Atualizar MarcacaoRepository para fazer JOIN com grupos_config
  - Atualizar schemas para pegar dados da fonte oficial
- [ ] **Testes:** Validar que queries retornam mesmos dados

**Arquivos:**
- `migrations/versions/XXXX_cleanup_base_marcacoes.py` - Migration
- `app/domains/marcacoes/repository.py` - Atualizar queries com JOIN
- `docs/features/auto-create-grupos/LIMPEZA_ARQUITETURAL.md` - Documentação

**Decisão Arquitetural:**
```
┌─────────────────────────────────────────────────────────────┐
│ OPÇÃO RECOMENDADA: Manter 2 tabelas com limpeza            │
├─────────────────────────────────────────────────────────────┤
│ base_grupos_config:                                         │
│   - Configuração do GRUPO (tipo_gasto, categoria)          │
│   - 1 registro por grupo                                    │
│                                                              │
│ base_marcacoes:                                             │
│   - Relação GRUPO + SUBGRUPO                                │
│   - N registros por grupo (1 por subgrupo)                 │
│   - JOIN com grupos_config para pegar configuração         │
└─────────────────────────────────────────────────────────────┘
```

---

### Sprint 2.1 - Backend Endpoints (4 horas)
**Dependências:** ⚠️ Sprint 2.0 deve ser completo primeiro

**Atividades:**
- [ ] Criar schema `GrupoCreate`, `GrupoResponse`
- [ ] Endpoint `POST /api/v1/marcacoes/grupos`
- [ ] Endpoint `POST /api/v1/marcacoes/grupos/{id}/subgrupos`
- [ ] Endpoint `POST /api/v1/marcacoes/grupos/batch` (opcional)
- [ ] Validações (duplicata, grupo pai existe)
- [ ] Unit tests (6-8 testes)

**Arquivos:**
- `app/domains/marcacoes/schemas.py` - Adicionar GrupoCreate, GrupoResponse
- `app/domains/marcacoes/router.py` - Adicionar 2-3 endpoints
- `app/domains/marcacoes/service.py` - Lógica de criação
- `app/domains/marcacoes/repository.py` - Queries
- `tests/domains/marcacoes/test_grupos_creation.py` - Testes

---

### Sprint 2.2 - Integração Upload (2 horas)
**Atividades:**
- [ ] Modificar `upload/processors/marker.py`
- [ ] Detectar grupos inexistentes
- [ ] Criar grupos via API
- [ ] Log de grupos criados
- [ ] Integration test

**Arquivos:**
- `app/domains/upload/processors/marker.py` - Auto-criação
- `app/domains/upload/service.py` - Retornar grupos criados
- `tests/domains/upload/test_auto_create_grupos.py` - Integration test

---

### Sprint 2.3 - Validação E2E (2 horas)
**Atividades:**
- [ ] Teste manual: upload com grupos novos
- [ ] Verificar grupos criados no banco
- [ ] Verificar marcação funciona
- [ ] Teste edge cases (duplicatas, caracteres especiais)
- [ ] **Validação pós-limpeza:** Confirmar JOIN funciona corretamente
- [ ] Documentação

**Arquivos:**
- `docs/features/auto-create-grupos/SPRINT2_COMPLETE.md`
- `docs/features/auto-create-grupos/API_DOCS.md`
- `docs/features/auto-create-grupos/LIMPEZA_ARQUITETURAL.md`

---

## 🚀 Deploy Checklist

### Pré-Deploy
- [ ] Tests passando (unit + integration)
- [ ] Migration criada (se necessário)
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado

### Deploy
- [ ] Merge para main
- [ ] Deploy backend
- [ ] Validar endpoints produção
- [ ] Teste upload produção

### Pós-Deploy
- [ ] Monitorar logs 24h
- [ ] Validar criação de grupos
- [ ] Verificar performance (batch creation)

---

## 🔜 Sprint 3 - UI Modal Criação (Opcional)

**Objetivo:** Interface para usuário revisar/editar grupos antes de criar

**Features:**
- Modal "+ Criar Grupo" durante upload
- Lista de grupos que serão criados
- Editar nome/categoria antes de confirmar
- Cancelar criação de grupos específicos

**Estimativa:** 1 dia  
**Dependências:** Sprint 2

---

## 📚 Referências

- **Sprint 1:** `docs/features/budget-consolidation/SPRINT1_COMPLETE.md`
- **Plano Geral:** `docs/features/budget-consolidation/PLANO_IMPLEMENTACAO.md`
- **Domínio Marcacoes:** `app/domains/marcacoes/`
- **Upload Processor:** `app/domains/upload/processors/marker.py`

---

**Status:** 🟡 Planejamento Completo  
**Próximo:** Iniciar Sprint 2.1 - Backend Endpoints
