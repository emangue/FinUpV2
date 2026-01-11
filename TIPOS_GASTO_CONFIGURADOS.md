# Relatório de Tipos de Gasto Configurados

## Configurações Atualizadas - Budget Detalhe

### ✅ Casa
**Filtro:** `GRUPO = 'Casa'`  
**Tipos de Gasto Incluídos:**
- Ajustável - Casa
- Fixo
- Débito
- Investimento - Ajustável

**Status:** ✅ Corrigido (antes era "Moradia")

### ✅ Cartão de Crédito
**Filtro:** `TipoTransacao = 'Cartão'`  
**Tipos de Gasto Incluídos:**
- Ajustável
- Fixo
- Ajustável - Delivery
- Ajustável - Saídas
- Ajustável - Supermercado
- Ajustável - Roupas
- Ajustável - Presentes
- Ajustável - Assinaturas
- Ajustável - Tech

**Status:** ✅ OK

### ✅ Doações
**Filtro:** `GRUPO = 'Doações'`  
**Tipos de Gasto Incluídos:**
- Ajustável - Doações

**Status:** ✅ OK (único tipo disponível)

### ✅ Saúde
**Filtro:** `GRUPO = 'Saúde'`  
**Tipos de Gasto Incluídos:**
- Ajustável - Esportes

**Status:** ✅ OK (único tipo disponível)

### ✅ Viagens
**Fios:**
- Ajustável - Viagens

**Status:** ✅ OK (único tipo disponível)

### ✅ Outros
**Filtro:** `GRUPO = 'Outros'`  
**Tipos de Gasto Incluídos:**
- Ajustável - Carro
- Ajustável - Uber
- Ajustável
- Receita - Outras

**Status:** ✅ Atualizado (adicionado "Ajustável" e "Receita - Outras")

## Endpoint Criado

### GET `/api/v1/budget/tipos-gasto-disponiveis`

**Query Parameters:**
- `fonte_dados`: "GRUPO" ou "TIPO_TRANSACAO"
- `filtro_valor`: Nome do grupo ou tipo de transação
- `user_id`: ID do usuário

**Exemplo:**
```bash
curl "http://localhost:8000/api/v1/budget/tipos-gasto-disponiveis?fonte_dados=GRUPO- Ajustável - Tech

**Ststa:**
```json
{
  "tipos_gasto": [
    "Ajustável - Casa",
    "Débito",
    "Fixo",
    "Investimento - Ajustável"
  ]
}
```

## Observações

1. **Acentuação:** Alguns tipos de gasto aparecem com variações de acentuação nas transações (ex: "Ajustavel" vs "Ajustável")
2. **Case Sensitive:** Filtros de grupo são case-sensitive ("Casa" ≠ "casa")
3. **Validação Automática:** Use o endpoint antes de configurar para garantir que todos os tipos estão incluídos

