#!/bin/bash
# 🔑 Configurar Chaves SSH para Deploy sem Senha
# Executar UMA VEZ no servidor via terminal web

set -e

echo "🔑 CONFIGURAÇÃO DE CHAVES SSH"
echo "========================================"
echo ""

# Criar diretório .ssh se não existir
echo "📁 Criando diretório .ssh..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Adicionar chaves autorizadas
echo "🔐 Adicionando chaves SSH autorizadas..."
cat > ~/.ssh/authorized_keys << 'SSH_KEYS'
# Deploy Automation 2026 (ED25519)
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFdCGuKwRlAxOh8rm2wyLlKlQLDswRDrJdorpdnRrYlt deploy@financas-20260112

# Emanuel Hostinger VPS (RSA)
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDJ1/acx9xfptNhlII3TqF/mZNFaOr38MHhpWkQMQye9Hd9jBVNqLBHpcjpVlOmJ/NgyCfCjM0MR186+vSYlvzL4sqZwtT1qJA0+SSFxhAUG4C9lHZE5jWxaltPCqH4KEmv92cka3YR4XfP50cqSkVdu81xLcd7lGDTI6sc8E70rzYyut76HWU1ZcXhQyiUnJE8p00AtbzRf0AVKOsqK1n+vLVzGcmST95FEUKkjNoMS/RQDq8P+yBngyTPxoTnjLIRwiL1moGaKy65deFNwjPBXS+ScBH9M1/ZHbpbG7K2F5gKcvYl/SHGzDlKWmWJFmd6035eznk6rTdgsVaz/ths6FsS5LX+K4af+CNf6C3ZfX/n1oQzrFSldaQ1ShmZFn+nbuqV3SMPyLJ+l0LUCOP2ZL09PvffX0cW7jnxpzyvInhPasKOoZWH7QjRHmGpsAvEHFMjjW00cwNTo7My/Si6wRMfytQa1o+/dOysnAAGdtnvIt5wAJ+3lQXsD4/3CbI7sK3y+8NLoVsM5rorsta22cuGL9olRqKvxdDXKrdbIC7DWO997a0znt7UL33vuLAncrqiwWTY7DVGsCwt5t3M+2Wwfj2H2efL63Pza6+QgN80DMqn0sNxhNd4Y/cg6cGwEkSvvUinGQksTK3GEGe6hZY+FzYJuJj42USKtw5r0w== emanuel-hostinger-vps
SSH_KEYS

chmod 600 ~/.ssh/authorized_keys

echo ""
echo "✅ Chaves SSH configuradas!"
echo ""
echo "📋 Chaves adicionadas:"
echo "   1. Deploy Automation 2026 (ED25519)"
echo "   2. Emanuel Hostinger VPS (RSA)"
echo ""
echo "🔒 Permissões corretas aplicadas"
echo ""
echo "========================================"
echo "✅ CONFIGURAÇÃO COMPLETA!"
echo "========================================"
echo ""
echo "🚀 Agora você pode fazer git push sem senha:"
echo "   git push vps main"
echo ""
