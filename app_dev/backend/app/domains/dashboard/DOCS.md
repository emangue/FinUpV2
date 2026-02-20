# Domínio Dashboard - Agregador

**Tipo:** Agregador  
**Política:** `docs/architecture/PROPOSTA_MODULARIDADE_PRAGMATICA.md`

## Dependências Permitidas

O domínio dashboard **consolida dados** de outros domínios para exibição. Não orquestra fluxos, apenas agrega:

| Domínio | Justificativa |
|---------|---------------|
| **transactions** | Busca `JournalEntry` para métricas (receitas, despesas, totais) |
| **budget** | Busca `BudgetPlanning` para comparativo orçado vs realizado |

## Responsabilidade

- Calcular métricas (totais, médias, breakdown por categoria)
- Montar dados para gráficos (chart data)
- Não modifica dados de outros domínios – apenas leitura

## Quando Adicionar Nova Dependência

Só adicionar se for necessário para **montar uma métrica ou gráfico**. Evitar lógica de negócio que pertence a outros domínios.
