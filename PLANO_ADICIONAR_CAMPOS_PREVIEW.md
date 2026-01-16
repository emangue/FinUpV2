# 🎯 Plano: Adicionar Campos Faltantes em Preview_Transacoes

## 📋 Decisões Tomadas pelo Usuário

### ✅ Campos que NÃO serão criados em journal_entries:
- ❌ `EstabelecimentoBase` - Manter apenas em preview (debug/validação)
- ❌ `ParcelaAtual` - Manter apenas em preview (debug/validação)
- ❌ `TotalParcelas` - Manter apenas em preview (debug/validação)

### ✅ Campo cartao vs nome_cartao:
- `preview.cartao` = Final do cartão (ex: "1234") - **útil para validação**
- `preview.nome_cartao` = Nome completo (ex: "Visa Itaú") - **vai para journal**
- `journal.NomeCartao` = Copia de `preview.nome_cartao` ✅
- **Decisão:** Manter `cartao` em preview (útil), mas NÃO criar em journal

---

## 🔴 CAMPOS CRÍTICOS A ADICIONAR EM PREVIEW

### 1. TipoTransacao

**Lógica Atual (descoberta):**
```python
# Baseada em tipo_documento + presença de cartão
if nome_cartao:
    TipoTransacao = "Cartão de Crédito"
elif valor < 0:
    TipoTransacao = "Despesas"
else:
    TipoTransacao = "Receitas"
```

**Validação no banco:**
```sql
-- Cartão de Crédito: 1891 transações (100% tem nome_cartao)
-- Despesas: 1329 transações (100% extrato, valor negativo)
-- Receitas: 928 transações (100% extrato, valor positivo)
```

**❓ Resposta à dúvida do usuário:**
> "tipo transacao nao deveria usar somente o valor pra tipo transacao?"

**NÃO!** A lógica atual é:
1. **Primeiro** checa se tem cartão → se sim, é "Cartão de Crédito"
2. **Depois** usa o valor → negativo="Despesas", positivo="Receitas"

Isso está **correto** porque:
- Cartões de crédito são tratados separadamente (dashboard usa isso)
- Extratos separam entrada (Receitas) de saída (Despesas)

**Onde preencher:** ✅ **Fase 2 (Marking)** - após ter `nome_cartao` e `valor`

---

### 2. Ano

**Lógica:**
```python
# Extrair de data (DD/MM/YYYY)
from datetime import datetime
dt = datetime.strptime(data, '%d/%m/%Y')
ano = dt.year  # 2025, 2026, etc
```

**Onde preencher:** ✅ **Fase 2 (Marking)** - junto com outros campos temporais

---

### 3. Mes (Opcional mas útil)

**Lógica:**
```python
# Extrair de data (DD/MM/YYYY)
dt = datetime.strptime(data, '%d/%m/%Y')
mes = dt.month  # 1 a 12
```

**Onde preencher:** ✅ **Fase 2 (Marking)** - junto com Ano

**Benefício:** Filtros mensais sem parsear `MesFatura` (que é YYYYMM)

---

## 🛠️ IMPLEMENTAÇÃO - PASSO A PASSO

### PASSO 1: Adicionar Colunas no Banco

```sql
-- Migration SQL
ALTER TABLE preview_transacoes ADD COLUMN TipoTransacao TEXT;
ALTER TABLE preview_transacoes ADD COLUMN Ano INTEGER;
ALTER TABLE preview_transacoes ADD COLUMN Mes INTEGER;
```

### PASSO 2: Atualizar Model de Preview

**Arquivo:** `app/domains/upload/models.py`

```python
class PreviewTransacao(Base):
    # ... campos existentes ...
    
    # Fase 2: IDs e Normalização (ADICIONAR)
    TipoTransacao = Column(String)  # "Cartão de Crédito", "Despesas", "Receitas"
    Ano = Column(Integer)            # 2025, 2026, etc
    Mes = Column(Integer)            # 1 a 12
```

### PASSO 3: Atualizar Dataclass MarkedTransaction

**Arquivo:** `app/domains/upload/processors/marker.py`

```python
@dataclass
class MarkedTransaction(RawTransaction):
    """
    Transação com IDs marcados
    """
    
    # Campos de identificação
    id_transacao: str = ""
    estabelecimento_base: str = ""
    valor_positivo: float = 0.0
    
    # Campos de parcela
    id_parcela: Optional[str] = None
    parcela_atual: Optional[int] = None
    total_parcelas: Optional[int] = None
    
    # 🆕 NOVOS CAMPOS
    tipo_transacao: str = ""         # "Cartão de Crédito", "Despesas", "Receitas"
    ano: int = 0                     # 2025, 2026, etc
    mes: int = 0                     # 1 a 12
```

### PASSO 4: Implementar Lógica no Marker

**Arquivo:** `app/domains/upload/processors/marker.py`

```python
class TransactionMarker:
    def mark(self, raw: RawTransaction) -> MarkedTransaction:
        """
        Marca transação com IDs únicos e campos temporais
        """
        # ... código existente ...
        
        # 🆕 Extrair ano e mês da data
        ano, mes = self._extrair_ano_mes(raw.data)
        
        # 🆕 Determinar tipo de transação
        tipo_transacao = self._determinar_tipo_transacao(
            raw.nome_cartao, 
            raw.valor
        )
        
        return MarkedTransaction(
            **raw.__dict__,
            id_transacao=id_transacao,
            estabelecimento_base=estabelecimento_base,
            valor_positivo=valor_positivo,
            id_parcela=id_parcela,
            parcela_atual=info_parcela['parcela'] if info_parcela else None,
            total_parcelas=info_parcela['total'] if info_parcela else None,
            # 🆕 NOVOS CAMPOS
            tipo_transacao=tipo_transacao,
            ano=ano,
            mes=mes
        )
    
    def _extrair_ano_mes(self, data_str: str) -> tuple[int, int]:
        """
        Extrai ano e mês de data DD/MM/YYYY
        
        Returns:
            (ano, mes) Ex: (2025, 12)
        """
        from datetime import datetime
        try:
            dt = datetime.strptime(data_str, '%d/%m/%Y')
            return dt.year, dt.month
        except ValueError as e:
            logger.error(f"Erro ao parsear data '{data_str}': {e}")
            # Fallback: tentar extrair manualmente
            partes = data_str.split('/')
            if len(partes) == 3:
                return int(partes[2]), int(partes[1])
            raise ValueError(f"Data inválida: {data_str}")
    
    def _determinar_tipo_transacao(
        self, 
        nome_cartao: Optional[str], 
        valor: float
    ) -> str:
        """
        Determina tipo de transação baseado em cartão e valor
        
        Regras (mesma lógica atual do sistema):
        1. Se tem cartão → "Cartão de Crédito"
        2. Se extrato + negativo → "Despesas"
        3. Se extrato + positivo → "Receitas"
        
        Returns:
            "Cartão de Crédito" | "Despesas" | "Receitas"
        """
        # Regra 1: Cartão sempre primeiro
        if nome_cartao and nome_cartao.strip():
            return "Cartão de Crédito"
        
        # Regra 2 e 3: Baseado no sinal
        if valor < 0:
            return "Despesas"
        else:
            return "Receitas"
```

### PASSO 5: Atualizar Dataclass ClassifiedTransaction

**Arquivo:** `app/domains/upload/processors/classifier.py`

```python
@dataclass
class ClassifiedTransaction(MarkedTransaction):
    """
    Transação classificada
    """
    
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    tipo_gasto: Optional[str] = None
    categoria_geral: Optional[str] = None
    origem_classificacao: str = 'Não Classificado'
    padrao_buscado: Optional[str] = None
    marcacao_ia: Optional[str] = None
    
    # ✅ Herda automaticamente: tipo_transacao, ano, mes
```

### PASSO 6: Atualizar Salvamento no Banco (Preview)

**Arquivo:** `app/domains/upload/service.py`

Localizar onde `PreviewTransacao` é criado e adicionar os novos campos:

```python
# Procurar por: preview_obj = PreviewTransacao(...)

preview_obj = PreviewTransacao(
    # ... campos existentes ...
    
    # Fase 2: Marking
    IdTransacao=classified.id_transacao,
    IdParcela=classified.id_parcela,
    EstabelecimentoBase=classified.estabelecimento_base,
    ParcelaAtual=classified.parcela_atual,
    TotalParcelas=classified.total_parcelas,
    ValorPositivo=classified.valor_positivo,
    # 🆕 NOVOS CAMPOS
    TipoTransacao=classified.tipo_transacao,
    Ano=classified.ano,
    Mes=classified.mes,
    
    # Fase 3: Classification
    GRUPO=classified.grupo,
    # ...
)
```

### PASSO 7: Atualizar Confirmação (Journal Entries)

**Arquivo:** `app/domains/upload/service.py`

Localizar método `confirm_upload` onde `JournalEntry` é criado:

```python
nova_transacao = JournalEntry(
    user_id=user_id,
    Data=item.data,
    Estabelecimento=item.lancamento,
    Valor=item.valor,
    ValorPositivo=item.valor_positivo,
    # 🆕 ADICIONAR
    TipoTransacao=item.TipoTransacao,  # ✅ JÁ existe em journal
    Ano=item.Ano,                       # ✅ JÁ existe em journal
    # Mes não vai para journal (opcional)
    
    MesFatura=item.mes_fatura.replace('-', '') if item.mes_fatura else None,
    arquivo_origem=item.nome_arquivo,
    banco_origem=item.banco,
    NomeCartao=item.nome_cartao,
    IdTransacao=item.id_transacao,
    IdParcela=item.id_parcela,
    # ❌ NÃO adicionar EstabelecimentoBase, ParcelaAtual, TotalParcelas (decisão do usuário)
    
    GRUPO=item.grupo,
    SUBGRUPO=item.subgrupo,
    TipoGasto=item.tipo_gasto,
    CategoriaGeral=item.categoria_geral,
    origem_classificacao=item.origem_classificacao,
    tipodocumento=item.tipo_documento,
    upload_history_id=history.id,
    created_at=now,
)
```

---

## 🧪 TESTES NECESSÁRIOS

### Teste 1: Upload de Fatura com Parcelas

**Arquivo:** `fatura-teste.csv`
```csv
Data,Estabelecimento,Valor
15/12/2025,NETFLIX (1/1),-39.90
15/12/2025,MERCADO (3/12),-150.00
```

**Validações:**
- ✅ `TipoTransacao = "Cartão de Crédito"`
- ✅ `Ano = 2025`
- ✅ `Mes = 12`
- ✅ `EstabelecimentoBase = "NETFLIX"` e `"MERCADO"` (só em preview)
- ✅ `ParcelaAtual = 1` e `3` (só em preview)

### Teste 2: Upload de Extrato (Receitas e Despesas)

**Arquivo:** `extrato-teste.csv`
```csv
Data,Lançamento,Valor
15/01/2026,PIX TRANSF EMANUEL,-1000.00
20/01/2026,Pix recebido de João,500.00
```

**Validações:**
- ✅ PIX saída: `TipoTransacao = "Despesas"`, `Ano = 2026`, `Mes = 1`
- ✅ PIX entrada: `TipoTransacao = "Receitas"`, `Ano = 2026`, `Mes = 1`
- ✅ Sem cartão: `NomeCartao = NULL`
- ✅ Sem parcela: `EstabelecimentoBase = lancamento original`

### Teste 3: Validar Journal Entries Após Confirmação

```sql
-- Deve ter TipoTransacao e Ano preenchidos
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN TipoTransacao IS NULL THEN 1 ELSE 0 END) as tipo_null,
    SUM(CASE WHEN Ano IS NULL THEN 1 ELSE 0 END) as ano_null
FROM journal_entries
WHERE upload_history_id = <ID_DO_TESTE>;
```

**Resultado esperado:** `tipo_null = 0`, `ano_null = 0`

---

## 📊 CHECKLIST FINAL

### Banco de Dados
- [ ] Migration SQL executada (TipoTransacao, Ano, Mes em preview)
- [ ] Colunas criadas com sucesso
- [ ] Índices adicionados se necessário

### Models
- [ ] `PreviewTransacao` atualizado (3 campos novos)
- [ ] `MarkedTransaction` atualizado (3 campos novos)
- [ ] `ClassifiedTransaction` herda automaticamente

### Processadores
- [ ] `TransactionMarker` implementa `_extrair_ano_mes()`
- [ ] `TransactionMarker` implementa `_determinar_tipo_transacao()`
- [ ] `TransactionMarker.mark()` preenche os 3 campos novos

### Service
- [ ] Salvamento em `preview_transacoes` inclui novos campos
- [ ] Confirmação em `journal_entries` copia `TipoTransacao` e `Ano`
- [ ] **NÃO** copia `Mes`, `EstabelecimentoBase`, `ParcelaAtual`, `TotalParcelas`

### Testes
- [ ] Upload de fatura funciona
- [ ] Upload de extrato funciona
- [ ] `TipoTransacao` correta em ambos os casos
- [ ] `Ano` e `Mes` preenchidos corretamente
- [ ] Journal entries tem `TipoTransacao` e `Ano` após confirmação

### Validação
- [ ] Dashboard continua funcionando (usa `TipoTransacao = 'Cartão de Crédito'`)
- [ ] Filtros de transações continuam funcionando
- [ ] Nenhuma query quebrada

---

## 🎯 RESUMO EXECUTIVO

**Campos a Adicionar em Preview:**
1. 🔴 **TipoTransacao** - Lógica: cartão→"Cartão de Crédito" | negativo→"Despesas" | positivo→"Receitas"
2. 🔴 **Ano** - Extrair de data (DD/MM/YYYY)
3. 🟡 **Mes** - Extrair de data (1-12)

**Onde preencher:** ✅ Fase 2 (Marking) - `marker.py`

**O que vai para Journal:**
- ✅ TipoTransacao
- ✅ Ano
- ❌ Mes (opcional, fica só em preview)
- ❌ EstabelecimentoBase (fica só em preview)
- ❌ ParcelaAtual (fica só em preview)
- ❌ TotalParcelas (fica só em preview)

**Decisão sobre `cartao`:**
- Manter em preview (útil para validação)
- NÃO criar em journal (já tem `NomeCartao`)

**Próximo Passo:** Implementar! Começar pelo PASSO 1 (Migration SQL).
