# 🖥️ VM Information Checklist

Preencha estas informações para configurar o deployment automatizado:

## 📡 Acesso à VM

- **IP ou Hostname:** `srv1045889.hstgr.cloud` ou `148.230.78.91`
- **Porta SSH:** `22` (padrão)
- **Usuário SSH:** `root`
- **Método de autenticação:** [x] Senha  [ ] Chave SSH
  - Se chave SSH, caminho: `(verificar no painel Hostinger)`

## 🐧 Sistema Operacional

- **OS:** [x] Ubuntu [ ] Debian [ ] CentOS [ ] Outro: `___________`
- **Versão:** `Ubuntu 24.04 with Easypanel`
- **Arquitetura:** [x] x86_64 [ ] ARM

## 🐍 Python

- **Python instalado?** [x] Sim [ ] Não
  - Se sim, versão: `Python 3.12.3`
- **pip instalado?** [ ] Sim [x] Não (precisa instalar)
- **venv disponível?** [x] Sim [ ] Não

## 🌐 Servidor Web

- **Web server instalado?** [ ] Nginx [ ] Apache [x] Nenhum (precisa instalar Nginx)
  - Se sim, versão: `(será instalado)`
- **Porta HTTP disponível?** [x] 80 [ ] Outra: `___________`
- **Porta HTTPS disponível?** [x] 443 [ ] Outra: `___________`

## 🗄️ Banco de Dados

- **Preferência:** [x] SQLite [ ] PostgreSQL [ ] MySQL
- **SQLite instalado?** [ ] Sim [x] Não (precisa instalar)
- **PostgreSQL instalado?** [ ] Sim [x] Não

## 🔒 Domínio e SSL

- **Tem domínio?** [ ] Sim [x] Não (pode usar IP: 148.230.78.91)
  - Se sim, qual: `(opcional - pode configurar depois)`
- **Domínio já aponta para VM?** [ ] Sim [x] Não
- **Quer SSL/HTTPS?** [x] Sim (Let's Encrypt) [ ] Não (apenas HTTP)

## 📁 Caminhos

- **Caminho para instalar app:** `/opt/financial-app`
- **Usuário que vai rodar o app:** `root` (inicial) → `financial-app` (criar depois)

## 🔐 Configurações de Segurança

- **Firewall ativo?** [ ] Sim [x] Não (UFW instalado mas inativo - ativar no deployment)
- **SELinux ativo?** [ ] Sim [x] Não (Ubuntu não usa)
- **Fail2ban instalado?** [ ] Sim [x] Não (instalar no deployment)

## 💾 Backup

- **Onde fazer backup remoto?** 
  - [x] Mesmo servidor (pasta diferente): `/backups/financial-app`
  - [ ] Servidor remoto via rsync/scp (configurar depois)
  - [ ] Cloud Storage (Google Drive, etc): `(opcional - configurar depois)`

## ⚙️ Recursos da VM

- **CPUs:** `2 cores`
- **RAM:** `8 GB`
- **Disco disponível:** `100 GB total`
- **Usuários esperados:** `5-10 usuários` (inicialmente você + família/amigos)

---

## 🤖 Script Automático de Coleta

**Cole este script na VM e execute para coletar informações automaticamente:**

```bash
#!/bin/bash
# Salve como: vm_info_collect.sh
# Execute: bash vm_info_collect.sh

echo "🖥️  VM Information Collection Script"
echo "===================================="
echo ""

echo "📡 Network Information:"
echo "  Hostname: $(hostname)"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo "  Public IP: $(curl -s ifconfig.me 2>/dev/null || echo 'N/A')"
echo ""

echo "🐧 Operating System:"
echo "  OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "  Kernel: $(uname -r)"
echo "  Architecture: $(uname -m)"
echo ""

echo "🐍 Python:"
which python3 > /dev/null && {
    echo "  Python3: $(python3 --version)"
    echo "  Path: $(which python3)"
} || echo "  Python3: NOT INSTALLED"

which pip3 > /dev/null && {
    echo "  pip3: $(pip3 --version | cut -d' ' -f2)"
} || echo "  pip3: NOT INSTALLED"

python3 -m venv --help > /dev/null 2>&1 && echo "  venv: AVAILABLE" || echo "  venv: NOT AVAILABLE"
echo ""

echo "🌐 Web Servers:"
which nginx > /dev/null && {
    echo "  Nginx: $(nginx -v 2>&1 | cut -d'/' -f2)"
} || echo "  Nginx: NOT INSTALLED"

which apache2 > /dev/null && {
    echo "  Apache: $(apache2 -v | head -1 | cut -d'/' -f2 | cut -d' ' -f1)"
} || echo "  Apache: NOT INSTALLED"
echo ""

echo "🗄️  Database:"
which psql > /dev/null && {
    echo "  PostgreSQL: $(psql --version | cut -d' ' -f3)"
} || echo "  PostgreSQL: NOT INSTALLED"

which mysql > /dev/null && {
    echo "  MySQL: $(mysql --version | cut -d' ' -f6 | cut -d',' -f1)"
} || echo "  MySQL: NOT INSTALLED"

which sqlite3 > /dev/null && {
    echo "  SQLite3: $(sqlite3 --version | cut -d' ' -f1)"
} || echo "  SQLite3: NOT INSTALLED"
echo ""

echo "🔒 Security:"
which ufw > /dev/null && {
    echo "  UFW: $(ufw status | head -1)"
} || echo "  UFW: NOT INSTALLED"

which firewall-cmd > /dev/null && {
    echo "  firewalld: INSTALLED"
} || echo "  firewalld: NOT INSTALLED"

sestatus > /dev/null 2>&1 && {
    echo "  SELinux: $(sestatus | grep 'SELinux status' | awk '{print $3}')"
} || echo "  SELinux: NOT AVAILABLE"

which fail2ban-client > /dev/null && {
    echo "  Fail2ban: INSTALLED"
} || echo "  Fail2ban: NOT INSTALLED"
echo ""

echo "⚙️  Resources:"
echo "  CPUs: $(nproc)"
echo "  RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "  Disk (root): $(df -h / | tail -1 | awk '{print $4}') available"
echo ""

echo "📁 Suggested Paths:"
echo "  App directory: /opt/financial-app"
echo "  App user: www-data"
echo "  Database: /opt/financial-app/instance/financas.db"
echo "  Logs: /opt/financial-app/logs"
echo ""

echo "✅ Collection complete! Copy this output to VM_INFO_CHECKLIST.md"
```

---

## 📋 Após Coletar Informações

Preencha o checklist acima com os dados coletados e salve este arquivo.

Os scripts de deployment usarão estas informações para:
- ✅ Configurar conexão SSH automatizada
- ✅ Gerar comandos de instalação adequados ao SO
- ✅ Configurar Nginx/Apache corretamente
- ✅ Definir caminhos de backup
- ✅ Configurar SSL se necessário
- ✅ Ajustar configurações de segurança

**Próximos passos:**
1. Execute o script na VM e cole a saída aqui
2. Preencha o checklist
3. Os scripts de deployment serão gerados automaticamente
