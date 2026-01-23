#!/bin/bash
set -e

echo "🚀 Iniciando migração no servidor..."

sshpass -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/.ssh_password ssh -o StrictHostKeyChecking=no root@148.230.78.91 bash << 'ENDSSH'
set -e

echo "📦 Atualizando código..."
cd /var/www/finup
git pull origin main

echo ""
echo "🔄 Executando migração..."
cd scripts/migration
python3 fix_migration_issues.py

echo ""
echo "✅ Validando contagens..."
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "
SELECT 
    'journal_entries' as tabela, 
    COUNT(*) as registros 
FROM journal_entries
UNION ALL
SELECT 'base_marcacoes', COUNT(*) FROM base_marcacoes
UNION ALL
SELECT 'bank_format_compatibility', COUNT(*) FROM bank_format_compatibility
UNION ALL  
SELECT 'generic_classification_rules', COUNT(*) FROM generic_classification_rules
UNION ALL
SELECT 'investimentos_portfolio', COUNT(*) FROM investimentos_portfolio
UNION ALL
SELECT 'investimentos_cenarios', COUNT(*) FROM investimentos_cenarios;
"

echo ""
echo "🎉 Migração concluída!"
ENDSSH

echo ""
echo "✅ Script executado com sucesso!"
