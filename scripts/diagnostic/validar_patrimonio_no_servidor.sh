#!/bin/bash
# Valida patrimônio no servidor (PostgreSQL)
# Compara com output do script Python local
#
# Uso:
#   1. Local:  python scripts/diagnostic/validar_patrimonio_local_vs_servidor.py
#   2. Servidor: ./scripts/diagnostic/validar_patrimonio_no_servidor.sh
#
# Ou via SSH (se tiver chave configurada):
#   ssh root@148.230.78.91 'cd /var/www/finup && bash scripts/diagnostic/validar_patrimonio_no_servidor.sh'

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================================"
echo "VALIDAÇÃO: Patrimônio no SERVIDOR (PostgreSQL)"
echo "======================================================================"

# Carregar .env do backend (contém DATABASE_URL)
if [ -f "app_dev/backend/.env" ]; then
  set -a
  source app_dev/backend/.env 2>/dev/null || true
  set +a
fi

# Extrair PGPASSWORD de DATABASE_URL se no formato postgresql://user:pass@host/db
if [ -z "$PGPASSWORD" ] && [ -n "$DATABASE_URL" ]; then
  PGPASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
fi

if [ -z "$PGPASSWORD" ]; then
  echo "❌ Defina PGPASSWORD, POSTGRES_PASSWORD ou DATABASE_URL no app_dev/backend/.env"
  exit 1
fi
export PGPASSWORD

echo ""
echo "--- Patrimônio por user_id (último mês) ---"
psql -h 127.0.0.1 -U finup_user -d finup_db << 'SQL'
WITH ultimo AS (
  SELECT p.user_id, MAX(h.anomes) as anomes
  FROM investimentos_portfolio p
  JOIN investimentos_historico h ON h.investimento_id = p.id
  GROUP BY p.user_id
),
totais AS (
  SELECT 
    p.user_id,
    u.anomes,
    SUM(CASE WHEN LOWER(TRIM(COALESCE(p.classe_ativo,''))) = 'ativo' THEN h.valor_total ELSE 0 END) as ativos,
    SUM(CASE WHEN LOWER(TRIM(COALESCE(p.classe_ativo,''))) = 'passivo' THEN h.valor_total ELSE 0 END) as passivos
  FROM investimentos_portfolio p
  JOIN investimentos_historico h ON h.investimento_id = p.id
  JOIN ultimo u ON u.user_id = p.user_id AND u.anomes = h.anomes
  GROUP BY p.user_id, u.anomes
)
SELECT 
  t.user_id,
  COALESCE(usr.email, '(sem email)') as email,
  t.anomes,
  ROUND(t.ativos::numeric, 2) as ativos,
  ROUND(t.passivos::numeric, 2) as passivos,
  ROUND((t.ativos + t.passivos)::numeric, 2) as pl
FROM totais t
LEFT JOIN users usr ON usr.id = t.user_id
ORDER BY t.user_id;
SQL

echo ""
echo "======================================================================"
echo "Compare com o output do script local:"
echo "  python scripts/diagnostic/validar_patrimonio_local_vs_servidor.py"
echo "======================================================================"
