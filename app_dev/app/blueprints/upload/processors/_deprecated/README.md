# Processadores Descontinuados

Esta pasta contém processadores específicos que foram substituídos pelos processadores genéricos.

## Arquivos Descontinuados

- **fatura_itau.py** - Substituído por `fatura_cartao.py` (genérico)
- **extrato_itau.py** - Substituído por `extrato_conta.py` (genérico)  
- **mercado_pago.py** - Substituído por `extrato_conta.py` (genérico)

## Motivo da Descontinuação

Os processadores genéricos (`fatura_cartao.py` e `extrato_conta.py`) utilizam detecção automática de colunas e mapeamento flexível, suportando qualquer formato de CSV/XLSX. Isso elimina a necessidade de processadores específicos para cada instituição financeira.

## Correção de Hash Implementada (26/12/2025)

Todos os processadores foram atualizados para lidar corretamente com transações duplicadas legítimas no mesmo arquivo. A solução implementada adiciona um sufixo sequencial (`_1`, `_2`, etc.) quando o mesmo hash aparece múltiplas vezes, garantindo que cada transação tenha um ID único.

## Atenção

Estes arquivos são mantidos apenas para referência histórica. Não devem ser usados em produção.
