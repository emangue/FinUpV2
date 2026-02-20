# Domínio Upload - Orquestrador

**Tipo:** Orquestrador  
**Política:** `docs/architecture/PROPOSTA_MODULARIDADE_PRAGMATICA.md`

## Dependências Permitidas

O domínio upload coordena o fluxo completo de processamento de arquivos financeiros. As dependências cruzadas são **justificadas por orquestração**:

| Domínio | Justificativa |
|---------|---------------|
| **transactions** | Cria/atualiza `JournalEntry` após processar arquivo; consulta `BaseParcelas` |
| **grupos** | Consulta `BaseGruposConfig` para classificação e validação de grupos |
| **categories** | Consulta `BaseMarcacao` para marcações e categorização |
| **budget** | Atualiza valor realizado após classificação |
| **exclusoes** | Aplica regras de exclusão de transações |
| **compatibility** | Valida formato do arquivo e compatibilidade banco/cartão |
| **patterns** | Consulta `BasePadroes` para regras de classificação |
| **classification** | Serviço de classificação genérica (generic rules) |

## Fluxo Principal

1. Recebe arquivo → valida (compatibility)
2. Processa → extrai transações
3. Classifica → usa patterns, grupos, classification
4. Aplica exclusões → exclusoes
5. Persiste → transactions, budget
6. Atualiza marcações → categories, marcacoes

## Quando Adicionar Nova Dependência

Só adicionar se o fluxo de upload **naturalmente** envolver o outro domínio. Evitar imports por conveniência.
