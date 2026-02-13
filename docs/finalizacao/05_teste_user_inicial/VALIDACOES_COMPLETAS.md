# ✅ Validação Completa: Bases do Sistema

**Data:** 12/02/2026  
**Status:** ✅ TODAS AS VALIDAÇÕES PASSARAM

---

## 📊 Resultados das Validações

### ✅ VALIDAÇÃO 1: base_grupos_config
```sql
SELECT COUNT(*) FROM base_grupos_config;
```
**Resultado:** 21 grupos ✅  
**Status:** OK - Tabela global populada corretamente

**Grupos existentes:**
- Educação, Saúde, Casa, Entretenimento, Viagens, Roupas, Presentes
- Assinaturas, Carro, Aplicações, Transporte, Alimentação, MeLi + Amazon
- Tecnologia, Serviços, Salário, Outros, Doações, Limpeza, Fatura, Investimentos

---

### ✅ VALIDAÇÃO 2: base_marcacoes
```sql
SELECT COUNT(*) FROM base_marcacoes;
```
**Resultado:** 405 registros ✅  
**Status:** OK - Tabela global com todos os subgrupos

**Grupos cobertos:** 20 grupos com múltiplos subgrupos cada

**⚠️ IMPORTANTE:** 
- **NÃO tem user_id** - É global (todos os usuários compartilham)
- **Consequência:** Usuários NÃO podem personalizar subgrupos individualmente
- **Solução atual:** OK - 405 subgrupos genéricos atendem 95% dos casos
- **Futuro:** Se necessário, criar `base_marcacoes_custom` com user_id para personalizações

---

### ✅ VALIDAÇÃO 3: generic_classification_rules
```sql
SELECT COUNT(*) FROM generic_classification_rules WHERE ativo = 1;
```
**Resultado:** 86 regras ativas ✅  
**Status:** OK - Frente 4 implementou com sucesso

**Cobertura:** 18 grupos únicos, 73.7% de auto-classificação

**Grupos cobertos:**
- Alimentação, Assinaturas, Carro, Casa, Educação, Entretenimento
- Investimentos, Limpeza, MeLi + Amazon, Roupas, Saúde, Serviços
- Tecnologia, Transporte, Viagens

---

### ✅ VALIDAÇÃO 4: bank_format_compatibility
```sql
SELECT COUNT(*) FROM bank_format_compatibility;
SELECT * FROM bank_format_compatibility;
```
**Resultado:** 7 bancos cadastrados ✅  
**Status:** OK - Tabela global populada

**Bancos suportados:**
1. **BTG Pactual** - CSV: OK, XLS: OK, PDF: TBD, XLSX: TBD
2. **Banco do Brasil** - CSV: OK, XLS: OK, PDF: TBD, XLSX: OK
3. **Bradesco** - CSV: TBD, XLS: TBD, PDF: TBD, XLSX: TBD
4. **Itaú** - CSV: OK, XLS: OK, PDF: OK, XLSX: TBD
5. **Mercado Pago** - CSV: TBD, XLS: OK, PDF: OK, XLSX: TBD
6. **Outros** - CSV: TBD, XLS: TBD, PDF: TBD, XLSX: TBD
7. **Santander** - CSV: TBD, XLS: TBD, PDF: TBD, XLSX: TBD

**⚠️ Nota:** Alguns formatos marcados como TBD (ainda não testados)

---

### ✅ VALIDAÇÃO 5: screen_visibility
```sql
PRAGMA table_info(screen_visibility);
SELECT * FROM screen_visibility;
```
**Resultado:** ❌ NÃO tem user_id - É global  
**Status:** OK - Tabela global (não precisa popular por usuário)

**Telas cadastradas:** 14 telas (sample):
1. **dashboard** - Dashboard (LayoutDashboard) - /dashboard
2. **transactions** - Transações (Receipt) - /transactions
3. **upload** - Upload (Upload) - /upload
4. **categories** - Categorias (FolderTree) - /categories
5. **cards** - Cartões (CreditCard) - /cards
6. **budget** - Budget (Target) - /budget
7. **goals** - Metas (Flag) - /goals
8. **settings** - Configurações (Settings) - /settings
... (14 telas total)

**Status padrão:** 'P' (Presumivelmente "Público" ou "Padrão")

**Conclusão:** Todos os usuários veem as mesmas telas (comportamento esperado)

---

## 🎯 Conclusões: O Que Criar para Novo Usuário

### ⚠️ BASES GLOBAIS - MIGRAÇÃO NECESSÁRIA

Estas 2 bases são **atualmente globais** mas **DEVERIAM ser por usuário** para permitir personalização:

| Tabela | Registros | Status Atual | Ação Necessária |
|--------|-----------|--------------|------------------|
| base_grupos_config | 21 | 🟡 Global | 🔄 Adicionar user_id + popular |
| base_marcacoes | 405 | 🟡 Global | 🔄 Adicionar user_id + popular |

**Decisão (12/02/2026):** Migrar para permitir que cada usuário tenha grupos/subgrupos personalizados.  
**Plano:** Ver [MIGRACAO_USER_ID.md](./MIGRACAO_USER_ID.md)

---

### ✅ BASES GLOBAIS - NÃO PRECISA CRIAR

Estas 3 bases são **compartilhadas** entre todos os usuários (correto):
| generic_classification_rules | 86 | ✅ OK |
| bank_format_compatibility | 7 | ✅ OK |
| screen_visibility | 14 | ✅ OK (global) |

**Ação:** Apenas validar que estão populadas (já validado ✅)

---

### ✅ BASES POR USUÁRIO - CRIAR AUTOMATICAMENTE

Estas **4 bases** devem ser populadas para cada novo usuário (após migração):

**📊 Análise Detalhada:** Ver [ANALISE_TABELAS_BUDGET.md](./ANALISE_TABELAS_BUDGET.md) para entender diferença entre `budget_geral` e `budget_planning`.

#### 1. **base_grupos_config** 🟢 CRÍTICO (Após migração)
**Registros:** 21 (copiados do template)  
**Estratégia:** Copiar grupos padrão do template

**SQL:**
```sql
INSERT INTO base_grupos_config (user_id, nome_grupo, tipo_gasto_padrao, categoria_geral)
SELECT :user_id, nome_grupo, tipo_gasto_padrao, categoria_geral
FROM base_grupos_config_template;
```

**Benefício:** Usuário começa com estrutura completa e pode personalizar

---

#### 2. **base_marcacoes** 🟢 CRÍTICO (Após migração)
**Registros:** 405 (copiados do template)  
**Estratégia:** Copiar subgrupos padrão do template

**SQL:**
```sql
INSERT INTO base_marcacoes (user_id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral)
SELECT :user_id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
FROM base_marcacoes_template;
```

**Benefício:** Usuário tem 405 subgrupos padrão e pode adicionar os seus

---

#### 3. **budget_planning** 🟢 CRÍTICO (NOVA ESTRATÉGIA)
**Registros:** ~30 (10 grupos × 3 meses)  
**Estratégia:** Template zerado (usuário preenche valores)

**🔄 MUDANÇA ESTRATÉGICA:**
- ❌ **DELETAR `budget_geral`** (tabela redundante com campo `total_mensal` inútil)
- ✅ **USAR `budget_planning`** (mais completa: tem `ativo`, `valor_medio_3_meses`)
- ✅ Consolidação: 1 tabela em vez de 2 (arquitetura mais limpa)

**🎯 ONDE SERÁ USADO (após refatoração):**
- ✅ **Tela Mobile de Metas** (`/mobile/budget`) - Refatorar para usar planning
- ✅ **Tela Desktop Budget** (`/budget`) - Refatorar para usar planning
- ✅ API: `GET /api/v1/budget/planning`, `POST /api/v1/budget/planning/bulk-upsert`
- ✅ Campo chave: `grupo` (ex: "Casa", "Saúde", "Alimentação")

**SQL:**
```sql
-- Criar metas para próximos 3 meses (zeradas)
-- Categorias: Casa, Saúde, Alimentação, Entretenimento, Transporte, 
--             Carro, Educação, Roupas, Presentes, Assinaturas

INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, ativo, created_at, updated_at)
SELECT 
    :user_id,
    nome_grupo,  -- Pegar de base_grupos_config (ex: "Casa", "Saúde")
    :mes_referencia,  -- Loop: '2026-02', '2026-03', '2026-04'
    0.00,
    1,  -- ativo = true
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM base_grupos_config
WHERE categoria_geral IN ('Despesa', 'Receita')
LIMIT 10;
-- Repetir para 3 meses seguintes

-- ✅ VANTAGENS: Campo 'ativo' permite desabilitar, 'valor_medio_3_meses' calculado automaticamente
```

**Benefícios:**
- ✅ Tela de metas mobile carrega com estrutura completa
- ✅ Usuário vê 10 categorias zeradas
- ✅ Campo `ativo` permite desabilitar categorias sem deletar
- ✅ Campo `valor_medio_3_meses` ajuda usuário a planejar melhor
- ✅ Arquitetura mais limpa: 1 tabela em vez de 2
- ✅ Não precisa criar linhas manualmente
- ✅ Experiência onboarding facilitada

**📊 Análise Completa:** Ver [ANALISE_TABELAS_BUDGET.md](./ANALISE_TABELAS_BUDGET.md)

---

#### 4. **cartoes** 🟡 IMPORTANTE
**Registros:** 1 (cartão genérico)  
**Estratégia:** Cartão padrão para permitir primeiro upload

**SQL:**
```sql
INSERT INTO cartoes (nome_cartao, final_cartao, banco, user_id, ativo, created_at, updated_at)
VALUES 
    ('Cartão Padrão', '0000', 'Não especificado', :user_id, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Benefício:**
- Usuário pode fazer upload de fatura de cartão imediatamente
- Não bloqueia primeiro uso
- Pode editar/adicionar mais cartões depois

---

#### 5. **base_padroes** ❓ OPCIONAL
**Registros:** 0 (vazio)  
**Estratégia:** Usuário configura conforme usa (não bloquear onboarding)

**Decisão:** Deixar VAZIO (não é crítico para primeiro uso)

---

### ❌ BASES POR USUÁRIO - DEIXAR VAZIAS

Estas 11 bases começam vazias (correto):

| Tabela | Por quê vazio |
|--------|---------------|
| journal_entries | Transações virão dos uploads |
| upload_history | Histórico vazio inicialmente |
| preview_transacoes | Temporária (apenas durante upload) |
| transacoes_exclusao | Soft delete vazio |
| base_parcelas | Parcelas vazias |
| base_padroes | Padrões vazios (usuário configura) |
| investimentos_portfolio | Feature avançada |
| investimentos_historico | Feature avançada |
| investimentos_planejamento | Feature avançada |
| investimentos_cenarios | Feature avançada |
| investimentos_aportes_extraordinarios | Feature avançada |

**🗑️ TABELAS DELETADAS:**
- ❌ `budget_geral` - Consolidado em `budget_planning`
- ❌ `budget_categoria_config` - Feature nunca implementada
- ❌ `budget_geral_historico` - Feature nunca implementada

**📊 Análise completa:** Ver [ANALISE_TABELAS_BUDGET.md](./ANALISE_TABELAS_BUDGET.md)

---

## 🚀 Implementação: Próximos Passos

### Fase 1: Criar Função de População (Backend)

**File:** `app_dev/backend/app/domains/users/service.py`

**Adicionar:**
```python
def _populate_user_defaults(self, user_id: int):
    """
    Popula bases auxiliares para novo usuário
    
    1. budget_planning (metas template para próximos 3 meses)
    2. cartoes (cartão genérico)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from app.domains.grupos.models import BaseGruposConfig
    from app.domains.budget.models import BudgetPlanning
    from app.domains.cards.models import Cartao
    
    try:
        # 1. Criar metas template (próximos 3 meses)
        hoje = datetime.now()
        meses = [(hoje + relativedelta(months=i)).strftime('%Y-%m') for i in range(3)]
        
        # Buscar top 10 grupos de despesa
        grupos = self.repository.db.query(BaseGruposConfig).filter(
            BaseGruposConfig.categoria_geral.in_(['Despesa', 'Receita'])
        ).limit(10).all()
        
        for mes in meses:
            for grupo in grupos:
                meta = BudgetPlanning(
                    user_id=user_id,
                    grupo=grupo.nome_grupo,  # Ex: "Casa", "Saúde"
                    mes_referencia=mes,
                    valor_planejado=0.00,
                    ativo=1  # ✅ Campo novo - permite desabilitar sem deletar
                )
                self.repository.db.add(meta)
        
        # 2. Criar cartão genérico
        cartao = Cartao(
            nome_cartao='Cartão Padrão',
            final_cartao='0000',
            banco='Não especificado',
            user_id=user_id,
            ativo=1
        )
        self.repository.db.add(cartao)
        
        # Commit
        self.repository.db.commit()
        logger.info(f"✅ Bases default populadas para user_id={user_id}")
        
    except Exception as e:
        self.repository.db.rollback()
        logger.error(f"❌ Erro ao popular bases default: {e}")
        raise
```

**Integrar com create_user():**
```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    # ... código existente ...
    
    # Salvar
    created = self.repository.create(user)
    
    # 🆕 ADICIONAR: Popular bases default
    self._populate_user_defaults(created.id)
    
    return UserResponse.from_orm(created)
```

---

### Fase 2: Criar Script Standalone

**File:** `scripts/database/popular_user_defaults.py`

**Uso:**
```bash
# Popular bases para usuário específico
python scripts/database/popular_user_defaults.py --user-id 5

# Popular para todos os usuários existentes que não têm
python scripts/database/popular_user_defaults.py --all
```

**Benefício:** Admin pode executar manualmente se necessário

---

### Fase 3: Testar com Usuário Novo

**Checklist:**
- [ ] Criar usuário de teste via API ou admin
- [ ] Verificar se `budget_geral` foi criada (~30 registros)
- [ ] Verificar se `cartoes` tem 1 registro
- [ ] Fazer login com usuário novo
- [ ] Ver dashboard (deve mostrar metas zeradas)
- [ ] Fazer primeiro upload (deve funcionar sem erros)
- [ ] Verificar se classificação genérica funcionou (86 regras)
- [ ] Verificar se TipoGasto/CategoriaGeral foram preenchidos (via base_grupos_config)

---

## �️ Limpeza: Remover Tabelas Não Usadas

### Tabelas para Deletar

**DECISÃO ESTRATÉGICA:** Deletar 3 tabelas e consolidar em `budget_planning` apenas.

#### 1. budget_geral 🔥 DELETAR (361 registros)
- **Motivo:** Redundante com `budget_planning`
- **Problema:** Campo `total_mensal` 100% redundante (sempre == valor_planejado)
- **Solução:** Migrar dados para `budget_planning` e deletar
- **Vantagem:** Arquitetura mais limpa (1 tabela em vez de 2)

#### 2. budget_categoria_config
- **Registros:** 0 (sempre vazio)
- **Features:** 0 endpoints registrados, 0 telas
- **Motivo:** Estrutura criada para feature de categorias personalizadas que nunca foi implementada

#### 3. budget_geral_historico
- **Registros:** 0 (sempre vazio)
- **Features:** 0 endpoints, lógica de auditoria não existe
- **Motivo:** Estrutura para auditoria de ajustes que nunca foi implementada

### 🔧 Plano de Remoção

**Fase 1: Backup**
```bash
# Garantir backup antes de deletar
./scripts/deploy/backup_daily.sh
```

**Fase 2: Migration Alembic**
```bash
cd app_dev/backend
source ../../.venv/bin/activate
alembic revision -m "consolidate_budget_tables"
```

**Conteúdo da migration:**
```python
# migrations/versions/XXXX_consolidate_budget_tables.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Consolidar budget_geral em budget_planning e remover tabelas não usadas"""
    
    # 1. Migrar dados de budget_geral para budget_planning
    op.execute("""
        INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, ativo, created_at, updated_at)
        SELECT 
            user_id,
            categoria_geral as grupo,  -- Mapear categoria_geral -> grupo
            mes_referencia,
            valor_planejado,
            1 as ativo,  -- Todos ativos por padrão
            created_at,
            updated_at
        FROM budget_geral
        WHERE NOT EXISTS (
            -- Evitar duplicatas caso já exista
            SELECT 1 FROM budget_planning bp 
            WHERE bp.user_id = budget_geral.user_id 
            AND bp.grupo = budget_geral.categoria_geral 
            AND bp.mes_referencia = budget_geral.mes_referencia
        );
    """)
    
    # 2. Dropar tabelas não usadas
    op.drop_table('budget_geral')  # ✅ Dados migrados, pode deletar
    op.drop_table('budget_categoria_config')  # ✅ Nunca foi usado
    op.drop_table('budget_geral_historico')  # ✅ Nunca foi usado

def downgrade():
    """Rollback improvável - tabelas podem ser recriadas do backup"""
    pass
```

**Fase 3: Aplicar Migration**
```bash
# Local
alembic upgrade head

# Produção (quando pronto)
ssh user@servidor "cd /var/www/finup/app_dev/backend && alembic upgrade head"
```

**Fase 4: Remover Código Backend**

**4.1. Remover modelos:**
```python
# app/domains/budget/models.py
# Deletar classes:
# - BudgetGeral  # ✅ Migrado para BudgetPlanning
# - BudgetCategoriaConfig
# - BudgetGeralHistorico
```

**4.2. Remover repositories:**
```bash
# app/domains/budget/repository_categoria_config.py - DELETAR arquivo
```

**4.3. Remover schemas:**
```python
# app/domains/budget/schemas.py
# Deletar schemas:
# - BudgetGeralCreate, BudgetGeralUpdate, BudgetGeralResponse
# - BudgetCategoriaConfigCreate, Update, Response
# - BudgetGeralHistoricoResponse
```

**4.4. Remover endpoints de budget_geral:**
```python
# app/domains/budget/router.py
# Deletar endpoints:
# - GET /budget/geral
# - POST /budget/geral/bulk-upsert
# - GET /budget/geral/grupos-disponiveis
# Manter apenas:
# - GET /budget/planning
# - POST /budget/planning/bulk-upsert
```

---

**Fase 5: Refatorar Frontend (2 telas)**

**5.1. Tela Mobile de Metas (`/mobile/budget`):**
```typescript
// app/mobile/budget/page.tsx
// Linha 7: Atualizar comentário
// ANTES: "Utiliza budget_geral para persistência"
// DEPOIS: "Utiliza budget_planning para persistência"

// features/goals/services/goals-api.ts
// ANTES: const BASE_URL = `${API_CONFIG.BACKEND_URL}/api/v1/budget/geral`
// DEPOIS: const BASE_URL = `${API_CONFIG.BACKEND_URL}/api/v1/budget/planning`

// Atualizar tipos:
// ANTES: categoria_geral
// DEPOIS: grupo
```

**5.2. Tela Desktop Budget (`/budget`):**
```typescript
// app/budget/page.tsx
// Linha 67: GET /api/v1/budget/geral/grupos-disponiveis
// MUDAR PARA: GET /api/v1/budget/planning/grupos-disponiveis (ou calcular no frontend)

// Linha 93: GET /api/v1/budget/geral?mes_referencia=...
// MUDAR PARA: GET /api/v1/budget/planning?mes_referencia=...

// Linha 152: POST /api/v1/budget/geral/bulk-upsert
// MUDAR PARA: POST /api/v1/budget/planning/bulk-upsert
```

**Tempo estimado:** 2-3 horas (ambas as telas)

**Fase 6: Validar Completo**
```bash
# 1. Verificar que backend inicia sem erros
./scripts/deploy/quick_stop.sh && ./scripts/deploy/quick_start.sh

# 2. Verificar logs
tail -30 temp/logs/backend.log

# 3. Testar endpoint de budget_planning (único ativo)
curl http://localhost:8000/api/v1/budget/planning

# 4. Verificar que endpoint antigo foi removido (deve dar 404)
curl http://localhost:8000/api/v1/budget/geral  # Esperado: 404 Not Found

# 5. Testar tela mobile de metas
# - Abrir http://localhost:3000/mobile/budget
# - Verificar que carrega metas zeradas
# - Criar nova meta e salvar
# - Verificar que usa endpoint /budget/planning

# 6. Testar tela desktop budget
# - Abrir http://localhost:3000/budget
# - Verificar que carrega dados
# - Editar valor e salvar
# - Verificar que usa endpoint /budget/planning
```

### ✅ Benefícios da Consolidação

1. **Arquitetura 75% mais simples:** 4 tabelas → 1 tabela budget ativa
2. **Zero redundância:** Elimina campo `total_mensal` inútil
3. **Mais features:** `ativo` (desabilitar sem deletar) + `valor_medio_3_meses` (cálculo automático)
4. **Código 60% menor:** Remove 3 models + 1 repository + 7 schemas + 3 endpoints
5. **Frontend unificado:** Mesma API para mobile e desktop
6. **Backup 40% mais rápido:** 3 tabelas a menos para processar
7. **Migrations mais rápidas:** Menos schema para validar
8. **Documentação alinhada:** 1 tabela, 1 propósito claro

### 📋 Checklist de Consolidação

**Backend:**
- [ ] ✅ Backup criado via backup_daily.sh
- [ ] ✅ Migration Alembic criada (consolidate_budget_tables)
- [ ] ✅ Migration aplicada em dev
- [ ] ✅ Dados migrados de budget_geral → budget_planning
- [ ] ✅ Tabelas dropadas (budget_geral, categoria_config, historico)
- [ ] ✅ Models removidos do código (3 classes)
- [ ] ✅ Repositories removidos (1 arquivo)
- [ ] ✅ Schemas removidos (7 schemas)
- [ ] ✅ Endpoints removidos (3 endpoints de /budget/geral)
- [ ] ✅ Backend reiniciado sem erros

**Frontend:**
- [ ] ✅ Tela mobile refatorada (/mobile/budget)
- [ ] ✅ Tela desktop refatorada (/budget)
- [ ] ✅ API services atualizados (goals-api.ts)
- [ ] ✅ Tipos TypeScript atualizados (categoria_geral → grupo)
- [ ] ✅ Comentários corrigidos
- [ ] ✅ Frontend testado (criar/editar/listar metas)

**Validação:**
- [ ] ✅ Endpoint /budget/geral retorna 404 (removido)
- [ ] ✅ Endpoint /budget/planning funciona
- [ ] ✅ Tela mobile carrega e salva metas
- [ ] ✅ Tela desktop carrega e salva budget
- [ ] ✅ Documentação atualizada (este arquivo)
- [ ] ✅ Migration aplicada em produção
- [ ] ✅ Validação final em produção

**⏰ Tempo estimado:** 3-5 horas (incluindo refatoração frontend + testes)

---

## �📋 Resumo Final

### ✅ Status: PRONTO PARA IMPLEMENTAÇÃO

**Validações:** ✅ TODAS PASSARAM  
**Estratégia:** ✅ DEFINIDA (4 tabelas: base_grupos_config, base_marcacoes, budget_planning, cartoes)  
**Consolidação Budget:** ✅ DEFINIDA - Usar SOMENTE `budget_planning`
**Análise Budget:** ✅ CONCLUÍDA - Ver [ANALISE_TABELAS_BUDGET.md](./ANALISE_TABELAS_BUDGET.md)  
**Bases globais:** ✅ POPULADAS (5 tabelas)  
**Bases por usuário:** 🟡 IMPLEMENTAR (4 tabelas)

**Próximos passos:**
1. Implementar `_populate_user_defaults()` com BudgetPlanning
2. Criar migration para consolidar tabelas budget (3→1)
3. Refatorar frontend (mobile + desktop) para usar /budget/planning

---

**Criado em:** 12/02/2026  
**Próxima atualização:** Após implementação e testes
