# 🚀 PROCESSO OBRIGATÓRIO DE DEPLOY

## ⚠️ LEIA ISTO ANTES DE QUALQUER DEPLOY

**Domínio de Produção:** https://finup.emangue.com.br  
**VM:** 148.230.78.91 (srv1045889.hstgr.cloud)  
**SSH:** `ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91`

---

## 📋 CHECKLIST OBRIGATÓRIO (Siga SEMPRE nesta ordem!)

### FASE 1: VALIDAÇÃO LOCAL (ANTES de fazer qualquer coisa)

- [ ] **1.1** Ler este arquivo (`DEPLOY_PROCESS.md`)
- [ ] **1.2** Verificar branch atual: `git branch --show-current` (deve ser `main`)
- [ ] **1.3** Garantir que está na raiz do projeto
- [ ] **1.4** Rodar validação local:
  ```bash
  ./scripts/validate_pre_deploy.sh
  ```
- [ ] **1.5** Se houver ERROS → **PARAR AQUI** e corrigir

---

### FASE 2: COMPARAÇÃO LOCAL vs VM

- [ ] **2.1** Executar script de comparação:
  ```bash
  ./scripts/compare_local_vs_vm.sh
  ```
- [ ] **2.2** Analisar diferenças encontradas:
  - Arquivos modificados
  - Arquivos novos
  - Arquivos deletados
  - Versão atual vs nova
  
- [ ] **2.3** **PARAR E PERGUNTAR AO USUÁRIO:**
  ```
  📊 Diferenças encontradas:
  - X arquivos modificados
  - Y arquivos novos
  - Z arquivos deletados
  
  ⚠️ AUTORIZAÇÃO NECESSÁRIA:
  Posso continuar com o deploy? (S/N)
  ```

- [ ] **2.4** Se usuário disser **NÃO** → **ABORTAR deploy**
- [ ] **2.5** Se usuário disser **SIM** → Continuar

---

### FASE 3: GIT (SEMPRE antes do deploy)

- [ ] **3.1** Verificar status do Git:
  ```bash
  git status
  ```

- [ ] **3.2** Se houver mudanças não commitadas:
  ```bash
  git add -A
  git commit -m "mensagem descritiva"
  ```

- [ ] **3.3** Verificar se está sincronizado com remote:
  ```bash
  git fetch origin
  git status
  ```

- [ ] **3.4** Se houver commits locais não enviados:
  ```bash
  git push origin main
  ```

- [ ] **3.5** **CONFIRMAR** que push foi bem-sucedido:
  ```bash
  git log origin/main --oneline -3
  ```

- [ ] **3.6** ✅ Git sincronizado → Pode continuar

---

### FASE 4: BACKUP DA VM

- [ ] **4.1** Criar backup do banco de dados atual da VM:
  ```bash
  ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
    "cd /opt/financial-app && \
     mkdir -p backups && \
     cp instance/financas.db backups/financas_backup_\$(date +%Y%m%d_%H%M%S).db"
  ```

- [ ] **4.2** Verificar que backup foi criado:
  ```bash
  ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
    "ls -lh /opt/financial-app/backups/ | tail -3"
  ```

---

### FASE 5: DEPLOY

- [ ] **5.1** Executar deploy:
  ```bash
  ./deployment_scripts/deploy_hostinger.sh
  ```

- [ ] **5.2** Aguardar conclusão (não interromper)

- [ ] **5.3** Verificar que não houve erros no rsync

---

### FASE 6: VALIDAÇÃO PÓS-DEPLOY

- [ ] **6.1** Reiniciar serviço na VM:
  ```bash
  ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
    "systemctl restart financial-app.service"
  ```

- [ ] **6.2** Aguardar 5 segundos:
  ```bash
  sleep 5
  ```

- [ ] **6.3** Verificar status do serviço:
  ```bash
  ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
    "systemctl status financial-app.service --no-pager"
  ```

- [ ] **6.4** Se status NÃO for `active (running)` → **ROLLBACK IMEDIATO**

- [ ] **6.5** Testar aplicação via domínio:
  ```bash
  curl -s https://finup.emangue.com.br/ | head -20
  ```

- [ ] **6.6** Verificar que retorna HTML válido (não erro 502/503/404)

- [ ] **6.7** Testar login:
  ```bash
  curl -s https://finup.emangue.com.br/auth/login | grep -i "login"
  ```

- [ ] **6.8** Verificar logs de erro:
  ```bash
  ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
    "tail -20 /opt/financial-app/logs/error.log"
  ```

- [ ] **6.9** Se houver ERROS → **ROLLBACK IMEDIATO**

---

### FASE 7: CONFIRMAÇÃO FINAL

- [ ] **7.1** Acessar https://finup.emangue.com.br no navegador
- [ ] **7.2** Fazer login com admin@email.com
- [ ] **7.3** Navegar pelas páginas principais
- [ ] **7.4** **PERGUNTAR AO USUÁRIO:**
  ```
  ✅ Deploy concluído!
  
  Por favor, acesse: https://finup.emangue.com.br
  E confirme que tudo está funcionando.
  
  Está tudo OK? (S/N)
  ```

- [ ] **7.5** Se usuário confirmar → ✅ **DEPLOY BEM-SUCEDIDO**
- [ ] **7.6** Se usuário reportar problema → **ROLLBACK**

---

## 🔴 ROLLBACK (se algo der errado)

```bash
# 1. Restaurar último backup do banco
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
  "cd /opt/financial-app && \
   LAST_BACKUP=\$(ls -t backups/financas_backup_*.db | head -1) && \
   cp \$LAST_BACKUP instance/financas.db"

# 2. Voltar para versão anterior do código (Git)
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
  "cd /opt/financial-app && \
   git fetch origin && \
   git reset --hard HEAD~1"

# 3. Reiniciar serviço
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
  "systemctl restart financial-app.service"

# 4. Verificar status
ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 \
  "systemctl status financial-app.service --no-pager"
```

---

## 🚫 NUNCA FAÇA

- ❌ Deploy sem commitar no Git antes
- ❌ Deploy sem comparar local vs VM
- ❌ Deploy sem pedir autorização do usuário
- ❌ Deploy sem fazer backup
- ❌ Deploy sem validar depois
- ❌ Usar IP direto (148.230.78.91) - sempre usar https://finup.emangue.com.br
- ❌ Modificar arquivos diretamente na VM via SSH
- ❌ Deletar backups sem confirmar
- ❌ Ignorar erros de validação

---

## ✅ SEMPRE FAÇA

- ✅ Leia este arquivo antes de CADA deploy
- ✅ Siga o checklist na ordem
- ✅ Peça autorização em TODAS as fases críticas
- ✅ Use o domínio https://finup.emangue.com.br
- ✅ Faça backup antes de deploy
- ✅ Valide DEPOIS do deploy
- ✅ Documente problemas encontrados
- ✅ Teste no ambiente local primeiro

---

## 📞 INFORMAÇÕES DE EMERGÊNCIA

**Domínio:** https://finup.emangue.com.br  
**IP VM:** 148.230.78.91  
**SSH Key:** ~/.ssh/id_rsa_hostinger  
**Usuário VM:** root  
**Diretório App:** /opt/financial-app  
**Serviço:** financial-app.service  
**Logs:** /opt/financial-app/logs/  
**Banco:** /opt/financial-app/instance/financas.db  

**Admin Login:**  
- Email: admin@email.com  
- Senha: admin123  

---

## 🔄 VERSIONAMENTO

Este documento deve ser atualizado sempre que:
- Processo de deploy mudar
- Novos passos forem adicionados
- Erros recorrentes forem identificados
- Melhorias forem sugeridas

**Última atualização:** 02/01/2026  
**Versão:** 1.0.0
