#!/bin/bash
# 🔒 Script para carregar credenciais de deploy
# Uso: source scripts/deploy/load_credentials.sh

CREDENTIALS_FILE=".env.deploy"

if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Erro: Arquivo $CREDENTIALS_FILE não encontrado!"
    echo "   Credenciais de deploy não configuradas."
    exit 1
fi

# Carregar variáveis
export $(grep -v '^#' "$CREDENTIALS_FILE" | xargs)

# Validar variáveis críticas
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_PASSWORD" ]; then
    echo "❌ Erro: Credenciais incompletas em $CREDENTIALS_FILE"
    exit 1
fi

echo "✅ Credenciais carregadas com sucesso"
echo "   Servidor: $SERVER_USER@$SERVER_HOST"
echo "   App Path: $SERVER_APP_PATH"
echo "   SSH Keys: ED25519 + RSA configuradas"
