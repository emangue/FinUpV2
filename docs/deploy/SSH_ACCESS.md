# 🔑 ACESSO SSH - CONFIGURAÇÃO E TROUBLESHOOTING

## ⚡ ACESSO RÁPIDO - COMANDOS ESSENCIAIS

### 🚀 Conectar ao Servidor
```bash
ssh minha-vps-hostinger
```

### 🔍 Comandos Críticos no Servidor
```bash
# Status dos serviços
systemctl status finup-backend finup-frontend

# Logs em tempo real
journalctl -u finup-backend -f

# Health check
curl -s http://localhost:8000/api/health

# Navegar para projeto
cd /var/www/finup

# Git status
git status && git log --oneline -3
```

## 🛠️ CONFIGURAÇÃO ATUAL

### 📋 Dados do Servidor
- **IP:** 148.230.78.91 
- **User:** root
- **Port:** 22
- **Hostname:** srv1045889
- **Provider:** Hostinger VPS

### 📝 SSH Config (~/.ssh/config)
```
# VS Code Remote SSH - Hostinger VPS
Host minha-vps-hostinger
    HostName 148.230.78.91
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ConnectTimeout 10
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

### 🔐 Chave SSH Configurada
- **Tipo:** ED25519 (mais segura)
- **Local:** `~/.ssh/id_ed25519`
- **Pública:** `~/.ssh/id_ed25519.pub`
- **Autorizada no servidor:** ✅ Em `/root/.ssh/authorized_keys`

## 🚨 TROUBLESHOOTING SSH

### ❌ "Connection refused"
```bash
# 1. Verificar se IP está correto
ping 148.230.78.91

# 2. Tentar SSH com verbose
ssh -vv minha-vps-hostinger

# 3. Verificar se chave existe
ls -la ~/.ssh/id_ed25519*

# 4. Testar com senha (backup)
ssh -o PreferredAuthentications=password root@148.230.78.91
# Senha: vywjib-fUqfow-2bohjiA1#
```

### ❌ "Permission denied"
```bash
# 1. Verificar permissões da chave
chmod 600 ~/.ssh/id_ed25519

# 2. Verificar se chave está no ssh-agent
ssh-add -l
ssh-add ~/.ssh/id_ed25519

# 3. Regenerar chave se necessário
ssh-keygen -t ed25519 -C "vscode-copilot" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub  # Copiar e adicionar no servidor
```

### ❌ Chave não autorizada no servidor
```bash
# Acessar via senha e adicionar chave
ssh -o PreferredAuthentications=password root@148.230.78.91

# No servidor:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID2giK86YuhwkQ9eLcDzOXNRYN4C/kjtCHZi/J5vXEMk vscode-copilot" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Testar nova conexão
exit
ssh minha-vps-hostinger
```

## 🔧 VS CODE REMOTE SSH

### 🎯 Conectar no VS Code
1. **Command Palette:** `Cmd+Shift+P`
2. **Comando:** `Remote-SSH: Connect to Host...`
3. **Escolher:** `minha-vps-hostinger`
4. **Plataforma:** `Linux`
5. **Aguardar conexão**

### 🗂️ Abrir Projeto no VS Code Remote
```
Remote Path: /var/www/finup
```

### 🚨 Problemas no VS Code Remote
```bash
# 1. Limpar cache do VS Code Remote
rm -rf ~/.vscode-server

# 2. Reinstalar extensão Remote SSH
# Command Palette > Extensions: Reinstall Extension > Remote SSH

# 3. Verificar logs do VS Code
# Command Palette > Remote-SSH: Show Log
```

## 📋 COMANDOS ESSENCIAIS NO SERVIDOR

### 🔍 Investigação de Problemas
```bash
# Sistema
top                          # Processos em execução
df -h                        # Espaço em disco
free -h                      # Memória disponível

# Serviços FinUp  
systemctl status finup-backend finup-frontend
journalctl -u finup-backend -n 50
journalctl -u finup-frontend -n 50

# Aplicação
cd /var/www/finup
git status
git log --oneline -5
ls -la app_dev/backend/
ps aux | grep -E "(uvicorn|python|node)"

# Banco de dados
cd /var/www/finup/app_dev/backend/database
ls -lh *.db
ls -lh backups_daily/ | head -5

# Rede e portas
netstat -tlnp | grep -E "(8000|3000)"
curl -s localhost:8000/api/health
curl -s localhost:3000
```

### 🔄 Reiniciar Serviços
```bash
# Backend apenas
systemctl restart finup-backend
systemctl status finup-backend --no-pager

# Frontend apenas  
systemctl restart finup-frontend
systemctl status finup-frontend --no-pager

# Ambos
systemctl restart finup-backend finup-frontend
systemctl status finup-backend finup-frontend --no-pager

# Verificar se subiram
sleep 3 && curl -s localhost:8000/api/health
```

### 📊 Monitoramento em Tempo Real
```bash
# Logs do backend
journalctl -u finup-backend -f

# Logs do frontend
journalctl -u finup-frontend -f  

# Ambos simultaneamente
journalctl -u finup-backend -u finup-frontend -f

# Logs de sistema
tail -f /var/log/syslog
```

## 🛡️ SEGURANÇA E BACKUP

### 🔐 Backup da Configuração SSH
```bash
# Local - backup da config SSH
cp ~/.ssh/config ~/.ssh/config.backup
cp ~/.ssh/id_ed25519* ~/Documents/backup_ssh/

# Servidor - backup da chave autorizada
ssh minha-vps-hostinger "cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.backup"
```

### 🚨 Recuperação de Emergência
```bash
# Se perder chave SSH, acessar via senha:
ssh -o PreferredAuthentications=password root@148.230.78.91
# Senha: vywjib-fUqfow-2bohjiA1#

# No servidor, verificar chaves autorizadas:
cat ~/.ssh/authorized_keys

# Adicionar nova chave:
echo "nova_chave_publica" >> ~/.ssh/authorized_keys
```

### 🔍 Auditoria de Segurança
```bash
ssh minha-vps-hostinger "
    # Verificar tentativas de login
    journalctl -u ssh -n 50 | grep 'Failed\|Accepted'
    
    # Verificar usuários logados
    who
    
    # Verificar chaves SSH
    cat ~/.ssh/authorized_keys | wc -l
    
    # Status do firewall
    ufw status verbose
"
```

## 📋 CHECKLIST DE VERIFICAÇÃO

### ✅ Antes de Trabalhar no Servidor
- [ ] ✅ SSH conecta: `ssh minha-vps-hostinger`
- [ ] ✅ VS Code Remote conecta
- [ ] ✅ Serviços ativos: `systemctl status finup-backend finup-frontend`
- [ ] ✅ Health check: `curl localhost:8000/api/health`
- [ ] ✅ Git sincronizado: `cd /var/www/finup && git status`

### ✅ Após Modificações no Servidor
- [ ] ✅ Serviços reiniciados com sucesso
- [ ] ✅ Logs sem erros críticos
- [ ] ✅ Health check passou
- [ ] ✅ Frontend acessível

### 🚨 Em Caso de Problemas
1. **Não consegue SSH:** Usar senha de backup
2. **Servidor lento:** Verificar `top` e `df -h`
3. **Serviço não sobe:** Ver `journalctl -u finup-backend -n 20`
4. **Erro no código:** Fazer `git pull` para atualizar

## 🎯 INTEGRAÇÃO COM DEPLOY

Os scripts de deploy usam automaticamente a configuração SSH:
```bash
# Deploy usa: ssh minha-vps-hostinger
./scripts/deploy/quick_deploy.sh
./scripts/deploy/deploy_safe_v2.sh

# Monitoramento pós-deploy
ssh minha-vps-hostinger 'journalctl -u finup-backend -f'
```

**🔥 IMPORTANTE:** Sempre manter acesso SSH funcionando para investigações e deploys!

---

## 🔐 CREDENCIAIS DO SISTEMA

**Aplicação Web (Frontend):**
- **Email:** admin@financas.com
- **Senha:** cahriZqonby8

## 🗄️ BANCOS DE DADOS

### Local (SQLite)
```bash
# Path do banco
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db

# Query exemplo
sqlite3 app_dev/backend/database/financas_dev.db "SELECT email FROM users;"
```

### Servidor (PostgreSQL)
```bash
# Conectar via SSH
ssh minha-vps-hostinger

# Query no PostgreSQL
PGPASSWORD='FinUp2026SecurePass' psql -h 127.0.0.1 -U finup_user -d finup_db -c "SELECT email FROM users;"

# Connection string completa
postgresql://finup_user:FinUp2026SecurePass@127.0.0.1:5432/finup_db
```

**⚠️ CRÍTICO:** 
- **Local usa SQLite** - arquivo único
- **Servidor usa PostgreSQL** - banco estruturado
- **Credenciais admin sincronizadas** entre ambientes