# 🚀 Quick Start - Deployment System

Sistema completo de deployment com testes, backups automatizados e detecção de mudanças.

## 📦 O que foi criado

### 1. **Scripts de Análise e Testes**
- `scripts/database_health_check.py` - Analisa qualidade dos dados
- `scripts/deployment_diff.py` - Detecta mudanças vs servidor
- `tests/deployment_health_check.py` - Suite de testes pré-deploy
- `scripts/backup_database.py` - Sistema de backup automatizado

### 2. **Script Master de Deploy**
- `scripts/deploy.py` - Orquestra todo o processo de deployment

### 3. **Documentação**
- `DEPLOYMENT.md` - Guia completo passo-a-passo
- `VM_INFO_CHECKLIST.md` - Checklist de informações da VM
- `.env.production.template` - Template de configuração

## ⚡ Uso Rápido

### Passo 1: Coletar informações da VM

```bash
# Na sua VM, execute:
bash VM_INFO_CHECKLIST.md  # (copie o script de coleta e execute)

# Preencha VM_INFO_CHECKLIST.md com os dados coletados
```

### Passo 2: Rodar verificações locais

```bash
# Ativar venv
source venv/bin/activate

# 1. Verificar saúde do banco de dados
python scripts/database_health_check.py

# 2. Rodar testes de deployment
python tests/deployment_health_check.py

# 3. Gerar relatório de mudanças
python scripts/deployment_diff.py --save-manifest

# 4. Criar backup local
python scripts/backup_database.py backup --tag pre-deploy
```

### Passo 3: Deploy Completo (Apenas Checks)

```bash
# Testar sem fazer deploy real
python scripts/deploy.py --target production --check-only \
  --vm-user SEU_USUARIO \
  --vm-host IP_DA_VM
```

### Passo 4: Deploy Real

```bash
# Deploy completo para produção
python scripts/deploy.py --target production \
  --vm-user SEU_USUARIO \
  --vm-host IP_DA_VM \
  --vm-path /opt/financial-app
```

## 📊 Scripts Individuais

### Database Health Check

```bash
# Console output
python scripts/database_health_check.py

# Salvar em arquivo
python scripts/database_health_check.py --output file

# Custom database
python scripts/database_health_check.py --db path/to/financas.db
```

**Exit codes:**
- `0` - Database healthy (score >= 70)
- `1` - Database has warnings (score 50-69)
- `2` - Database has critical issues (score < 50)

### Deployment Diff

```bash
# Gerar diff report
python scripts/deployment_diff.py

# Salvar manifest local
python scripts/deployment_diff.py --save-manifest

# Comparar com manifest específico
python scripts/deployment_diff.py --server-manifest server_manifest.json

# Output para arquivo
python scripts/deployment_diff.py --output deployment_diff_20260102.md
```

### Deployment Tests

```bash
# Rodar todos os testes
python tests/deployment_health_check.py

# Com banco customizado
python tests/deployment_health_check.py --db path/to/financas.db
```

**Exit codes:**
- `0` - All tests passed
- `1` - Some warnings (can deploy with caution)
- `2` - Critical failures (deployment blocked)

### Backup System

```bash
# Criar backup
python scripts/backup_database.py backup

# Criar backup com tag
python scripts/backup_database.py backup --tag manual-important

# Listar backups
python scripts/backup_database.py list

# Limpar backups antigos (>30 dias)
python scripts/backup_database.py cleanup

# Restaurar backup
python scripts/backup_database.py restore backups/financas.db.backup_20260102_120000.gz

# Configurar cron (instrução)
python scripts/backup_database.py setup-cron

# Backup automático (para cron)
python scripts/backup_database.py auto
```

**Configurar backup automático:**

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 2 AM):
0 2 * * * cd /path/to/project && /path/to/venv/bin/python scripts/backup_database.py auto
```

## 🎯 Workflow Completo de Deployment

```bash
#!/bin/bash
# Script completo de deployment

# 1. Verificações locais
echo "🔍 Step 1: Local checks"
python scripts/database_health_check.py || exit 1
python tests/deployment_health_check.py || exit 1

# 2. Gerar diff
echo "📊 Step 2: Generate diff report"
python scripts/deployment_diff.py --save-manifest

# 3. Backup local
echo "💾 Step 3: Local backup"
python scripts/backup_database.py backup --tag pre-deploy-$(date +%Y%m%d)

# 4. Deploy (apenas checks primeiro)
echo "🔍 Step 4: Deployment checks"
python scripts/deploy.py --target production --check-only \
  --vm-user $VM_USER \
  --vm-host $VM_HOST

# 5. Confirmar e deployar
read -p "Continue with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" = "yes" ]; then
  echo "🚀 Step 5: Deploying..."
  python scripts/deploy.py --target production \
    --vm-user $VM_USER \
    --vm-host $VM_HOST
fi

echo "✅ Deployment complete!"
```

## 📋 Checklist Pré-Deploy

- [ ] Banco de dados analisado (`database_health_check.py`)
- [ ] Health score >= 70
- [ ] Todos os testes passando (`deployment_health_check.py`)
- [ ] Diff report gerado e revisado
- [ ] Backup local criado
- [ ] Informações da VM coletadas
- [ ] `.env.production` configurado na VM
- [ ] SSH funcional para a VM
- [ ] Backup remoto configurado (opcional mas recomendado)

## 🔒 Segurança

### Arquivos que NUNCA devem ir pro git:

```
.env.production
financas.db
*.db
backups/
flask_session/
logs/
server_manifest.json
local_manifest.json
```

Já estão em `.gitignore` ✅

### Gerar SECRET_KEY segura:

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### Permissões corretas na VM:

```bash
# Após deployment
chmod 600 .env.production
chmod 664 instance/financas.db
chmod 775 backups/ logs/ uploads_temp/
```

## 🐛 Troubleshooting

### "No module named 'app'"

```bash
# Certifique-se de estar no diretório raiz do projeto
cd /path/to/ProjetoFinancasV3
source venv/bin/activate
```

### "Database not found"

```bash
# Verifique o caminho
ls -la financas.db

# Se não existir, inicialize
python -c "from app.models import init_db; init_db()"
```

### "Permission denied" ao acessar VM

```bash
# Verifique conexão SSH
ssh -v user@vm-ip

# Configure chave SSH
ssh-copy-id user@vm-ip
```

### Scripts não executam

```bash
# Dar permissão de execução
chmod +x scripts/*.py tests/*.py
```

## 📞 Próximos Passos

1. **Testar localmente:**
   ```bash
   python scripts/database_health_check.py
   python tests/deployment_health_check.py
   ```

2. **Preencher VM_INFO_CHECKLIST.md**

3. **Configurar VM (seguir DEPLOYMENT.md completo)**

4. **Fazer primeiro deployment:**
   ```bash
   python scripts/deploy.py --target production --check-only \
     --vm-user SEU_USUARIO --vm-host IP_VM
   ```

5. **Configurar backup automático na VM**

## 📚 Documentação Completa

Ver `DEPLOYMENT.md` para guia detalhado passo-a-passo incluindo:
- Setup completo da VM
- Configuração Nginx + Gunicorn
- SSL com Let's Encrypt
- systemd service
- Firewall e segurança
- Troubleshooting completo

---

**Versão:** 3.0.1  
**Data:** 02/01/2026  
**Status:** ✅ Pronto para deployment
