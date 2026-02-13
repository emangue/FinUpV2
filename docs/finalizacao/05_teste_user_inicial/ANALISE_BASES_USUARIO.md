# 🔍 Análise Completa: Bases de Dados e Estratégia de Auto-Criação

**Data:** 12/02/2026  
**Objetivo:** Entender exatamente quais bases têm user_id, como funcionam, e o que deve ser criado para novo usuário

---

## 🗄️ MAPEAMENTO COMPLETO DAS 24 TABELAS

### 🟢 TABELAS COM user_id (Dados por Usuário)

#### ✅ Obrigatórias - TEM user_id
1. **journal_entries** - Transações financeiras do usuário
2. **upload_history** - Histórico de uploads do usuário
3. **budget_geral** - Metas por grupo/mês do usuário
4. **budget_geral_historico** - Histórico de metas do usuário
5. **budget_categoria_config** - Config de categorias do budget (usuário)
6. **budget_planning** - Planejamento de budget do usuário
7. **cartoes** - Cartões de crédito do usuário
8. **base_padroes** - Padrões de estabelecimentos do usuário
9. **base_parcelas** - Parcelas do usuário
10. **preview_transacoes** - Preview temporário durante upload (usuário)
11. **transacoes_exclusao** - Transações excluídas do usuário (soft delete)
12. **investimentos_portfolio** - Carteira de investimentos do usuário
13. **investimentos_historico** - Histórico de transações de investimentos
14. **investimentos_planejamento** - Planejamento de aportes do usuário
15. **investimentos_cenarios** - Cenários de simulação do usuário
16. **investimentos_aportes_extraordinarios** - Aportes extras do usuário

#### 📊 Total: 16 tabelas COM user_id

---

### 🔵 TABELAS SEM user_id (Dados Globais/Sistema)

#### ✅ Correto - NÃO precisam de user_id
1. **users** - Tabela de usuários (não tem user_id próprio, é a fonte!)
2. **base_grupos_config** - Config GLOBAL de grupos (21 grupos padrão)
3. **base_marcacoes** - Grupos/subgrupos GLOBAIS (405 registros)
4. **generic_classification_rules** - Regras genéricas GLOBAIS (86 regras)
5. **bank_format_compatibility** - Formatos de banco GLOBAIS
6. **screen_visibility** - Visibilidade de telas (global ou deveria ter user_id?)
7. **alembic_version** - Controle de migrations (sistema)

#### 📊 Total: 7 tabelas SEM user_id

---

## 🎯 DESCOBERTA CRÍTICA: Como TipoGasto e CategoriaGeral Funcionam

### Fluxo Atual de Classificação

**1. Usuário classifica transação** (escolhe GRUPO + SUBGRUPO)

**2. Sistema busca TipoGasto e CategoriaGeral:**

**Fonte PRIMÁRIA:** `base_grupos_config` (tabela global, 21 grupos)

```python
# app/domains/transactions/service.py - update_transaction()
from app.domains.grupos.models import BaseGruposConfig
grupo_config = self.repository.db.query(BaseGruposConfig).filter(
    BaseGruposConfig.nome_grupo == transaction.GRUPO
).first()

if grupo_config:
    transaction.TipoGasto = grupo_config.tipo_gasto_padrao
    transaction.CategoriaGeral = grupo_config.categoria_geral
```

**Exemplo:**
- Usuário escolhe: GRUPO="Casa", SUBGRUPO="Aluguel"
- Sistema busca em `base_grupos_config`: 
  - `Casa` → `tipo_gasto_padrao="Ajustável"`, `categoria_geral="Despesa"`
- Salva em `journal_entries`: 
  - `TipoGasto="Ajustável"`, `CategoriaGeral="Despesa"`

**⚠️ IMPORTANTE:** `base_marcacoes` (405 registros) NÃO É USADA para TipoGasto/CategoriaGeral!

**Função de `base_marcacoes`:**
- Lista de **SUBGRUPOS disponíveis** para cada GRUPO
- Usada apenas para popular **dropdowns** no frontend
- **NÃO** é consultada para determinar TipoGasto/CategoriaGeral

---

### 📊 Dados Atuais: base_grupos_config (21 grupos)

```sql
SELECT nome_grupo, tipo_gasto_padrao, categoria_geral FROM base_grupos_config;
```

| nome_grupo | tipo_gasto_padrao | categoria_geral |
|-----------|-------------------|-----------------|
| Educação | Fixo | Despesa |
| Saúde | Fixo | Despesa |
| Casa | Ajustável | Despesa |
| Entretenimento | Ajustável | Despesa |
| Viagens | Ajustável | Despesa |
| Roupas | Ajustável | Despesa |
| Presentes | Ajustável | Despesa |
| Assinaturas | Ajustável | Despesa |
| Carro | Ajustável | Despesa |
| Aplicações | Investimentos | Investimentos |
| ... | ... | ... |

**Total:** 21 grupos oficiais

---

### 📊 Dados Atuais: base_marcacoes (405 registros)

```sql
SELECT DISTINCT GRUPO FROM base_marcacoes ORDER BY GRUPO;
```

| GRUPO |
|-------|
| Alimentação |
| Assinaturas |
| Carro |
| Casa |
| Doações |
| Educação |
| Entretenimento |
| Fatura |
| Investimentos |
| MeLi + Amazon |
| Outros |
| Presentes |
| Roupas |
| Salário |
| Saúde |
| Serviços |
| Tecnologia |
| Transferência Entre Contas |
| Transporte |
| Viagens |

**Total:** 20 grupos, 405 combinações (GRUPO + SUBGRUPO)

**Exemplo de subgrupos:**
- Alimentação: Almoço, Café da Manhã, Comida Congelada, Ovos, Pedidos para casa, Saídas, Supermercado, Água
- Assinaturas: Amazon, Amazon Prime, Anuidade, Apple, Audible, CONECTCAR, ConectCar, ...

---

### 📊 Dados Atuais: generic_classification_rules (86 regras)

```sql
SELECT DISTINCT grupo, tipo_gasto FROM generic_classification_rules ORDER BY grupo;
```

| grupo | tipo_gasto |
|-------|------------|
| Alimentação | Ajustável |
| Assinaturas | Ajustável |
| Carro | Ajustável |
| Casa | Ajustável |
| Casa | Despesa |
| Educação | Fixo |
| Entretenimento | Ajustável |
| Entretenimento | Despesa |
| Investimentos | Investimentos |
| Limpeza | Fixo |
| MeLi + Amazon | Ajustável |
| Roupas | Ajustável |
| Saúde | Fixo |
| Saúde | Despesa |
| Serviços | Ajustável |
| Tecnologia | Ajustável |
| Transporte | Ajustável |
| Viagens | Ajustável |
| Viagens | Viagens |

**Total:** 18 grupos únicos cobertos por regras genéricas

---

## 🎯 PROPOSTA CORRIGIDA: O Que Criar para Novo Usuário?

### ✅ CRIAR AUTOMATICAMENTE

#### 1. **budget_geral** - Metas Template 🟡 IMPORTANTE

**Por quê:** Facilita onboarding - usuário vê estrutura e só ajusta valores

**Estratégia:** Template zerado baseado em `base_grupos_config`

**SQL:**
```sql
-- Criar metas para próximos 3 meses (fev, mar, abr 2026)
-- Apenas grupos principais (excluir "Aplicações", "Fatura", etc)
INSERT INTO budget_geral (user_id, categoria_geral, mes_referencia, valor_planejado, total_mensal, created_at, updated_at)
SELECT 
    :new_user_id,
    categoria_geral,
    :mes_referencia,  -- Loop: '2026-02', '2026-03', '2026-04'
    0.00,             -- Usuário preenche depois
    0.00,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM base_grupos_config
WHERE categoria_geral IN ('Despesa', 'Receita')  -- Excluir Investimentos inicialmente
ORDER BY nome_grupo;
```

**Resultado:** ~30 registros (10 grupos × 3 meses)

**Benefício:**
- Usuário vê estrutura completa de metas
- Não precisa criar linhas manualmente
- Apenas preenche valores (experiência simples)

---

#### 2. **cartoes** - Cartão Genérico 🟡 IMPORTANTE

**Por quê:** Muitos uploads são de cartão de crédito - não bloquear primeiro upload

**SQL:**
```sql
INSERT INTO cartoes (nome_cartao, final_cartao, banco, user_id, ativo, created_at, updated_at)
VALUES 
    ('Cartão Padrão', '0000', 'Não especificado', :new_user_id, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Resultado:** 1 cartão genérico criado

**Benefício:** 
- Usuário pode fazer upload de fatura imediatamente
- Pode editar/adicionar mais cartões depois

---

#### 3. **base_padroes** - Padrões Pessoais ❓ AVALIAR

**Análise necessária:**
- Ver o que é `base_padroes` (padrões de estabelecimentos?)
- Se for para mapear "Estabelecimento X → Grupo Y", CRIAR VAZIO
- Usuário configura conforme usa

**Decisão:** Deixar VAZIO (usuário configura gradualmente)

---

### ❌ NÃO CRIAR (Deixar Vazio)

#### 1. **journal_entries** ❌
**Por quê:** Usuário ainda não tem transações (popular no primeiro upload)

#### 2. **upload_history** ❌
**Por quê:** Histórico vazio (criado no primeiro upload)

#### 3. **preview_transacoes** ❌
**Por quê:** Tabela temporária (apenas durante upload)

#### 4. **transacoes_exclusao** ❌
**Por quê:** Soft delete vazio inicialmente

#### 5. **budget_geral_historico** ❌
**Por quê:** Histórico vazio (criado quando houver mudanças)

#### 6. **budget_categoria_config** ❌
**Por quê:** Config vazia (usuário personaliza depois)

#### 7. **budget_planning** ❌
**Por quê:** Planejamento vazio (feature avançada)

#### 8. **investimentos_*** ❌
**Por quê:** Feature avançada - usuário configura quando começar a usar

#### 9. **base_parcelas** ❌
**Por quê:** Parcelas vazias (criadas durante uploads)

---

### 🔵 NÃO CRIAR (Já são Globais - Sem user_id)

#### 1. **base_grupos_config** ✅ JÁ EXISTE
**Status:** 21 grupos padrão já populados (tabela global)

**Ação:** Apenas **validar** que está populada

**Validação:**
```sql
SELECT COUNT(*) FROM base_grupos_config;
-- Esperado: 21 registros
```

---

#### 2. **base_marcacoes** ⚠️ PROBLEMA DETECTADO!

**Status Atual:** 405 registros GLOBAIS (sem user_id)

**Problema:** Todos os usuários compartilham os mesmos 405 subgrupos!

**Consequências:**
- ✅ **Vantagem:** Consistência entre usuários
- ✅ **Vantagem:** Não precisa popular para cada usuário
- ⚠️ **Desvantagem:** Usuário NÃO PODE personalizar subgrupos
- ⚠️ **Desvantagem:** Admin A adiciona subgrupo "X" → aparece para TODOS os usuários

**Análise:**
```sql
-- Verificar se base_marcacoes tem user_id
PRAGMA table_info(base_marcacoes);
-- Resultado: ❌ SEM user_id
```

**❓ DECISÃO NECESSÁRIA:**

**Opção A: Manter Global (Status Quo)**
- ✅ Simples
- ✅ Não precisa popular
- ⚠️ Usuários não podem personalizar

**Opção B: Adicionar user_id (Migração Complexa)**
- ✅ Cada usuário tem seus subgrupos
- ✅ Personalização total
- ❌ Complexo (migração + popular para cada usuário)
- ❌ Aumenta banco (405 registros × N usuários)

**🎯 RECOMENDAÇÃO:** Opção A (manter global) **MAS** documentar limitação

**Justificativa:**
- 405 subgrupos genéricos atendem 95% dos casos
- Usuário pode "ignorar" subgrupos que não usa (não aparecem nos dropdowns se não houver transações)
- Economiza complexidade
- Se futuro: adicionar tabela `base_marcacoes_custom` (user_id) para personalizações

---

#### 3. **generic_classification_rules** ✅ JÁ EXISTE
**Status:** 86 regras já populadas (Frente 4 implementou)

**Ação:** Apenas **validar** que está ativa

**Validação:**
```sql
SELECT COUNT(*) FROM generic_classification_rules WHERE ativo = 1;
-- Esperado: 86 regras
```

---

#### 4. **bank_format_compatibility** ❓ VALIDAR

**Ação necessária:**
```sql
SELECT * FROM bank_format_compatibility;
```

**Se vazio:** Popular com formatos suportados (Itaú, Nubank, MercadoPago, etc)

---

#### 5. **screen_visibility** ❓ VALIDAR

**Análise necessária:**
```sql
SELECT * FROM screen_visibility LIMIT 10;
PRAGMA table_info(screen_visibility);
```

**Se tem user_id:** Popular com valores default (todas as telas visíveis)  
**Se não tem user_id:** Deixar global

---

## 📋 CHECKLIST: Validações Necessárias

### Validar Bases Sistema (Globais)

- [ ] **base_grupos_config:** Tem 21 grupos?
  ```sql
  SELECT COUNT(*) FROM base_grupos_config;
  ```

- [ ] **base_marcacoes:** Tem 405 registros? Documentar que é global
  ```sql
  SELECT COUNT(*) FROM base_marcacoes;
  ```

- [ ] **generic_classification_rules:** Tem 86 regras ativas?
  ```sql
  SELECT COUNT(*) FROM generic_classification_rules WHERE ativo = 1;
  ```

- [ ] **bank_format_compatibility:** Está populada?
  ```sql
  SELECT COUNT(*) FROM bank_format_compatibility;
  ```

- [ ] **screen_visibility:** Tem user_id? Precisa popular?
  ```sql
  PRAGMA table_info(screen_visibility);
  SELECT * FROM screen_visibility LIMIT 5;
  ```

---

### Implementar População Automática

- [ ] Criar função `_populate_user_defaults(user_id)` em `UserService`
- [ ] Implementar `popular_metas_template(user_id)` - budget_geral
- [ ] Implementar `popular_cartao_generico(user_id)` - cartoes
- [ ] Integrar com `create_user()` (chamar automático após criar user)
- [ ] Testar com usuário novo

---

## 🎯 PROPOSTA FINAL: Dados para Usuário Novo

### ✅ AUTO-CRIAR (3 tabelas)

| Tabela | Registros | Estratégia |
|--------|----------|------------|
| **budget_geral** | ~30 | Template zerado (3 meses, 10 grupos) |
| **cartoes** | 1 | Cartão genérico padrão |
| **base_padroes** | 0 | Vazio (usuário configura) |

### 🔵 VALIDAR (5 tabelas globais)

| Tabela | Status | Ação |
|--------|--------|------|
| **base_grupos_config** | ✅ 21 grupos | Apenas validar |
| **base_marcacoes** | ⚠️ 405 global | Documentar limitação |
| **generic_classification_rules** | ✅ 86 regras | Apenas validar |
| **bank_format_compatibility** | ❓ | Validar se populada |
| **screen_visibility** | ❓ | Validar schema/dados |

### ❌ DEIXAR VAZIO (11 tabelas)

- journal_entries (transações virão dos uploads)
- upload_history (histórico vazio)
- preview_transacoes (temporária)
- transacoes_exclusao (soft delete vazio)
- budget_geral_historico (histórico vazio)
- budget_categoria_config (config vazia)
- budget_planning (planejamento vazio)
- base_parcelas (parcelas vazias)
- investimentos_* (5 tabelas - feature avançada)

---

## 🚀 Próximos Passos

1. **Executar validações** (checklist acima)
2. **Implementar `_populate_user_defaults()`** no backend
3. **Criar usuário de teste** e validar
4. **Fazer primeiro upload** e verificar:
   - Classificação genérica funcionou? (86 regras)
   - Grupos/subgrupos disponíveis? (base_marcacoes)
   - TipoGasto/CategoriaGeral corretos? (base_grupos_config)
5. **Documentar** experiência first-time user
6. **Decidir** sobre tela de auto-cadastro (signup)

---

**Status:** 🟡 Análise completa - Aguardando validações  
**Próximo:** Executar checklist de validações
