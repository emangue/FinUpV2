# 📝 Sumário Executivo: Estratégia de Dados para Novo Usuário

**Data:** 12/02/2026  
**Status:** ✅ Análise completa, pronto para implementação

---

## 🎯 Conclusão Principal

Para novo usuário, devemos criar **APENAS 2-3 tabelas**:
1. ✅ **budget_geral** (~30 registros) - Metas template zeradas
2. ✅ **cartoes** (1 registro) - Cartão genérico padrão
3. ❓ **base_padroes** (0 registros) - Vazio (opcional)

**Por quê tão poucos?** Porque descobrimos que a maioria das bases auxiliares **são globais** (compartilhadas entre todos os usuários)!

---

## 🔍 Descoberta Crítica: Bases São Globais

### ✅ BASES GLOBAIS (7 tabelas - SEM user_id)

| Tabela | Registros | Validado | Função |
|--------|-----------|----------|--------|
| **base_grupos_config** | 21 | ✅ | Grupos oficiais (Casa, Carro, Saúde, etc) |
| **base_marcacoes** | 405 | ✅ | Subgrupos de cada grupo (GLOBAL!) |
| **generic_classification_rules** | 86 | ✅ | Regras de auto-classificação |
| **bank_format_compatibility** | 7 | ✅ | Bancos suportados (Itaú, Nubank, etc) |
| **screen_visibility** | 14 | ✅ | Telas do sistema |
| **users** | N | - | Tabela de usuários |
| **alembic_version** | 1 | - | Controle de migrations |

**Impacto:** NÃO precisa criar/popular para cada usuário! ✅

---

## 🎯 Como Funciona a Classificação (TipoGasto/CategoriaGeral)

### Fluxo Descoberto:

**1. Usuário classifica transação:**
- Escolhe GRUPO: "Casa"
- Escolhe SUBGRUPO: "Aluguel"

**2. Sistema busca metadados em `base_grupos_config`:**
```python
grupo_config = db.query(BaseGruposConfig).filter(
    BaseGruposConfig.nome_grupo == "Casa"
).first()

# Resultado:
# tipo_gasto_padrao = "Ajustável"
# categoria_geral = "Despesa"
```

**3. Sistema salva em `journal_entries`:**
```python
transaction.GRUPO = "Casa"
transaction.SUBGRUPO = "Aluguel"
transaction.TipoGasto = "Ajustável"       # ← Vem de base_grupos_config
transaction.CategoriaGeral = "Despesa"    # ← Vem de base_grupos_config
```

### ⚠️ Importante:

**`base_marcacoes` (405 registros) NÃO É USADA** para determinar TipoGasto/CategoriaGeral!

**Função real de `base_marcacoes`:**
- Lista de **subgrupos disponíveis** para popular dropdowns no frontend
- **Não** afeta lógica de negócio (classificação)
- É **global** (todos os usuários veem os mesmos subgrupos)

---

## 📊 Proposta Aprovada: O Que Criar

### ✅ CRIAR AUTOMATICAMENTE (2 tabelas)

#### 1. **budget_geral** - Metas Template
**Registros:** ~30 (10 grupos × 3 meses)  
**Estratégia:** Template zerado (usuário preenche valores)

**SQL:**
```sql
-- Criar metas para fev, mar, abr 2026
-- Top 10 grupos: Casa, Saúde, Alimentação, Entretenimento, 
--                Transporte, Carro, Educação, Roupas, Presentes, Assinaturas

INSERT INTO budget_geral (user_id, categoria_geral, mes_referencia, valor_planejado, total_mensal, created_at, updated_at)
SELECT 
    :user_id,
    categoria_geral,
    :mes_referencia,  -- Loop: '2026-02', '2026-03', '2026-04'
    0.00,
    0.00,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM base_grupos_config
WHERE categoria_geral IN ('Despesa', 'Receita')
LIMIT 10;
```

**Benefício:**
- ✅ Usuário vê estrutura completa de metas no primeiro acesso
- ✅ Não precisa criar linhas manualmente (apenas preencher valores)
- ✅ Experiência onboarding facilitada

---

#### 2. **cartoes** - Cartão Genérico
**Registros:** 1  
**Estratégia:** Cartão padrão para permitir primeiro upload

**SQL:**
```sql
INSERT INTO cartoes (nome_cartao, final_cartao, banco, user_id, ativo, created_at, updated_at)
VALUES 
    ('Cartão Padrão', '0000', 'Não especificado', :user_id, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Benefício:**
- ✅ Usuário pode fazer upload de fatura imediatamente
- ✅ Não bloqueia primeiro uso
- ✅ Pode editar/adicionar mais cartões depois

---

### ❌ DEIXAR VAZIO (13 tabelas)

| Tabela | Por quê vazio |
|--------|---------------|
| journal_entries | Transações virão dos uploads |
| upload_history | Histórico vazio |
| preview_transacoes | Temporária (apenas durante upload) |
| transacoes_exclusao | Soft delete vazio |
| budget_geral_historico | Histórico vazio |
| budget_categoria_config | Config vazia (usuário personaliza) |
| budget_planning | Planejamento vazio |
| base_padroes | Padrões vazios (usuário configura) |
| base_parcelas | Parcelas vazias |
| investimentos_* (5 tabelas) | Feature avançada (usuário configura) |

---

## 🚀 Implementação

### Fase 1: Backend

**File:** `app_dev/backend/app/domains/users/service.py`

**Adicionar método:**
```python
def _populate_user_defaults(self, user_id: int):
    """
    Popula bases auxiliares para novo usuário
    
    1. budget_geral (metas template para próximos 3 meses)
    2. cartoes (cartão genérico)
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from app.domains.grupos.models import BaseGruposConfig
    from app.domains.budget.models import BudgetGeral
    from app.domains.cards.models import Cartao
    
    # 1. Criar metas template (próximos 3 meses, top 10 grupos)
    hoje = datetime.now()
    meses = [(hoje + relativedelta(months=i)).strftime('%Y-%m') for i in range(3)]
    
    grupos = self.repository.db.query(BaseGruposConfig).filter(
        BaseGruposConfig.categoria_geral.in_(['Despesa', 'Receita'])
    ).limit(10).all()
    
    for mes in meses:
        for grupo in grupos:
            meta = BudgetGeral(
                user_id=user_id,
                categoria_geral=grupo.categoria_geral,
                mes_referencia=mes,
                valor_planejado=0.00,
                total_mensal=0.00
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
    
    self.repository.db.commit()
```

**Integrar:**
```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    # ... código existente ...
    created = self.repository.create(user)
    
    # 🆕 Popular bases default
    self._populate_user_defaults(created.id)
    
    return UserResponse.from_orm(created)
```

---

### Fase 2: Script Standalone

**File:** `scripts/database/popular_user_defaults.py`

**Uso:**
```bash
# Popular para usuário específico
python scripts/database/popular_user_defaults.py --user-id 5

# Popular para todos os usuários sem dados
python scripts/database/popular_user_defaults.py --all
```

---

### Fase 3: Testes

**Checklist:**
- [ ] Criar usuário de teste
- [ ] Verificar `budget_geral` (~30 registros)
- [ ] Verificar `cartoes` (1 registro)
- [ ] Login e ver dashboard (metas zeradas devem aparecer)
- [ ] Fazer upload de arquivo
- [ ] Verificar classificação genérica (86 regras)
- [ ] Verificar TipoGasto/CategoriaGeral preenchidos

---

## 📚 Documentos de Referência

1. **[ANALISE_BASES_USUARIO.md](./ANALISE_BASES_USUARIO.md)** - Análise completa de todas as 24 tabelas
2. **[VALIDACOES_COMPLETAS.md](./VALIDACOES_COMPLETAS.md)** - Resultados das validações SQL
3. **[MAPEAMENTO_BASES_DEFAULT.md](./MAPEAMENTO_BASES_DEFAULT.md)** - Documento original (atualizado)

---

## ✅ Próximos Passos

1. **Implementar** `_populate_user_defaults()` no backend
2. **Criar** script standalone para população manual
3. **Testar** com usuário novo
4. **Validar** primeiro upload e classificação
5. **Documentar** experiência first-time user
6. **Decidir** sobre tela de auto-cadastro (signup público)

---

**Status:** 🟡 Pronto para implementação  
**Estimativa:** 2-3 horas de desenvolvimento + 1 hora de testes  
**Impacto:** Alto - Melhora significativamente onboarding de novos usuários
