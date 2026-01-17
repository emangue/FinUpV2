# 🗺️ Mapeamento: Preview Upload → Journal Entries

## 📊 Análise Completa de Campos

### ✅ CAMPOS PRESENTES EM AMBOS (OK)

| Preview Transacoes | Journal Entries | Preenchido Por | Status |
|--------------------|-----------------|----------------|--------|
| `data` | `Data` | Fase 1 (Raw) | ✅ OK |
| `lancamento` | `Estabelecimento` | Fase 1 (Raw) | ✅ OK |
| `valor` | `Valor` | Fase 1 (Raw) | ✅ OK |
| `ValorPositivo` | `ValorPositivo` | Fase 2 (Marking) | ✅ OK |
| `IdTransacao` | `IdTransacao` | Fase 2 (Marking) | ✅ OK |
| `IdParcela` | `IdParcela` | Fase 2 (Marking) | ✅ OK |
| `EstabelecimentoBase` | ❌ **FALTA** | Fase 2 (Marking) | ⚠️ CRIAR |
| `ParcelaAtual` | ❌ **FALTA** | Fase 2 (Marking) | ⚠️ CRIAR |
| `TotalParcelas` | ❌ **FALTA** | Fase 2 (Marking) | ⚠️ CRIAR |
| `GRUPO` | `GRUPO` | Fase 3 (Classification) | ✅ OK |
| `SUBGRUPO` | `SUBGRUPO` | Fase 3 (Classification) | ✅ OK |
| `TipoGasto` | `TipoGasto` | Fase 3 (Classification) | ✅ OK |
| `CategoriaGeral` | `CategoriaGeral` | Fase 3 (Classification) | ✅ OK |
| `origem_classificacao` | `origem_classificacao` | Fase 3 (Classification) | ✅ OK |
| `banco` | `banco_origem` | Fase 1 (Raw) | ✅ OK |
| `nome_arquivo` | `arquivo_origem` | Fase 1 (Raw) | ✅ OK |
| `tipo_documento` | `tipodocumento` | Fase 1 (Raw) | ✅ OK |
| `nome_cartao` | `NomeCartao` | Fase 1 (Raw) | ✅ OK |
| `mes_fatura` | `MesFatura` | Fase 1 (Raw) | ✅ OK (convertido YYYY-MM → YYYYMM) |
| `IgnorarDashboard` | `IgnorarDashboard` | Fase 1 (Raw) | ✅ OK |
| `user_id` | `user_id` | Fase 1 (Raw) | ✅ OK |

---

### ❌ CAMPOS FALTANDO EM PREVIEW (CRÍTICOS)

Estes campos existem em `journal_entries` mas **NÃO** em `preview_transacoes`:

| Campo Journal Entries | Quando Preenchido | Como Preencher | Prioridade |
|-----------------------|-------------------|----------------|------------|
| **`TipoTransacao`** | Fase 2 (deveria) | Derivar de `tipo_documento` + `valor` | 🔴 ALTA |
| **`Ano`** | Fase 2 (deveria) | Extrair de `data` (DD/MM/YYYY → YYYY) | 🔴 ALTA |
| **`Mes`** | Fase 2 (deveria) | Extrair de `data` (DD/MM/YYYY → MM) | 🟡 MÉDIA |

---

### 🔍 CAMPOS EXTRAS EM PREVIEW (Não vão para Journal)

Estes campos existem apenas em `preview_transacoes` (são úteis para validação/debug):

| Campo Preview | Propósito | Manter? |
|---------------|-----------|---------|
| `ValidarIA` | Flag de validação | ✅ Sim (útil) |
| `MarcacaoIA` | Sugestão de marcação | ✅ Sim (útil) |
| `padrao_buscado` | Debug de classificação | ✅ Sim (útil) |
| `is_duplicate` | Flag de duplicata | ✅ Sim (útil) |
| `duplicate_reason` | Motivo duplicata | ✅ Sim (útil) |
| `session_id` | Controle de sessão | ✅ Sim (essencial) |
| `cartao` | Final do cartão | ✅ Sim (validação) |
| `TemParcela` | Flag booleana | ⚠️ Redundante (usar ParcelaAtual/TotalParcelas) |

---

## 🔧 CORREÇÕES NECESSÁRIAS

### 1. ⚠️ **Adicionar Campos Faltando em `journal_entries`**

```python
# app/domains/transactions/models.py - Adicionar:
class JournalEntry(Base):
    # ... campos existentes ...
    
    # 🆕 NOVOS CAMPOS (compatibilidade com preview)
    EstabelecimentoBase = Column(String)  # Sem parcela XX/YY
    ParcelaAtual = Column(Integer)         # Ex: 1 (de 12)
    # TotalParcelas JÁ existe (verificar nome)
    
    # VERIFICAR se TotalParcelas ou total_parcelas
```

### 2. ⚠️ **Adicionar Campos Faltando em `preview_transacoes`**

```python
# app/domains/upload/models.py - Adicionar:
class PreviewTransacao(Base):
    # ... campos existentes ...
    
    # 🆕 NOVOS CAMPOS (necessários para journal_entries)
    TipoTransacao = Column(String)  # 'CREDITO' ou 'DEBITO'
    Ano = Column(Integer)            # Extraído de data
    Mes = Column(Integer)            # Extraído de data (1-12)
```

### 3. ⚠️ **Atualizar Processadores**

#### Fase 1 (Raw) - Determinar TipoTransacao

```python
# app/domains/upload/processors/raw/*.py
# Adicionar lógica:

def determinar_tipo_transacao(tipo_documento: str, valor: float) -> str:
    """
    Determina se é CREDITO ou DEBITO
    
    Regras:
    - Fatura: valor negativo → DEBITO (compra)
    - Fatura: valor positivo → CREDITO (estorno/reembolso)
    - Extrato: valor negativo → DEBITO (saída)
    - Extrato: valor positivo → CREDITO (entrada)
    """
    if valor < 0:
        return 'DEBITO'
    else:
        return 'CREDITO'
```

#### Fase 2 (Marking) - Extrair Ano e Mes

```python
# app/domains/upload/processors/marker.py
# Adicionar em MarkedTransaction:

from datetime import datetime

def extrair_ano_mes(data_str: str) -> tuple[int, int]:
    """
    Extrai ano e mês de data DD/MM/YYYY
    
    Returns:
        (ano, mes) Ex: (2025, 12)
    """
    dt = datetime.strptime(data_str, '%d/%m/%Y')
    return dt.year, dt.month

# No método mark():
ano, mes = extrair_ano_mes(raw.data)
marked.ano = ano
marked.mes = mes
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

### Campos Obrigatórios (NOT NULL) - SEMPRE preenchidos?

- [x] `user_id` - ✅ Preenchido na Fase 1
- [x] `Data` - ✅ Preenchido na Fase 1 (raw.data)
- [x] `Estabelecimento` - ✅ Preenchido na Fase 1 (raw.lancamento)
- [x] `Valor` - ✅ Preenchido na Fase 1 (raw.valor)
- [x] `ValorPositivo` - ✅ Preenchido na Fase 2 (abs(valor))
- [ ] `TipoTransacao` - ❌ **NÃO preenchido** (CRIAR)
- [x] `IdTransacao` - ✅ Preenchido na Fase 2 (hash FNV-1a)

### Campos Opcionais - Verificar lógica

- [ ] `TipoGasto` - ⚠️ Pode ser NULL (não classificado)
- [ ] `GRUPO` - ⚠️ Pode ser NULL (não classificado)
- [ ] `SUBGRUPO` - ⚠️ Pode ser NULL (não classificado)
- [ ] `CategoriaGeral` - ⚠️ Pode ser NULL (não classificado)
- [x] `MesFatura` - ✅ Preenchido (YYYYMM) ou NULL (extrato)
- [ ] `Ano` - ❌ **NÃO preenchido** (CRIAR)
- [x] `NomeCartao` - ✅ Preenchido (fatura) ou NULL (extrato)
- [x] `IgnorarDashboard` - ✅ Default 0

---

## 🎯 PLANO DE AÇÃO

### Prioridade ALTA (Bloqueia funcionalidade)

1. **Adicionar `TipoTransacao` em preview e journal_entries**
   - Modificar models
   - Atualizar processadores (Fase 1 ou 2)
   - Testar upload extrato + fatura

2. **Adicionar `Ano` em preview e journal_entries**
   - Modificar models
   - Atualizar Fase 2 (Marking) para extrair ano
   - Validar filtros de dashboard que usam Ano

### Prioridade MÉDIA (Melhoria de consistência)

3. **Adicionar `EstabelecimentoBase`, `ParcelaAtual`, `TotalParcelas` em journal_entries**
   - Verificar se não quebra queries existentes
   - Atualizar service.py para salvar estes campos
   - Testar com faturas parceladas

4. **Adicionar `Mes` (opcional) em preview/journal**
   - Útil para filtros mensais sem parsear MesFatura
   - Extrair na Fase 2 junto com Ano

### Prioridade BAIXA (Otimização futura)

5. **Remover campo redundante `TemParcela` de preview**
   - Usar `ParcelaAtual IS NOT NULL` como flag
   - Simplificar lógica

---

## 📝 EXEMPLO DE FLUXO CORRETO

### Upload de Fatura (Cartão de Crédito)

```python
# Fase 1: Raw
raw = RawTransaction(
    data='15/12/2025',
    lancamento='NETFLIX (1/1)',
    valor=-39.90,
    banco='Itaú',
    tipo_documento='fatura',
    nome_cartao='Visa Itaú',
    # 🆕 NOVO
    tipo_transacao='DEBITO'  # valor negativo = compra
)

# Fase 2: Marking
marked = MarkedTransaction(
    ...raw.__dict__,
    id_transacao='ABC123...',
    estabelecimento_base='NETFLIX',
    valor_positivo=39.90,
    parcela_atual=1,
    total_parcelas=1,
    # 🆕 NOVO
    ano=2025,
    mes=12
)

# Fase 3: Classification
classified = ClassifiedTransaction(
    ...marked.__dict__,
    grupo='Assinaturas',
    subgrupo='Streaming',
    tipo_gasto='Ajustável',
    categoria_geral='Despesa',  # Cartão sempre Despesa
    origem_classificacao='Base Padrões'
)

# Confirmação: Salvar em journal_entries
journal = JournalEntry(
    user_id=1,
    Data='15/12/2025',
    Estabelecimento='NETFLIX (1/1)',
    EstabelecimentoBase='NETFLIX',  # 🆕
    Valor=-39.90,
    ValorPositivo=39.90,
    TipoTransacao='DEBITO',  # 🆕
    TipoGasto='Ajustável',
    GRUPO='Assinaturas',
    SUBGRUPO='Streaming',
    CategoriaGeral='Despesa',
    IdTransacao='ABC123...',
    IdParcela=None,
    ParcelaAtual=1,  # 🆕
    TotalParcelas=1,  # 🆕
    MesFatura='202512',
    Ano=2025,  # 🆕
    Mes=12,  # 🆕 (opcional)
    arquivo_origem='fatura-itau-202512.csv',
    banco_origem='Itaú',
    NomeCartao='Visa Itaú',
    tipodocumento='fatura',
    origem_classificacao='Base Padrões',
    IgnorarDashboard=0,
    upload_history_id=42
)
```

### Upload de Extrato (Conta Corrente)

```python
# Fase 1: Raw
raw = RawTransaction(
    data='15/01/2026',
    lancamento='PIX TRANSF EMANUEL15/01',
    valor=-1000.00,
    banco='BTG',
    tipo_documento='extrato',
    nome_cartao=None,
    # 🆕 NOVO
    tipo_transacao='DEBITO'  # valor negativo = saída
)

# Fase 2: Marking
marked = MarkedTransaction(
    ...raw.__dict__,
    id_transacao='XYZ789...',
    estabelecimento_base='PIX TRANSF EMANUEL15/01',  # Preserva data no nome
    valor_positivo=1000.00,
    parcela_atual=None,
    total_parcelas=None,
    # 🆕 NOVO
    ano=2026,
    mes=1
)

# Fase 3: Classification
classified = ClassifiedTransaction(
    ...marked.__dict__,
    grupo='Transferência Entre Contas',
    subgrupo='PIX',
    tipo_gasto='Transferência',
    categoria_geral='Transferência',  # Grupo contém "transferência"
    origem_classificacao='Regras Genéricas'
)

# Confirmação: Salvar em journal_entries
journal = JournalEntry(
    user_id=1,
    Data='15/01/2026',
    Estabelecimento='PIX TRANSF EMANUEL15/01',
    EstabelecimentoBase='PIX TRANSF EMANUEL15/01',  # 🆕
    Valor=-1000.00,
    ValorPositivo=1000.00,
    TipoTransacao='DEBITO',  # 🆕
    TipoGasto='Transferência',
    GRUPO='Transferência Entre Contas',
    SUBGRUPO='PIX',
    CategoriaGeral='Transferência',
    IdTransacao='XYZ789...',
    IdParcela=None,
    ParcelaAtual=None,  # 🆕
    TotalParcelas=None,  # 🆕
    MesFatura=None,  # Extrato não tem fatura
    Ano=2026,  # 🆕
    Mes=1,  # 🆕 (opcional)
    arquivo_origem='extrato-btg-202601.csv',
    banco_origem='BTG',
    NomeCartao=None,
    tipodocumento='extrato',
    origem_classificacao='Regras Genéricas',
    IgnorarDashboard=0,
    upload_history_id=43
)
```

---

## 🚨 IMPACTO EM QUERIES EXISTENTES

### Queries que podem quebrar após adicionar campos:

1. **Dashboard queries** - Verificar se usam `Ano` ou `Mes`
   - ✅ Atualmente usam `MesFatura` (YYYYMM) - sem impacto
   - ⚠️ Se começarem a usar `Ano`, precisa popular retroativamente

2. **Filtros de transações** - Verificar se usam `TipoTransacao`
   - ✅ Atualmente não usam - sem impacto
   - 🔮 Futuro: pode adicionar filtro por tipo

3. **Relatórios** - Verificar se usam campos de parcela
   - ⚠️ Alguns podem usar `IdParcela` - verificar se `ParcelaAtual` precisa retroativo

---

## 📌 PRÓXIMOS PASSOS

1. ⚠️ **Decidir:** Popular retroativamente ou apenas novos registros?
   - Se retroativo: criar script de migração
   - Se apenas novos: adicionar `nullable=True`

2. ⚠️ **Criar migration SQL** para adicionar colunas
   - `ALTER TABLE journal_entries ADD COLUMN TipoTransacao TEXT;`
   - `ALTER TABLE journal_entries ADD COLUMN Ano INTEGER;`
   - `ALTER TABLE journal_entries ADD COLUMN EstabelecimentoBase TEXT;`
   - `ALTER TABLE journal_entries ADD COLUMN ParcelaAtual INTEGER;`
   - `ALTER TABLE preview_transacoes ADD COLUMN TipoTransacao TEXT;`
   - `ALTER TABLE preview_transacoes ADD COLUMN Ano INTEGER;`
   - `ALTER TABLE preview_transacoes ADD COLUMN Mes INTEGER;`

3. ⚠️ **Atualizar processadores** (marker.py, raw/*.py)

4. ✅ **Testar com ambos tipos**:
   - Upload de fatura parcelada
   - Upload de extrato com PIX

---

## 🎯 RESUMO EXECUTIVO

**Campos FALTANDO:**
- 🔴 `TipoTransacao` (CRÍTICO - obrigatório em journal_entries)
- 🔴 `Ano` (CRÍTICO - usado em dashboard)
- 🟡 `EstabelecimentoBase` (IMPORTANTE - consistência)
- 🟡 `ParcelaAtual` (IMPORTANTE - parcelas)
- 🟢 `Mes` (OPCIONAL - conveniência)

**Ação Imediata:**
1. Adicionar `TipoTransacao` e `Ano` ANTES de próximo upload
2. Atualizar processadores para preencher estes campos
3. Testar com arquivo de teste (fatura + extrato)
