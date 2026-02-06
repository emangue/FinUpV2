# ✅ Checklist de Deploy - FinUp Mobile V1.0

**Objetivo:** Garantir que todos os passos necessários sejam seguidos antes de fazer deploy em produção.

**Versão:** 1.0  
**Data:** 01/02/2026

---

## 📋 Pré-Deploy

### 1. Código e Git

- [ ] **Todas as mudanças commitadas**
  ```bash
  git status  # Deve estar limpo
  ```

- [ ] **Branch main atualizada**
  ```bash
  git checkout main
  git pull origin main
  ```

- [ ] **Versão atualizada**
  - [ ] `package.json` version incrementada
  - [ ] `VERSION.md` atualizado
  - [ ] `CHANGELOG.md` atualizado

- [ ] **Sem arquivos sensíveis**
  ```bash
  git log --all --full-history -- '**/.env*'  # Deve estar vazio
  ```

### 2. Testes

- [ ] **Testes E2E passando**
  ```bash
  npm run test:e2e
  ```

- [ ] **Validação de acessibilidade**
  ```bash
  node scripts/testing/validate_accessibility.js
  # Máximo 10 issues críticas
  ```

- [ ] **Build sem erros**
  ```bash
  cd app_dev/frontend
  npm run build
  # Deve completar sem erros
  ```

- [ ] **Backend sem erros**
  ```bash
  cd app_dev/backend
  python -c "from app.main import app"
  # Não deve dar erro de import
  ```

### 3. Banco de Dados

- [ ] **Migrations atualizadas**
  ```bash
  cd app_dev/backend
  alembic current  # Verificar versão
  alembic check    # Sem diferenças
  ```

- [ ] **Backup realizado**
  ```bash
  ./scripts/deploy/backup_daily.sh
  # Confirmar backup criado
  ```

- [ ] **Paridade dev-prod validada**
  ```bash
  python scripts/testing/validate_parity.py
  # Deve mostrar 100% paridade
  ```

### 4. Configurações

- [ ] **Variáveis de ambiente configuradas**
  - [ ] `.env` local não commitado
  - [ ] `.env.example` atualizado
  - [ ] Secrets em produção configurados

- [ ] **URLs corretas**
  - [ ] `BACKEND_URL` aponta para produção
  - [ ] `FRONTEND_URL` configurado
  - [ ] CORS origins específicos (não "*")

- [ ] **Secrets rotacionados (se necessário)**
  - [ ] JWT_SECRET_KEY forte (64 chars hex)
  - [ ] DATABASE_PASSWORD forte
  - [ ] API keys atualizadas

---

## 🚀 Deploy Backend

### 5. Preparação do Servidor

- [ ] **SSH funcionando**
  ```bash
  ssh minha-vps-hostinger
  # Ou: ssh root@148.230.78.91
  ```

- [ ] **Diretório do projeto existe**
  ```bash
  cd /var/www/finup
  pwd  # Confirmar path
  ```

- [ ] **Git configurado**
  ```bash
  git remote -v  # origin apontando para GitHub
  ```

### 6. Atualizar Código

- [ ] **Pull do código**
  ```bash
  cd /var/www/finup
  git pull origin main
  ```

- [ ] **Verificar commit**
  ```bash
  git log --oneline -1  # Deve ser o último commit local
  ```

### 7. Dependências e Migrations

- [ ] **Atualizar dependências Python**
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt --upgrade
  ```

- [ ] **Aplicar migrations**
  ```bash
  cd app_dev/backend
  alembic upgrade head
  alembic current  # Confirmar versão
  ```

### 8. Reiniciar Serviços

- [ ] **Reiniciar backend**
  ```bash
  sudo systemctl restart finup-backend
  systemctl status finup-backend  # Verificar ativo
  ```

- [ ] **Verificar logs**
  ```bash
  journalctl -u finup-backend -n 50  # Últimas 50 linhas
  # Não deve ter erros
  ```

- [ ] **Health check**
  ```bash
  curl -s http://localhost:8000/api/health | jq
  # Deve retornar {"status": "healthy"}
  ```

---

## 🎨 Deploy Frontend

### 9. Build e Deploy

- [ ] **Build de produção**
  ```bash
  cd app_dev/frontend
  npm run build
  # Verificar pasta .next/ criada
  ```

- [ ] **Copiar build (se necessário)**
  ```bash
  # Se usar servidor estático separado
  rsync -av .next/ user@servidor:/var/www/finup/frontend/
  ```

- [ ] **Reiniciar frontend**
  ```bash
  sudo systemctl restart finup-frontend
  systemctl status finup-frontend
  ```

### 10. Validação Frontend

- [ ] **Site acessível**
  ```bash
  curl -I https://meufinup.com.br
  # HTTP/1.1 200 OK
  ```

- [ ] **Assets carregando**
  - [ ] Abrir no navegador
  - [ ] Verificar console (F12) - sem erros
  - [ ] Imagens carregando
  - [ ] CSS aplicado

---

## 🔍 Testes Pós-Deploy

### 11. Smoke Tests

- [ ] **Login funciona**
  - Acessar /auth/login
  - Fazer login
  - Verificar redirecionamento

- [ ] **Dashboard carrega**
  - Métricas aparecem
  - Sem erros no console

- [ ] **Budget funciona**
  - Lista de categorias aparece
  - Edição de meta funciona

- [ ] **Transações carregam**
  - Lista aparece
  - Filtros funcionam

- [ ] **Upload funciona**
  - Página carrega
  - Input de arquivo visível

- [ ] **Profile funciona**
  - Dados do usuário aparecem
  - Edição funciona
  - Logout funciona

### 12. Testes de Performance

- [ ] **Lighthouse Audit**
  ```bash
  npm run lighthouse -- --view
  ```
  - [ ] Performance: ≥85
  - [ ] Accessibility: ≥90
  - [ ] Best Practices: ≥90
  - [ ] SEO: ≥80

- [ ] **Tempo de resposta API**
  ```bash
  curl -w "@curl-format.txt" -s https://api.meufinup.com.br/api/health
  # time_total < 1s
  ```

### 13. Testes de Segurança

- [ ] **HTTPS ativo**
  ```bash
  curl -I https://meufinup.com.br | grep -i "HTTP/2 200"
  ```

- [ ] **Headers de segurança**
  - [ ] Strict-Transport-Security presente
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY

- [ ] **CORS específico**
  ```bash
  curl -H "Origin: https://site-malicioso.com" https://api.meufinup.com.br/api/health
  # Não deve ter header Access-Control-Allow-Origin
  ```

- [ ] **Rate limiting ativo**
  ```bash
  # Fazer 10 requests rápidas
  for i in {1..10}; do curl -s https://api.meufinup.com.br/api/login; done
  # Deve retornar 429 após algumas requisições
  ```

---

## 📊 Monitoramento Pós-Deploy

### 14. Configurar Alertas

- [ ] **Logs sendo gerados**
  ```bash
  tail -f /var/log/finup/backend.log
  tail -f /var/log/finup/frontend.log
  ```

- [ ] **Disk space ok**
  ```bash
  df -h  # Uso < 80%
  ```

- [ ] **Memória ok**
  ```bash
  free -h  # Swap usage < 50%
  ```

- [ ] **CPU ok**
  ```bash
  top  # Load average < num_cores
  ```

### 15. Documentação

- [ ] **CHANGELOG atualizado**
  - Descrever mudanças principais
  - Listar bugs corrigidos
  - Mencionar breaking changes

- [ ] **README atualizado**
  - Versão atual documentada
  - Instruções de instalação corretas

- [ ] **Documentação de API**
  - Swagger/OpenAPI atualizado: /docs
  - Novos endpoints documentados

---

## 🎯 Checklist de Rollback

**(Se algo der errado)**

### 16. Plano B - Reverter Deploy

- [ ] **Identificar último commit estável**
  ```bash
  git log --oneline -10
  git tag -l "v*" | tail -5
  ```

- [ ] **Rollback do código**
  ```bash
  git checkout <ultimo_commit_estavel>
  # Ou: git revert <commit_problematico>
  ```

- [ ] **Rollback do banco (se necessário)**
  ```bash
  alembic downgrade -1  # Voltar 1 migration
  # Ou: restaurar backup
  ./scripts/deploy/restore_backup.sh <data>
  ```

- [ ] **Reiniciar serviços**
  ```bash
  sudo systemctl restart finup-backend finup-frontend
  ```

- [ ] **Notificar equipe**
  - Enviar mensagem sobre rollback
  - Documentar problema encontrado

---

## 📝 Comunicação

### 17. Avisos

- [ ] **Notificar usuários (se necessário)**
  - Enviar email sobre novas features
  - Atualizar página de status

- [ ] **Documentar deploy**
  - Registrar data/hora
  - Anotar problemas encontrados
  - Listar lições aprendidas

- [ ] **Atualizar STATUS_EXECUTIVO.md**
  - Marcar sprint como completa
  - Atualizar percentuais de conclusão

---

## ✅ Conclusão do Deploy

### 18. Validação Final

- [ ] **Todos os checklist items completos**
- [ ] **Sistema operacional em produção**
- [ ] **Sem erros críticos nos logs**
- [ ] **Usuários conseguem usar normalmente**
- [ ] **Performance dentro do esperado**
- [ ] **Backup de sucesso realizado**

### 19. Próximos Passos

- [ ] **Monitorar por 24h**
  - Verificar logs a cada 2-4h
  - Responder a feedbacks de usuários

- [ ] **Sprint Review**
  - Revisar o que funcionou bem
  - Identificar melhorias para próximo deploy

- [ ] **Planejar próxima sprint**
  - Priorizar backlog
  - Alocar recursos

---

## 🆘 Contatos de Emergência

**Se algo der muito errado durante o deploy:**

- **DevOps Lead:** [contato]
- **Backend Lead:** [contato]
- **Frontend Lead:** [contato]
- **DBA:** [contato]
- **Suporte Servidor:** suporte@hostinger.com

---

## 📚 Recursos Úteis

**Comandos de Diagnóstico:**

```bash
# Ver status de todos os serviços
systemctl list-units --type=service --state=running | grep finup

# Ver uso de recursos
htop

# Ver conexões ativas
netstat -tulpn | grep -E "8000|3000|5432"

# Testar conectividade
ping -c 3 api.meufinup.com.br

# Ver certificado SSL
openssl s_client -connect meufinup.com.br:443 -servername meufinup.com.br | openssl x509 -noout -dates
```

**Scripts Úteis:**

- `./scripts/deploy/quick_start.sh` - Iniciar servidores local
- `./scripts/deploy/quick_stop.sh` - Parar servidores local
- `./scripts/deploy/backup_daily.sh` - Backup manual
- `./scripts/deploy/validate_server_access.sh` - Validar acesso SSH
- `./scripts/testing/validate_accessibility.js` - Validar WCAG

---

**Última atualização:** 01/02/2026  
**Versão do checklist:** 1.0  
**Autor:** Sprint 4 Team  
**Status:** ✅ Pronto para uso
