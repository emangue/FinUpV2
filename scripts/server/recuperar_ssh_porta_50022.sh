#!/bin/bash
# =============================================================================
# RECUPERAR SSH — Porta 50022
# =============================================================================
# Execute este script NO SERVIDOR via Console VNC da Hostinger (como root).
# Não execute localmente!
#
# Uso: copie e cole o conteúdo no console VNC, ou:
#      scp este arquivo para o servidor e execute: bash recuperar_ssh_porta_50022.sh
#
# Ref: docs/deploy/RECUPERACAO_SSH_PORTA_CUSTOMIZADA.md
# =============================================================================

set -euo pipefail

[[ $EUID -ne 0 ]] && { echo "Execute como root."; exit 1; }

# Sua chave pública — ATUALIZE se usar outra chave
PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID2giK86YuhwkQ9eLcDzOXNRYN4C/kjtCHZi/J5vXEMk vscode-copilot"
SSH_PORT=50022
DEPLOY_USER="deploy"

echo "=========================================="
echo "  Recuperação SSH — Porta $SSH_PORT"
echo "=========================================="

# 1. Criar usuário deploy se não existir
if ! id "$DEPLOY_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" "$DEPLOY_USER"
    usermod -aG sudo "$DEPLOY_USER"
    echo "[OK] Usuário $DEPLOY_USER criado"
else
    echo "[OK] Usuário $DEPLOY_USER já existe"
fi

# 2. Configurar SSH para deploy
mkdir -p /home/$DEPLOY_USER/.ssh
grep -qF "$PUBKEY" /home/$DEPLOY_USER/.ssh/authorized_keys 2>/dev/null || echo "$PUBKEY" >> /home/$DEPLOY_USER/.ssh/authorized_keys
sort -u /home/$DEPLOY_USER/.ssh/authorized_keys -o /home/$DEPLOY_USER/.ssh/authorized_keys
chmod 700 /home/$DEPLOY_USER/.ssh
chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys
chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh
echo "[OK] Chave adicionada ao usuário $DEPLOY_USER"

# 3. Também em root (para compatibilidade com scripts que usam root)
mkdir -p /root/.ssh
grep -qF "$PUBKEY" /root/.ssh/authorized_keys 2>/dev/null || echo "$PUBKEY" >> /root/.ssh/authorized_keys
sort -u /root/.ssh/authorized_keys -o /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
echo "[OK] Chave adicionada ao root"

# 4. Backup e configurar sshd
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d)

# Garantir Port 50022
if grep -q "^Port " /etc/ssh/sshd_config; then
    sed -i "s/^Port .*/Port $SSH_PORT/" /etc/ssh/sshd_config
else
    sed -i "s/^#Port .*/Port $SSH_PORT/" /etc/ssh/sshd_config
fi
grep -q "^Port $SSH_PORT" /etc/ssh/sshd_config || echo "Port $SSH_PORT" >> /etc/ssh/sshd_config

# Permitir root e deploy
sed -i 's/^#*PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*PubkeyAuthentication .*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# 5. Validar e reiniciar (ssh ou sshd conforme versão do Ubuntu)
sshd -t || { echo "[ERRO] Config sshd inválida"; exit 1; }
systemctl restart ssh 2>/dev/null || systemctl restart sshd 2>/dev/null || service ssh restart
echo "[OK] SSH reiniciado na porta $SSH_PORT"

# 6. UFW
if command -v ufw &>/dev/null; then
    ufw allow ${SSH_PORT}/tcp 2>/dev/null || true
    ufw deny 22/tcp 2>/dev/null || true
    ufw --force enable 2>/dev/null || true
    echo "[OK] UFW: porta $SSH_PORT liberada, 22 bloqueada"
fi

echo ""
echo "=========================================="
echo "  PRONTO! Teste do seu Mac:"
echo "  ssh -p $SSH_PORT deploy@148.230.78.91"
echo "=========================================="
