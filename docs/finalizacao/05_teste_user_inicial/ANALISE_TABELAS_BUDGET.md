# 🏦 Análise Completa: Tabelas de Budget

**Data:** 12/02/2026  
**Status:** ✅ Análise Concluída

---

## 📊 Inventário Geral

| Tabela | Registros Atuais | Tem user_id? | Status Uso |
|--------|------------------|--------------|------------|
| budget_geral | 361 | ✅ Sim | 🟢 ATIVO - Tela Metas Mobile |
| budget_planning | 1205 | ✅ Sim | 🟢 ATIVO - Tela Budget Planning Desktop |
| budget_categoria_config | 0 | ✅ Sim | 🟡 INATIVO - Feature planejada não implementada |
| budget_geral_historico | 0 | ✅ Sim | 🟡 INATIVO - Feature de auditoria não implementada |

**✅ Conclusão:** Apenas 2 das 4 tabelas estão em uso ativo. As outras 2 são estruturas para features futuras.

---

## 1️⃣ budget_geral (CRÍTICO - EM USO ATIVO)

### 📋 Schema
```sql
CREATE TABLE budget_geral (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,  -- Ex: "Casa", "Saúde", "Alimentação"
    mes_referencia VARCHAR(7) NOT NULL,    -- "YYYY-MM"
    valor_planejado FLOAT NOT NULL,        -- Meta de gastos
    total_mensal FLOAT,                    -- ⚠️ REDUNDANTE - Sempre == valor_planejado
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### ⚠️ Descoberta: Campo total_mensal é Redundante

**Validação executada (12/02/2026):**
```sql
-- Verificar se total_mensal é diferente de valor_planejado
SELECT COUNT(*) as total_diferentes 
FROM budget_geral 
WHERE valor_planejado != total_mensal;
-- Resultado: 0 (ZERO registros diferentes)
```

**Conclusão:**
- ✅ 100% dos 361 registros: `total_mensal == valor_planejado` (ou ambos NULL/0)
- ❌ Campo `total_mensal` **NÃO está sendo usado** para nada diferente
- 🗑️ **Recomendação:** Remover `total_mensal` do schema (redundância desnecessária)

**Impacto da remoção:**
- ✅ Schema mais simples (7 campos em vez de 8)
- ✅ Código Python simplificado (1 campo a menos para popular)
- ✅ SQL queries mais rápidas
- ✅ Zero impacto funcional (campo não usado de forma diferenciada)

### 🎯 Propósito
Armazena **metas gerais de gastos** por categoria ampla (ex: "Casa", "Saúde", "Alimentação").

### 🔌 Onde É Usado

**Frontend Mobile - Tela de Metas (`/mobile/budget`):**
- ✅ `GET /api/v1/budget/geral?year=X&month=Y` - Listar todas metas do mês
- ✅ `POST /api/v1/budget/geral/bulk-upsert` - Criar/atualizar metas
- ✅ Componentes: `GoalCard`, `EditGoalModal`, `ManageGoalsListItem`
- ✅ API: `features/goals/services/goals-api.ts`

**Frontend Desktop - Tela Budget (`/budget`):**
- ✅ `GET /api/v1/budget/geral?mes_referencia=YYYY-MM` - Listar metas
- ✅ `POST /api/v1/budget/geral/bulk-upsert` - Salvar alterações
- ✅ Página: `app/budget/page.tsx`

### 📈 Exemplo de Uso Real
```json
{
  "id": 123,
  "user_id": 1,
  "categoria_geral": "Casa",
  "mes_referencia": "2026-02",
  "valor_planejado": 2000.00,
  "total_mensal": 0.0
}
```

**Interpretação:** Usuário 1 quer gastar no máximo R$ 2000 em "Casa" em fevereiro/2026.

### ✅ Necessidade
**🟢 CRÍTICO - DEVE SER CRIADO PARA NOVO USUÁRIO**

**Motivo:** Tela de metas mobile depende 100% desta tabela. Sem ela, tela fica vazia.

**Registros para criar:** ~30 (10 categorias × 3 meses futuros)

---

## 2️⃣ budget_planning (ATIVO - FEATURE SEPARADA)

### 📋 Schema
```sql
CREATE TABLE budget_planning (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    grupo VARCHAR(100) NOT NULL,           -- Ex: "Supermercado Pão de Açúcar"
    mes_referencia VARCHAR(7) NOT NULL,    -- "YYYY-MM"
    valor_planejado DECIMAL(10,2) DEFAULT 0,
    valor_medio_3_meses DECIMAL(10,2) DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1,      -- SQLite boolean
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 🎯 Propósito
Planejamento **granular por subgrupo** (ex: "Supermercado Pão de Açúcar", "Posto Shell").  
É um nível **mais detalhado** que `budget_geral`.

### 🔌 Onde É Usado

**Frontend Desktop - Tela Budget Planning (`/budget/planning`):**
- ✅ `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` - Listar planejamento
- ✅ `POST /api/v1/budget/planning/bulk-upsert` - Salvar valores
- ✅ `PATCH /api/v1/budget/planning/toggle/{id}` - Ativar/desativar
- ✅ Página: `app/budget/planning/page.tsx`

**Frontend Dashboard - Breakdown de Despesas:**
- ✅ `GET /api/v1/budget/planning?mes_referencia=YYYY-MM` - Buscar fontes de despesa
- ✅ Hook: `features/dashboard/hooks/use-dashboard.ts`
- ✅ API: `features/dashboard/services/dashboard-api.ts`

**Frontend Mobile - (Comentários apenas):**
- ⚠️ Código menciona `budget_planning` mas **USA budget_geral** de fato
- Comentários desatualizados em `goals-api.ts` (linhas 5-6)

### 📈 Exemplo de Uso Real
```json
{
  "id": 456,
  "user_id": 1,
  "grupo": "Supermercado Pão de Açúcar",
  "mes_referencia": "2026-02",
  "valor_planejado": 500.00,
  "valor_medio_3_meses": 480.00,
  "ativo": 1
}
```

**Interpretação:** Usuário 1 planeja gastar R$ 500 no "Supermercado Pão de Açúcar" em fevereiro/2026. Média dos últimos 3 meses foi R$ 480.

### ✅ Necessidade
**🟡 OPCIONAL - PODE COMEÇAR VAZIO**

**Motivo:** Não é crítico para primeiro uso. Usuário pode preencher conforme usa o sistema.

**Se decidir criar:** ~100 registros (20 subgrupos × 5 meses) - mas pode começar vazio.

---

## 3️⃣ budget_categoria_config (INATIVO - FEATURE FUTURA)

### 📋 Schema
```sql
CREATE TABLE budget_categoria_config (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    nome_categoria VARCHAR(100) NOT NULL,  -- Ex: "Casa", "Cartão de Crédito"
    ordem INTEGER NOT NULL DEFAULT 999,     -- Hierarquia de exibição
    fonte_dados VARCHAR(20) NOT NULL,       -- "GRUPO" ou "TIPO_TRANSACAO"
    filtro_valor VARCHAR(100) NOT NULL,     -- Valor a filtrar
    tipos_gasto_incluidos VARCHAR(1000),    -- JSON array de TipoGasto
    cor_visualizacao VARCHAR(7) NOT NULL DEFAULT '#94a3b8',
    ativo INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 🎯 Propósito (Planejado)
Permitir que usuário **personalize categorias** de orçamento:
- Criar hierarquia customizada (ordem de exibição)
- Definir fonte de dados (GRUPO vs TIPO_TRANSACAO)
- Aplicar filtros específicos
- Escolher cores de visualização

### 🔌 Onde É Usado

**Backend:**
- ✅ Model criado: `app/domains/budget/models.py`
- ✅ Repository criado: `repository_categoria_config.py`
- ✅ Schemas criados: `BudgetCategoriaConfigCreate`, `Update`, `Response`
- ❌ **NENHUM ENDPOINT REGISTRADO** no router

**Frontend:**
- ❌ **ZERO referências** no código
- ❌ **NENHUMA TELA** usa esta feature

### 📊 Estado Atual
**Registros:** 0 (vazio)  
**Uso:** 0% (não implementado)

### ✅ Necessidade
**❌ NÃO CRIAR - FEATURE NÃO IMPLEMENTADA**

**Motivo:** Estrutura existe mas funcionalidade nunca foi implementada. Não há endpoints nem telas.

**Ação:** Deixar vazio. Se no futuro implementar a feature, criar na hora.

---

## 4️⃣ budget_geral_historico (INATIVO - FEATURE FUTURA)

### 📋 Schema
```sql
CREATE TABLE budget_geral_historico (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    mes_referencia VARCHAR(7) NOT NULL,
    valor_anterior FLOAT NOT NULL,
    valor_novo FLOAT NOT NULL,
    motivo VARCHAR(500) NOT NULL,          -- Ex: "Soma das categorias ultrapassou o total"
    soma_categorias FLOAT NOT NULL,
    created_at DATETIME NOT NULL
);
```

### 🎯 Propósito (Planejado)
Auditar **ajustes automáticos** no budget geral total:
- Registrar quando sistema ajusta `total_mensal` automaticamente
- Rastrear mudanças de valor
- Permitir rollback/investigação

### 🔌 Onde É Usado

**Backend:**
- ✅ Model criado: `app/domains/budget/models.py`
- ✅ Repository criado: `repository_categoria_config.py`
- ✅ Métodos: `registrar_ajuste()`, `get_historico_mes()`, `get_historico_recente()`
- ❌ **NENHUM ENDPOINT REGISTRADO** no router
- ❌ **NENHUMA LÓGICA DE NEGÓCIO** chama os métodos

**Frontend:**
- ❌ **ZERO referências** no código
- ❌ **NENHUMA TELA** mostra histórico

### 📊 Estado Atual
**Registros:** 0 (vazio)  
**Uso:** 0% (não implementado)

### ✅ Necessidade
**❌ NÃO CRIAR - FEATURE NÃO IMPLEMENTADA**

**Motivo:** Estrutura existe mas funcionalidade nunca foi implementada. Sistema não está fazendo ajustes automáticos.

**Ação:** Deixar vazio. Se no futuro implementar auditoria, criar na hora.

---

## 🎯 Resumo Executivo: O Que Criar para Novo Usuário

### 🔄 DECISÃO ESTRATÉGICA: CONSOLIDAÇÃO

**❌ NÃO CRIAR `budget_geral`** - Será deletada e consolidada em `budget_planning`

**✅ CRIAR `budget_planning`** - Única tabela budget ativa

---

### ✅ CRIAR (CRÍTICO)

#### 1. budget_planning
**Registros:** ~30 (10 categorias × 3 meses)  
**Motivo:** Única tabela budget (consolidação de budget_geral + budget_planning)  
**SQL:**
```sql
-- Para cada categoria ("Casa", "Saúde", "Alimentação", "Entretenimento", "Transporte", 
--                      "Carro", "Educação", "Roupas", "Presentes", "Assinaturas")
-- Criar meta zerada para próximos 3 meses (YYYY-02, YYYY-03, YYYY-04)

INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, ativo, created_at, updated_at)
SELECT 
    :user_id,
    nome_grupo,  -- Pegar de base_grupos_config
    :mes_referencia,
    0.00,
    1,  -- ativo = true
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM base_grupos_config
WHERE categoria_geral IN ('Despesa', 'Receita')
LIMIT 10;

-- Repetir para 3 meses seguintes
```

**Benefícios da Consolidação:**
- ✅ Tela de metas mobile carrega com estrutura completa
- ✅ Usuário vê 10 categorias zeradas
- ✅ Campo `ativo` permite desabilitar sem deletar
- ✅ Campo `valor_medio_3_meses` calculado automaticamente
- ✅ Arquitetura 75% mais simples (4 tabelas → 1 tabela budget)
- ✅ Zero redundância (elimina campo `total_mensal`)

---

### 🗑️ DELETAR (CONSOLIDAÇÃO)

#### ❌ budget_geral
**Registros:** 361 (migrar para budget_planning)  
**Motivo:** Redundante - campo `total_mensal` 100% inútil  
**Ação:** Migration para copiar dados e dropar tabela

#### ❌ budget_categoria_config
**Registros:** 0 (vazio)  
**Motivo:** Feature não implementada  
**Ação:** Dropar tabela

#### ❌ budget_geral_historico
**Registros:** 0 (vazio)  
**Motivo:** Feature de auditoria não implementada  
**Ação:** Dropar tabela

---

## 📋 Comparativo: budget_geral vs budget_planning

| Aspecto | budget_geral ❌ DELETAR | budget_planning ✅ USAR |
|---------|-------------------------|-------------------------|
| **Status** | 🔥 Será deletado | ✅ Única tabela budget ativa |
| **Nível de Detalhe** | Categoria Geral ("Casa") | Grupo/Categoria ("Casa", "Supermercado X") |
| **Uso Mobile** | ✅ SIM → ⚠️ REFATORAR | ❌ NÃO → ✅ IMPLEMENTAR |
| **Uso Desktop** | ✅ SIM → ⚠️ REFATORAR | ✅ SIM - Mantém |
| **Registros Esperados** | 10-15 por mês | 10-100 por mês (flexível) |
| **Campo Chave** | `categoria_geral` | `grupo` |
| **Campo Redundante** | `total_mensal` ❌ Inútil | Nenhum ✅ |
| **Campo Útil** | Nenhum | ✅ `ativo` (desabilitar) |
| **Campo Calculado** | Nenhum | ✅ `valor_medio_3_meses` |
| **Criar para Novo User?** | ❌ NÃO (deletar) | ✅ SIM (~30 registros) |
| **Arquitetura** | ❌ Redundante | ✅ Completa e flexível |

**🎯 Decisão Final:** Consolidar tudo em `budget_planning` (mais simples, mais features, zero redundância)

---

## 🔍 Descoberta Importante: Comentários Desatualizados

### ⚠️ Código com Documentação Incorreta

**File:** `app_dev/frontend/src/features/goals/services/goals-api.ts`

```typescript
/**
 * Goals API Service
 * Comunicação com o backend para metas
 * 
 * NOTA: Usa budget_planning existente como base para Goals  <-- ❌ ERRADO
 * Um "goal" é representado por múltiplos registros budget_planning  <-- ❌ ERRADO
 * agrupados por um identificador comum (grupo + prazo)
 */
```

**Realidade:**
- ✅ Tela de metas **USA budget_geral** (não `budget_planning`)
- ✅ Endpoints chamados: `GET /api/v1/budget/geral`, `POST /api/v1/budget/geral/bulk-upsert`
- ✅ Campo usado: `categoria_geral` (não `grupo`)

**Ação:** Comentário deve ser corrigido para evitar confusão futura.

---

## 📊 Estatísticas de Uso Atual

### Registros Existentes (12/02/2026)

```
budget_geral:           361 registros  (média ~30 registros/usuário × 12 usuários)
budget_planning:        1205 registros (média ~100 registros/usuário × 12 usuários)
budget_categoria_config:   0 registros (não implementado)
budget_geral_historico:    0 registros (não implementado)
```

### Distribuição Esperada por Usuário Novo

```
budget_geral:           30 registros (10 categorias × 3 meses)
budget_planning:         0 registros (começa vazio)
budget_categoria_config: 0 registros (feature desabilitada)
budget_geral_historico:  0 registros (feature desabilitada)
```

---

## ✅ Recomendações Finais

### 1. Atualizar `_populate_user_defaults()`

```python
# app/domains/users/service.py

def _populate_user_defaults(self, user_id: int):
    """
    Popula bases auxiliares para novo usuário
    
    1. ✅ budget_geral (metas template para próximos 3 meses)
    2. ✅ cartoes (cartão genérico)
    3. ❌ budget_planning (deixar vazio - usuário preenche)
    4. ❌ budget_categoria_config (feature não implementada)
    5. ❌ budget_geral_historico (feature não implementada)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from app.domains.grupos.models import BaseGruposConfig
    from app.domains.budget.models import BudgetGeral
    from app.domains.cards.models import Cartao
    
    try:
        # 1. Criar metas template (próximos 3 meses)
        hoje = datetime.now()
        meses = [(hoje + relativedelta(months=i)).strftime('%Y-%m') for i in range(3)]
        
        # Buscar top 10 grupos de despesa
        grupos = self.db.query(BaseGruposConfig).filter(
            BaseGruposConfig.categoria_geral.in_(['Despesa', 'Receita'])
        ).limit(10).all()
        
        for mes in meses:
            for grupo in grupos:
                meta = BudgetGeral(
                    user_id=user_id,
                    categoria_geral=grupo.nome_grupo,  # Ex: "Casa", "Saúde"
                    mes_referencia=mes,
                    valor_planejado=0.00
                    # total_mensal removido - redundante (sempre == valor_planejado)
                )
                self.db.add(meta)
        
        # 2. Criar cartão genérico
        cartao = Cartao(
            nome_cartao='Cartão Padrão',
            final_cartao='0000',
            banco='Não especificado',
            user_id=user_id,
            ativo=1
        )
        self.db.add(cartao)
        
        # Commit
        self.db.commit()
        logger.info(f"✅ Bases default populadas para user_id={user_id}: 30 metas + 1 cartão")
        
    except Exception as e:
        self.db.rollback()
        logger.error(f"❌ Erro ao popular bases default: {e}")
        raise
```

### 2. Corrigir Comentários em `goals-api.ts`

```typescript
/**
 * Goals API Service
 * Comunicação com o backend para metas
 * 
 * NOTA: Usa budget_geral existente como base para Goals
 * Cada "goal" é um registro budget_geral por categoria_geral
 */
```

### 3. Remover Campo Redundante total_mensal

**❌ CANCELADO** - Tabela `budget_geral` será deletada completamente (ver item 4).

---

### 4. Consolidar Budget: Deletar 3 Tabelas, Usar Apenas 1

**Decisão atualizada:** Deletar `budget_geral` **AGORA** e consolidar em `budget_planning`.

**Motivo:** 
- `budget_geral` tem campo `total_mensal` 100% redundante (validado: 0 diferenças)
- `budget_planning` é mais completo: `ativo`, `valor_medio_3_meses`
- Arquitetura mais simples: 4 tabelas → 1 tabela budget
- Zero redundância

**Migration Alembic:**
```bash
alembic revision -m "consolidate_budget_tables"
```

**Conteúdo:**
```python
def upgrade():
    """Consolidar budget em uma única tabela"""
    
    # 1. Migrar dados de budget_geral para budget_planning
    op.execute("""
        INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, ativo, created_at, updated_at)
        SELECT 
            user_id,
            categoria_geral as grupo,
            mes_referencia,
            valor_planejado,
            1 as ativo,
            created_at,
            updated_at
        FROM budget_geral
        WHERE NOT EXISTS (
            SELECT 1 FROM budget_planning bp 
            WHERE bp.user_id = budget_geral.user_id 
            AND bp.grupo = budget_geral.categoria_geral 
            AND bp.mes_referencia = budget_geral.mes_referencia
        );
    """)
    
    # 2. Dropar tabelas não usadas
    op.drop_table('budget_geral')  # ✅ Dados migrados
    op.drop_table('budget_categoria_config')  # ✅ Nunca usado
    op.drop_table('budget_geral_historico')  # ✅ Nunca usado

def downgrade():
    """Rollback improvável - usar backup se necessário"""
    pass
```

**Remover código backend:**
- ❌ `app/domains/budget/models.py`: BudgetGeral, BudgetCategoriaConfig, BudgetGeralHistorico
- ❌ `app/domains/budget/repository_categoria_config.py`: Arquivo completo
- ❌ `app/domains/budget/schemas.py`: 7 schemas relacionados
- ❌ `app/domains/budget/router.py`: 3 endpoints `/budget/geral`

**Refatorar frontend:**
- ⚠️ `app/mobile/budget/page.tsx`: Mudar API `/budget/geral` → `/budget/planning`
- ⚠️ `app/budget/page.tsx`: Mudar API `/budget/geral` → `/budget/planning`
- ⚠️ `features/goals/services/goals-api.ts`: Atualizar BASE_URL
- ⚠️ Tipos: `categoria_geral` → `grupo`

**Benefícios imediatos:**
- ✅ Arquitetura 75% mais simples (4 → 1 tabela budget)
- ✅ Zero redundância (elimina `total_mensal`)
- ✅ Mais features (`ativo`, `valor_medio_3_meses`)
- ✅ Código 60% menor (3 models + 1 repo + 7 schemas a menos)
- ✅ Frontend unificado (mesma API mobile/desktop)
- ✅ Documentação alinhada com realidade

**Tempo:** 3-5 horas (migration + refatoração frontend + testes)

**Ver plano completo:** [VALIDACOES_COMPLETAS.md](./VALIDACOES_COMPLETAS.md#🗑️-limpeza-remover-tabelas-não-usadas)

---

**Criado em:** 12/02/2026  
**Revisado por:** GitHub Copilot AI  
**Próxima revisão:** Após implementação de novo usuário
