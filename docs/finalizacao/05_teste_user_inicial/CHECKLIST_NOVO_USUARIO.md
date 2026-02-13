# ✅ Checklist: Criação de Novo Usuário

**Data:** 12/02/2026  
**Objetivo:** Garantir que todas as bases necessárias sejam criadas para novo usuário

---

## 🎯 Visão Geral

**Ordem de Execução:**
1. **Criar usuário** (tabela `users`)
2. **Popular bases auxiliares** (automático via `_populate_user_defaults()`)
3. **Validar criação** (verificar que tudo foi criado)

**Tabelas criadas:** 4 (base_grupos_config, base_marcacoes, budget_planning, cartoes)  
**Tempo estimado:** ~500ms (automático)

---

## 📋 FASE 1: Criar Usuário (Manual ou API)

### Via API POST /api/v1/users/register

**Request:**
```json
{
  "email": "novo@usuario.com",
  "username": "novousuario",
  "password": "senha_segura_123"
}
```

**Response esperado:**
```json
{
  "id": 5,
  "email": "novo@usuario.com",
  "username": "novousuario",
  "is_active": true,
  "role": "user",
  "created_at": "2026-02-12T10:30:00"
}
```

### Via SQL (Método alternativo)

```sql
INSERT INTO users (email, username, password_hash, is_active, role, created_at, updated_at)
VALUES (
    'novo@usuario.com',
    'novousuario',
    '<hash_bcrypt_da_senha>',
    1,
    'user',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
```

**✅ Checklist Fase 1:**
- [ ] Usuário criado na tabela `users`
- [ ] ID do usuário obtido (ex: `user_id = 5`)
- [ ] Email único (não duplicado)
- [ ] Senha hashada (bcrypt)
- [ ] `is_active = 1` (ativo)
- [ ] `role = 'user'` (padrão)

---

## 📋 FASE 2: Popular Bases Auxiliares (AUTOMÁTICO)

**Execução:** Automática via `_populate_user_defaults()` no backend

**Processo:**
```python
# app/domains/users/service.py - método create_user()
created = self.repository.create(user)
self._populate_user_defaults(created.id)  # ← Chama automático
```

### 2.1. base_grupos_config (21 registros)

**O que cria:**
```sql
INSERT INTO base_grupos_config (user_id, nome_grupo, tipo_gasto_padrao, categoria_geral)
SELECT 5, nome_grupo, tipo_gasto_padrao, categoria_geral
FROM base_grupos_config_template;
```

**Registros criados:** 21 grupos padrão
- Casa, Saúde, Alimentação, Entretenimento, Transporte
- Carro, Educação, Roupas, Presentes, Assinaturas
- Tecnologia, Serviços, Salário, Outros, Doações
- Limpeza, Fatura, Investimentos, Aplicações, Viagens, MeLi + Amazon

**✅ Validar:**
```sql
SELECT COUNT(*) FROM base_grupos_config WHERE user_id = 5;
-- Esperado: 21
```

---

### 2.2. base_marcacoes (405 registros)

**O que cria:**
```sql
INSERT INTO base_marcacoes (user_id, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral)
SELECT 5, GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
FROM base_marcacoes_template;
```

**Registros criados:** 405 subgrupos padrão
- 20 grupos com múltiplos subgrupos cada
- Exemplos: "Supermercado Pão de Açúcar", "Posto Shell", "Ifood"

**✅ Validar:**
```sql
SELECT COUNT(*) FROM base_marcacoes WHERE user_id = 5;
-- Esperado: 405
```

---

### 2.3. budget_planning (~30 registros)

**O que cria:**
```sql
-- Criar metas zeradas para próximos 3 meses
-- 10 categorias × 3 meses = 30 registros

INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, ativo, created_at, updated_at)
SELECT 
    5,
    nome_grupo,  -- Ex: "Casa", "Saúde", "Alimentação"
    '2026-02',   -- Mês atual
    0.00,
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM base_grupos_config
WHERE user_id = 5
  AND categoria_geral IN ('Despesa', 'Receita')
LIMIT 10;

-- Repetir para '2026-03' e '2026-04'
```

**Registros criados:** ~30 metas zeradas
- 10 categorias principais (Casa, Saúde, Alimentação, etc.)
- 3 meses futuros (mês atual + 2 próximos)
- Todos com `valor_planejado = 0.00` (usuário preenche depois)
- Todos com `ativo = 1` (habilitados)

**✅ Validar:**
```sql
SELECT COUNT(*) FROM budget_planning WHERE user_id = 5;
-- Esperado: ~30 (10 categorias × 3 meses)

SELECT DISTINCT mes_referencia FROM budget_planning WHERE user_id = 5 ORDER BY mes_referencia;
-- Esperado: 2026-02, 2026-03, 2026-04
```

---

### 2.4. cartoes (1 registro)

**O que cria:**
```sql
INSERT INTO cartoes (nome_cartao, final_cartao, banco, user_id, ativo, created_at, updated_at)
VALUES (
    'Cartão Padrão',
    '0000',
    'Não especificado',
    5,
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
```

**Registros criados:** 1 cartão genérico
- Nome: "Cartão Padrão"
- Final: "0000"
- Banco: "Não especificado"
- Status: Ativo

**Benefício:** Usuário pode fazer primeiro upload de fatura sem bloquear

**✅ Validar:**
```sql
SELECT * FROM cartoes WHERE user_id = 5;
-- Esperado: 1 registro com nome_cartao = 'Cartão Padrão'
```

---

## 📋 FASE 3: Validação Completa

### 3.1. Verificar Todas as Bases Criadas

**Script de validação:**
```sql
-- 1. base_grupos_config
SELECT 'base_grupos_config' as tabela, COUNT(*) as registros 
FROM base_grupos_config WHERE user_id = 5;
-- Esperado: 21

-- 2. base_marcacoes
SELECT 'base_marcacoes' as tabela, COUNT(*) as registros 
FROM base_marcacoes WHERE user_id = 5;
-- Esperado: 405

-- 3. budget_planning
SELECT 'budget_planning' as tabela, COUNT(*) as registros 
FROM budget_planning WHERE user_id = 5;
-- Esperado: ~30

-- 4. cartoes
SELECT 'cartoes' as tabela, COUNT(*) as registros 
FROM cartoes WHERE user_id = 5;
-- Esperado: 1

-- TOTAL GERAL
SELECT 
    21 + 405 + 30 + 1 as total_esperado,
    (SELECT COUNT(*) FROM base_grupos_config WHERE user_id = 5) +
    (SELECT COUNT(*) FROM base_marcacoes WHERE user_id = 5) +
    (SELECT COUNT(*) FROM budget_planning WHERE user_id = 5) +
    (SELECT COUNT(*) FROM cartoes WHERE user_id = 5) as total_criado;
-- Esperado: ~457 registros total
```

**✅ Checklist Validação:**
- [ ] `base_grupos_config`: 21 registros
- [ ] `base_marcacoes`: 405 registros
- [ ] `budget_planning`: ~30 registros (10 categorias × 3 meses)
- [ ] `cartoes`: 1 registro
- [ ] **TOTAL:** ~457 registros criados automaticamente

---

### 3.2. Testar Login e Acesso

**Login via API:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"novo@usuario.com","password":"senha_segura_123"}'
```

**Response esperado:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "email": "novo@usuario.com",
    "username": "novousuario"
  }
}
```

**✅ Checklist Login:**
- [ ] Login bem-sucedido (status 200)
- [ ] Token JWT recebido
- [ ] `user.id` correto

---

### 3.3. Testar Dashboard (Primeira Visualização)

**Abrir:** `http://localhost:3000/dashboard`

**Comportamento esperado:**
- ✅ Dashboard carrega sem erros
- ✅ Mostra "Nenhuma transação encontrada" (correto - ainda não fez upload)
- ✅ Mostra 10 categorias de metas zeradas (budget_planning)
- ✅ Gráficos vazios (correto)

**✅ Checklist Dashboard:**
- [ ] Página carrega (sem erro 500)
- [ ] Mostra metas zeradas
- [ ] Sem transações (correto para novo usuário)

---

### 3.4. Testar Primeiro Upload

**Upload de arquivo:**
```bash
curl -X POST http://localhost:8000/api/v1/upload/preview \
  -H "Authorization: Bearer <token>" \
  -F "file=@extrato_janeiro.csv" \
  -F "banco=itau" \
  -F "tipo_documento=extrato" \
  -F "mes_fatura=2026-01" \
  -F "formato=csv"
```

**Response esperado:**
```json
{
  "sessionId": "session_20260212_103000_5",
  "totalRegistros": 150,
  "message": "Preview gerado com sucesso"
}
```

**✅ Checklist Upload:**
- [ ] Preview criado (status 200)
- [ ] `sessionId` retornado
- [ ] Transações salvas em `preview_transacoes`
- [ ] Classificação automática funcionou (86 regras genéricas)
- [ ] Grupos/subgrupos preenchidos (via base_marcacoes)

---

### 3.5. Validar Classificação Automática

**Verificar classificação:**
```sql
SELECT 
    origem_classificacao,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM preview_transacoes WHERE user_id = 5), 2) as percentual
FROM preview_transacoes
WHERE user_id = 5
  AND session_id = 'session_20260212_103000_5'
GROUP BY origem_classificacao
ORDER BY total DESC;
```

**Esperado:**
- `regras_genericas`: 73.7% (~110 transações)
- `base_padroes`: ~10% (~15 transações)
- `nao_classificado`: ~16% (~25 transações)

**✅ Checklist Classificação:**
- [ ] Pelo menos 70% classificados automaticamente
- [ ] Grupos/subgrupos populados
- [ ] TipoGasto e CategoriaGeral preenchidos

---

## 📊 Resumo Final: O Que Foi Criado

| Tabela | Registros | Detalhes |
|--------|-----------|----------|
| **users** | 1 | Usuário principal |
| **base_grupos_config** | 21 | Grupos padrão |
| **base_marcacoes** | 405 | Subgrupos padrão |
| **budget_planning** | ~30 | Metas zeradas (10 categorias × 3 meses) |
| **cartoes** | 1 | Cartão genérico |
| **TOTAL** | **~458** | **Registros criados automaticamente** |

---

## 🚫 Tabelas que Começam Vazias (CORRETO)

Estas tabelas **NÃO** são criadas automaticamente (ficam vazias até uso):

| Tabela | Por quê vazio | Quando preenche |
|--------|---------------|-----------------|
| `journal_entries` | Transações reais virão dos uploads | Após confirmar primeiro upload |
| `upload_history` | Histórico vazio | Após primeiro upload |
| `preview_transacoes` | Temporária | Durante preview de upload |
| `transacoes_exclusao` | Soft delete | Quando usuário excluir transações |
| `base_parcelas` | Parcelas | Quando usuário cadastrar parcelas manualmente |
| `base_padroes` | Padrões personalizados | Após uploads repetidos (gerado automaticamente) |

---

## ⏱️ Timeline de Criação

```
t=0ms   → POST /api/v1/users/register
t=50ms  → Usuário criado na tabela users
t=100ms → _populate_user_defaults() inicia
t=150ms → base_grupos_config: 21 registros inseridos
t=250ms → base_marcacoes: 405 registros inseridos
t=350ms → budget_planning: 30 registros inseridos
t=400ms → cartoes: 1 registro inserido
t=450ms → Commit no banco
t=500ms → Response 201 Created enviado
```

**Tempo total:** ~500ms (tudo automático)

---

## 🔧 Troubleshooting

### Problema: Bases não foram criadas

**Verificar logs do backend:**
```bash
tail -50 temp/logs/backend.log | grep -i "populate_user_defaults"
```

**Esperado:**
```
✅ Bases default populadas para user_id=5
```

**Se houver erro:**
```bash
❌ Erro ao popular bases default: <erro_aqui>
```

**Ações:**
1. Ver erro completo nos logs
2. Executar script standalone: `python scripts/database/popular_user_defaults.py --user-id 5`
3. Validar manualmente com SQLs acima

---

### Problema: Usuario criado mas bases vazias

**Executar script standalone:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
source app_dev/venv/bin/activate
cd app_dev/backend
python ../../scripts/database/popular_user_defaults.py --user-id 5
```

**Validar:**
```sql
SELECT COUNT(*) FROM base_grupos_config WHERE user_id = 5;
SELECT COUNT(*) FROM base_marcacoes WHERE user_id = 5;
SELECT COUNT(*) FROM budget_planning WHERE user_id = 5;
SELECT COUNT(*) FROM cartoes WHERE user_id = 5;
```

---

## 📚 Referências

- **Estratégia completa:** [VALIDACOES_COMPLETAS.md](./VALIDACOES_COMPLETAS.md)
- **Análise budget:** [ANALISE_TABELAS_BUDGET.md](./ANALISE_TABELAS_BUDGET.md)
- **Migration bases:** [MIGRACAO_USER_ID.md](./MIGRACAO_USER_ID.md)
- **Processo upload:** [MAPEAMENTO_PROCESSO_UPLOAD.md](./MAPEAMENTO_PROCESSO_UPLOAD.md)

---

**Criado em:** 12/02/2026  
**Atualizado:** Após cada mudança na estratégia de criação
