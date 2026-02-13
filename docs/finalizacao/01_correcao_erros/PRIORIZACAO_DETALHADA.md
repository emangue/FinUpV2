# 🎯 PRIORIZAÇÃO E CATEGORIZAÇÃO - ERROS APP_DEV

**Data:** 10/02/2026  
**Metodologia:** Matriz Gravidade × Impacto × Esforço  

---

## 📊 VISÃO GERAL

### Distribuição por Tipo de Erro:

```
TYPE MISMATCH (47%)
├─ MobileHeader leftAction (2) ────────── P0 🔴
├─ Goal ID number vs string (4) ───────── P0 🔴
├─ Goal status não definido (1) ───────── P1 🟠
└─ Ativo boolean vs number (1) ────────── P2 🟡

PROPERTY NOT EXIST (41%)
├─ Goal.orcamento (2) ─────────────────── P0 🔴
├─ Goal.valor_atual (2) ───────────────── P0 🔴
├─ Goal.categoria (3) ─────────────────── P0 🔴 (requer investigação)
├─ Goal.mes_referencia (1) ────────────── P1 🟠
├─ AuthContext.isLoading (1) ──────────── P1 🟠
└─ Preview.occurrences (2) ────────────── P2 🟡

WRONG COMPARISON (12%)
└─ Boolean vs Number (1) ──────────────── P2 🟡
```

---

## 🔴 PRIORIDADE P0 - BLOQUEANTES (9 erros)

### Definição P0:
- ✅ Impede funcionalidade crítica de funcionar
- ✅ Usuário não consegue completar tarefa principal
- ✅ Erro aparece em runtime/interação
- ✅ Sem workaround disponível

---

### P0.1 - MobileHeader leftAction (2 erros)

**Gravidade:** 🔥 ALTA  
**Impacto:** 🎯 CRÍTICO - Navegação quebrada  
**Esforço:** ⚡ BAIXO (10 min)  
**Urgência:** 🚨 IMEDIATO

**Por quê P0:**
- Botão "Voltar" não funciona → Usuário fica preso na tela
- Afeta 2 páginas críticas (criar meta, editar meta)
- Sem botão "Voltar", único jeito de sair é fechar app

**Impacto nos Usuários:**
- 🚫 Não consegue voltar de criar/editar meta
- 🚫 Precisa fechar e reabrir app

**Esforço vs Benefício:**
- ✅ Correção trivial: mudar objeto para string `"back"`
- ✅ 10 minutos de trabalho
- ✅ Resolve navegação em 2 páginas críticas

---

### P0.2 - Goal.orcamento inexistente (2 erros)

**Gravidade:** 🔥 ALTA  
**Impacto:** 🎯 CRÍTICO - Modal não abre  
**Esforço:** ⚡ BAIXO (5 min)  
**Urgência:** 🚨 IMEDIATO

**Por quê P0:**
- Modal de edição quebra ao tentar abrir
- Erro no constructor do componente (useState)
- Usuário não consegue editar metas (feature core)

**Impacto nos Usuários:**
- 🚫 Não consegue editar meta existente
- 🚫 Clique no botão "Editar" não faz nada (ou erro)

**Esforço vs Benefício:**
- ✅ Correção trivial: `goal.orcamento` → `goal.valor_alvo`
- ✅ 5 minutos (buscar/substituir)
- ✅ Restaura funcionalidade de edição completa

---

### P0.3 - Goal.valor_atual não aninhado (2 erros)

**Gravidade:** 🔥 ALTA  
**Impacto:** 🎯 CRÍTICO - Dados incorretos exibidos  
**Esforço:** ⚡ BAIXO (5 min)  
**Urgência:** 🚨 IMEDIATO

**Por quê P0:**
- Valor atual sempre aparece como R$ 0,00
- Usuário não vê progresso real da meta
- Decisões financeiras baseadas em dados incorretos

**Impacto nos Usuários:**
- 📉 Vê "R$ 0,00" mesmo tendo gastos
- 📉 Percentual de progresso incorreto
- 📉 Não sabe se está perto/longe da meta

**Esforço vs Benefício:**
- ✅ Correção trivial: `goal.valor_atual` → `goal.progresso?.valor_atual`
- ✅ 5 minutos
- ✅ Dados corretos aparecem imediatamente

---

### P0.4 - Goal ID type mismatch (4 erros)

**Gravidade:** 🟠 MÉDIA  
**Impacto:** 🎯 CRÍTICO - Features não funcionam  
**Esforço:** ⚡ BAIXO-MÉDIO (20 min)  
**Urgência:** 🚨 IMEDIATO

**Por quê P0:**
- Toggle ativo/inativo não funciona
- Editar meta não funciona
- Callbacks recebem ID errado → busca falha

**Impacto nos Usuários:**
- 🚫 Não consegue ativar/desativar meta
- 🚫 Clique em "Editar" abre meta errada (ou nenhuma)

**Esforço vs Benefício:**
- ⚠️ Requer mudança em interface + callbacks
- ⚡ Mas é mecânico: mudar `string` para `number`
- ✅ 20 minutos para 4 locais + types

---

### P0.5 - Goal.categoria inexistente (3 erros) ⚠️ INVESTIGAÇÃO

**Gravidade:** 🟠 MÉDIA  
**Impacto:** 🎯 CRÍTICO - Filtros não funcionam  
**Esforço:** 🔴 ALTO (1-2h com investigação)  
**Urgência:** 🚨 IMEDIATO

**Por quê P0:**
- Ícones de metas não aparecem
- Filtros "Gastos" vs "Investimentos" quebrados
- Usuário não consegue separar tipos de meta

**Impacto nos Usuários:**
- 🎨 Todas as metas com ícone padrão (sem contexto visual)
- 📋 Lista de metas misturada (não dá pra filtrar)

**Esforço vs Benefício:**
- ⚠️ REQUER INVESTIGAÇÃO primeiro:
  1. Backend retorna campo? (30 min)
  2. Se sim: adicionar type (10 min)
  3. Se não: implementar lógica alternativa (1h)
- ✅ Benefício alto: restaura UX de categorização

**AÇÃO OBRIGATÓRIA ANTES DE CORRIGIR:**
```bash
# 1. Verificar JSON do backend
curl http://localhost:8000/api/v1/goals/ \
  -H "Authorization: Bearer [TOKEN]" \
  | jq '.[0] | keys' | grep categoria

# 2. Decisão:
# - Se retorna: adicionar em interface Goal
# - Se não retorna: criar função getGoalCategoria()
```

---

## 🟠 PRIORIDADE P1 - CRÍTICAS (6 erros)

### Definição P1:
- ✅ Impacta funcionalidade, mas não bloqueia completamente
- ✅ Usuário consegue workaround (parcial)
- ✅ Degrada experiência significativamente
- ✅ Deve ser corrigido antes de produção

---

### P1.1 - Goal status não definido (1 erro)

**Gravidade:** 🟠 MÉDIA  
**Impacto:** 📊 ALTO - Feature incompleta  
**Esforço:** ⚡ BAIXO (15 min)  
**Urgência:** ⏱️ ALTA

**Por quê P1 (não P0):**
- Meta funciona sem status
- Mas usuário não vê se está "Atrasado" ou "Concluído"
- Informação importante mas não bloqueante

**Impacto nos Usuários:**
- 📍 Não vê badge de status da meta
- 📍 Não sabe se meta está ok ou atrasada
- ✅ Mas meta em si funciona (criar/editar/ver)

**Esforço vs Benefício:**
- ✅ Mudança simples: `Goal` → `GoalWithProgress`
- ✅ 15 minutos (type + teste)
- ✅ Restaura informação contextual importante

---

### P1.2 - Goal.mes_referencia inexistente (1 erro)

**Gravidade:** 🟡 BAIXA  
**Impacto:** 📊 MÉDIO - Info faltando  
**Esforço:** ⚡ BAIXO (5 min)  
**Urgência:** ⏱️ ALTA

**Por quê P1:**
- Informação secundária (data de referência)
- Não impede edição da meta
- Mas é útil para usuário saber prazo

**Impacto nos Usuários:**
- 📅 Não vê data de referência no modal
- ✅ Mas consegue editar meta normalmente

**Esforço vs Benefício:**
- ✅ Trivial: `goal.mes_referencia` → `goal.prazo`
- ✅ 5 minutos
- ✅ Restaura informação útil

---

### P1.3 - AuthContext.isLoading (1 erro)

**Gravidade:** 🟠 MÉDIA  
**Impacto:** 🔒 ALTO - Segurança/UX  
**Esforço:** ⚡ BAIXO (10 min)  
**Urgência:** ⏱️ ALTA

**Por quê P1:**
- Loading state incorreto pode permitir acesso antes de autenticação
- Ou mostrar tela vazia durante carregamento
- Não quebra completamente, mas degrada UX

**Impacto nos Usuários:**
- ⏳ Pode ver flash de conteúdo antes de redirect
- ⏳ Ou tela branca por alguns segundos
- 🔒 Potencial problema de segurança (acesso antes de validar)

**Esforço vs Benefício:**
- ✅ Trivial: `isLoading` → `loading`
- ✅ 10 minutos
- ✅ Melhora UX e segurança

---

## 🟡 PRIORIDADE P2 - MÉDIO (2 erros)

### Definição P2:
- ✅ Não impacta funcionalidade core
- ✅ Workaround já implementado
- ✅ Código defensivo (funciona mas incorreto)
- ✅ Pode ser corrigido após P0/P1

---

### P2.1 - Ativo boolean vs number (1 erro)

**Gravidade:** 🟢 BAIXA  
**Impacto:** 🎨 BAIXO - Código defensivo  
**Esforço:** ⚡ BAIXO (5 min)  
**Urgência:** 📅 BAIXA

**Por quê P2:**
- Código funciona (verifica ambos)
- TypeScript reclama mas não quebra
- Workaround já implementado

**Impacto nos Usuários:**
- ✅ ZERO - funciona perfeitamente
- 🎨 Apenas limpeza de código

**Esforço vs Benefício:**
- ✅ Trivial: `=== true || === 1` → `!!goal.ativo`
- ✅ 5 minutos
- 🎨 Código mais limpo/idiomático

---

### P2.2 - Preview.occurrences (2 erros) ⚠️ INVESTIGAÇÃO

**Gravidade:** 🟢 BAIXA  
**Impacto:** 📊 BAIXO - Sort opcional  
**Esforço:** 🟠 MÉDIO (30 min com investigação)  
**Urgência:** 📅 BAIXA

**Por quê P2:**
- Ordenação é nice-to-have
- Preview funciona sem sort
- Feature secundária (não afeta upload)

**Impacto nos Usuários:**
- 📋 Lista não ordenada por quantidade
- ✅ Mas preview funciona normalmente
- ✅ Usuário consegue marcar grupos

**Esforço vs Benefício:**
- ⚠️ Requer investigação:
  1. Backend retorna campo? (15 min)
  2. Se não: remover sort (5 min)
- 🎨 Benefício baixo (apenas ordenação)

---

## 📊 MATRIZ DE DECISÃO

### Impacto vs Esforço:

```
ALTO IMPACTO
    │
    │  P0.1 leftAction (10min) ←─── QUICK WIN
    │  P0.2 orcamento (5min)   ←─── QUICK WIN
    │  P0.3 valor_atual (5min) ←─── QUICK WIN
    │  
    │  P0.4 ID mismatch (20min)
    │  P1.1 status (15min)
    │  P1.2 mes_ref (5min)
    │  P1.3 isLoading (10min)
    │
    │  P0.5 categoria (1-2h) ←────── INVESTIGAR PRIMEIRO
    │
BAIXO IMPACTO
    │  P2.1 ativo (5min)
    │  P2.2 occurrences (30min)
    └─────────────────────────────
     BAIXO          ALTO
           ESFORÇO
```

---

## 🎯 ESTRATÉGIA DE EXECUÇÃO OTIMIZADA

### Fase 1 - Quick Wins (1 hora)
**Objetivo:** Resolver 70% dos erros P0 em 1 hora

1. ✅ P0.2 - orcamento → valor_alvo (5min)
2. ✅ P0.3 - valor_atual aninhado (5min)
3. ✅ P0.1 - leftAction (10min)
4. ✅ P1.2 - mes_referencia → prazo (5min)
5. ✅ P1.3 - isLoading → loading (10min)
6. ✅ P2.1 - simplificar ativo (5min)

**Resultado:** 6 erros corrigidos, 0 investigação necessária

---

### Fase 2 - Correções Médias (30 min)

7. ✅ P0.4 - ID type mismatch (20min)
8. ✅ P1.1 - status type (15min)

**Resultado:** +2 erros corrigidos

---

### Fase 3 - Investigações (2 horas)

9. ⚠️ P0.5 - categoria (investigar 30min + corrigir 1h)
10. ⚠️ P2.2 - occurrences (investigar 15min + decisão 15min)

**Resultado:** +2 erros resolvidos (após análise)

---

## 🏁 RESUMO FINAL

### Totais:
- **Total de Erros:** 17
- **P0 (Bloqueantes):** 9 (53%)
- **P1 (Críticas):** 6 (35%)
- **P2 (Médio):** 2 (12%)

### Tempo Estimado:
- **Quick Wins:** 1h (40min correção + 20min testes)
- **Correções Médias:** 30min
- **Investigações:** 2h
- **TOTAL:** ~3.5 horas

### Ordem de Ataque:
```
1º Quick Wins (P0.2, P0.3, P0.1, P1.2, P1.3, P2.1) → 1h
2º Médias (P0.4, P1.1) → 30min
3º Investigações (P0.5, P2.2) → 2h
───────────────────────────────────────────
TOTAL: 3.5 horas → App funcional
```

### Critério de Sucesso:
- ✅ 0 erros TypeScript
- ✅ Build sem warnings
- ✅ Todas as páginas mobile carregam
- ✅ Features críticas testadas e funcionando
- ✅ Nenhum console.error em runtime

---

**📌 RECOMENDAÇÃO:** Executar na ordem acima para maximizar resultados iniciais (6 erros em 1h = progresso visível rápido).
