# 🗄️ Mapeamento de Bases e Dados Default - Usuário Novo

**Data:** 12/02/2026  
**Objetivo:** Mapear todas as bases e definir o que deve ser criado automaticamente para novo usuário

---

## 📊 Tabelas do Sistema (24 tabelas)

### ✅ VALIDAÇÕES REALIZADAS: Ver [VALIDACOES_COMPLETAS.md](./VALIDACOES_COMPLETAS.md)

### 🔵 TABELAS GLOBAIS (7 - Sem user_id)
1. **users** - Tabela de usuários (é a fonte!)
2. **base_grupos_config** - ✅ 21 grupos padrão
3. **base_marcacoes** - ✅ 405 registros (grupos/subgrupos globais)
4. **generic_classification_rules** - ✅ 86 regras ativas
5. **bank_format_compatibility** - ✅ 7 bancos cadastrados
6. **screen_visibility** - ✅ 14 telas cadastradas
7. **alembic_version** - Controle de migrations

### 🟢 TABELAS POR USUÁRIO (16 - Com user_id)
8. **journal_entries** - Transações financeiras
9. **upload_history** - Histórico de uploads
10. **budget_geral** - 🎯 CRIAR: Metas por grupo/mês
11. **budget_geral_historico** - Histórico de metas
12. **budget_categoria_config** - Config de categorias do budget
13. **budget_planning** - Planejamento de budget
14. **cartoes** - 🎯 CRIAR: Cartões de crédito
15. **base_padroes** - Padrões de estabelecimentos
16. **base_parcelas** - Parcelas
17. **preview_transacoes** - Preview temporário durante upload
18. **transacoes_exclusao** - Transações excluídas (soft delete)
19. **investimentos_portfolio** - Carteira de investimentos
20. **investimentos_historico** - Histórico de transações
21. **investimentos_planejamento** - Planejamento de aportes
22. **investimentos_cenarios** - Cenários de simulação
23. **investimentos_aportes_extraordinarios** - Aportes extras

**🎯 CRIAR AUTOMATICAMENTE:** Apenas 2 tabelas (#10 budget_geral, #14 cartoes)

---

## 🎯 DESCOBERTA CRÍTICA: base_marcacoes É GLOBAL!

### ⚠️ IMPORTANTE: base_marcacoes NÃO tem user_id

**Status:** ✅ É tabela GLOBAL (405 registros compartilhados)  
**Consequência:** Todos os usuários veem os mesmos grupos/subgrupos

**Validação:**
```sql
PRAGMA table_info(base_marcacoes);
-- Resultado: ❌ SEM user_id (colunas: id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral)

SELECT COUNT(*) FROM base_marcacoes;
-- Resultado: 405 registros
```

**Implicações:**
- ✅ **Vantagem:** Consistência entre usuários (todos veem os mesmos subgrupos)
- ✅ **Vantagem:** Não precisa popular para cada novo usuário
- ⚠️ **Limitação:** Usuário NÃO PODE personalizar subgrupos individualmente
- ⚠️ **Limitação:** Admin adiciona subgrupo → aparece para TODOS

**Decisão:** ✅ MANTER COMO ESTÁ (global)  
**Justificativa:** 405 subgrupos genéricos atendem 95% dos casos

**Alternativa futura:** Criar `base_marcacoes_custom` (com user_id) para personalizações

---

## 🎯 Análise: O Que Deve Ser Criado Automaticamente?

### 🔵 BASES GLOBAIS - JÁ EXISTEM (Não criar por usuário)

#### 1. **base_grupos_config** ✅ VALIDADO
**Status:** 21 grupos populados (tabela global)  
**Ação:** Nenhuma (já está OK)

#### 2. **base_marcacoes** ✅ VALIDADO
**Status:** 405 registros populados (tabela global)  
**Ação:** Nenhuma (já está OK)

#### 3. **generic_classification_rules** ✅ VALIDADO
**Status:** 86 regras ativas (tabela global)  
**Ação:** Nenhuma (Frente 4 já implementou)

#### 4. **bank_format_compatibility** ✅ VALIDADO
**Status:** 7 bancos cadastrados (tabela global)  
**Ação:** Nenhuma (já está OK)

#### 5. **screen_visibility** ✅ VALIDADO
**Status:** 14 telas cadastradas (tabela global, sem user_id)  
**Ação:** Nenhuma (todos os usuários veem as mesmas telas)

---

### ✅ CRIAR AUTOMATICAMENTE (Por Usuário)

#### 1. **budget_geral** (Metas) 🟢 CRÍTICO
**Por quê:** Facilita onboarding - usuário só ajusta valores

**Estratégia:** Criar metas "template" com valor R$ 0

**Dados default:**
```sql
-- Criar meta para TODOS os grupos principais, mês atual + próximos 11 meses
INSERT INTO budget_geral (user_id, ano, mes, grupo, subgrupo, valor_planejado, valor_real)
SELECT 
    :new_user_id,
    :ano_atual,
    m.mes,
    g.nome,
    'Geral',
    0.00,  -- Valor zerado para usuário preencher
    0.00
FROM base_grupos_config g
CROSS JOIN (
    SELECT 1 AS mes UNION SELECT 2 UNION SELECT 3 UNION 
    SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION 
    SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION 
    SELECT 10 UNION SELECT 11 UNION SELECT 12
) m
WHERE g.ativo = 1;
```

**Benefício:** 
- Usuário vê estrutura completa de metas
- Só precisa preencher valores (não criar linhas)
- Facilita entendimento do sistema

**Alternativa:** Criar apenas para os próximos 3 meses (menos intimidante)

---

#### 2. **cartoes** 🟡 IMPORTANTE
**Por quê:** Muitos uploads são de cartão de crédito

**Dados default:**
```sql
-- Criar cartão genérico para usuário começar
INSERT INTO cartoes (nome_cartao, final_cartao, banco, user_id, ativo, created_at, updated_at)
VALUES 
    ('Cartão Padrão', '0000', 'Não especificado', :new_user_id, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Benefício:** 
- Usuário pode fazer upload de fatura sem configurar cartão primeiro
- Pode editar depois

---

#### 3. **base_padroes** ❓ OPCIONAL
**Decisão:** Deixar VAZIO (usuário configura gradualmente conforme usa)

---

### ❌ NÃO CRIAR (Vazios para novo usuário)

#### 1. **journal_entries** ❌
**Por quê:** Usuário ainda não tem transações (vai popular no upload)

#### 2. **upload_history** ❌
**Por quê:** Usuário ainda não fez uploads

#### 3. **preview_transacoes** ❌
**Por quê:** Temporária (apenas durante upload)

#### 4. **transacoes_exclusao** ❌
**Por quê:** Usuário ainda não excluiu nada

#### 5. **budget_geral_historico** ❌
**Por quê:** Histórico vazio inicialmente

#### 6. **investimentos_*** ❌
**Por quê:** Feature avançada - usuário configura depois

#### 7. **screen_visibility** ❌ (ou criar padrão?)
**Análise necessária:** Ver se tem valores default ou é vazio

#### 8. **generic_classification_rules** (Tabela Sistema - NÃO tem user_id)
**Status Atual:** ✅ Já tem 86 regras (Frente 4 implementou)

---

## 🔍 Análise do Fluxo Atual de Cadastro

### Backend - Endpoint de Criação de Usuário

**File:** `app_dev/backend/app/domains/users/service.py`

```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    """
    Cria novo usuário
    
    Lógica atual:
    - Verifica se email já existe
    - Hash da senha
    - Define timestamps
    """
    # Verificar se email já existe
    if self.repository.email_exists(user_data.email):
        raise HTTPException(...)
    
    # Criar modelo
    now = datetime.now()
    user = User(
        email=user_data.email,
        nome=user_data.nome,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        ativo=1,
        created_at=now,
        updated_at=now
    )
    
    # Salvar
    created = self.repository.create(user)
    return UserResponse.from_orm(created)
```

**❌ PROBLEMA:** Só cria registro em `users` - NÃO popula bases auxiliares!

---

### Frontend - Tela de Cadastro

**Status:** 🔴 NÃO EXISTE!

**Busca realizada:**
- ❌ Não encontrado: página de signup/cadastro/register
- ❌ Não encontrado: formulário de novo usuário (não-admin)
- ✅ Encontrado: Admin pode criar usuários via `/users` (POST)

**Conclusão:** Usuários só podem ser criados pelo admin atualmente!

---

## 🎯 Plano de Implementação

### Fase 1: Popular Bases Automaticamente (Backend)

**Criar função:** `populate_user_defaults(user_id: int)`

**Local:** `app_dev/backend/app/domains/users/service.py`

```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    # ... código existente ...
    
    # Salvar
    created = self.repository.create(user)
    
    # 🆕 ADICIONAR: Popular bases default
    self._populate_user_defaults(created.id)
    
    return UserResponse.from_orm(created)

def _populate_user_defaults(self, user_id: int):
    """
    Popula bases auxiliares para novo usuário
    
    1. base_marcacoes (copiar de base_grupos_config)
    2. budget_geral (metas template para ano atual)
    3. cartoes (cartão genérico)
    """
    # Implementação detalhada a seguir
```

---

### Fase 2: Criar Script de População

**File:** `scripts/database/popular_user_defaults.py`

**Funções:**
1. `popular_marcacoes(user_id)` - Copia grupos de base_grupos_config
2. `popular_metas_template(user_id, ano)` - Cria metas zeradas
3. `popular_cartao_generico(user_id)` - Cria cartão padrão

**Execução:**
- Automática: Chamada após criar usuário (backend)
- Manual: Admin pode rodar para usuários existentes

---

### Fase 3: Validar Bases Sistema (Globais)

**Verificar e popular se vazio:**

1. **base_grupos_config** - Grupos principais do sistema
2. **bank_format_compatibility** - Formatos de banco suportados
3. **generic_classification_rules** - 86 regras já criadas ✅

**Script:** `scripts/database/popular_bases_sistema.py`

---

### Fase 4: Tela de Cadastro Frontend (Opcional)

**Se quiser permitir auto-cadastro (sem admin):**

**File:** `app_dev/frontend/src/app/signup/page.tsx`

**Features:**
- Formulário: nome, email, senha, confirmar senha
- Validação: email único, senha forte
- Redirect: Login após cadastro
- Feedback: "Aguarde aprovação do admin" (se usuário inicia inativo)

**Endpoint novo:** `POST /api/auth/signup` (rate limited)

---

## 📋 Checklist de Implementação

### Etapa 1: Bases Sistema (Globais)
- [ ] Verificar se `base_grupos_config` está populada
- [ ] Verificar se `bank_format_compatibility` está populada
- [ ] Verificar se `generic_classification_rules` tem 86 regras ✅
- [ ] Criar script `popular_bases_sistema.py` se necessário

### Etapa 2: Função de População Automática
- [ ] Criar `_populate_user_defaults()` em `UserService`
- [ ] Implementar `popular_marcacoes()` (copiar de base_grupos_config)
- [ ] Implementar `popular_metas_template()` (ano atual + próximos meses)
- [ ] Implementar `popular_cartao_generico()` (cartão padrão)
- [ ] Integrar com `create_user()` (chamar automático)

### Etapa 3: Validação
- [ ] Criar usuário de teste via API
- [ ] Verificar se `base_marcacoes` foi populada
- [ ] Verificar se `budget_geral` tem metas template
- [ ] Verificar se `cartoes` tem cartão genérico
- [ ] Fazer primeiro upload e validar classificação

### Etapa 4: Tela de Cadastro (Opcional)
- [ ] Criar página `/signup` no frontend
- [ ] Criar endpoint `POST /auth/signup` no backend
- [ ] Implementar validações (email único, senha forte)
- [ ] Adicionar rate limiting (anti-spam)
- [ ] Testar fluxo completo: cadastro → login → primeiro uso

---

## 🎯 Proposta de Metas Template

### Estratégia Recomendada: Metas "Zeradas" para o Ano Atual

**Vantagens:**
- ✅ Usuário vê estrutura completa do sistema
- ✅ Facilita entendimento de como metas funcionam
- ✅ Só precisa preencher valores (não criar linhas)
- ✅ Menos intimidante que criar tudo do zero

**Desvantagens:**
- ⚠️ Muitas linhas (12 meses × 20 grupos = 240 registros)
- ⚠️ Pode parecer complexo inicialmente

### Alternativa 1: Apenas Próximos 3 Meses
```sql
-- Criar metas para mês atual + 2 próximos
WHERE m.mes BETWEEN :mes_atual AND (:mes_atual + 2)
```

**Benefício:** Menos assustador para novo usuário

### Alternativa 2: Apenas Grupos Principais (Top 10)
```sql
-- Criar metas apenas para grupos mais usados
WHERE g.nome IN ('Casa', 'Mercado', 'Carro', 'Saúde', 'Entretenimento', 
                 'Transporte', 'Educação', 'Lazer', 'Vestuário', 'Diversos')
```

**Benefício:** Foco nos grupos essenciais

### ⭐ RECOMENDAÇÃO FINAL:
**Opção Híbrida:** 
- Próximos 3 meses
- Apenas 10 grupos principais
- Total: 3 × 10 = 30 registros (gerenciável)

---

## 🔍 Análise: Screen Visibility

**Verificar:** Esta tabela controla visibilidade de telas?

```sql
SELECT * FROM screen_visibility LIMIT 10;
```

**Se sim:**
- Definir valores default (todas as telas visíveis)
- Popular automaticamente para novo usuário

**Se não (vazio):**
- Pode deixar vazio (sistema usa fallback)

---

## 📊 Resumo das Bases

| Tabela | Tipo | Criar Auto? | Estratégia |
|--------|------|-------------|------------|
| **base_marcacoes** | User | ✅ SIM | Copiar de base_grupos_config |
| **budget_geral** | User | ✅ SIM | Template zerado (3 meses, 10 grupos) |
| **cartoes** | User | ✅ SIM | Cartão genérico |
| **base_grupos_config** | Sistema | ✅ Validar | Popular se vazio |
| **bank_format_compatibility** | Sistema | ✅ Validar | Popular se vazio |
| **generic_classification_rules** | Sistema | ✅ OK | 86 regras já criadas |
| **journal_entries** | User | ❌ NÃO | Vazio (popular no upload) |
| **upload_history** | User | ❌ NÃO | Vazio |
| **investimentos_*** | User | ❌ NÃO | Feature avançada (usuário configura) |
| **screen_visibility** | User | ❓ Validar | Depende do comportamento |

---

## 🚀 Próximos Passos

1. **Validar bases sistema** (base_grupos_config, bank_format_compatibility)
2. **Implementar `_populate_user_defaults()`** no backend
3. **Criar usuário de teste** e validar população automática
4. **Fazer primeiro upload** e validar classificação genérica funciona
5. **Documentar** experiência first-time user
6. **Decidir** se cria tela de auto-cadastro (signup) ou mantém admin-only

---

**Status:** 🟡 Mapeamento completo - Pronto para implementação  
**Próximo:** Implementar Fase 1 (popular bases automaticamente)
