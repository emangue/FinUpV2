#!/bin/bash
sshpass -f /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/.ssh_password ssh root@148.230.78.91 << 'ENDSSH'
cd /var/www/finup
git pull origin main
cd scripts/migration
python3 fix_migration_issues.py
echo "=== VERIFICANDO RESULTADO ==="
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "SELECT COUNT(*) FROM journal_entries;"
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "SELECT COUNT(*) FROM base_marcacoes;"
PGPASSWORD='FinUp2026SecurePass' psql -h localhost -U finup_user -d finup_db -c "SELECT COUNT(*) FROM bank_format_compatibility;"
ENDSSH
