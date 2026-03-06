#!/bin/bash
# =============================================================================
# setup.sh — Setup de segurança do VPS FinUp
# =============================================================================
#
# COMO USAR:
#   1. Acesse o servidor via Console VNC do Hostinger (hPanel → VPS → Console)
#   2. Faça login como root
#   3. Execute:
#        curl -fsSL https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPO/main/scripts/server/setup.sh | bash
#      OU copie e cole o script diretamente no console
#
# O QUE ESTE SCRIPT FAZ:
#   - Cria usuário 'deploy' (não-root) com acesso Docker
#   - Configura SSH na porta 50022 (sem root login, sem senha)
#   - Gera chave SSH ed25519 para GitHub Actions
#   - Configura UFW: libera apenas 80, 443, 50022
#   - Instala e configura fail2ban (proteção brute-force)
#   - Para qualquer Nginx rodando no host (será movido para Docker)
#   - Cria estrutura de diretórios em /opt/finup
#
# APÓS RODAR:
#   - Anote a CHAVE PRIVADA exibida no final → vai para GitHub Secret SSH_PRIVATE_KEY
#   - Atualize ~/.ssh/config na sua máquina local (porta 50022)
#   - NÃO feche este console até confirmar acesso SSH no novo usuário
#
# =============================================================================

set -euo pipefail

# ─── Cores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[AVISO]${NC} $*"; }
err()  { echo -e "${RED}[ERRO]${NC} $*"; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $*"; }

# ─── Verificações iniciais ─────────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && err "Execute como root."
[[ "$(uname -s)" != "Linux" ]] && err "Apenas Linux suportado."

SSH_PORT="${SSH_PORT:-50022}"
DEPLOY_USER="deploy"
APP_DIR="/opt/finup"
DEPLOY_KEY_PATH="/home/${DEPLOY_USER}/.ssh/github_actions"

echo ""
echo "======================================================"
echo "  Setup de Segurança — VPS FinUp"
echo "  SSH port : ${SSH_PORT}"
echo "  App dir  : ${APP_DIR}"
echo "  Usuario  : ${DEPLOY_USER}"
echo "======================================================"
echo ""

# =============================================================================
# 1. Atualizar sistema
# =============================================================================
info "1/8 Atualizando sistema..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
    curl wget git unzip \
    fail2ban ufw \
    htop iotop \
    ca-certificates gnupg lsb-release
ok "Sistema atualizado"

# =============================================================================
# 2. Instalar Docker (se não instalado)
# =============================================================================
info "2/8 Verificando Docker..."
if ! command -v docker &>/dev/null; then
    info "Instalando Docker Engine..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    ok "Docker instalado: $(docker --version)"
else
    ok "Docker já instalado: $(docker --version)"
fi

if ! docker compose version &>/dev/null; then
    warn "Docker Compose v2 não encontrado. Instalando plugin..."
    apt-get install -y docker-compose-plugin
fi
ok "Docker Compose: $(docker compose version --short)"

# =============================================================================
# 3. Criar usuário deploy
# =============================================================================
info "3/8 Criando usuário '${DEPLOY_USER}'..."
if id "${DEPLOY_USER}" &>/dev/null; then
    warn "Usuário '${DEPLOY_USER}' já existe — pulando criação"
else
    adduser --disabled-password --gecos "" "${DEPLOY_USER}"
    ok "Usuário '${DEPLOY_USER}' criado"
fi

usermod -aG docker "${DEPLOY_USER}"
usermod -aG sudo  "${DEPLOY_USER}"
ok "Usuário adicionado aos grupos docker e sudo"

# Configurar sudo sem senha para comandos Docker (deploy não precisará de senha)
echo "${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/local/bin/docker" \
    > /etc/sudoers.d/deploy-docker
chmod 440 /etc/sudoers.d/deploy-docker

# =============================================================================
# 4. Gerar chave SSH para GitHub Actions
# =============================================================================
info "4/8 Gerando chave SSH para GitHub Actions..."
mkdir -p "/home/${DEPLOY_USER}/.ssh"
chmod 700 "/home/${DEPLOY_USER}/.ssh"

if [[ -f "${DEPLOY_KEY_PATH}" ]]; then
    warn "Chave SSH já existe em ${DEPLOY_KEY_PATH} — pulando geração"
else
    ssh-keygen -t ed25519 -C "github-actions-finup-deploy" \
        -f "${DEPLOY_KEY_PATH}" -N ""
    ok "Chave SSH gerada"
fi

# Autorizar a chave pública gerada
cat "${DEPLOY_KEY_PATH}.pub" >> "/home/${DEPLOY_USER}/.ssh/authorized_keys"
sort -u "/home/${DEPLOY_USER}/.ssh/authorized_keys" -o "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chmod 600 "/home/${DEPLOY_USER}/.ssh/authorized_keys"
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"
ok "Chave pública adicionada a authorized_keys"

# =============================================================================
# 5. Hardening SSH
# =============================================================================
info "5/8 Configurando SSH (porta ${SSH_PORT}, sem root, sem senha)..."

# Backup do sshd_config original
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%Y%m%d)

cat > /etc/ssh/sshd_config <<SSHEOF
# FinUp — SSH hardened config
Port ${SSH_PORT}

# Autenticação
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
ChallengeResponseAuthentication no
UsePAM yes

# Restrições
AllowUsers ${DEPLOY_USER}
MaxAuthTries 3
MaxSessions 5
LoginGraceTime 30

# Keepalive (detectar conexões mortas)
ClientAliveInterval 300
ClientAliveCountMax 2

# Segurança extra
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PermitEmptyPasswords no
PrintMotd no

# Banner
Banner /etc/ssh/banner

# Log detalhado
LogLevel VERBOSE
SSHEOF

# Banner de aviso
cat > /etc/ssh/banner <<BANNEREOF

  ██████████████████████████████████████████████████
  ██  ACESSO RESTRITO — FinUp Production Server  ██
  ██  Conexões são registradas e monitoradas.    ██
  ██████████████████████████████████████████████████

BANNEREOF

# Validar config antes de aplicar
sshd -t || err "Configuração SSH inválida! Verifique /etc/ssh/sshd_config"
systemctl restart ssh
ok "SSH reiniciado na porta ${SSH_PORT}"

# =============================================================================
# 6. Configurar UFW (Firewall)
# =============================================================================
info "6/8 Configurando firewall UFW..."

ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Apenas 3 portas abertas
ufw allow 80/tcp   comment "Nginx HTTP"
ufw allow 443/tcp  comment "Nginx HTTPS"
ufw allow "${SSH_PORT}/tcp" comment "SSH deploy"

# Bloquear explicitamente portas internas (redundante com deny incoming, mas documentado)
ufw deny 5432/tcp  comment "PostgreSQL — interno somente"
ufw deny 6379/tcp  comment "Redis — interno somente"
ufw deny 8000/tcp  comment "Backend FastAPI — interno somente"
ufw deny 3000/tcp  comment "Next.js — interno somente"
ufw deny 3001/tcp  comment "Next.js admin — interno somente"

ufw --force enable
ok "UFW ativo:"
ufw status numbered

# =============================================================================
# 7. Configurar fail2ban
# =============================================================================
info "7/8 Configurando fail2ban..."

cat > /etc/fail2ban/jail.local <<F2BEOF
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 3
backend  = systemd

# SSH na porta customizada
[sshd]
enabled  = true
port     = ${SSH_PORT}
filter   = sshd
logpath  = /var/log/auth.log
maxretry = 3
bantime  = 86400

# Nginx — requisições inválidas repetidas
[nginx-http-auth]
enabled  = true
port     = http,https
filter   = nginx-http-auth
logpath  = /var/log/nginx/error.log
maxretry = 5

# Nginx — scan de URLs suspeitas
[nginx-botsearch]
enabled  = true
port     = http,https
filter   = nginx-botsearch
logpath  = /var/log/nginx/access.log
maxretry = 2
bantime  = 86400
F2BEOF

systemctl enable fail2ban
systemctl restart fail2ban
ok "fail2ban configurado e ativo"

# =============================================================================
# 8. Parar Nginx do host (será gerenciado pelo Docker)
# =============================================================================
info "8/8 Verificando Nginx no host..."
if systemctl is-active --quiet nginx; then
    warn "Nginx rodando no host — parando e desabilitando (Docker Compose assumirá)"
    systemctl stop nginx
    systemctl disable nginx
    ok "Nginx do host parado"
else
    ok "Nginx não está rodando no host"
fi

# =============================================================================
# Criar estrutura de diretórios da aplicação
# =============================================================================
info "Criando estrutura /opt/finup..."
mkdir -p "${APP_DIR}"/{nginx/conf.d,certbot/{conf,www},backups,secrets}
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}"
chmod 700 "${APP_DIR}/secrets"
ok "Estrutura criada em ${APP_DIR}"

# =============================================================================
# Imprimir resumo e instruções
# =============================================================================
PRIVATE_KEY=$(cat "${DEPLOY_KEY_PATH}")
PUBLIC_KEY=$(cat "${DEPLOY_KEY_PATH}.pub")

echo ""
echo "======================================================"
echo -e "${GREEN}  SETUP CONCLUÍDO COM SUCESSO!${NC}"
echo "======================================================"
echo ""
echo -e "${YELLOW}  PRÓXIMOS PASSOS (OBRIGATÓRIOS):${NC}"
echo ""
echo "  1. ADICIONE os seguintes Secrets no GitHub:"
echo "     (Settings → Secrets and variables → Actions → New repository secret)"
echo ""
echo "     SSH_HOST        = $(curl -s ifconfig.me 2>/dev/null || echo '148.230.78.91')"
echo "     SSH_PORT        = ${SSH_PORT}"
echo "     SSH_USER        = ${DEPLOY_USER}"
echo ""
echo "  2. SSH_PRIVATE_KEY — copie a chave abaixo COMPLETA:"
echo ""
echo "─────────────────── INÍCIO DA CHAVE PRIVADA ───────────────────"
echo "${PRIVATE_KEY}"
echo "──────────────────── FIM DA CHAVE PRIVADA ─────────────────────"
echo ""
echo "  3. Atualize o ~/.ssh/config na sua máquina LOCAL:"
echo ""
echo "     Host finup-vps"
echo "         HostName 148.230.78.91"
echo "         Port ${SSH_PORT}"
echo "         User ${DEPLOY_USER}"
echo "         IdentityFile ~/.ssh/sua_chave_local"
echo "         IdentitiesOnly yes"
echo ""
echo "  4. Teste o acesso SSH a partir da sua máquina:"
echo "     ssh -p ${SSH_PORT} ${DEPLOY_USER}@$(curl -s ifconfig.me 2>/dev/null || echo '148.230.78.91')"
echo ""
echo "  5. Siga o README de deploy para configurar .env.prod e subir os containers"
echo ""
echo -e "${RED}  ATENÇÃO: Não feche este console até confirmar SSH funcionando!${NC}"
echo "======================================================"
