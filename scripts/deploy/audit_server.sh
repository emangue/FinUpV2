#!/bin/bash
# Script de Auditoria do Servidor VPS
# Execute no servidor: bash audit_server.sh

echo "========================================"
echo "   AUDITORIA DO SERVIDOR - VPS"
echo "========================================"
echo ""

echo "📋 1. INFORMAÇÕES DO SISTEMA"
echo "----------------------------------------"
echo "Hostname: $(hostname)"
echo "IP: $(hostname -I | awk '{print $1}')"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime -p)"
echo ""

echo "👥 2. USUÁRIOS DO SISTEMA"
echo "----------------------------------------"
cat /etc/passwd | grep -E '/home|/root' | cut -d: -f1,6,7
echo ""

echo "📁 3. DIRETÓRIOS EM /var/www"
echo "----------------------------------------"
if [ -d "/var/www" ]; then
    ls -lah /var/www/ 2>/dev/null
    echo ""
    echo "Tamanho total:"
    du -sh /var/www/* 2>/dev/null | sort -rh
else
    echo "Pasta /var/www não existe"
fi
echo ""

echo "🏠 4. DIRETÓRIOS EM /home"
echo "----------------------------------------"
ls -lah /home/ 2>/dev/null
for dir in /home/*; do
    if [ -d "$dir" ]; then
        echo ""
        echo "Conteúdo de $dir:"
        ls -lah "$dir" 2>/dev/null | head -20
    fi
done
echo ""

echo "🔧 5. SERVIÇOS SYSTEMD CUSTOMIZADOS"
echo "----------------------------------------"
systemctl list-unit-files --type=service | grep -E 'enabled|static' | grep -v '@' | grep -v 'systemd-\|getty\|dbus\|cron\|rsyslog\|ssh\|networking\|ufw\|apparmor' | head -20
echo ""

echo "⚙️ 6. SERVIÇOS ATIVOS RELEVANTES"
echo "----------------------------------------"
systemctl list-units --type=service --state=running | grep -v 'systemd\|getty\|dbus\|cron\|rsyslog\|ssh\|user@\|accounts-daemon\|polkit' | head -20
echo ""

echo "🔍 7. PROCESSOS NODE/PYTHON/NGINX"
echo "----------------------------------------"
echo "Node.js:"
ps aux | grep node | grep -v grep || echo "Nenhum processo Node"
echo ""
echo "Python/Uvicorn:"
ps aux | grep -E 'python|uvicorn' | grep -v grep || echo "Nenhum processo Python"
echo ""
echo "Nginx:"
ps aux | grep nginx | grep -v grep || echo "Nginx não está rodando"
echo ""

echo "🌐 8. PORTAS ESCUTANDO"
echo "----------------------------------------"
ss -tulpn | grep LISTEN | grep -E ':(80|443|3000|8000|5432|27017|3306)' || echo "Nenhuma porta de aplicação aberta"
echo ""

echo "🔒 9. NGINX CONFIGURAÇÃO"
echo "----------------------------------------"
if [ -d "/etc/nginx" ]; then
    echo "Sites habilitados:"
    ls -la /etc/nginx/sites-enabled/ 2>/dev/null
    echo ""
    echo "Conteúdo de sites-available:"
    ls -la /etc/nginx/sites-available/ 2>/dev/null
else
    echo "Nginx não está instalado"
fi
echo ""

echo "💾 10. BANCO DE DADOS"
echo "----------------------------------------"
echo "PostgreSQL:"
systemctl status postgresql 2>/dev/null | grep -E "Active|Loaded" || echo "PostgreSQL não instalado/ativo"
echo ""
echo "MySQL/MariaDB:"
systemctl status mysql 2>/dev/null | grep -E "Active|Loaded" || echo "MySQL não instalado/ativo"
echo ""
echo "MongoDB:"
systemctl status mongodb 2>/dev/null | grep -E "Active|Loaded" || echo "MongoDB não instalado/ativo"
echo ""

echo "🔐 11. FIREWALL (UFW)"
echo "----------------------------------------"
ufw status verbose 2>/dev/null || echo "UFW não está instalado"
echo ""

echo "🗂️ 12. REPOSITÓRIOS GIT"
echo "----------------------------------------"
echo "Procurando repositórios Git..."
find /var/www /home -name ".git" -type d 2>/dev/null | while read gitdir; do
    projdir=$(dirname "$gitdir")
    echo ""
    echo "📦 $projdir"
    cd "$projdir"
    echo "   Remote: $(git remote -v 2>/dev/null | head -1)"
    echo "   Branch: $(git branch 2>/dev/null | grep '*')"
    echo "   Último commit: $(git log -1 --oneline 2>/dev/null)"
done
echo ""

echo "💿 13. ESPAÇO EM DISCO"
echo "----------------------------------------"
df -h | grep -E 'Filesystem|/$|/var|/home'
echo ""

echo "🧠 14. USO DE MEMÓRIA"
echo "----------------------------------------"
free -h
echo ""

echo "🔑 15. CHAVES SSH AUTORIZADAS"
echo "----------------------------------------"
for user in $(ls /home); do
    if [ -f "/home/$user/.ssh/authorized_keys" ]; then
        echo "Usuário: $user"
        cat "/home/$user/.ssh/authorized_keys" | head -2
        echo ""
    fi
done
if [ -f "/root/.ssh/authorized_keys" ]; then
    echo "Usuário: root"
    cat "/root/.ssh/authorized_keys" | head -2
fi
echo ""

echo "========================================"
echo "   AUDITORIA CONCLUÍDA"
echo "========================================"
echo ""
echo "📋 Próximos passos:"
echo "   1. Revise os serviços/processos ativos"
echo "   2. Identifique deploys antigos para remover"
echo "   3. Backup de dados importantes antes de limpar"
