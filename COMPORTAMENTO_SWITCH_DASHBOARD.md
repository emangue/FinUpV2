# 🎚️ Comportamento do Switch "Dashboard" nas Transações

## 📋 Como Funciona

### Switch de Dashboard
Cada transação possui um switch que controla se ela aparece ou não no dashboard.

**Campo no banco:** `IgnorarDashboard` (0 ou 1)

### Estados do Switch

| Switch Visual | Valor no Banco | Significado | Aparece no Dashboard? |
|--------------|----------------|-------------|----------------------|
| ⚫ **LIGADO** (preto) | `IgnorarDashboard = 0` | Incluir no dashboard | ✅ **SIM** |
| ⚪ DESLIGADO (cinza) | `IgnorarDashboard = 1` | Ignorar no dashboard | ❌ **NÃO** |

### Exemplos de Uso

**Quando LIGAR o switch (incluir no dashboard):**
- Despesas normais: alimentação, transporte, compras
- Receitas: salário, freelance, vendas
- Gastos com cartão que você quer controlar

**Quando DESLIGAR o switch (ignorar no dashboard):**
- Transferências entre contas próprias (TED, PIX entre suas contas)
- Rendimentos automáticos de investimentos
- Pagamentos de parcelas internas
- Ajustes contábeis
- Transações duplicadas

---

## 🔄 Fluxo de Atualização

### 1. Na Página de Transações

Quando você clica no switch:

```
1. Switch é clicado
   ↓
2. Frontend atualiza visualmente (otimista)
   ↓
3. Faz PATCH /api/transactions/update/{id}
   ↓
4. Backend atualiza banco de dados
   ↓
5. Frontend recarrega lista de transações
   ↓
6. Switch reflete estado real do banco
```

### 2. No Dashboard

O dashboard **NÃO é atualizado automaticamente** quando você muda o switch em Transações.

**Por quê?**
- Dashboard e Transações são páginas separadas
- Não há comunicação em tempo real entre elas (por design de segurança)
- Evita requisições desnecessárias ao backend

**Solução:**
- Clique no botão **"Atualizar Dashboard"** após modificar transações
- Ou simplesmente **recarregue a página** do dashboard (F5)

---

## 🐛 Problemas Comuns e Soluções

### Problema 1: "Mudei o switch mas o dashboard não mudou"

**Causa:** Dashboard não foi atualizado após a mudança

**Solução:**
```
1. Vá para a página Dashboard
2. Clique em "Atualizar Dashboard"
   OU
3. Pressione F5 para recarregar
```

### Problema 2: "O switch está mostrando o estado errado"

**Causa:** Cache do navegador ou estado desatualizado

**Solução:**
```
1. Pressione Ctrl+Shift+R (force refresh)
2. Ou limpe o cache do navegador
3. Recarregue a página de Transações
```

### Problema 3: "Mudei várias transações mas o total não bateu"

**Causa:** Você pode estar olhando para períodos diferentes

**Verificar:**
- Dashboard está mostrando o mesmo **ano** e **mês** das transações alteradas?
- Exemplo: Se mudou transações de **março/2024**, o dashboard deve estar em **2024 + mês 03**
- Se está em "Todos os meses", certifique-se de estar no ano correto

---

## 🧪 Como Testar

### Teste Manual Completo

1. **Escolha uma transação:**
   - Vá para Transações
   - Anote o valor (ex: R$ 1.234,56)
   - Anote a data (ex: 15/03/2024)
   - Anote se é Receita ou Despesa

2. **Verifique o dashboard ANTES:**
   - Vá para Dashboard
   - Selecione o mesmo período (2024 + março)
   - Anote o total de Receitas/Despesas

3. **Mude o switch:**
   - Volte para Transações
   - Clique no switch da transação escolhida
   - Aguarde a confirmação visual
   - Veja no console: "✅ Atualizado no backend"

4. **Verifique o dashboard DEPOIS:**
   - Vá para Dashboard
   - Clique em "Atualizar Dashboard"
   - Compare o total:
     - Se LIGOU o switch: total AUMENTOU em R$ 1.234,56
     - Se DESLIGOU o switch: total DIMINUIU em R$ 1.234,56

### Logs do Console

Abra o Console do navegador (F12) para ver:

```javascript
// Ao clicar no switch
🔄 Toggle switch: MERCADOLIVRE*3PRODUTOS - APARECERÁ no dashboard
   Valor atual: 1, Novo valor: 0
✅ Atualizado no backend: 0

// Ao clicar em "Atualizar Dashboard"
🔄 Atualizando dashboard manualmente...
```

---

## 📊 Verificação Técnica

### Query SQL do Dashboard

O dashboard filtra automaticamente:

```sql
SELECT SUM(ABS(Valor))
FROM JournalEntry
WHERE user_id = 1
  AND Data LIKE '%/03/2024'
  AND CategoriaGeral = 'Despesa'
  AND IgnorarDashboard = 0  -- ← FILTRO APLICADO
```

### Teste via API

```bash
# 1. Ligar switch (aparecer no dashboard)
curl -X PATCH "http://localhost:8000/api/v1/transactions/update/{ID}" \
  -H "Content-Type: application/json" \
  -d '{"IgnorarDashboard": 0}'

# 2. Verificar dashboard
curl "http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3"

# 3. Desligar switch (não aparecer no dashboard)
curl -X PATCH "http://localhost:8000/api/v1/transactions/update/{ID}" \
  -H "Content-Type: application/json" \
  -d '{"IgnorarDashboard": 1}'

# 4. Verificar dashboard novamente
curl "http://localhost:8000/api/v1/dashboard/metrics?year=2024&month=3"
```

---

## 🎯 Resumo

✅ **O que funciona:**
- Switch atualiza o banco de dados corretamente
- Dashboard filtra transações baseado em `IgnorarDashboard`
- Logs aparecem no console para debug

⚠️ **O que você precisa fazer:**
- Clicar em "Atualizar Dashboard" após mudanças
- Verificar que está no período correto (ano/mês)
- Aguardar a confirmação visual antes de navegar

🔮 **Melhorias futuras possíveis:**
- WebSocket para atualização em tempo real
- Cache invalidation automático
- Notificações toast ao mudar switch
- Badge com contador de mudanças pendentes

---

**Última atualização:** 06/01/2026
