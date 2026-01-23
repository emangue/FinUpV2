# 🚀 Guia de Deploy via Git Push

## 📋 O que foi implementado

**Sistema de auto-deploy via git push:**
- Você faz `git push vps main` do seu MacBook
- Servidor automaticamente:
  1. Faz backup do banco
  2. Atualiza código (`git checkout`)
  3. Instala dependências Python
  4. Aplica migrations (Alembic)
  5. Reinicia backend (systemctl)
  6. Reinicia frontend (se existir)
  7. Registra tudo em log

## 🔧 Setup Inicial (FAZER UMA VEZ)

### No Servidor (via terminal web da VPS):

1. **Copiar script de setup:**
   ```bash
   cd /tmp
   cat > setup_git_deploy.sh << 'EOF'
   [COPIAR CONTEÚDO DE scripts/deploy/setup_git_deploy.sh AQUI]
   EOF
   ```

2. **Executar setup:**
   ```bash
   chmod +x setup_git_deploy.sh
   bash setup_git_deploy.sh
   ```

   **Resultado esperado:**
   ```
   ✅ SETUP COMPLETO!
   📋 Próximos passos:
   1. No seu MacBook, adicione o remote VPS...
   ```

### No Seu MacBook:

3. **Adicionar remote VPS:**
   ```bash
   cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
   git remote add vps root@64.23.241.43:/var/repo/finup.git
   ```

4. **Verificar remotes:**
   ```bash
   git remote -v
   ```
   
   **Deve mostrar:**
   ```
   origin  https://github.com/emangue/FinUpV2.git (fetch)
   origin  https://github.com/emangue/FinUpV2.git (push)
   vps     root@64.23.241.43:/var/repo/finup.git (fetch)
   vps     root@64.23.241.43:/var/repo/finup.git (push)
   ```

5. **Primeiro push (vai pedir senha):**
   ```bash
   git push vps main
   ```

## ⚡ Uso Diário

**Workflow completo:**

```bash
# 1. Fazer mudanças no código
vim app_dev/backend/app/domains/transactions/service.py

# 2. Testar localmente
./scripts/deploy/quick_start.sh

# 3. Commitar
git add -A
git commit -m "feat: adiciona nova funcionalidade X"

# 4. Push para GitHub (backup)
git push origin main

# 5. Deploy automático na VPS
git push vps main
```

**Resultado esperado:**
```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
...
remote: 🚀 DEPLOY INICIADO: Thu Jan 23 15:30:00 UTC 2026
remote: 📥 1/6: Atualizando código...
remote: 💾 2/6: Fazendo backup...
remote: 📦 3/6: Instalando dependências...
remote: 🗄️  4/6: Aplicando migrations...
remote: 🔄 5/6: Reiniciando backend...
remote: ✅ Backend reiniciado
remote: 🎨 6/6: Reiniciando frontend...
remote: ✅ DEPLOY CONCLUÍDO: Thu Jan 23 15:30:45 UTC 2026
To root@64.23.241.43:/var/repo/finup.git
   abc1234..def5678  main -> main
```

## 📊 Monitoramento

**Ver logs de deploy em tempo real (no servidor):**
```bash
tail -f /var/log/finup-deploy.log
```

**Ver últimos deploys:**
```bash
tail -100 /var/log/finup-deploy.log
```

**Ver status dos serviços:**
```bash
systemctl status finup-backend
systemctl status finup-frontend
```

## 🔥 Rollback (se algo der errado)

**No seu MacBook:**
```bash
# Ver commits recentes
git log --oneline -5

# Voltar para commit anterior
git reset --hard <commit-hash-anterior>

# Forçar push
git push vps main --force
```

**Ou no servidor (via terminal web):**
```bash
cd /var/www/finup
git log --oneline -5
git checkout <commit-hash-anterior>
systemctl restart finup-backend
```

## 🚨 Troubleshooting

**Problema: Push pede senha toda vez**

Solução: Configurar chave SSH no servidor

```bash
# No MacBook
cat ~/.ssh/id_rsa.pub

# No servidor
mkdir -p ~/.ssh
echo "<sua-chave-publica>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**Problema: Backend não reinicia**

```bash
# No servidor
systemctl status finup-backend
journalctl -u finup-backend -n 50
```

**Problema: Migrations falham**

```bash
# No servidor
cd /var/www/finup/app_dev/backend
source ../venv/bin/activate
alembic current
alembic upgrade head
```

## 🎯 Vantagens deste setup

- ✅ **Zero SSH manual** - apenas git push
- ✅ **Deploy em ~30-45 segundos**
- ✅ **Backup automático** antes de cada deploy
- ✅ **Logs completos** de cada deploy
- ✅ **Rollback fácil** via git
- ✅ **Migrations automáticas**
- ✅ **Reinicialização de serviços** automática

## 📚 Recursos Adicionais

**Ver todas as branches no servidor:**
```bash
git ls-remote vps
```

**Push de outra branch:**
```bash
git push vps develop:main
```

**Apenas update sem deploy (se precisar):**
```bash
# No servidor
cd /var/www/finup
git fetch origin
git merge origin/main
# (não reinicia serviços)
```

---

**Versão:** 1.0  
**Data:** 23/01/2026  
**Autor:** Sistema de Deploy Automático
