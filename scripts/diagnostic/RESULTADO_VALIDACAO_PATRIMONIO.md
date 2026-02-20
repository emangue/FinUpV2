# Validação Patrimônio: Local vs Servidor

**Data:** 15/02/2026

## Resultado da comparação

| user_id | email | Ambiente | Ativos | Passivos | PL | anomes |
|---------|-------|----------|--------|----------|-----|--------|
| 1 | admin@financas.com | **LOCAL** | R$ 2.453.610,87 | R$ -1.069.304,08 | R$ 1.384.306,79 | 202512 |
| 1 | admin@financas.com | **SERVIDOR** | R$ 1.226.805,43 | R$ -534.652,04 | R$ 692.153,39 | 202512 |
| 4 | teste@email.com | **LOCAL** | R$ 235.413,03 | R$ -98.512,57 | R$ 136.900,46 | 202512 |
| 4 | teste@email.com | **SERVIDOR** | R$ 235.413,03 | R$ -98.512,57 | R$ 136.900,46 | 202512 |

## Conclusão

- **user_id=1:** Valores diferentes. O servidor tem ~50% dos valores do local.
- **user_id=4:** Valores idênticos.

### Causa identificada

| Ambiente | Registros (user_id=1, anomes=202512) |
|----------|--------------------------------------|
| **Local** | 30 |
| **Servidor** | 15 |

O local tem o dobro de registros. O servidor está correto; a base local tem duplicatas em `investimentos_historico`.

### Próximos passos

1. Verificar duplicatas no local:
   ```sql
   -- No SQLite local
   SELECT investimento_id, anomes, COUNT(*), SUM(valor_total)
   FROM investimentos_historico h
   JOIN investimentos_portfolio p ON p.id = h.investimento_id
   WHERE p.user_id = 1 AND h.anomes = 202512
   GROUP BY investimento_id, anomes
   HAVING COUNT(*) > 1;
   ```

2. Comparar contagem de registros:
   ```sql
   -- Local
   SELECT COUNT(*) FROM investimentos_historico h
   JOIN investimentos_portfolio p ON p.id = h.investimento_id
   WHERE p.user_id = 1 AND h.anomes = 202512;

   -- Servidor (via SSH)
   PGPASSWORD=... psql -h 127.0.0.1 -U finup_user -d finup_db -c "SELECT COUNT(*) FROM investimentos_historico h JOIN investimentos_portfolio p ON p.id = h.investimento_id WHERE p.user_id = 1 AND h.anomes = 202512;"
   ```
