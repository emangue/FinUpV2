# PROPOSTA DE MARCAÇÕES GENÉRICAS - Sistema de Finanças V5
## Análise da JournalEntry - Janeiro 2026

### RESUMO EXECUTIVO

Com base na análise de **4.141 transações** na base de dados, identificamos oportunidades significativas para automatização através de marcações genéricas. A análise revelou:

- ✅ **27 candidatos ideais** com classificação consistente (>=5 transações)
- ⚠️ **20 estabelecimentos** que precisam de padronização 
- 🔍 **8 padrões** baseados em palavras-chave para automação

---

## 1. CANDIDATOS PRIORITÁRIOS (Implementação Imediata)

### 1.1 Categoria: TRANSPORTE - UBER
**Estabelecimentos:** `Uber* Trip`, `UBER* TRIP`, `Uber * Pending`, `UBER* PENDING`, `UBER *UBER *TRIP`

```json
{
  "padrão": "(?i).*(uber|UBER).*",
  "grupo": "Transporte",
  "subgrupo": "Uber", 
  "tipo_gasto": "Ajustável",
  "prioridade": "ALTA",
  "frequencia": 251,
  "valor_medio": -45.07
}
```

### 1.2 Categoria: INVESTIMENTOS - MERCADO PAGO
**Estabelecimentos:** `Rendimentos`, `Reserva por gastos Emergência`, `Reserva por gasto Emergência`, `Dinheiro retirado Emergência`

```json
{
  "padrão": "(?i).*(rendimentos|reserva|emergência).*",
  "grupo": "Investimentos", 
  "subgrupo": "MP",
  "tipo_gasto": "Investimentos",
  "prioridade": "ALTA",
  "frequencia": 804,
  "valor_medio": "variável"
}
```

### 1.3 Categoria: ASSINATURAS - APPLE
**Estabelecimentos:** `Apple.com/bill`, `APPLE.COM/BILL`

```json
{
  "padrão": "(?i).*(apple\\.com|APPLE\\.COM).*",
  "grupo": "Assinaturas",
  "subgrupo": "Apple", 
  "tipo_gasto": "Ajustável",
  "prioridade": "ALTA",
  "frequencia": 59,
  "valor_medio": -35.48
}
```

### 1.4 Categoria: ALIMENTAÇÃO - DELIVERY
**Estabelecimentos:** `Vendify Cond Lodz`, `VFY COMERCIO LOCACAO E`

```json
{
  "padrão": "(?i).*(vendify|vfy).*",
  "grupo": "Alimentação",
  "subgrupo": "Delivery",
  "tipo_gasto": "Ajustável", 
  "prioridade": "MÉDIA",
  "frequencia": 57,
  "valor_medio": -29.82
}
```

### 1.5 Categoria: CARRO - CONECTCAR
**Estabelecimentos:** `Pagamento CONECTCAR` (diferentes variações)

```json
{
  "padrão": "(?i).*(conectcar|connect car).*",
  "grupo": "Carro",
  "subgrupo": "ConnectCar",
  "tipo_gasto": "Ajustável",
  "prioridade": "MÉDIA", 
  "frequencia": 170,
  "valor_medio": -14.46
}
```

---

## 2. REGRAS GENÉRICAS POR PALAVRA-CHAVE

### 2.1 Serviços Streaming/Assinaturas
```json
{
  "spotify": {
    "padrão": "(?i).*spotify.*",
    "grupo": "Assinaturas", 
    "subgrupo": "Spotify",
    "frequencia": 23
  },
  "netflix": {
    "padrão": "(?i).*netflix.*", 
    "grupo": "Assinaturas",
    "subgrupo": "Netflix"
  }
}
```

### 2.2 E-commerce
```json
{
  "amazon": {
    "padrão": "(?i).*amazon.*",
    "grupo": "Assinaturas",
    "subgrupo": "Amazon",
    "frequencia": 28
  },
  "mercadolivre": {
    "padrão": "(?i).*(mercadolivre|mercado livre).*",
    "grupo": "MeLi + Amazon", 
    "subgrupo": "MeLi + Amazon"
  }
}
```

### 2.3 Alimentação
```json
{
  "burger": {
    "padrão": "(?i).*burger.*",
    "grupo": "Entretenimento",
    "subgrupo": "Saídas",
    "frequencia": 21
  },
  "supermercado": {
    "padrão": "(?i).*(supermercado|atacadista).*",
    "grupo": "Alimentação",
    "subgrupo": "Supermercado"
  }
}
```

---

## 3. CASOS QUE PRECISAM DE PADRONIZAÇÃO

### 3.1 ESTABELECIMENTO: "Pagamento CONECTCAR"
**Problema:** Classificado inconsistentemente em 4 subgrupos diferentes
- `ConnectCar` (73 vezes) ✅ Correto
- `Sem Parar` (97 vezes) ⚠️ Incorreto
- `Estacionamento` (38 vezes) ⚠️ Incorreto  
- `Outros` (1 vez) ⚠️ Incorreto

**Solução:** Padronizar TODOS para `Carro > ConnectCar`

### 3.2 ESTABELECIMENTO: "CONTA VIVO" 
**Problema:** Classificado em 2 subgrupos
- `Celular` (24 vezes) ✅ Correto
- `Internet` (23 vezes) ⚠️ Pode estar correto para combo

**Solução:** Definir regra baseada no valor ou criar subgrupo `Vivo Combo`

### 3.3 ESTABELECIMENTO: "Apple.com/bill"
**Problema:** Classificado em 7 subgrupos diferentes
- `Apple` (31 vezes) ✅ Correto
- `Google Photos`, `Paramount+`, etc. ⚠️ Incorreto

**Solução:** Padronizar TODOS para `Assinaturas > Apple`

---

## 4. IMPLEMENTAÇÃO TÉCNICA

### 4.1 Tabela de Regras Genéricas
```sql
CREATE TABLE IF NOT EXISTS generic_classification_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_regra TEXT NOT NULL,
    padrao_regex TEXT NOT NULL,
    grupo TEXT NOT NULL,
    subgrupo TEXT NOT NULL, 
    tipo_gasto TEXT NOT NULL,
    prioridade INTEGER DEFAULT 1,
    ativo BOOLEAN DEFAULT 1,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Função de Aplicação
```python
def aplicar_marcacao_generica(estabelecimento: str) -> dict:
    """
    Aplica regras de marcação genérica baseadas no estabelecimento
    
    Ordem de prioridade:
    1. Correspondência exata (base_marcacoes)
    2. Regras regex (generic_classification_rules) 
    3. Regras por palavra-chave
    4. Classificação manual/padrão
    """
    
    # Buscar em generic_classification_rules
    for regra in get_regras_ativas():
        if re.match(regra.padrao_regex, estabelecimento):
            return {
                'grupo': regra.grupo,
                'subgrupo': regra.subgrupo, 
                'tipo_gasto': regra.tipo_gasto,
                'origem': f'regra_generica_{regra.nome_regra}'
            }
    
    return None
```

### 4.3 Integração no Upload
```python
def process_transaction_classification(estabelecimento: str):
    """Ordem de aplicação das regras de classificação"""
    
    # 1. Verificar base_marcacoes (específicas)
    marcacao_especifica = buscar_marcacao_especifica(estabelecimento)
    if marcacao_especifica:
        return marcacao_especifica
    
    # 2. Aplicar regras genéricas 
    marcacao_generica = aplicar_marcacao_generica(estabelecimento)
    if marcacao_generica:
        return marcacao_generica
        
    # 3. Usar classificação padrão/manual
    return classificacao_padrao()
```

---

## 5. PLANO DE IMPLEMENTAÇÃO

### Fase 1 - Regras Prioritárias (1 semana)
1. ✅ Implementar regras para UBER (251 transações)
2. ✅ Implementar regras para Investimentos MP (804 transações) 
3. ✅ Implementar regras para Apple (59 transações)
4. ✅ Testar em ambiente de desenvolvimento

### Fase 2 - Padronização (1 semana) 
1. ⚠️ Corrigir classificações inconsistentes do CONECTCAR
2. ⚠️ Padronizar Apple.com/bill 
3. ⚠️ Revisar outros casos inconsistentes
4. ✅ Validar correções

### Fase 3 - Expansão (2 semanas)
1. 🔍 Implementar regras por palavra-chave
2. 🔍 Criar interface de gerenciamento de regras
3. 🔍 Sistema de logs para tracking de aplicação
4. 🔍 Relatórios de eficácia das regras

---

## 6. MÉTRICAS DE SUCESSO

### Cobertura Esperada
- **Fase 1:** 1.114 transações automatizadas (26.9% do total)
- **Fase 2:** +400 transações padronizadas (36.6% do total)  
- **Fase 3:** +500 transações com regras expandidas (48.7% do total)

### KPIs
- ✅ % de transações classificadas automaticamente
- ✅ Redução no tempo de upload/validação
- ✅ Consistência de classificação (mesmo estabelecimento = mesma classificação)
- ✅ % de transações que precisam de revisão manual

---

## 7. RISCOS E MITIGAÇÕES

### Risco: Over-classification
**Problema:** Regras muito amplas classificam incorretamente
**Mitigação:** Começar com regras específicas e expandir gradualmente

### Risco: Conflito de Regras  
**Problema:** Múltiplas regras aplicáveis ao mesmo estabelecimento
**Mitigação:** Sistema de prioridades clara (específico > genérico)

### Risco: Performance
**Problema:** Muitas regras regex podem impactar performance
**Mitigação:** Cache de resultados + índices otimizados

---

## 8. NEXT STEPS

1. **Aprovação da proposta** ✋ 
2. **Implementação da tabela `generic_classification_rules`**
3. **Desenvolvimento das funções de aplicação**
4. **Testes com dados históricos**
5. **Deploy gradual (Fase 1 → 2 → 3)**

---

**Total de transações analisadas:** 4.141  
**Potencial de automação:** ~2.000 transações (48.3%)  
**Redução estimada no trabalho manual:** 60-70%  

**Data da análise:** 16 de Janeiro de 2026  
**Responsável:** GitHub Copilot