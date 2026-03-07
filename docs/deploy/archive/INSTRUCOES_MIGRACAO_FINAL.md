# 🚀 MIGRAÇÃO FINAL - SQLite → PostgreSQL

## Status Atual
- ✅ 16 de 26 tabelas migradas (2.654 registros)
- ❌ journal_entries: 0 de 7.738 (CRÍTICO!)
- ❌ generic_classification_rules: 0 de 55
- ❌ investimentos_*: 0 de 1.270

## Script Criado
`scripts/migration/fix_migration_issues.py` - Corrige problemas de schema

## Executar no Servidor

```bash
# 1. SSH no servidor
ssh root@148.230.78.91

# 2. Atualizar código
cd /var/www/finup
git pull origin main

# 3. Executar migração
cd scripts/migration
python3 fix_migration_issues.py

# 4. Validar resultados
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "
SELECT 'journal_entries' as tabela, COUNT(*) as registros FROM journal_entries
UNION ALL SELECT 'base_marcacoes', COUNT(*) FROM base_marcacoes  
UNION ALL SELECT 'bank_format_compatibility', COUNT(*) FROM bank_format_compatibility
UNION ALL SELECT 'generic_classification_rules', COUNT(*) FROM generic_classification_rules
UNION ALL SELECT 'investimentos_portfolio', COUNT(*) FROM investimentos_portfolio
UNION ALL SELECT 'investimentos_cenarios', COUNT(*) FROM investimentos_cenarios
UNION ALL SELECT 'investimentos_historico', COUNT(*) FROM investimentos_historico;"
```

## Resultados Esperados
- journal_entries: 7.738 ✅
- base_marcacoes: 405 ✅ (já migrado)
- bank_format_compatibility: 7 ✅ (já migrado)
- generic_classification_rules: 55 ✅
- investimentos_portfolio: 626 ✅
- investimentos_cenarios: 6 ✅
- investimentos_historico: 626 ✅

## Após Migração Bem-Sucedida

Reiniciar backend para garantir conexões limpas:
```bash
systemctl restart finup-backend
systemctl status finup-backend
```

Testar admin pages:
- https://meufinup.com.br/settings/bancos (deve mostrar 7 bancos)
- https://meufinup.com.br/settings/screens (deve mostrar 35 telas)
- https://meufinup.com.br/settings/categorias-genericas (deve mostrar 55 regras)

Testar dashboard:
- https://meufinup.com.br/dashboard (deve mostrar 7.738 transações)

## Se Houver Erros

Verificar log de erro:
```bash
tail -50 /var/www/finup/scripts/migration/fix_migration_issues.py
```

Se erro persistir, fazer rollback e tentar novamente:
```bash
# Limpar PostgreSQL
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "
TRUNCATE TABLE journal_entries RESTART IDENTITY CASCADE;
TRUNCATE TABLE generic_classification_rules RESTART IDENTITY CASCADE;
TRUNCATE TABLE investimentos_portfolio, investimentos_cenarios, investimentos_historico, investimentos_aportes_extraordinarios RESTART IDENTITY CASCADE;"

# Executar migração novamente
python3 fix_migration_issues.py
```

## Commits Relacionados
- 19b9f100: Script inicial de migração (290 linhas)
- 54d8cc62: Script de correção para problemas de schema
- (pending): Correção final com todas as 29 colunas
