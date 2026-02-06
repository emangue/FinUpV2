# 🔍 Análise: Diferença Saldo e Investimentos (Desktop vs Mobile)

**Data:** 01/02/2026 21:45  
**Status:** 🐛 BUG IDENTIFICADO  
**Prioridade:** ⚠️ ALTA

---

## 🎯 Problema Reportado

Usuário reportou que:
1. **Saldo e Investimentos** no Dashboard Mobile não batem com o Desktop
2. **Metas (Trackers)** não aparecem no Dashboard Mobile

---

## 📊 Comparação: Desktop vs Mobile

### Dados na Imagem (Mobile - Fev/2026, modo "Ano"):
```
Receitas:      R$ 477.091,74
Despesas:      R$ 316.264,20
Saldo:         R$  63.783,17
Investimentos: R$  97.044,37
```

### Teste Backend (Fevereiro 2025 - Modo Mês):

#### Endpoint Desktop: `/dashboard/metrics?year=2025&month=2`
```json
{
  "total_receitas": 29532.66,
  "total_despesas": 21312.24,
  "saldo_periodo": 8220.42,  // ✅ Receitas - Despesas (sem investimentos)
  "num_transacoes": 158
}
```

#### Endpoint Mobile: `/transactions/receitas-despesas?data_inicio=2025-02-01&data_fim=2025-02-28`
```json
{
  "receitas": 29532.66,      // ✅ IGUAL ao desktop
  "despesas": 21312.24,      // ✅ IGUAL ao desktop
  "investimentos": 4898.32,  // ✅ NOVO (não existe no desktop)
  "saldo": 3322.10           // ❌ DIFERENTE (receitas - despesas - investimentos)
}
```

**Diferença:**
- Desktop: `saldo = receitas - despesas` (8.220,42)
- Mobile: `saldo = receitas - despesas - investimentos` (3.322,10)

---

## 🐛 Bug Identificado: YTD Incorreto

### O Que Esperávamos (YTD):
**"Ano" = Últimos 12 meses** (Out/2025 a Fev/2026)

### O Que Está Acontecendo:
**"Ano" = Janeiro até mês selecionado** (Jan/2026 a Fev/2026)

### Código Atual (`dashboard/page.tsx`, linha 56-58):
```typescript
else {
  // Year-to-Date (Janeiro até mês selecionado)  ❌ ERRADO
  startDate = startOfYear(selectedMonth)  // Janeiro do ano
  endDate = endOfMonth(selectedMonth)
}
```

### Teste (Modo "Ano", Fev/2026):

#### Desktop: `year=2026` (ano completo)
```json
{
  "total_receitas": 14830.40,
  "total_despesas": 520.00,
  "saldo_periodo": 14310.40
}
```

#### Mobile: `data_inicio=2025-10-01&data_fim=2026-02-28` (últimos 5 meses)
```json
{
  "receitas": 110611.75,
  "despesas": 72402.71,
  "investimentos": 11775.07,
  "saldo": 26433.97
}
```

**❌ VALORES COMPLETAMENTE DIFERENTES!**

Desktop mostra **só Janeiro/2026 até agora** (2 meses).  
Mobile mostra **Out/2025 a Fev/2026** (5 meses).

---

## 🧮 Cálculo de Saldo: Desktop vs Mobile

### Desktop (`/dashboard/metrics`):
```typescript
// Código: dashboard/repository.py, linha 71
saldo_periodo = total_receitas + despesas_raw  // despesas_raw é NEGATIVO
```

**Lógica:**
- `despesas_raw` = SUM(Valor) onde Valor é NEGATIVO
- `saldo = receitas + despesas_raw`
- Ex: `8220.42 = 29532.66 + (-21312.24)`

**Não inclui investimentos no saldo.**

---

### Mobile (`/transactions/receitas-despesas`):
```python
# Código: transactions/service.py, linha após query de investimentos
receitas = float(receitas_result or 0)
despesas = abs(float(despesas_result or 0))
investimentos = abs(float(investimentos_result or 0))
saldo = receitas - despesas - investimentos
```

**Lógica:**
- `despesas` = ABS(SUM(Valor)) = valor POSITIVO
- `investimentos` = ABS(SUM(Valor)) = valor POSITIVO
- `saldo = receitas - despesas - investimentos`
- Ex: `3322.10 = 29532.66 - 21312.24 - 4898.32`

**Inclui investimentos no saldo.**

---

## 🎯 Decisões a Tomar

### 1. **Saldo Deve Incluir Investimentos?**

**Opção A:** Desktop está correto (não incluir)
- Investimentos não são "gastos", são alocação de patrimônio
- Saldo = dinheiro disponível (receitas - despesas)
- Mobile deveria seguir mesma lógica

**Opção B:** Mobile está correto (incluir)
- Investimentos reduzem dinheiro disponível no curto prazo
- Saldo = fluxo de caixa real (saídas - entradas)
- Desktop deveria adicionar campo de investimentos

**Recomendação:** Seguir **Opção A** (lógica do desktop). Investimentos são mostrados separadamente, não entram no saldo.

---

### 2. **YTD = Janeiro-Atual ou Últimos 12 Meses?**

**Opção A:** YTD = Janeiro até agora (Year-To-Date tradicional)
- Ex: Fev/2026 → Jan/2026 a Fev/2026
- Padrão em finanças corporativas

**Opção B:** YTD = Últimos 12 meses (Rolling 12 months)
- Ex: Fev/2026 → Mar/2025 a Fev/2026
- Melhor para análise de tendências

**Contexto do PRD (Seção 4.1.2):**
> "Visualizar acumulado do ano (Janeiro até o mês selecionado)"

**Recomendação:** Seguir **Opção A** (Janeiro até mês selecionado), conforme PRD.

---

## ✅ Solução Proposta

### 1. **Corrigir Cálculo de Saldo no Mobile**

**Antes:**
```python
saldo = receitas - despesas - investimentos
```

**Depois:**
```python
saldo = receitas - despesas  # Investimentos mostrados separadamente
```

**Impacto:** Saldo Mobile passará a bater com Desktop.

---

### 2. **Manter YTD = Janeiro até mês selecionado**

O código já está correto (`startOfYear(selectedMonth)`). O que precisa é **validar se está buscando os dados certos**.

**Código atual (`dashboard/page.tsx`, linha 56-58):**
```typescript
else {
  // Year-to-Date (Janeiro até mês selecionado)
  startDate = startOfYear(selectedMonth)  // ✅ Correto
  endDate = endOfMonth(selectedMonth)
}
```

**Exemplo (Fev/2026):**
- `startDate = 2026-01-01`
- `endDate = 2026-02-28`

**Teste no Backend:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/transactions/receitas-despesas?data_inicio=2026-01-01&data_fim=2026-02-28"
```

**Resultado esperado:** Dados de Janeiro e Fevereiro de 2026 (não Out/2025).

---

### 3. **Adicionar Card de Investimentos Separado**

Investimentos devem aparecer como **métrica separada**, não integrada ao saldo.

**Layout:**
```
┌─────────────────────────┐
│ Receitas                │
│ R$ 477.091,74          │
└─────────────────────────┘

┌─────────────────────────┐
│ Despesas                │
│ R$ 316.264,20          │
└─────────────────────────┘

┌─────────────────────────┐
│ Saldo                   │
│ R$ 160.827,54          │  ← receitas - despesas
└─────────────────────────┘

┌─────────────────────────┐
│ Investimentos           │
│ R$ 97.044,37           │  ← mostrado separadamente
└─────────────────────────┘
```

---

## 🎯 Questão 2: Metas (Trackers) no Dashboard

### Resposta: NÃO, não estão no escopo do Dashboard Mobile V1.0

**Conforme PRD (Seção 4.1):**
```
Dashboard Mobile contém:
1. MonthScrollPicker
2. YTDToggle
3. Métricas Principais (4 cards)
4. [Futura] CTA "Importar Arquivo"
```

**Metas (Trackers) estão em:**
- **Sprint 2:** Tela `/mobile/budget` (já implementada)
- **PRD Seção 4.3:** Metas (Budget) Mobile

**Localização:**
```
/mobile/dashboard → Métricas gerais (receitas, despesas, saldo, investimentos)
/mobile/budget    → Metas por categoria (Trackers)
```

**Ícone na Bottom Navigation:**
- 🎯 **Metas** (terceiro ícone) → Vai para `/mobile/budget`

---

## 📋 Checklist de Correções

### Prioridade ALTA (Corrigir agora):
- [ ] Corrigir cálculo de saldo no mobile (remover investimentos)
- [ ] Validar se YTD está buscando período correto (Jan-Atual)
- [ ] Testar Desktop vs Mobile (devem bater)

### Prioridade MÉDIA (Sprint 3+):
- [ ] Adicionar CTA "Importar Arquivo" no Dashboard Mobile
- [ ] Melhorar feedback visual de loading

### Fora do Escopo V1.0:
- [ ] Trackers no Dashboard (já estão em `/mobile/budget`)

---

## 🧪 Testes de Validação

### Cenário 1: Fev/2026, Modo "Mês"
```bash
# Desktop
curl "http://localhost:8000/api/v1/dashboard/metrics?year=2026&month=2"

# Mobile
curl "http://localhost:8000/api/v1/transactions/receitas-despesas?data_inicio=2026-02-01&data_fim=2026-02-28"

# Esperado:
# - Receitas iguais ✅
# - Despesas iguais ✅
# - Saldo iguais ✅ (após correção)
# - Investimentos só no Mobile ✅
```

### Cenário 2: Fev/2026, Modo "Ano" (YTD)
```bash
# Desktop
curl "http://localhost:8000/api/v1/dashboard/metrics?year=2026"

# Mobile
curl "http://localhost:8000/api/v1/transactions/receitas-despesas?data_inicio=2026-01-01&data_fim=2026-02-28"

# Esperado:
# - Ambos somam Jan+Fev/2026 ✅
# - Valores devem bater ✅
```

---

## 📚 Referências

- **PRD:** `/docs/features/mobile-v1/01-PRD/PRD.md` (Seção 4.1)
- **Style Guide:** `/docs/features/mobile-v1/01-PRD/STYLE_GUIDE.md`
- **Código Desktop:** `app_dev/frontend/src/app/dashboard/page.tsx`
- **Código Mobile:** `app_dev/frontend/src/app/mobile/dashboard/page.tsx`
- **Service Desktop:** `app_dev/backend/app/domains/dashboard/repository.py`
- **Service Mobile:** `app_dev/backend/app/domains/transactions/service.py`

---

**Status:** 🐛 BUG IDENTIFICADO - Aguardando decisão do usuário  
**Data de Criação:** 01/02/2026 21:45  
**Próximos Passos:** Implementar correção no cálculo de saldo
