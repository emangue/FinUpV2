#!/bin/bash
# Testa upload no servidor e diagnostica Base Parcelas
# Executar: ssh host 'bash -s' < scripts/diagnostic/test_upload_server.sh
# Ou na VM: cd /var/www/finup && bash scripts/diagnostic/test_upload_server.sh

set -e
cd /var/www/finup 2>/dev/null || cd "$(dirname "$0")/../.."
DB="app_dev/backend/database/financas_dev.db"

echo "=============================================="
echo "DIAGNÓSTICO UPLOAD - Base Parcelas"
echo "=============================================="

# 1. Criar CSV de teste com PRODUTOS GLOBO
CSV_TEST="/tmp/fatura-test-$$.csv"
cat > "$CSV_TEST" << 'EOF'
data,lançamento,valor
2025-06-20,PRODUTOS GLOBO    07/12,59.9
2025-05-11,WINE.COM.BR*52723 09/12,73.18
2025-12-07,VIVARA XVL        02/03,135.34
EOF
echo "1. CSV de teste criado: $CSV_TEST"
head -5 "$CSV_TEST"

# 2. Obter token (teste@email.com = user 4, ou admin)
echo ""
echo "2. Obtendo token..."
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"teste123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@finup.com","password":"admin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)
fi

if [ -z "$TOKEN" ]; then
  echo "   ⚠️ Não foi possível obter token. Verificando preview mais recente..."
else
  echo "   ✅ Token obtido"
  
  # 3. Fazer upload
  echo ""
  echo "3. Fazendo upload..."
  RESP=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/upload/preview" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$CSV_TEST" \
    -F "banco=Itaú" \
    -F "tipoDocumento=fatura" \
    -F "cartao=Azul" \
    -F "mesFatura=2026-01" \
    -F "formato=CSV")
  
  SESSION=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null)
  echo "   Session: $SESSION"
  echo "$RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin)
s=d.get('estatisticas',{})
print(f'   Base Parcelas: {s.get(\"base_parcelas\",\"?\")}')
print(f'   Base Padrões: {s.get(\"base_padroes\",\"?\")}')
print(f'   Total: {s.get(\"total\",\"?\")}')
" 2>/dev/null || true
fi

# 4. Consultar preview_transacoes mais recente
echo ""
echo "4. Preview transações (última sessão) - IdParcela e origem:"
sqlite3 "$DB" "
SELECT pt.user_id, pt.IdParcela, pt.origem_classificacao, pt.EstabelecimentoBase, pt.Valor
FROM preview_transacoes pt
JOIN (SELECT session_id, user_id FROM upload_history ORDER BY id DESC LIMIT 1) uh ON pt.session_id = uh.session_id
WHERE pt.IdParcela IS NOT NULL
LIMIT 10;
" 2>/dev/null || echo "   (nenhuma com IdParcela)"

# 5. Todas as parcelas do preview (com e sem IdParcela)
echo ""
echo "5. Transações com parcela no lançamento (EstabelecimentoBase):"
sqlite3 "$DB" "
SELECT pt.id, pt.user_id, pt.IdParcela, pt.origem_classificacao, substr(pt.lancamento,1,45) as lanc
FROM preview_transacoes pt
JOIN (SELECT session_id FROM upload_history ORDER BY id DESC LIMIT 1) uh ON pt.session_id = uh.session_id
WHERE pt.lancamento LIKE '%/%' AND pt.lancamento GLOB '*[0-9][0-9]/[0-9][0-9]'
LIMIT 15;
" 2>/dev/null || echo "   (erro ou vazio)"

# 6. base_parcelas para PRODUTOS GLOBO
echo ""
echo "6. base_parcelas PRODUTOS GLOBO:"
sqlite3 "$DB" "
SELECT user_id, id_parcela, valor_parcela, qtd_parcelas 
FROM base_parcelas 
WHERE estabelecimento_base LIKE '%GLOBO%';
" 2>/dev/null

# 7. user_id do último upload
echo ""
echo "7. user_id do último upload:"
sqlite3 "$DB" "SELECT user_id, session_id FROM upload_history ORDER BY id DESC LIMIT 1;" 2>/dev/null

rm -f "$CSV_TEST"
echo ""
echo "=============================================="
