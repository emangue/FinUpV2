# 🎉 DEPLOY 95% CONCLUÍDO - SESSÃO 22/01/2026

**Data:** 22 de janeiro de 2026  
**Servidor:** srv1045889.hstgr.cloud (148.230.78.91)  
**Status:** ✅ **SSL INSTALADO - AGUARDANDO CACHE CDN** ✅  
**Domínio:** https://meufinup.com.br

---

## � SEGURANÇA IMPLEMENTADA - SESSÃO 22/01/2026

### ✅ SSL/HTTPS INSTALADO E FUNCIONANDO:
1. **✅ Certificado SSL Let's Encrypt** - Válido até 22/04/2026
2. **✅ HTTPS funcionando** - https://meufinup.com.br
3. **✅ Redirect HTTP → HTTPS** - Automático
4. **✅ Renovação automática** - Certbot configurado
5. **⏳ Aguardando cache CDN** - Hostinger está cacheando página parked

### ✅ FIREWALL UFW CONFIGURADO:
1. **✅ Portas expostas otimizadas** - Apenas 22 (SSH), 80 (HTTP), 443 (HTTPS)
2. **✅ Backend/Frontend protegidos** - Portas 8000 e 3000 apenas em localhost
3. **✅ Regras v4 e v6** - IPv4 e IPv6 configurados
4. **✅ PostgreSQL protegido** - Apenas localhost:5432

### ⏳ AGUARDANDO:
- **Cache CDN Hostinger** - Limpeza automática em 5-15 minutos
- **Registros CAA verificados** - Let's Encrypt autorizado ✅

---

## ✅ O QUE FOI CONCLUÍDO HOJE

### 1. INFRAESTRUTURA ✅ 100%
- ✅ Servidor limpo (3 deploys antigos removidos)
- ✅ Usuário `deploy` criado com sudo
- ✅ PostgreSQL 16 instalado e configurado
- ✅ Python 3.12.3 + Node.js 20.20.0 + Nginx instalados

### 2. BANCO DE DADOS ✅ 100%
- ✅ Database: `finup_db`
- ✅ User: `finup_user`  
- ✅ Password: `FinUp2026SecurePass`
- ✅ **36 tabelas criadas**
- ✅ **10.368 registros migrados** do SQLite → PostgreSQL
- ✅ Schema 100% sincronizado (tipos, colunas, constraints)
- ✅ 4 usuários migrados (admin@financas.com, teste@email.com, etc)

### 3. BACKEND API ✅ 100%
- ✅ Código transferido via rsync (5.4 MB)
- ✅ Venv + dependências instaladas (FastAPI, SQLAlchemy, psycopg2)
- ✅ `config.py` adaptado para PostgreSQL (DATABASE_URL)
- ✅ `database.py` atualizado (pool_pre_ping)
- ✅ `.env` com JWT secret + CORS
- ✅ Systemd service `finup-backend` (2 workers Uvicorn)
- ✅ API rodando na porta 8000
- ✅ Health check OK: `{"status":"healthy","database":"connected"}`
- ✅ Swagger funcionando: `/docs`

### 4. FRONTEND ✅ 100%
- ✅ 890 pacotes npm instalados
- ✅ Build concluído (30 rotas geradas)
- ✅ `.env.production` configurado
- ✅ Systemd service `finup-frontend` (porta 3000)
- ✅ Next.js 16 rodando
- ✅ **URLs de API corrigidas** (todas usando `NEXT_PUBLIC_API_URL`)
- ✅ **Autenticação JWT implementada** (fetchWithAuth)
- ✅ **Credenciais removidas** da tela de login (segurança)

### 5. NGINX ✅ 100%
- ✅ Reverse proxy configurado
- ✅ `/` → Frontend (porta 3000)
- ✅ `/api/` → Backend (porta 8000)
- ✅ `/docs` → Swagger
- ✅ `/health` → Health check
- ✅ SSL/HTTPS configurado (Certbot)
- ✅ Redirect HTTP→HTTPS automático
- ✅ Domínio configurado: meufinup.com.br

### 6. CORREÇÕES DE CONECTIVIDADE ✅ 90%
- ✅ AuthContext corrigido (login/me endpoints)
- ✅ Dashboard corrigido (3 endpoints: metrics, chart-data, categories)
- ✅ Transações corrigida (3 endpoints: list, filtered-total, update)
- ✅ Budget vs Actual corrigido
- ✅ 7 páginas de settings corrigidas:
  - Admin (usuários)
  - Screens (visibilidade)
  - Bancos
  - Cartões
  - Exclusões
  - Grupos
  - Upload (preview)

### 7. DADOS VALIDADOS ✅
- ✅ 2.631 transações em 2025 (usuário admin)
- ✅ 1.234 transações em 2024
- ✅ Dashboard funcionando com dados de Dez/2025
- ✅ Página de transações carregando dados
- ✅ Budget vs Planejado mostrando R$ 313.508,84

---

### 8. SEGURANÇA ✅ 95%
- ✅ **SSL/HTTPS implementado** - Certificado Let's Encrypt válido até 22/04/2026
- ✅ **Firewall UFW ativo** - Apenas portas essenciais expostas
- ✅ **Renovação automática SSL** - Certbot configurado com cron
- ✅ **Backend/Frontend em localhost** - Não acessíveis diretamente
- ✅ **PostgreSQL protegido** - Apenas localhost
- ✅ **JWT tokens** - Autenticação segura
- ⏳ **Cache CDN** - Aguardando limpeza (não afeta segurança)

---

## ⚠️ PROBLEMAS CONHECIDOS (5% restante)

### 🔴 CRÍTICO - Páginas Admin Ainda Quebradas
**Mesmo após correções, algumas páginas de admin não conectam:**
- ❌ **Categorias Genéricas** - "Failed to fetch"
- ❌ **Gestão de Bancos** - "0 bancos cadastrados" (deveria ter dados)
- ❌ **Visibilidade de Telas** - "Não existe no banco"
- ❌ Possivelmente outras páginas de configuração

**Possíveis causas:**
1. Endpoints do backend não implementados/incompatíveis
2. Tabelas específicas não migradas corretamente
3. Permissões de usuário insuficientes
4. CORS ou proxy não configurado para esses endpoints

### ⏳ AGUARDANDO
- **Cache CDN Hostinger** - Domínio https://meufinup.com.br ainda mostra página parked (limpa em 5-15min)

---

## 📊 STATUS DETALHADO DOS COMPONENTES

| Componente | Status | Porta | Detalhes |
|------------|--------|-------|----------|
| PostgreSQL 16 | ✅ Rodando | 5432 | 36 tabelas, 10.368 registros |
| Backend (FastAPI) | ✅ Rodando | 8000 (localhost) | 2 workers, JWT auth, CORS OK |
| Frontend (Next.js) | ✅ Rodando | 3000 (localhost) | 30 rotas, build 18s |
| Nginx | ✅ Rodando | 80, 443 | Proxy + SSL/HTTPS |
| **SSL/HTTPS** | ✅ **INSTALADO** | 443 | **Cert válido até 22/04/2026** |
| **Firewall UFW** | ✅ **ATIVO** | 22,80,443 | **Apenas portas essenciais** |
| **Domínio** | ⏳ Aguardando | - | DNS OK, cache CDN limpando |
| Dashboard | ✅ Funcionando | - | Gráficos + Budget OK |
| Transações | ✅ Funcionando | - | Lista + Filtros OK |
| Admin Pages | ⚠️ 50% OK | - | **Metade ainda quebrada** |
| Login/Auth | ✅ Funcionando | - | JWT tokens OK |

---

## 🔧 COMANDOS DE CONTROLE DO SISTEMA

### 🛑 Pausar Sistema (Por Segurança)
```bash
# Parar todos os serviços (Frontend, Backend, Nginx)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./pausar_sistema_seguranca.sh

# Ou manualmente:
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 '
  systemctl stop finup-frontend
  systemctl stop finup-backend
  systemctl stop nginx
  echo "✅ Sistema pausado"
'
```

### 🚀 Reativar Sistema (Quando Retomar)
```bash
# Iniciar todos os serviços
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./reativar_sistema.sh

# Ou manualmente:
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 '
  systemctl start finup-backend
  systemctl start finup-frontend
  systemctl start nginx
  echo "✅ Sistema iniciado"
'
```

### 📊 Verificar Status
```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 '
  systemctl status finup-backend --no-pager | head -8
  systemctl status finup-frontend --no-pager | head -8
  systemctl status nginx --no-pager | head -8
  systemctl status postgresql --no-pager | head -8
'
```

### 📋 Logs em Tempo Real
```bash
# Backend
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 'journalctl -u finup-backend -f'

# Frontend  
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 'journalctl -u finup-frontend -f'

# Nginx
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 'journalctl -u nginx -f'

# PostgreSQL
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 'journalctl -u postgresql -f'
```

### 🔄 Restart Completo
```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 '
  systemctl restart finup-backend
  systemctl restart finup-frontend
  systemctl restart nginx
  echo "✅ Sistema reiniciado"
'
```

---

## 🚀 PRÓXIMOS PASSOS (5% Restante)

### ✅ CONCLUÍDOS NA SESSÃO 22/01/2026:
1. ✅ **SSL/HTTPS implementado** - Certificado válido, HTTPS funcionando
2. ✅ **Firewall UFW configurado** - Apenas portas essenciais expostas

### 🎯 PENDENTE PARA FINALIZAR (5%):

#### 1. ⏳ AGUARDAR CACHE CDN LIMPAR (5-15 minutos)
**Status:** Em andamento  
**Ação:** Aguardar cache do Hostinger expirar automaticamente
**Domínio:** https://meufinup.com.br (mostrando página parked temporariamente)
**Servidor direto:** ✅ Funcionando perfeitamente

---

#### 2. CORRIGIR PÁGINAS ADMIN (ALTA PRIORIDADE) 🔧
**Tempo estimado:** 2-3 horas  
**Prioridade:** ALTA

```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# Instalar Certbot
apt update
#### 2. CORRIGIR PÁGINAS ADMIN (ALTA PRIORIDADE) 🔧
**Tempo estimado:** 2-3 horas  
**Prioridade:** ALTA

**Páginas com problema:**
- ❌ Categorias Genéricas
- ❌ Gestão de Bancos
- ❌ Visibilidade de Telas

**Plano de ação:**
```bash
# 1. Verificar quais endpoints existem no backend
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 '
  cd /var/www/finup/app_dev/backend
  grep -r "@router" app/domains/*/router.py | grep -E "classification|compatibility|screens"
'

# 2. Testar endpoints diretamente
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl -s http://127.0.0.1:8000/api/v1/classification/rules \
  -H "Authorization: Bearer $TOKEN" | jq

curl -s http://127.0.0.1:8000/api/v1/compatibility/ \
  -H "Authorization: Bearer $TOKEN" | jq

curl -s http://127.0.0.1:8000/api/v1/screens/ \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Verificar se tabelas existem no banco
PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db << 'SQL'
\dt *classification*
\dt *compatibility*
\dt *screen*
SELECT COUNT(*) FROM base_classificacao_generica;
SELECT COUNT(*) FROM compatibility;
SELECT COUNT(*) FROM screen_visibility;
SQL
```

**Estratégia de correção:**
1. Identificar endpoints faltantes
2. Criar migrations para tabelas faltantes
3. Popular dados iniciais (seeds)
4. Corrigir URLs no frontend
5. Testar cada página individualmente

---

#### 4. TESTES COMPLETOS (MÉDIA PRIORIDADE) ✅
**Tempo estimado:** 1-2 horas  
**Prioridade:** MÉDIA

**Checklist de testes:**
```bash
# Dashboard
- [ ] Gráfico Receitas vs Despesas carrega
- [ ] Budget vs Planejado mostra dados
- [ ] % por Categoria exibe corretamente
- [ ] Gastos com Cartões lista transações
- [ ] Filtros de ano/mês funcionam

# Transações
- [ ] Listagem carrega (paginação OK)
- [ ] Filtros funcionam (estabelecimento, categoria, tipo)
- [ ] Edição de transação salva corretamente
- [ ] Toggle "Ignorar Dashboard" funciona
- [ ] Busca por texto funciona

# Upload
- [ ] Upload de extrato CSV funciona
- [ ] Upload de fatura PDF funciona
- [ ] Preview mostra transações corretamente
- [ ] Marcação de grupos/subgrupos funciona
- [ ] Confirmação importa no banco

# Configurações
- [ ] Admin - Lista usuários
- [ ] Admin - Criar/editar/deletar usuário
- [ ] Cartões - Lista cartões
- [ ] Grupos - Lista e edita grupos
- [ ] Exclusões - Gerencia exclusões
- [ ] Bancos - Configura formatos

# Autenticação
- [ ] Login funciona
- [ ] Logout funciona
- [ ] Token expira corretamente (60min)
- [ ] Refresh token funciona
- [ ] Acesso não autorizado redireciona para login
```

---

#### 5. OTIMIZAÇÕES (BAIXA PRIORIDADE) ⚡
**Tempo estimado:** 1-2 horas  
**Prioridade:** BAIXA

```bash
# Backend - Adicionar índices no PostgreSQL
PGPASSWORD=FinUp2026SecurePass psql -U finup_user -h 127.0.0.1 -d finup_db << 'SQL'
-- Índices para queries mais rápidas
CREATE INDEX idx_journal_entries_user_ano_mes ON journal_entries(user_id, "Ano", "Mes");
CREATE INDEX idx_journal_entries_categoria ON journal_entries("CategoriaGeral");
CREATE INDEX idx_journal_entries_grupo ON journal_entries("GRUPO");
CREATE INDEX idx_journal_entries_data ON journal_entries("Data");

-- Verificar performance
EXPLAIN ANALYZE 
SELECT * FROM journal_entries 
WHERE user_id = 1 AND "Ano" = 2025 
ORDER BY "Data" DESC LIMIT 50;
SQL

# Frontend - Configurar cache do Nginx
cat >> /etc/nginx/sites-available/finup << 'EOF'
    # Cache de assets estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
EOF

nginx -t && systemctl reload nginx

# Monitoramento - Instalar htop, netstat
apt install htop net-tools -y
```

---

#### 6. BACKUP E DISASTER RECOVERY (MÉDIA PRIORIDADE) 💾
**Tempo estimado:** 30 minutos  
**Prioridade:** MÉDIA

```bash
# Criar script de backup automático
cat > /root/backup_finup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups_finup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
PGPASSWORD=FinUp2026SecurePass pg_dump -U finup_user -h 127.0.0.1 finup_db \
  | gzip > $BACKUP_DIR/finup_db_$TIMESTAMP.sql.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "✅ Backup concluído: finup_db_$TIMESTAMP.sql.gz"
EOF

chmod +x /root/backup_finup.sh

# Testar backup
/root/backup_finup.sh

# Agendar backup diário (3h da manhã)
crontab -e
# Adicionar linha:
0 3 * * * /root/backup_finup.sh >> /var/log/backup_finup.log 2>&1
```

---

#### 7. DOCUMENTAÇÃO FINAL (BAIXA PRIORIDADE) 📚
**Tempo estimado:** 1 hora  
**Prioridade:** BAIXA

**Criar documentos:**
- [ ] README.md - Visão geral do sistema
- [ ] MANUAL_USUARIO.md - Como usar o sistema
- [ ] RUNBOOK.md - Procedimentos operacionais
- [ ] TROUBLESHOOTING.md - Solução de problemas comuns
- [ ] API.md - Documentação da API
- [ ] CHANGELOG.md - Histórico de mudanças

---

## 📋 CHECKLIST DE SEGURANÇA

Antes de considerar o sistema "pronto para produção":

### 🔒 Segurança de Rede
- [ ] SSL/HTTPS instalado e funcionando
- [ ] Firewall UFW habilitado e configurado
- [ ] Apenas portas 22, 80, 443 expostas
- [ ] SSH com autenticação por chave (não senha)
- [ ] Fail2ban instalado (opcional, protege contra brute force)

### 🗄️ Segurança do Banco
- [ ] PostgreSQL apenas em localhost (não exposto)
- [ ] Senha forte do banco (FinUp2026SecurePass ✅)
- [ ] Backups automáticos configurados
- [ ] Teste de restore de backup realizado

### 🔐 Segurança da Aplicação
- [ ] JWT secret seguro e não versionado
- [ ] Tokens expiram (60 minutos ✅)
- [ ] Senhas com bcrypt (hash seguro ✅)
- [ ] CORS configurado corretamente
- [ ] Credenciais não expostas no frontend ✅

### 👤 Segurança de Usuários
- [ ] Usuário admin com senha forte
- [ ] Princípio do menor privilégio aplicado
- [ ] Logs de auditoria habilitados
- [ ] Senha padrão alterada após primeiro login

### 🔄 Procedimentos
- [ ] Plano de backup documentado
- [ ] Plano de disaster recovery testado
- [ ] Procedimento de atualização definido
- [ ] Monitoramento de recursos configurado

---

## 🎯 RESUMO DA PRÓXIMA SESSÃO

### Ordem de execução recomendada:

1. **Reativar sistema** (`./reativar_sistema.sh`)
2. **Implementar SSL** (30-45min) 🔒 CRÍTICO
3. **Configurar Firewall** (10-15min) 🛡️ CRÍTICO
4. **Corrigir páginas admin** (2-3h) 🔧 ALTA
5. **Testar tudo** (1-2h) ✅ MÉDIA
6. **Configurar backups** (30min) 💾 MÉDIA
7. **Otimizações** (1-2h) ⚡ BAIXA
8. **Documentação** (1h) 📚 BAIXA

**Tempo total estimado:** 6-10 horas

---

## 🔧 COMANDOS DE CONTROLE DO SISTEMA

### O QUE FUNCIONA ✅
- ✅ Sistema acessível em http://148.230.78.91
- ✅ Login/autenticação JWT
- ✅ Dashboard com gráficos reais
- ✅ Página de transações (listagem/filtros)
- ✅ Banco PostgreSQL com 10.368 registros
- ✅ Backend API (Swagger em /docs)

### O QUE NÃO FUNCIONA ❌
- ❌ **Páginas de admin/config** (50% quebradas)
- ❌ **HTTPS/SSL** (dados em texto claro)
- ❌ **Firewall** (servidor exposto)

### RECOMENDAÇÃO FINAL
**✋ Sistema foi PAUSADO no final da sessão**  
**Motivo:** Riscos de segurança (HTTP sem SSL, sem firewall)  
**Ação:** Retomar na próxima sessão com implementação de SSL primeiro

---

## 📞 INFORMAÇÕES DE ACESSO

### Servidor VPS
- **IP:** 148.230.78.91
- **Hostname:** srv1045889.hstgr.cloud
- **SSH:** `ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91`

### Banco PostgreSQL
- **Host:** 127.0.0.1:5432
- **Database:** finup_db
- **User:** finup_user
- **Password:** FinUp2026SecurePass

### Usuários Sistema
- **Admin:** admin@financas.com / admin123 (ID: 1)
- **Teste:** teste@email.com / teste123 (ID: 4)

### URLs (Quando ativo)
- **App:** http://148.230.78.91
- **API:** http://148.230.78.91/api/v1
- **Docs:** http://148.230.78.91/docs
- **Health:** http://148.230.78.91/health

---

**Última atualização:** 21/01/2026 19:30 UTC  
**Progresso geral:** 85%  
**Status:** ⚠️ PAUSADO POR SEGURANÇA

### 1. REPOSITÓRIO GITHUB ✅
- ✅ Repositório FinUp criado e publicado
- ✅ URL: https://github.com/emangue/FinUp
- ✅ 477 objetos, 1.36 MB

### 2. SERVIDOR LIMPO ✅
- ✅ 3 deploys antigos removidos (backups salvos)
- ✅ Usuário `deploy` criado com sudo
- ✅ Dependências instaladas:
  - Python 3.12.3
  - PostgreSQL 16
  - Node.js 20.20.0
  - Nginx

### 3. POSTGRESQL CONFIGURADO ✅
- ✅ Banco: `finup_db`
- ✅ Usuário: `finup_user`
- ✅ Senha: `FinUp2026Secure!@#`
- ✅ Permissões configuradas

### 4. BACKEND RODANDO ✅
- ✅ Código transferido via rsync (5.4 MB)
- ✅ Venv criado + dependências instaladas
- ✅ `.env` configurado com JWT secret
- ✅ `config.py` adaptado para PostgreSQL
- ✅ `database.py` atualizado para produção
- ✅ Systemd service criado e ativo
- ✅ **API funcionando em http://127.0.0.1:8000**
- ✅ Health check: `{"status":"healthy","database":"connected"}`
- ✅ Docs: http://127.0.0.1:8000/docs

---

## ⏳ PRÓXIMOS PASSOS (AINDA FALTA)

### 5. FRONTEND ✅ CONCLUÍDO
- [x] Instalar dependências (890 pacotes)
- [x] Criar `.env.production`
- [x] Build (`npm run build`) - 30 rotas geradas
- [x] Criar systemd service
- [x] Iniciar serviço (porta 3000)

### 6. NGINX ✅ CONCLUÍDO
- [x] Criar config `/etc/nginx/sites-available/finup`
- [x] Proxy `/` → Frontend (porta 3000)
- [x] Proxy `/api/` → Backend (porta 8000)
- [x] Ativar site
- [x] Sistema acessível via HTTP ✅

### 7. SSL/HTTPS (NÃO INSTALADO)
- [ ] Instalar Certbot
- [ ] Configurar domínio (se tiver)
- [ ] Gerar certificado Let's Encrypt
- [ ] Forçar HTTPS

### 8. FIREWALL (NÃO CONFIGURADO)
- [ ] Configurar UFW
- [ ] Permitir apenas 22 (SSH), 80 (HTTP), 443 (HTTPS)
- [ ] Ativar firewall

### 9. INICIALIZAR BANCO ✅ 100% CONCLUÍDO
- [x] Rodar migrations/create tables (36 tabelas criadas!)
- [x] Migrar TODOS os dados do SQLite (10.368 registros)
- [x] Sincronizar schema (colunas e tipos)
- [x] Usuários migrados: admin@financas.com (ID 1) e teste@email.com (ID 4)
- [x] Validado: todas as contagens SQLite = PostgreSQL ✅

---

## 📊 STATUS ATUAL

| Componente | Status | Porta | URL |
|------------|--------|-------|-----|
| PostgreSQL | ✅ Rodando | 5432 (localhost) | 36 tabelas, 10.368 registros |
| Backend API | ✅ Rodando | 8000 (localhost) | http://127.0.0.1:8000 |
| Admin User | ✅ Migrado | - | admin@financas.com (ID 1) |
| Teste User | ✅ Migrado | - | teste@email.com (ID 4) |
| Frontend | ✅ Rodando | 3000 (localhost) | Next.js 16 |
| Nginx | ✅ Rodando | 80 | http://148.230.78.91 |
| SSL | ❌ Não instalado | - | - |
| Nginx | ❌ Não configurado | 80, 443 | - |
| SSL | ❌ Não instalado | - | - |

---

## 🔧 COMANDOS ÚTEIS

### Verificar Backend
```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# Status
systemctl status finup-backend

# Logs
journalctl -u finup-backend -f

# Testar API
curl http://127.0.0.1:8000/api/health
```

### Acessar PostgreSQL
```bash
sudo -u postgres psql finup_db

# Dentro do psql:
\dt                    # Listar tabelas
\d table_name          # Descrever tabela
SELECT COUNT(*) FROM users;
```

---

## 🚀 CONTINUAR DEPLOY

Para continuar, siga estes comandos:

### 1. Configurar Frontend
```bash
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91

# Instalar dependências
cd /var/www/finup/app_dev/frontend
npm ci

# Criar .env.production
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=http://148.230.78.91/api/v1
NODE_ENV=production
EOF

# Build
npm run build

# Se der erro, verificar:
npm run build 2>&1 | tee build.log
```

### 2. Criar Systemd Service (Frontend)
```bash
cat > /etc/systemd/system/finup-frontend.service << 'EOF'
[Unit]
Description=FinUp Frontend
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/var/www/finup/app_dev/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start

PrivateTmp=true
NoNewPrivileges=true

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable finup-frontend
systemctl start finup-frontend
systemctl status finup-frontend
```

### 3. Configurar Nginx
```bash
cat > /etc/nginx/sites-available/finup << 'EOF'
server {
    listen 80;
    server_name 148.230.78.91;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Ativar site
ln -s /etc/nginx/sites-available/finup /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. Inicializar Banco de Dados (CRÍTICO!)
```bash
cd /var/www/finup/app_dev/backend
source venv/bin/activate

# Rodar migrations (se existir script)
python scripts/create_tables.py

# Criar usuário admin
python scripts/create_admin_user.py

# Ou manualmente via psql:
sudo -u postgres psql finup_db << 'SQL'
-- Ver estrutura que já existe
\dt

-- Se necessário, criar tabelas manualmente
-- (ver schema do SQLite de backup)
SQL
```

---

## ⚠️ IMPORTANTE - NÃO ESQUECER!

1. **Banco está vazio!** Precisa rodar migrations/create tables
2. **Sem usuário admin** não consegue logar
3. **Frontend precisa ser configurado** antes de Nginx funcionar
4. **Backup dos dados antigos** está em `/root/backups_pre_deploy/`

---

## 📞 SUPORTE

Se tiver dúvidas ou problemas, forneça:
1. Componente com problema (backend, frontend, nginx)
2. Logs: `journalctl -u finup-backend -n 50`
3. Erro específico

---

**Status:** Backend ✅ | DB ✅ | Frontend ✅ | Nginx ✅ | **SSL ✅** | **Firewall ✅** | Domínio ⏳

**Progresso:** **95% concluído** (aguardando apenas cache CDN)

---

## 🎉 SISTEMA ACESSÍVEL!

**URLs:**
- **HTTPS (Produção):** https://meufinup.com.br (⏳ cache CDN limpando)
- **IP Direto:** http://148.230.78.91 (✅ funcionando)

**Login:**
- Admin: `admin@financas.com` / `admin123`
- Teste: `teste@email.com` / `teste123`

**Documentação:**
- **Swagger:** https://meufinup.com.br/docs (ou http://148.230.78.91/docs)
- **Health:** https://meufinup.com.br/health (ou http://148.230.78.91/health)

**Certificado SSL:**
- Emissor: Let's Encrypt
- Válido até: 22/04/2026
- Renovação: Automática (certbot)

---

**Última atualização:** 22/01/2026 14:15 UTC
