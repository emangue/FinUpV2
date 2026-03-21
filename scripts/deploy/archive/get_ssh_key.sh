#!/bin/bash
# 🔑 Script para obter chaves SSH públicas
# Uso: ./scripts/deploy/get_ssh_key.sh [ed25519|rsa]

source "$(dirname "$0")/load_credentials.sh"

KEY_TYPE=${1:-"ed25519"}

case "$KEY_TYPE" in
    ed25519)
        echo "$SSH_KEY_ED25519"
        ;;
    rsa)
        echo "$SSH_KEY_RSA"
        ;;
    all)
        echo "# Chave ED25519 (Deploy Automation 2026)"
        echo "$SSH_KEY_ED25519"
        echo ""
        echo "# Chave RSA (Emanuel Hostinger VPS)"
        echo "$SSH_KEY_RSA"
        ;;
    *)
        echo "❌ Uso: $0 [ed25519|rsa|all]"
        exit 1
        ;;
esac
