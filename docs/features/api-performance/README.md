# API Performance — Mapeamento & Plano de Ação

> Diagnóstico completo das chamadas de API do FinUpV2, identificação de gargalos e propostas de melhoria priorizadas.

## Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| [01-mapeamento-apis.md](./01-mapeamento-apis.md) | Mapeamento completo de todos os endpoints por feature |
| [02-problemas-identificados.md](./02-problemas-identificados.md) | Diagnóstico detalhado de cada problema de performance |
| [03-plano-de-acao.md](./03-plano-de-acao.md) | Propostas de melhoria priorizadas com impacto estimado |
| [04-cashflow-tabela-materializada.md](./04-cashflow-tabela-materializada.md) | Proposta detalhada da tabela `plano_cashflow_mes` |
| [05-scroll-mes-mapeamento.md](./05-scroll-mes-mapeamento.md) | Diagnóstico do bug "scroll nasce no mês atual e pula para o mês com dados" |
| [06-scroll-mes-plano-de-acao.md](./06-scroll-mes-plano-de-acao.md) | Plano de ação para o picker nascer diretamente no mês correto |

## Contexto

O app apresenta lentidão nas telas principais. Após mapeamento, os principais gargalos são:

- **Dashboard:** 11 chamadas simultâneas no mount
- **Cashflow:** Computação dinâmica de 12 meses (48-60 queries/requisição) sem tabela materializada
- **Investimentos:** 3 RTTs separados que poderiam ser 1
- **Goals/Orçamento:** Full refetch após toda mutação
- **Módulos sem cache:** Investimentos, Plano, Bancos, Categorias, Transações
- **MonthScrollPicker:** Nasce no mês atual e faz scroll visível até o mês com dados

## Status

- [x] Mapeamento realizado (Mar/2026)
- [ ] Implementação — Alta prioridade
- [ ] Implementação — Média prioridade
- [ ] Implementação — Baixa prioridade
