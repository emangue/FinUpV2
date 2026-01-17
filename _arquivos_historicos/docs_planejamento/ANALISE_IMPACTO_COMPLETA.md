# 📊 ANÁLISE DE IMPACTO COMPLETA - Refatoração de Categorias

**Data:** 14/01/2026  
**Escopo:** Alteração de TipoGasto (22→5 valores) + Criação de base_grupos_config

---

## 🎯 RESUMO EXECUTIVO

### Mudanças Principais

1. **TipoGasto:** 22 valores → 5 valores (Fixo, Ajustável, Investimentos, Transferência, Receita)
2. **base_grupos_config:** Nova tabela (3 colunas: nome_grupo, tipo_gasto_padrao, categoria_geral)
3. **Lógica:** GRUPO passa a ser fonte da verdade → base_grupos_config determina TipoGasto

### Tabelas Afetadas no Banco

| Tabela | Campo Impactado | Tipo de Mudança | Criticidade |
|--------|-----------------|-----------------|-------------|
| `journal_entries` | `TipoGasto` | Migrar 22→5 valores | 🔴 CRÍTICA |
| `base_padroes` | `tipo_gasto_sugerido` | Regenerar pós-migração | 🟡 ALTA |
| `base_parcelas` | `tipo_gasto_sugerido` | Adicionar `categoria_geral` | 🟡 ALTA |
| `budget_planning` | `tipo_gasto` | Migrar 22→5 valores | 🟠 MÉDIA |
| `base_grupos_config` | - | **CRIAR nova tabela** | 🟢 NOVA |

---

## 📁 ARQUIVOS IMPACTADOS POR CATEGORIA

### 🔴 BACKEND - Modelos e Schema (10 arquivos)

**Modelos SQLAlchemy:**
1. `app/domains/transactions/models.py` - **JournalEntry.TipoGasto** (campo principal)
2. `app/domains/patterns/models.py` - **BasePadroes.tipo_gasto_sugerido**
3. `app/domains/transactions/models.py` - **BaseParcelas.tipo_gasto_sugerido**
4. `app/domains/budget/models.py` - **BudgetPlanning.tipo_gasto**
5. `app/domains/budget/models.py` - **BudgetCategoriaConfig.tipos_gasto_incluidos** (JSON array)

**Schemas Pydantic:**
6. `app/domains/transactions/schemas.py` - **TransactionCreate.TipoGasto**, **TransactionUpdate.TipoGasto**, **TransactionFilter.tipo_gasto**
7. `app/domains/upload/schemas.py` - **UploadPreviewItem.TipoGasto**
8. `app/domains/budget/schemas.py` - **BudgetCreate.tipo_gasto**, **BudgetResponse.tipo_gasto**, **TipoGastoComMedia**

**⚠️ AÇÃO:** Nenhuma mudança estrutural necessária (campos já existem), mas valores permitidos serão validados.

---

### 🔴 BACKEND - Repositories (8 arquivos)

**Filtros de TipoGasto:**
1. `app/domains/transactions/repository.py`
   - `get_transactions()` - linhas 68-72
   - `get_totais_por_dia()` - linhas 114-118
   - `get_transacoes_paginadas()` - linhas 168-172
   - ✅ **Já suporta lista de TipoGasto** (usa `.in_()` e aceita array)

2. `app/domains/budget/repository.py`
   - `get_by_tipo_gasto_and_month()` - linha 47
   - `upsert()` - linha 96
   - ✅ **Compatível** - só precisa valores migrados

3. `app/domains/categories/repository.py`
   - `get_subgrupos_por_tipo()` - linha 47
   - `get_tipo_gasto_de_grupo()` - linha 69
   - ⚠️ **CRÍTICO:** Retorna TipoGasto de base_marcacoes → deve buscar de base_grupos_config

**⚠️ AÇÃO:** Criar novo método `get_tipo_gasto_from_config(grupo)` que busca em base_grupos_config.

---

### 🔴 BACKEND - Services (5 arquivos)

1. `app/domains/transactions/service.py`
   - `update_transaction()` - linhas 133-141: Busca TipoGasto de base_marcacoes quando GRUPO/SUBGRUPO mudam
   - `_buscar_tipo_gasto_base_marcacoes()` - linhas 153-198: **MÉTODO INTEIRO DEVE SER SUBSTITUÍDO**
   - `get_tipos_gasto_com_medias()` - linhas 298-324: Retorna lista de TipoGasto únicos
   - ⚠️ **CRÍTICO:** Substituir lógica por busca em base_grupos_config

2. `app/domains/budget/service.py`
   - `get_totais_dashboard()` - linhas 65, 145: Filtra por `CategoriaGeral = 'Despesa'`
   - ✅ **Compatível** - CategoriaGeral não muda

3. `app/domains/upload/service.py`
   - `create_preview_items()` - linha 450, 561: Define CategoriaGeral
   - `confirm_upload()` - linha 728: Persiste CategoriaGeral
   - ✅ **Compatível** - CategoriaGeral já existe

**⚠️ AÇÃO:**
- Criar helper `determinar_tipo_gasto_via_config(session, grupo)` 
- Substituir `_buscar_tipo_gasto_base_marcacoes()` por novo helper

---

### 🔴 BACKEND - Classificadores (4 arquivos)

1. `app/domains/upload/processors/classifier.py` (PRINCIPAL)
   - `_determine_categoria_geral()` - linha 55: Lógica de CategoriaGeral baseada em GRUPO
   - `_classify_nivel1_parcelas()` - linha 221: Usa `parcela.tipo_gasto_sugerido`
   - `_classify_nivel2_padroes()` - linha 278: Usa `padrao.tipo_gasto_sugerido`
   - `_classify_nivel3_historico()` - linha 368: Copia TipoGasto de transação histórica
   - ⚠️ **CRÍTICO:** Níveis 1, 2, 3 usarão valores simplificados (5 em vez de 22)

2. `app/domains/upload/processors/generic_rules_classifier.py`
   - 39 regras hardcoded com `tipo_gasto` específico (ex: "Ajustável - Viagens", "Fixo")
   - ⚠️ **CRÍTICO:** Substituir todos os valores antigos por novos 5 valores
   - Exemplo: "Ajustável - Viagens" → "Ajustável", "Fixo" → "Fixo"

**⚠️ AÇÃO:**
- Atualizar 39 regras em generic_rules_classifier.py
- Garantir que _determine_categoria_geral() funcione com novo base_grupos_config

---

### 🔴 BACKEND - Scripts de Migração (6 arquivos)

1. `scripts/populate_budget_example.py`
   - Linhas 18-31: Cria exemplos com TipoGasto antigos ("Ajustável - Viagens", "Ajustável - Casa")
   - ⚠️ **ATUALIZAR** com novos 5 valores

2. `scripts/popular_medias_historico.py`
   - Linhas 64-69: `SELECT DISTINCT TipoGasto FROM journal_entries WHERE CategoriaGeral = 'Despesa'`
   - ✅ **Compatível** - funcionará com valores simplificados

3. `scripts/migrate_add_budget_planning.py`
   - Linha 49: Define `tipo_gasto VARCHAR(50)`
   - ✅ **Compatível** - estrutura não muda

4. `scripts/migrate_preview_add_all_fields.py`
   - Linhas 46-47: Define `tipo_gasto`, `categoria_geral`
   - ✅ **Compatível**

5. `regenerate_sql.py` (RAIZ)
   - ⚠️ **CRÍTICO:** Regenera base_padroes → deve usar novo base_grupos_config
   - Necessita atualização similar ao pattern_generator.py

**⚠️ AÇÃO:**
- Atualizar populate_budget_example.py
- Garantir regenerate_sql.py use base_grupos_config

---

### 🟡 BACKEND - Scripts de Debug/Validação (5 arquivos)

1. `analise_categoria_geral.py`
2. `debug_dashboard.py`
3. `teste_switch_completo.py`
4. `test_ignorar_dashboard.py`
5. `validar_configuracoes.py`

✅ **Compatível** - Scripts de análise funcionam com qualquer valor de TipoGasto.

---

### 🟡 FRONTEND - Types (2 arquivos)

1. `frontend/src/features/categories/types/index.ts`
   ```typescript
   TipoGasto: string  // Linha 5, 11
   ```

2. `frontend/src/core/types/shared.types.ts`
   ```typescript
   TIPOGASTO?: string;  // Linha 49
   TIPOGASTO: string;   // Linha 57
   ```

✅ **Compatível** - Types são strings genéricas, não enums.

---

### 🟡 FRONTEND - Componentes de Transações (5 arquivos)

1. `features/transactions/components/edit-transaction-modal.tsx`
   - Linha 33: `TipoGasto: string`
   - Linha 183: Display read-only de TipoGasto
   - ✅ **Compatível** - só exibe valor

2. `features/transactions/components/transaction-filters.tsx`
   - Linhas 176-179: Filtro select para TipoGasto
   - ⚠️ **ATUALIZAR:** Options do select para mostrar apenas 5 valores

3. `app/transactions/page.tsx`
   - Linhas 96-97, 174-177, 228-231: Constrói query params `tipo_gasto`
   - Linha 496: Display de `transaction.TipoGasto`
   - ✅ **Compatível** - aceita array de valores

**⚠️ AÇÃO:** Atualizar options do filtro para mostrar apenas 5 valores.

---

### 🟡 FRONTEND - Componentes de Dashboard (4 arquivos)

1. `features/dashboard/components/tipo-gasto-breakdown-modal.tsx`
   - Linhas 22-42: Modal de detalhamento por TipoGasto
   - Linha 57-58: Endpoint `/api/dashboard/subgrupos-by-tipo?tipo_gasto=X`
   - ✅ **Compatível** - funcionará com valores simplificados

2. `features/dashboard/components/budget-vs-actual.tsx`
   - Linha 190: Filtra por `item.tipo_gasto`
   - ✅ **Compatível**

3. `features/dashboard/components/demais-breakdown-modal.tsx`
   - Linhas 15-26: Exibe lista de TipoGastoItem
   - ✅ **Compatível**

**Nenhuma ação necessária** - Componentes adaptam automaticamente aos novos valores.

---

### 🟡 FRONTEND - Upload/Confirmação (3 arquivos)

1. `app/upload/confirm-ai/page.tsx`
   - Linhas 54, 95, 189, 233: Usa `tipoGasto` field
   - Linhas 667-671: Input para editar TipoGasto
   - ⚠️ **ATUALIZAR:** Options do input para 5 valores

2. `app/upload/confirm/page.tsx`
   - Linhas 59, 99, 155, 191: Usa `TipoGasto` field
   - Linhas 548-552: Input para editar TipoGasto
   - ⚠️ **ATUALIZAR:** Options do input para 5 valores

3. `app/upload/preview/[sessionId]/page.tsx`
   - Linha 47: `tipo_gasto?: string`
   - ✅ **Compatível**

**⚠️ AÇÃO:** Substituir options de inputs por select com 5 valores fixos.

---

### 🟡 FRONTEND - Budget (2 arquivos)

1. `app/budget/simples/page.tsx`
   - Linhas 21, 28: Types `tipo_gasto: string` e `[tipo_gasto: string]: number`
   - Linhas 94-95, 127-128: Mapeia por `tipo_gasto`
   - Linha 466: Passa `tipoGasto` para modal
   - ✅ **Compatível** - Carrega dinamicamente de API

2. `features/budget/components/budget-media-drilldown-modal.tsx`
   - Linha 77: Query param `tipo_gasto`
   - ✅ **Compatível**

**Nenhuma ação necessária** - Carregamento dinâmico.

---

### 🟡 FRONTEND - Settings (1 arquivo)

1. `app/settings/categorias/page.tsx`
   - Linha 31: `handleSave({GRUPO, SUBGRUPO, TipoGasto})`
   - ⚠️ **ATUALIZAR:** Form deve usar select com 5 valores

**⚠️ AÇÃO:** Garantir que form de edição use novo base_grupos_config.

---

## 🎯 ARQUIVOS QUE **NÃO** PRECISAM MUDAR

### ✅ Dashboard (usa CategoriaGeral, não TipoGasto diretamente)
- `app/domains/dashboard/repository.py` - Filtra por CategoriaGeral='Despesa'/'Receita'

### ✅ Upload Models
- `app/domains/upload/models.py` - Campos já existem

### ✅ Scripts de debug
- Todos os 5 arquivos de teste/validação

---

## 📊 MATRIZ DE IMPACTO

| Componente | Impacto | Esforço | Dependência |
|------------|---------|---------|-------------|
| **base_grupos_config** | 🟢 Criação | Baixo | Nenhuma |
| **Migração journal_entries** | 🔴 Alto | Médio | base_grupos_config criada |
| **Migração budget_planning** | 🟠 Médio | Baixo | base_grupos_config criada |
| **Regeneração base_padroes** | 🔴 Alto | Alto | Todas migrações concluídas |
| **Atualizar generic_rules** | 🟠 Médio | Médio | base_grupos_config criada |
| **Helper determinar_tipo_gasto** | 🔴 Alto | Médio | base_grupos_config criada |
| **Frontend - Filtros** | 🟡 Baixo | Baixo | Backend migrado |
| **Frontend - Upload** | 🟡 Baixo | Baixo | Backend migrado |

---

## 🚨 PONTOS CRÍTICOS DESCOBERTOS

### 1. **base_grupos_config NÃO EXISTE AINDA**
   - ❌ Nenhum arquivo referencia esta tabela
   - ✅ Precisa ser criada ANTES de qualquer migração
   - ✅ Precisa ser populada com 16 grupos

### 2. **generic_rules_classifier.py usa valores hardcoded**
   - 39 regras com TipoGasto antigos
   - Necessita atualização manual linha a linha

### 3. **TransactionService._buscar_tipo_gasto_base_marcacoes() será obsoleto**
   - Método inteiro de 45 linhas (153-198) deve ser substituído
   - Novo helper será 5 linhas: busca em base_grupos_config

### 4. **base_padroes NÃO tem gerador ativo em app_dev**
   - ✅ Localizado APENAS em `_arquivos_historicos/codigos_apoio/pattern_generator.py`
   - ✅ **CONFIRMADO:** NÃO é usado (nenhuma referência em app_dev)
   - ✅ base_padroes é APENAS **LIDA** pelo classifier (Nível 2)
   - ❌ NENHUM processo automatizado popula base_padroes atualmente
   - 💡 **AÇÃO:** Criar novo script de regeneração OU adaptar o histórico

### 5. **Frontend carrega TipoGasto dinamicamente**
   - Budget page faz `GET /api/transactions/tipos-gasto-com-medias`
   - Adaptará automaticamente aos 5 novos valores
   - ✅ **Sem risco de quebra**

---

## 📝 CHECKLIST DE REVISÃO

### Backend
- [x] Models/Schemas - Estrutura compatível
- [x] Repositories - Métodos suportam novos valores
- [x] Services - Identificado método crítico para substituir
- [x] Classifiers - 39 regras identificadas para atualizar
- [x] Scripts migração - 2 arquivos precisam atualização

### Frontend
- [x] Types - Strings genéricas (sem enum)
- [x] Transaction components - 1 filtro precisa options
- [x] Dashboard - Componentes adaptativos
- [x] Upload - 2 inputs precisam options fixos
- [x] Budget - Carregamento dinâmico (OK)
- [x] Settings - Form precisa usar base_grupos_config

### Database
- [ ] base_grupos_config - **CRIAR**
- [ ] Seed data 16 grupos - **POPULAR**
- [ ] Migration journal_entries - **EXECUTAR**
- [ ] Migration budget_planning - **EXECUTAR**
- [ ] Regenerar base_padroes - **EXECUTAR**

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ **Análise completa concluída**
2. ⏳ **Reorganizar plano em etapas incrementais** (próximo passo)
3. ⏳ Criar base_grupos_config
4. ⏳ Criar helper determinar_tipo_gasto_via_config()
5. ⏳ Migrar dados
6. ⏳ Testar e validar

---

**Total de arquivos identificados: 62 arquivos**
- Backend: 33 arquivos
- Frontend: 29 arquivos
- Base de dados: 5 tabelas

**Arquivos críticos (requerem mudança): 18 arquivos**
**Arquivos compatíveis (sem mudança): 44 arquivos**
