# 📊 Relatório: Base Padrões - Estratégias de Migração

**Data:** 15/01/2026  
**Contexto:** Fase 6B - Decisão sobre como migrar `base_padroes`

---

## 🔍 ANÁLISE ATUAL

### Estatísticas Gerais
- **Total de registros:** 373
- **Valores distintos de tipo_gasto_sugerido:** 22
- **Confiança:** Todos são `alta` (100%)
- **Status:** Todos são `ativo` (assume-se)

### Distribuição por Tipo de Gasto (Top 15)
```
Ajustável - Viagens             46 registros
Ajustável - Saídas              45 registros
Ajustável - Roupas              43 registros
Fixo                            34 registros
Ajustável - Carro               33 registros
Ajustável - Assinaturas         30 registros
Investimentos - Ajustável       27 registros
Ajustável                       19 registros
Ajustável - Doações             13 registros
Ajustável - Presentes           13 registros
Ajustável - Delivery            11 registros
Investimentos - Fixo            11 registros
Ajustável - Casa                10 registros
Ajustável - Esportes             7 registros
Ajustável - Tech                 7 registros
```

---

## 🎯 OPÇÕES DE MIGRAÇÃO

### OPÇÃO 1: Migração Incremental (Rápido - ~30min)
**Estratégia:** Atualizar tipo_gasto_sugerido via base_grupos_config

**Processo:**
1. Para cada registro em base_padroes:
   - Buscar `grupo_sugerido` → `base_grupos_config.tipo_gasto_padrao`
   - Atualizar `tipo_gasto_sugerido` com valor encontrado
2. Similar ao que foi feito em base_parcelas

**Vantagens:**
✅ Rápido (mesmo script adaptado de base_parcelas)
✅ Preserva histórico de padrões aprendidos
✅ Preserva `confianca`, `contagem`, `percentual_consistencia`
✅ Mantém estrutura existente

**Desvantagens:**
⚠️ Se `grupo_sugerido` também estiver com valores antigos, pode ser complexo
⚠️ Pode ter padrões obsoletos (estabelecimentos que não existem mais)

**Exemplo de Conversão:**
```
Ajustável - Viagens → Ajustável  (via grupo "Viagens")
Fixo → Fixo  (se grupo tem tipo_gasto_padrao=Fixo)
Investimentos - Ajustável → Investimentos  (via grupo "Investimentos")
```

---

### OPÇÃO 2: Regeneração Completa (Demorado - ~2h)
**Estratégia:** Recriar base_padroes do zero usando journal_entries

**Processo:**
1. Analisar TODAS as transações em journal_entries
2. Agrupar por estabelecimento normalizado + faixa de valor
3. Para cada grupo:
   - Calcular GRUPO mais frequente
   - Calcular SUBGRUPO mais frequente
   - Mapear tipo_gasto via base_grupos_config
   - Calcular confiança baseado em consistência
4. Popular nova base_padroes

**Vantagens:**
✅ Base limpa e atualizada
✅ Reflete realidade atual das transações
✅ Remove padrões obsoletos automaticamente
✅ Tipo_gasto sempre correto (via base_grupos_config)

**Desvantagens:**
❌ Demorado (~2h para processar 4.153 transações)
❌ Perde informações de padrões antigos (se úteis)
❌ Precisa criar lógica de segmentação por faixa de valor
❌ Precisa criar lógica de cálculo de confiança

**Requer:**
- Script de análise de journal_entries
- Lógica de segmentação (FIXO vs faixas)
- Lógica de cálculo de percentual_consistencia
- Validação de resultados

---

### OPÇÃO 3: Manter Read-Only (Sem trabalho)
**Estratégia:** Deixar base_padroes como está

**Processo:**
1. Não fazer nada
2. Novos uploads continuarão usando:
   - Base Parcelas (já atualizada)
   - Journal Entries (já atualizado)
   - Regras Genéricas (já atualizado)
   - Base Padrões (valores antigos, mas funcionando)

**Vantagens:**
✅ Zero trabalho imediato
✅ Sistema continua funcionando
✅ Nível 2 do classifier ainda funciona (lê tipo_gasto_sugerido)

**Desvantagens:**
⚠️ Base_padroes retorna valores antigos (Ajustável - Viagens)
⚠️ Classifier precisa mapear manualmente para novo sistema
⚠️ Inconsistência entre base_parcelas (nova) e base_padroes (antiga)
⚠️ Dificulta futuras análises

**Nota:** Classifier já foi atualizado em Fase 5 para retornar apenas 5 valores, então mesmo que base_padroes retorne valores antigos, o classifier os converte automaticamente.

---

## 🔍 ANÁLISE DETALHADA - Campo grupo_sugerido

**Crucial para OPÇÃO 1:** Precisamos saber se grupo_sugerido já usa valores simples ou compostos.

### Query para verificar:
```sql
SELECT DISTINCT grupo_sugerido, COUNT(*) 
FROM base_padroes 
GROUP BY grupo_sugerido 
ORDER BY COUNT(*) DESC 
LIMIT 20;
```

**Se grupo_sugerido já for simples:**
- Ex: "Viagens", "Roupas", "Carro"
- ✅ OPÇÃO 1 funciona perfeitamente

**Se grupo_sugerido for composto:**
- Ex: "Ajustável - Viagens", "Fixo - Aluguel"
- ⚠️ OPÇÃO 1 precisa de passo adicional (normalizar grupo_sugerido também)

---

## 💡 RECOMENDAÇÃO

Baseado no contexto do projeto:

### 🥇 **RECOMENDO: OPÇÃO 1 (Migração Incremental)**

**Justificativa:**
1. ✅ Rápido e testado (já funcionou em base_parcelas)
2. ✅ Preserva trabalho histórico (373 padrões aprendidos)
3. ✅ Suficiente para sistema funcionar 100%
4. ✅ Se grupo_sugerido estiver limpo, é trivial
5. ✅ Compatível com Fase 5 (classifier já converte valores)

**Próximos Passos:**
1. Verificar se `grupo_sugerido` está limpo (query acima)
2. Se sim: adaptar script `migrate_fase6a_base_parcelas.py` para base_padroes
3. Se não: adicionar step de normalização de grupo_sugerido
4. Executar dry-run
5. Aplicar migração

**Tempo estimado:** 30min - 1h (dependendo da necessidade de normalização)

---

### 🥈 **ALTERNATIVA: OPÇÃO 3 (Manter Read-Only)**

Se tempo for crítico:
- Deixar base_padroes como está
- Sistema funciona 100% (classifier converte automaticamente)
- Marcar como "technical debt" para limpar depois
- Economia de tempo: ~1h

---

### 🥉 **NÃO RECOMENDO: OPÇÃO 2 (Regeneração Completa)**

**Por quê:**
- Desnecessário neste momento
- Custo/benefício ruim (2h vs funcionalidade zero adicional)
- Pode ser feito depois se realmente necessário
- Sistema já funciona com valores antigos (classifier converte)

---

## 📋 CHECKLIST - OPÇÃO 1 (Se escolhida)

- [ ] 1. Query: verificar estrutura de grupo_sugerido
- [ ] 2. Adaptar script migrate_fase6a para base_padroes
- [ ] 3. Se necessário: adicionar normalização de grupo_sugerido
- [ ] 4. Executar dry-run
- [ ] 5. Validar conversões
- [ ] 6. Aplicar migração
- [ ] 7. Testar upload completo
- [ ] 8. Validar que classifier retorna valores corretos

---

## 🎯 DECISÃO DO USUÁRIO

**Perguntas para o usuário:**

1. **Qual opção prefere?**
   - [ ] OPÇÃO 1: Migração Incremental (~30min-1h)
   - [ ] OPÇÃO 2: Regeneração Completa (~2h)
   - [ ] OPÇÃO 3: Manter Read-Only (0min, deixar para depois)

2. **Se OPÇÃO 1:** Primeiro vou verificar se grupo_sugerido está limpo. Se não estiver, você quer que eu normalize também?

3. **Prioridade:** Prefere finalizar logo (OPÇÃO 3) e focar no Frontend, ou garantir 100% de consistência agora (OPÇÃO 1)?

---

**Aguardando orientação do usuário para prosseguir.** 🔍
