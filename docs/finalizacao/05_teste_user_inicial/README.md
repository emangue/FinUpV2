# 5️⃣ Teste Usuário Inicial

**Frente:** Teste de Usuário Inicial  
**Status:** � EM ANDAMENTO - Análise concluída  
**Prioridade:** 🔴 CRÍTICA  
**Responsável:** A definir  
**Data Início:** 12/02/2026  
**Deadline:** A definir

---

## 📚 **LEIA PRIMEIRO:** Documentação Completa

### 📊 Sumário Executivo
🌟 **[SUMARIO_EXECUTIVO.md](./SUMARIO_EXECUTIVO.md)** - Conclusões principais e estratégia aprovada

### 📖 Análises Detalhadas
1. **[ANALISE_BASES_USUARIO.md](./ANALISE_BASES_USUARIO.md)** - 24 tabelas mapeadas
2. **[VALIDACOES_COMPLETAS.md](./VALIDACOES_COMPLETAS.md)** - Resultados das validações SQL (todas passaram)
3. **[MAPEAMENTO_BASES_DEFAULT.md](./MAPEAMENTO_BASES_DEFAULT.md)** - Documento original atualizado

---

## 🎯 Descobertas Principais (12/02/2026)

### ✅ Bases São Globais (NÃO criar por usuário)

| Base | Registros | Status |
|------|-----------|--------|
| base_grupos_config | 21 | ✅ Validado |
| base_marcacoes | 405 | ✅ Validado |
| generic_classification_rules | 86 | ✅ Validado |
| bank_format_compatibility | 7 | ✅ Validado |
| screen_visibility | 14 | ✅ Validado |

**Impacto:** Não precisa popular para cada usuário! Economia de ~500 registros/usuário

### 🔍 Como Funciona TipoGasto/CategoriaGeral

**Fonte:** `base_grupos_config` (não `base_marcacoes`!)

```
Usuário escolhe GRUPO → Sistema busca base_grupos_config → Retorna tipo_gasto_padrao + categoria_geral
```

**⚠️ base_marcacoes (405 registros):** Apenas para listar subgrupos nos dropdowns (não afeta classificação)

---

## ✅ Estratégia Aprovada: O Que Criar para Novo Usuário

### CRIAR AUTOMATICAMENTE (apenas 2 tabelas!)

#### 1. **budget_geral** - Metas Template
- **Registros:** ~30 (10 grupos × 3 meses)
- **Valores:** 0.00 (usuário preenche depois)
- **Benefício:** Estrutura completa, usuário não cria linhas manualmente

#### 2. **cartoes** - Cartão Genérico
- **Registros:** 1 (Cartão Padrão, final 0000)
- **Benefício:** Não bloqueia primeiro upload de fatura

### DEIXAR VAZIO (13 tabelas)
- journal_entries, upload_history, preview_transacoes, transacoes_exclusao
- budget_geral_historico, budget_categoria_config, budget_planning
- base_padroes, base_parcelas, investimentos_* (5 tabelas)

---

## 📋 Escopo Geral

### Incluído
- ✅ Definição de dados default por usuário
- ✅ Teste de criação/edição de metas
- ✅ Teste de upload do primeiro arquivo
- ✅ Validação de bases auxiliares
- ✅ Fluxo completo de onboarding

### Excluído
- ❌ Testes de performance
- ❌ Testes de carga
- ❌ Usuários existentes (foco em novos)

---

## 👤 Sub-frente 5a: Dados Gerados Automaticamente

### Objetivo
Definir quais dados devem ser criados automaticamente quando um novo usuário é cadastrado.

### 5a.1 Análise de Necessidades

**Perguntas Críticas:**
- [ ] Quais bases DEVEM ter dados ao criar usuário?
- [ ] Quais bases podem ficar vazias inicialmente?
- [ ] Quais defaults fazem sentido?
- [ ] O que usuário precisa para começar a usar?

### 5a.2 Dados por Base

#### ✅ OBRIGATÓRIOS (devem existir)

**1. base_marcacoes (Grupos/Subgrupos)**
```python
# Gerados no setup inicial
grupos_default = [
    # Despesas
    {'nome': 'Alimentação', 'tipo': 'Grupo', 'categoria': 'Despesa'},
    {'nome': 'Supermercado', 'tipo': 'Subgrupo', 'categoria': 'Despesa', 'pai': 'Alimentação'},
    {'nome': 'Restaurante', 'tipo': 'Subgrupo', 'categoria': 'Despesa', 'pai': 'Alimentação'},
    {'nome': 'Transporte', 'tipo': 'Grupo', 'categoria': 'Despesa'},
    {'nome': 'Casa', 'tipo': 'Grupo', 'categoria': 'Despesa'},
    {'nome': 'Lazer', 'tipo': 'Grupo', 'categoria': 'Despesa'},
    {'nome': 'Saúde', 'tipo': 'Grupo', 'categoria': 'Despesa'},
    
    # Receitas
    {'nome': 'Salário', 'tipo': 'Grupo', 'categoria': 'Receita'},
    {'nome': 'Freelance', 'tipo': 'Grupo', 'categoria': 'Receita'},
    {'nome': 'Investimentos', 'tipo': 'Grupo', 'categoria': 'Receita'},
]
```
**Motivo:** Upload e classificação de transações precisam de categorias

**2. base_grupos_config (Tipos de Gasto)**
```python
# Gerados no setup inicial (compartilhados entre usuários)
tipos_default = [
    {'grupo': 'Alimentação', 'tipo': 'ESSENCIAL'},
    {'grupo': 'Transporte', 'tipo': 'ESSENCIAL'},
    {'grupo': 'Casa', 'tipo': 'ESSENCIAL'},
    {'grupo': 'Saúde', 'tipo': 'ESSENCIAL'},
    {'grupo': 'Lazer', 'tipo': 'SUPERFLUO'},
]
```
**Motivo:** Classificação automática e dashboards precisam de tipos

#### 🔵 OPCIONAIS (podem ficar vazios)

**3. budget_geral (Metas/Orçamento)**
```python
# Criar estrutura vazia para ano atual
for month in range(1, 13):
    BudgetGeral(
        user_id=user_id,
        Ano=current_year,
        Mes=month,
        # Todos os valores NULL - usuário preenche depois
    )
```
**Motivo:** Estrutura facilita criação de metas, mas valores são definidos pelo usuário

**4. grupos_planning (Planejamento Mensal)**
```python
# Fica vazio inicialmente
# Será populado no primeiro upload
```
**Motivo:** Depende de transações reais

**5. journal_entries (Transações)**
```python
# Fica vazio inicialmente
# Usuário importa ou cria manualmente
```
**Motivo:** Dados financeiros reais do usuário

**6. base_cartoes (Cartões de Crédito)**
```python
# Fica vazio inicialmente
# Usuário adiciona seus cartões
```
**Motivo:** Informação pessoal do usuário

### 5a.3 Implementação do Setup

```python
# app/domains/users/service.py
def setup_new_user(user_id: int, db: Session):
    """
    Configura dados iniciais para novo usuário
    """
    logger.info(f"Iniciando setup para usuário {user_id}")
    
    try:
        # 1. Grupos padrão (se não existem globalmente)
        _create_default_groups(db)
        
        # 2. Tipos de gasto (se não existem globalmente)
        _create_default_tipos(db)
        
        # 3. Budget estrutura vazia para ano atual
        _create_budget_structure(user_id, db)
        
        db.commit()
        logger.info(f"Setup concluído para usuário {user_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro no setup do usuário {user_id}: {e}")
        raise

def _create_default_groups(db: Session):
    """Cria grupos padrão se não existem"""
    existing = db.query(BaseMarcacao).count()
    if existing > 0:
        logger.info("Grupos já existem, pulando criação")
        return
    
    for grupo_data in GRUPOS_DEFAULT:
        grupo = BaseMarcacao(**grupo_data)
        db.add(grupo)

def _create_default_tipos(db: Session):
    """Cria tipos padrão se não existem"""
    existing = db.query(BaseGruposConfig).count()
    if existing > 0:
        logger.info("Tipos já existem, pulando criação")
        return
    
    for tipo_data in TIPOS_DEFAULT:
        tipo = BaseGruposConfig(**tipo_data)
        db.add(tipo)

def _create_budget_structure(user_id: int, db: Session):
    """Cria estrutura de budget vazia para ano atual"""
    current_year = datetime.now().year
    
    for month in range(1, 13):
        budget = BudgetGeral(
            user_id=user_id,
            Ano=current_year,
            Mes=month
        )
        db.add(budget)
```

### Checklist 5a
- [ ] Definir lista completa de grupos default
- [ ] Definir lista completa de tipos default
- [ ] Implementar função setup_new_user
- [ ] Integrar no endpoint de registro
- [ ] Testar criação de novo usuário
- [ ] Validar que dados foram criados corretamente

---

## 🎯 Sub-frente 5b: Criar/Editar Metas

### Objetivo
Testar completamente o fluxo de criação e edição de metas, incluindo salvar meta do ano todo.

### 5b.1 Cenários de Teste

#### Cenário 1: Criar Meta para Mês Específico
```markdown
1. [ ] Acessar tela de metas
2. [ ] Selecionar mês (ex: Janeiro/2026)
3. [ ] Selecionar grupo (ex: Alimentação)
4. [ ] Inserir valor (ex: R$ 1.000,00)
5. [ ] Salvar
6. [ ] Validar que salvou em budget_geral
7. [ ] Validar que aparece no dashboard
```

#### Cenário 2: Editar Meta Existente
```markdown
1. [ ] Acessar tela de metas
2. [ ] Selecionar mês com meta existente
3. [ ] Alterar valor (ex: R$ 1.000,00 → R$ 1.200,00)
4. [ ] Salvar
5. [ ] Validar que atualizou em budget_geral
6. [ ] Validar que dashboard reflete mudança
```

#### Cenário 3: Criar Meta para Ano Todo
```markdown
1. [ ] Acessar tela de metas
2. [ ] Selecionar "Ano Todo" ou "Todos os Meses"
3. [ ] Selecionar grupo (ex: Aluguel)
4. [ ] Inserir valor (ex: R$ 2.500,00)
5. [ ] Salvar
6. [ ] **VALIDAÇÃO CRÍTICA:**
   - [ ] Salvou em TODOS os 12 meses
   - [ ] Cada mês tem valor R$ 2.500,00
   - [ ] Dashboard exibe corretamente
```

### 5b.2 Implementação do "Salvar Ano Todo"

#### Backend - API
```python
# app/domains/budget/router.py
@router.post("/metas/bulk")
def create_meta_bulk(
    data: MetaBulkCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria/atualiza meta para múltiplos meses
    """
    ano = data.ano
    grupo = data.grupo
    valor = data.valor
    meses = data.meses  # Lista de meses, ou [1-12] para ano todo
    
    for mes in meses:
        # Buscar meta existente
        meta = db.query(BudgetGeral).filter_by(
            user_id=user_id,
            Ano=ano,
            Mes=mes
        ).first()
        
        if meta:
            # Atualizar campo específico do grupo
            setattr(meta, grupo, valor)
        else:
            # Criar nova entrada
            meta = BudgetGeral(
                user_id=user_id,
                Ano=ano,
                Mes=mes
            )
            setattr(meta, grupo, valor)
            db.add(meta)
    
    db.commit()
    return {"message": f"Meta atualizada para {len(meses)} meses"}
```

#### Frontend - Componente
```typescript
// src/features/budget/components/meta-form.tsx
function MetaForm() {
  const [aplicarAnoTodo, setAplicarAnoTodo] = useState(false)
  
  const handleSubmit = async (values) => {
    const meses = aplicarAnoTodo 
      ? [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
      : [values.mes]
    
    await fetch('/api/v1/budget/metas/bulk', {
      method: 'POST',
      body: JSON.stringify({
        ano: values.ano,
        grupo: values.grupo,
        valor: values.valor,
        meses: meses
      })
    })
    
    toast.success(
      aplicarAnoTodo 
        ? 'Meta aplicada para o ano todo!' 
        : 'Meta salva com sucesso!'
    )
  }
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Campos do formulário */}
      
      <div className="flex items-center">
        <Checkbox 
          checked={aplicarAnoTodo}
          onCheckedChange={setAplicarAnoTodo}
        />
        <label>Aplicar para o ano todo</label>
      </div>
      
      <Button type="submit">
        {aplicarAnoTodo ? 'Salvar para Ano Todo' : 'Salvar'}
      </Button>
    </form>
  )
}
```

### 5b.3 Validações Necessárias

```python
# app/domains/budget/schemas.py
class MetaBulkCreate(BaseModel):
    ano: int = Field(..., ge=2000, le=2100)
    grupo: str = Field(..., min_length=1)
    valor: float = Field(..., gt=0)
    meses: List[int] = Field(..., min_items=1, max_items=12)
    
    @validator('meses')
    def validate_meses(cls, v):
        if not all(1 <= m <= 12 for m in v):
            raise ValueError('Meses devem estar entre 1 e 12')
        return v
```

### Checklist 5b
- [ ] Implementar endpoint bulk de metas
- [ ] Criar componente com checkbox "ano todo"
- [ ] Testar criação de meta para 1 mês
- [ ] Testar criação de meta para ano todo
- [ ] Validar que todos os 12 meses foram atualizados
- [ ] Testar edição de meta existente
- [ ] Validar dashboard após mudanças

---

## 📤 Sub-frente 5c: Upload Primeiro Arquivo

### Objetivo
Testar o upload do primeiro arquivo de um usuário novo, validando todo o fluxo e atualização de bases.

### 5c.1 Fluxo Completo

```markdown
**Pré-condições:**
- Usuário criado (com dados default)
- Nenhuma transação ainda

**Passos:**
1. [ ] Acessar tela de upload
2. [ ] Selecionar arquivo (extrato ou fatura)
3. [ ] Fazer upload
4. [ ] Aguardar processamento
5. [ ] Visualizar preview
6. [ ] Classificar transações não classificadas
7. [ ] Confirmar import
8. [ ] Validar sucesso

**Pós-condições:**
- [ ] journal_entries populado
- [ ] grupos_planning populado
- [ ] Dashboard exibe dados
- [ ] Metas comparam com gastos reais
```

### 5c.2 Validações de Bases Auxiliares

#### Script de Validação
```python
# scripts/testing/validate_first_upload.py
def validate_first_upload(user_id: int, db: Session):
    """
    Valida que primeiro upload atualizou todas as bases
    """
    logger.info(f"Validando primeiro upload do usuário {user_id}")
    
    # 1. journal_entries deve ter transações
    journal_count = db.query(JournalEntry).filter_by(
        user_id=user_id
    ).count()
    assert journal_count > 0, "journal_entries vazio após upload"
    logger.info(f"✓ journal_entries: {journal_count} transações")
    
    # 2. grupos_planning deve ter sido populado
    planning_count = db.query(GruposPlanning).filter_by(
        user_id=user_id
    ).count()
    assert planning_count > 0, "grupos_planning não foi populado"
    logger.info(f"✓ grupos_planning: {planning_count} registros")
    
    # 3. Validar integridade dos dados
    transactions = db.query(JournalEntry).filter_by(
        user_id=user_id
    ).all()
    
    for t in transactions:
        # Deve ter IdTransacao único
        assert t.IdTransacao, f"Transação sem IdTransacao"
        
        # Deve ter grupo válido
        assert t.Grupo, f"Transação {t.IdTransacao} sem grupo"
        
        # Grupo deve existir em base_marcacoes
        grupo_exists = db.query(BaseMarcacao).filter_by(
            Marcacao=t.Grupo
        ).first()
        assert grupo_exists, f"Grupo '{t.Grupo}' não existe em base_marcacoes"
    
    logger.info("✓ Validação completa com sucesso!")
```

### 5c.3 Bases Atualizadas no Upload

```markdown
| Base               | Quando Atualizada | Como Validar |
|--------------------|-------------------|--------------|
| journal_entries    | Sempre            | COUNT > 0    |
| upload_history     | Sempre            | Registro criado |
| grupos_planning    | Primeira vez      | COUNT > 0    |
| budget_geral       | Se meta existe    | Valores comparados |
| base_marcacoes     | Se novo grupo     | Grupo existe |
```

### Checklist 5c
- [ ] Criar usuário de teste novo
- [ ] Fazer primeiro upload
- [ ] Validar preview exibe transações
- [ ] Classificar transações
- [ ] Confirmar import
- [ ] Executar script de validação
- [ ] Validar dashboard exibe dados
- [ ] Validar metas vs gastos reais

---

## 🧪 Fluxo Completo de Validação

### Teste End-to-End Completo

```markdown
**Preparação:**
1. [ ] Deletar usuário de teste (se existir)
2. [ ] Preparar arquivo de teste (extrato/fatura)

**Execução:**
1. [ ] Criar novo usuário
2. [ ] Login
3. [ ] Validar dashboard vazio (EmptyState)
4. [ ] Criar primeira meta
5. [ ] Fazer primeiro upload
6. [ ] Validar transações no dashboard
7. [ ] Editar transação
8. [ ] Criar meta para ano todo
9. [ ] Validar que todos os meses foram atualizados
10. [ ] Fazer segundo upload
11. [ ] Validar que não houve duplicatas

**Validações Finais:**
- [ ] Todas as bases têm dados corretos
- [ ] Dashboard funciona perfeitamente
- [ ] Navegação entre telas OK
- [ ] Metas vs gastos corretos
- [ ] Usuário consegue usar app sem problemas
```

---

## 📊 Métricas

### Progresso
```
5a - Dados Default:   ░░░░░░░░░░ 0%
5b - Metas:           ░░░░░░░░░░ 0%
5c - Upload:          ░░░░░░░░░░ 0%
Validação E2E:        ░░░░░░░░░░ 0%
TOTAL:                ░░░░░░░░░░ 0%
```

---

## 🚧 Riscos

1. **Alto:** Setup inicial pode falhar e usuário fica sem dados
2. **Alto:** Upload primeiro arquivo pode não atualizar bases
3. **Médio:** Meta ano todo pode não salvar todos os meses

### Mitigações
1. Adicionar try/catch e fallback no setup
2. Script de validação após cada upload
3. Validação no backend antes de confirmar sucesso

---

## 📝 Próximos Passos

1. [ ] Implementar setup de dados default
2. [ ] Implementar endpoint bulk de metas
3. [ ] Criar script de validação de upload
4. [ ] Executar teste E2E completo
5. [ ] Documentar comportamentos observados

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [04_BASE_GENERICA.md](./04_BASE_GENERICA.md) (relacionado)
- [03_REVISAO_UPLOAD.md](./03_REVISAO_UPLOAD.md) (relacionado)

---

**Última Atualização:** 10/02/2026
