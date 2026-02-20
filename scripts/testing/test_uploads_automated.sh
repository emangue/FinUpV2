#!/bin/bash
# Script de Testes Automatizados - Upload e Validações
# Data: 13/02/2026
# Usuário: teste@email.com (user_id=4)

set -e  # Exit on error

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
BASE_URL="http://localhost:8000/api/v1"
DB_PATH="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db"
ARQUIVOS_DIR="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/_arquivos_historicos/_csvs_historico"
USER_ID=4
TOKEN=""

# Arquivos de teste
UPLOAD_FILES=(
  "MP202501.xlsx:MercadoPago:extrato:Gold:2025-01"
  "MP202502.xlsx:MercadoPago:extrato:Gold:2025-02"
  "MP202503.xlsx:MercadoPago:extratoo:Gold:2025-03"
  "fatura_itau-202510.csv:Itaú:fatura:Platinum:2025-10"
  "fatura_itau-202511.csv:Itaú:fatura:Platinum:2025-11"
  "fatura_itau-202512.csv:Itaú:fatura:Platinum:2025-12"
)

# Funções auxiliares
log_section() {
  echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

log_info() {
  echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Login e obter token
get_token() {
  log_section "🔐 Fazendo Login"
  
  RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "teste@email.com",
      "password": "teste123"
    }')
  
  TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
  
  if [ -z "$TOKEN" ]; then
    log_error "Falha ao obter token"
    echo "$RESPONSE"
    exit 1
  fi
  
  log_success "Token obtido"
}

# Validação SQL
validate_sql() {
  local description=$1
  local query=$2
  
  log_info "$description"
  sqlite3 "$DB_PATH" "$query" | sed 's/^/  /'
}

# Estado inicial
check_initial_state() {
  log_section "📊 Estado Inicial do Usuário"
  
  validate_sql "Transações:" "SELECT COUNT(*) FROM journal_entries WHERE user_id = $USER_ID;"
  validate_sql "Padrões:" "SELECT COUNT(*) FROM base_padroes WHERE user_id = $USER_ID;"
  validate_sql "Parcelas:" "SELECT COUNT(*) FROM base_parcelas WHERE user_id = $USER_ID;"
  validate_sql "Uploads:" "SELECT COUNT(*) FROM upload_history WHERE user_id = $USER_ID;"
}

# Upload de arquivo
upload_file() {
  local index=$1
  local file_info="${UPLOAD_FILES[$index]}"
  
  IFS=':' read -r filename banco tipo cartao mes <<< "$file_info"
  
  log_section "🚀 UPLOAD #$((index+1)) - $filename"
  
  local file_path="$ARQUIVOS_DIR/$filename"
  
  if [ ! -f "$file_path" ]; then
    log_error "Arquivo não encontrado: $file_path"
    return 1
  fi
  
  log_info "Enviando para preview..."
  
  # Determinar formato baseado na extensão
  local formato="Excel"
  if [[ "$filename" == *.csv ]]; then
    formato="CSV"
  elif [[ "$filename" == *.pdf ]]; then
    formato="PDF"
  fi
  
  # Fazer preview
  PREVIEW_RESPONSE=$(curl -s -X POST "$BASE_URL/upload/preview" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file_path" \
    -F "banco=$banco" \
    -F "tipoDocumento=$tipo" \
    -F "cartao=$cartao" \
    -F "mesFatura=$mes" \
    -F "formato=$formato")
  
  # Extrair session_id
  SESSION_ID=$(echo "$PREVIEW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])" 2>/dev/null || echo "")
  
  if [ -z "$SESSION_ID" ]; then
    log_error "Falha ao obter session_id"
    echo "$PREVIEW_RESPONSE" | python3 -m json.tool
    return 1
  fi
  
  log_success "Preview gerado: $SESSION_ID"
  
  # Estatísticas do preview
  echo "$PREVIEW_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
stats = data.get('estatisticas', {})
print(f'  Total transações: {stats.get(\"total\", 0)}')
print(f'  Base Genérica: {stats.get(\"base_generica\", 0)} ({stats.get(\"percentual_base_generica\", 0):.1f}%)')
print(f'  Base Padrões: {stats.get(\"base_padroes\", 0)} ({stats.get(\"percentual_base_padroes\", 0):.1f}%)')
print(f'  Não Classificado: {stats.get(\"nao_classificado\", 0)} ({stats.get(\"percentual_nao_classificado\", 0):.1f}%)')
" 2>/dev/null || echo "  (estatísticas não disponíveis)"
  
  # Confirmar upload
  log_info "Confirmando upload..."
  
  CONFIRM_RESPONSE=$(curl -s -X POST "$BASE_URL/upload/confirm/$SESSION_ID" \
    -H "Authorization: Bearer $TOKEN")
  
  UPLOAD_ID=$(echo "$CONFIRM_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('upload_history_id', 0))" 2>/dev/null || echo "0")
  
  if [ "$UPLOAD_ID" == "0" ]; then
    log_error "Falha ao confirmar upload"
    echo "$CONFIRM_RESPONSE" | python3 -m json.tool
    return 1
  fi
  
  log_success "Upload confirmado: ID $UPLOAD_ID"
  
  # Validações SQL pós-upload
  log_section "📊 Validações SQL - Upload #$((index+1))"
  
  validate_sql "Total de transações:" \
    "SELECT COUNT(*) FROM journal_entries WHERE user_id = $USER_ID;"
  
  validate_sql "Transações deste upload:" \
    "SELECT COUNT(*) FROM journal_entries WHERE user_id = $USER_ID AND upload_history_id = $UPLOAD_ID;"
  
  validate_sql "Total de padrões (base_padroes):" \
    "SELECT COUNT(*) FROM base_padroes WHERE user_id = $USER_ID;"
  
  validate_sql "Padrões com alta confiança:" \
    "SELECT COUNT(*) FROM base_padroes WHERE user_id = $USER_ID AND confianca = 'alta';"
  
  validate_sql "Top 5 padrões mais frequentes:" \
    "SELECT padrao_estabelecimento, contagem, confianca 
     FROM base_padroes 
     WHERE user_id = $USER_ID 
     ORDER BY contagem DESC LIMIT 5;"
  
  validate_sql "Total de parcelas ativas:" \
    "SELECT COUNT(*) FROM base_parcelas WHERE user_id = $USER_ID AND status = 'ativa';"
  
  validate_sql "Parcelas finalizadas:" \
    "SELECT COUNT(*) FROM base_parcelas WHERE user_id = $USER_ID AND status = 'finalizado';"
  
  validate_sql "Origem de classificação (este upload):" \
    "SELECT origem_classificacao, COUNT(*) as qtd, 
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
     FROM journal_entries 
     WHERE user_id = $USER_ID AND upload_history_id = $UPLOAD_ID
     GROUP BY origem_classificacao;"
  
  echo ""
  sleep 2  # Pausa entre uploads
}

# Teste de dashboard (via API)
test_dashboard() {
  log_section "📊 Testando Dashboard"
  
  log_info "Dashboard - Resumo geral"
  curl -s "$BASE_URL/dashboard/summary?user_id=$USER_ID" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool || log_error "Dashboard não disponível"
  
  log_info "Dashboard - Por categoria"
  curl -s "$BASE_URL/dashboard/by-category?user_id=$USER_ID&ano=2025&mes=1" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20 || log_error "Dashboard por categoria não disponível"
}

# Teste de transações
test_transactions() {
  log_section "📝 Testando Transações"
  
  validate_sql "Total de transações no banco:" \
    "SELECT COUNT(*) FROM journal_entries WHERE user_id = $USER_ID;"
  
  validate_sql "Transações por mês:" \
    "SELECT Ano, Mes, COUNT(*) as qtd 
     FROM journal_entries 
     WHERE user_id = $USER_ID 
     GROUP BY Ano, Mes 
     ORDER BY Ano, Mes;"
  
  validate_sql "Transações por banco:" \
    "SELECT banco_origem, COUNT(*) as qtd 
     FROM journal_entries 
     WHERE user_id = $USER_ID 
     GROUP BY banco_origem;"
  
  validate_sql "Top 10 estabelecimentos:" \
    "SELECT EstabelecimentoBase, COUNT(*) as qtd, SUM(ValorPositivo) as total
     FROM journal_entries 
     WHERE user_id = $USER_ID 
     GROUP BY EstabelecimentoBase 
     ORDER BY qtd DESC LIMIT 10;"
}

# Relatório final
generate_report() {
  log_section "📄 Gerando Relatório Final"
  
  validate_sql "Resumo completo:" \
    "SELECT 
       (SELECT COUNT(*) FROM journal_entries WHERE user_id = $USER_ID) as total_transacoes,
       (SELECT COUNT(*) FROM base_padroes WHERE user_id = $USER_ID) as total_padroes,
       (SELECT COUNT(*) FROM base_parcelas WHERE user_id = $USER_ID AND status = 'ativa') as parcelas_ativas,
       (SELECT COUNT(*) FROM base_parcelas WHERE user_id = $USER_ID AND status = 'finalizado') as parcelas_finalizadas,
       (SELECT COUNT(*) FROM upload_history WHERE user_id = $USER_ID) as total_uploads;"
  
  validate_sql "Evolução de aprendizado (Base Padrões):" \
    "SELECT 
       uh.id as upload,
       uh.nome_arquivo,
       COUNT(*) FILTER (WHERE je.origem_classificacao = 'Base Padrões') as base_padroes,
       COUNT(*) as total,
       ROUND(COUNT(*) FILTER (WHERE je.origem_classificacao = 'Base Padrões') * 100.0 / COUNT(*), 1) as pct_padroes
     FROM upload_history uh
     JOIN journal_entries je ON je.upload_history_id = uh.id
     WHERE uh.user_id = $USER_ID
     GROUP BY uh.id
     ORDER BY uh.id;"
}

# ==================== EXECUÇÃO PRINCIPAL ====================

main() {
  log_section "🚀 INICIANDO BATERIA DE TESTES AUTOMATIZADOS"
  echo "Usuário: teste@email.com (ID: $USER_ID)"
  echo "Data: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  
  # 1. Login
  get_token
  
  # 2. Estado inicial
  check_initial_state
  
  # 3. Uploads sequenciais
  for i in "${!UPLOAD_FILES[@]}"; do
    upload_file "$i"
  done
  
  # 4. Testes de funcionalidades
  test_dashboard
  test_transactions
  
  # 5. Relatório final
  generate_report
  
  log_section "✅ TESTES CONCLUÍDOS COM SUCESSO"
  log_success "Todos os uploads foram processados"
  log_success "Validações SQL executadas"
  log_info "Verifique os resultados acima"
}

# Executar
main "$@"
