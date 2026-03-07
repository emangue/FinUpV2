# 🚀 PROCESSO DE DEPLOY - REGRAS OBRIGATÓRIAS

## ⚠️ FLUXO ÚNICO - NUNCA VIOLAR

```
LOCAL → GIT → SERVIDOR
```

**NUNCA editar código diretamente no servidor!**

## 🔄 Comandos Rápidos

### 1. Deploy Simples (após modificar código)
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./scripts/deploy/quick_deploy.sh
```

### 2. Deploy com Validação Completa
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5  
./scripts/deploy/safe_deploy.sh
```

### 3. Deploy de Emergência (hotfix)
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./scripts/deploy/emergency_deploy.sh "descrição do hotfix"
```

## 📋 Checklist Obrigatório

### ✅ ANTES de Fazer Deploy

- [ ] ✅ Código modificado LOCALMENTE
- [ ] ✅ Testado localmente (se possível)
- [ ] ✅ Commit com mensagem clara
- [ ] ✅ Push para GitHub
- [ ] ✅ Verificar que não há mudanças uncommitted

### ✅ DURANTE o Deploy

- [ ] ✅ SSH no servidor
- [ ] ✅ `cd /var/www/finup`
- [ ] ✅ `git pull origin main`
- [ ] ✅ Reiniciar serviços necessários
- [ ] ✅ Verificar logs de erro

### ✅ APÓS Deploy

- [ ] ✅ Testar endpoints críticos
- [ ] ✅ Verificar logs em tempo real
- [ ] ✅ Confirmar que aplicação está funcionando

## 🚫 PROIBIÇÕES ABSOLUTAS

### ❌ NUNCA fazer no servidor:

```bash
# ❌ NÃO FAZER ISSO!
ssh servidor
vim /var/www/finup/app_dev/backend/app/domains/auth/router.py
nano /var/www/finup/app_dev/backend/app/main.py
echo "fix" > /var/www/finup/arquivo.py
```

### ❌ NUNCA instalar dependências só no servidor:

```bash
# ❌ ERRADO - requirements.txt fica desatualizado
ssh servidor  
pip install nova_biblioteca

# ✅ CORRETO
# Local: adicionar ao requirements.txt
# git commit + push
# Servidor: pip install -r requirements.txt
```

## 📋 Comandos do Servidor (após git pull)

### Reiniciar Backend
```bash
systemctl restart finup-backend
systemctl status finup-backend --no-pager
```

### Reiniciar Frontend  
```bash
systemctl restart finup-frontend
systemctl status finup-frontend --no-pager
```

### Verificar Logs
```bash
journalctl -u finup-backend -f
journalctl -u finup-frontend -f
```

### Aplicar Migrations (se necessário)
```bash
cd /var/www/finup/app_dev/backend
source venv/bin/activate
alembic upgrade head
```

## 🔍 Troubleshooting

### Se Deploy Falhou
1. **Verificar logs:** `journalctl -u finup-backend -n 50`
2. **Sintaxe Python:** `python3 -m py_compile arquivo.py`
3. **Dependências:** `pip install -r requirements.txt`
4. **Rollback:** `git checkout HEAD~1 -- arquivo.py`

### Se Servidor Parou
1. **Verificar status:** `systemctl status finup-backend`
2. **Restart forçado:** `systemctl restart finup-backend`
3. **Logs detalhados:** `journalctl -u finup-backend -n 100`

## 🎯 Exemplos de Uso

### Deploy de correção simples:
```bash
# 1. LOCAL - Corrigir código
vim app_dev/backend/app/domains/auth/router.py

# 2. GIT - Commit e push  
git add .
git commit -m "fix: corrige bug X"
git push origin main

# 3. SERVIDOR - Deploy automático
./scripts/deploy/quick_deploy.sh
```

### Deploy com mudança no banco:
```bash
# 1. LOCAL - Modificar modelo + criar migration
alembic revision --autogenerate -m "adiciona campo Y"

# 2. GIT - Commit tudo
git add .
git commit -m "feat: adiciona campo Y ao modelo Z"  
git push origin main

# 3. SERVIDOR - Deploy com migration
./scripts/deploy/safe_deploy.sh --with-migrations
```

## 🚨 Situações de Emergência

### Se alguém editou código diretamente no servidor:
```bash
# 1. Verificar mudanças não-commitadas
ssh servidor "cd /var/www/finup && git status"

# 2. Se há mudanças importantes, salvar:
ssh servidor "cd /var/www/finup && git stash push -m 'mudanças servidor'"

# 3. Trazer para local:
git pull origin main

# 4. Aplicar stash local e commitar:
git stash pop  
git add .
git commit -m "feat: mudanças vindas do servidor"
git push origin main
```

## ✅ Validação Automática

Os scripts de deploy automaticamente verificam:
- ✅ Git status limpo (sem uncommitted changes)
- ✅ Push realizado (local sincronizado com GitHub) 
- ✅ Servidor consegue fazer pull
- ✅ Backend reinicia sem erros
- ✅ Endpoints críticos funcionando

**Seguindo este processo, NUNCA teremos problemas de sincronização!** 🎯