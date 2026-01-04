# ✅ DECISÕES APROVADAS - Otimização de Colunas

**Data:** 03/01/2026  
**Status:** Pronto para implementar

---

## 🎯 DECISÕES DO USUÁRIO

### ✅ 1. tipodocumento - Popular usando TipoTransacao

**Regra aprovada:**
```sql
UPDATE journal_entries SET tipodocumento = 'Cartão'
WHERE TipoTransacao = 'Cartão de Crédito';

UPDATE journal_entries SET tipodocumento = 'Extrato'
WHERE TipoTransacao IN ('Receitas', 'Despesas');
```

**Motivo:** Crítico para deduplicador funcionar corretamente (96.9% NULL atualmente)

---

### ✅ 2. Merge MarcacaoIA + forma_classificacao → origem_classificacao

**Nova coluna:** `origem_classificacao VARCHAR(50)`

**Valores aprovados:**
- `Automática - Base Padrões`
- `Automática - Histórico`
- `Automática - Parcela`
- `Automática - Palavras-chave`
- `Automática - Fatura`
- `Semi-Automática` (foi automática mas editada)
- `Manual` (classificação manual)
- `Manual - Lote` (várias ao mesmo tempo)
- `Ignorada`
- `Não Classificada`

**Formato:** `[Tipo] - [Origem]` (conciso e completo)

**Vantagens:**
- 1 coluna em vez de 2
- Mantém toda informação
- Valores auto-explicativos
- Simplifica código

**Ver:** [PROPOSTA_MERGE_CLASSIFICACAO.md](PROPOSTA_MERGE_CLASSIFICACAO.md) para script completo

---

### ✅ 3. Criar coluna arquivo_origem

**Nova coluna:** `arquivo_origem TEXT`

**Valores:**
- Nome do arquivo original do upload
- `'dado_historico'` para registros antigos

**Motivo:** Rastreabilidade completa dos uploads

---

### ✅ 4. Eliminar TipoTransacaoAjuste

**Motivo:** Redundante com TipoTransacao

---

### ✅ 5. Padronizar banco_origem

**Padronizações aprovadas:**
- `'Itau Person'`, `'Itaú Person'`, `'Extrato - extrato_itau.xls'`, `'Fatura - fatura_itau*'` → `'Itaú'`
- `'Mercado Pago - mp_agosto.xlsx'` → `'Mercado Pago'`
- `'BTG - extrato_btg.xls'` → `'BTG'`

---

### ⏳ 6. Campo Ano - BACKLOG

**Decisão:** NÃO mexer agora

**Motivo:** Lógica complexa (Extrato usa Data, Fatura usa DT_Fatura)

**Ação:** Documentado em [BACKLOG_VALIDACOES.md](BACKLOG_VALIDACOES.md) para validar depois

---

## 📊 IMPACTO FINAL

### Schema

**Antes:** 30 colunas  
**Depois:** 21 colunas  
**Redução:** 30% (9 colunas net)

### Mudanças Detalhadas

**Eliminar (11 colunas):**
1. ValidarIA
2. CartaoCodigo8
3. FinalCartao
4. IdOperacao
5. TipoLancamento
6. TransacaoFutura
7. banco
8. NomeTitular
9. TipoTransacaoAjuste
10. MarcacaoIA (mesclada)
11. forma_classificacao (mesclada)

**Criar (2 colunas):**
1. arquivo_origem (rastreabilidade)
2. origem_classificacao (merge)

**Renomear (2 colunas):**
1. origem → banco_origem
2. DT_Fatura → MesFatura

**Popular (2 colunas):**
1. tipodocumento (via TipoTransacao)
2. origem_classificacao (via MarcacaoIA + forma_classificacao)

**Padronizar (1 coluna):**
1. banco_origem (valores consistentes)

---

## 📄 DOCUMENTAÇÃO GERADA

1. **[PROPOSTA_MERGE_CLASSIFICACAO.md](PROPOSTA_MERGE_CLASSIFICACAO.md)**
   - Detalhes completos do merge
   - Script SQL de migração
   - Lógica de atualização no código
   - Checklist de implementação

2. **[PROPOSTA_OTIMIZACAO_COLUNAS.md](PROPOSTA_OTIMIZACAO_COLUNAS.md)**
   - Análise completa de todas as 30 colunas
   - Justificativas para cada decisão
   - Script SQL master

3. **[BACKLOG_VALIDACOES.md](BACKLOG_VALIDACOES.md)**
   - Questão do campo Ano (para depois)
   - Outras validações pendentes

4. **[RELATORIO_USO_COLUNAS.md](RELATORIO_USO_COLUNAS.md)**
   - Mapeamento de uso no código
   - Análise de impacto de mudanças

---

## 🛠️ SCRIPT SQL CONSOLIDADO

Ver [PROPOSTA_MERGE_CLASSIFICACAO.md](PROPOSTA_MERGE_CLASSIFICACAO.md) para script completo.

**Fases:**
1. ✅ Criar colunas novas (arquivo_origem, origem_classificacao)
2. ✅ Padronizar banco_origem
3. ✅ Popular tipodocumento via TipoTransacao
4. ✅ Popular origem_classificacao via merge
5. ✅ Renomear colunas
6. ✅ Eliminar colunas antigas

---

## ✅ PRONTO PARA EXECUTAR

**Todos os scripts estão prontos e documentados!**

**Próximo passo:** Revisar [PROPOSTA_MERGE_CLASSIFICACAO.md](PROPOSTA_MERGE_CLASSIFICACAO.md) e aprovar execução.

---

## 🚀 BENEFÍCIOS

1. **Schema mais limpo:** 30% menos colunas
2. **Deduplicador funcional:** tipodocumento preenchido
3. **Rastreabilidade:** arquivo_origem
4. **Classificação clara:** origem_classificacao concisa
5. **Valores consistentes:** banco_origem padronizado
6. **Código simplificado:** 1 coluna em vez de 2 para classificação

**Banco de dados pronto para produção!** 🎉
