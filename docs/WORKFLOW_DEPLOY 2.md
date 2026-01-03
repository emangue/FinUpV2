# Workflow de Desenvolvimento e Deploy - FinUp

## 🔄 Fluxo de Trabalho

### Desenvolvimento (app_dev)

**Sempre trabalhe em `app_dev/`:**
- ✅ `app_dev/backend/` - Backend Flask API
- ✅ `app_dev/frontend/` - Frontend React + Vite
- ✅ `run_dev_api.py` - Servidor de desenvolvimento

**Portas de desenvolvimento:**
- Backend: `http://localhost:5002`
- Frontend: `http://localhost:5174`

### Deploy para Produção (app)

Quando estiver pronto para fazer deploy, execute:

```bash
python scripts/deploy_dev_to_prod.py
```

## 🔍 Validações Automáticas

O script de deploy executa as seguintes validações:

### 1. Verificações de Código
- ✅ Syntax check em todos os arquivos Python
- ✅ Verificação de imports quebrados
- ✅ Validação de modelos do banco de dados
- ✅ Verificação de rotas duplicadas

### 2. Verificações de Segurança
- ✅ Variáveis de ambiente configuradas
- ✅ Secret keys não expostas
- ✅ Debug mode desabilitado em prod
- ✅ CORS configurado corretamente

### 3. Verificações de Frontend
- ✅ Build do React sem erros
- ✅ Dependências instaladas
- ✅ Assets otimizados

### 4. Verificações de Banco de Dados
- ✅ Migrations aplicadas
- ✅ Schema consistente
- ✅ Dados críticos preservados

## 📋 Processo de Deploy

### Passo 1: Validação Automática
```bash
python scripts/deploy_dev_to_prod.py --validate-only
```

### Passo 2: Revisão Manual
O script mostra:
- ✅ Todas as validações executadas
- 📊 Relatório de diferenças entre dev e prod
- ⚠️ Avisos e atenções necessárias

### Passo 3: Confirmação
```
❓ Deseja prosseguir com o deploy? (sim/não)
```

### Passo 4: Backup Automático
Se confirmado, o script:
1. Cria backup completo de `app/` em `backups_local/`
2. Timestamp: `app_backup_YYYYMMDD_HHMMSS.tar.gz`
3. Backup do banco de dados

### Passo 5: Deploy
1. Sobrescreve `app/` com conteúdo de `app_dev/`
2. Atualiza dependências se necessário
3. Reinicia serviços

### Passo 6: Deploy na VM (Opcional)
```bash
python scripts/deploy_dev_to_prod.py --deploy-vm
```

## 🚨 Rollback

Se algo der errado:

```bash
python scripts/rollback_deployment.py
```

Restaura o último backup automaticamente.

## 📁 Estrutura de Arquivos

```
ProjetoFinancasV3/
├── app/                    # ❌ NÃO EDITAR - Produção
├── app_dev/                # ✅ SEMPRE TRABALHAR AQUI
│   ├── backend/
│   └── frontend/
├── backups_local/          # Backups automáticos
│   └── app_backup_*.tar.gz
├── scripts/
│   ├── deploy_dev_to_prod.py
│   ├── rollback_deployment.py
│   └── validate_deployment.py
└── docs/
    └── WORKFLOW_DEPLOY.md  # Este arquivo
```

## ⚙️ Configuração Inicial

1. **Primeira vez:**
```bash
cd scripts
python deploy_dev_to_prod.py --setup
```

2. **Configurar VM (se aplicável):**
```bash
python deploy_dev_to_prod.py --configure-vm
```

## 📝 Boas Práticas

### Durante Desenvolvimento
- ✅ Sempre trabalhe em `app_dev/`
- ✅ Teste localmente antes de fazer deploy
- ✅ Documente mudanças em `changes/`
- ✅ Use versionamento (git) para `app_dev/`

### Antes do Deploy
- ✅ Execute validações completas
- ✅ Revise todas as mudanças
- ✅ Confirme que testes passam
- ✅ Verifique se não há secrets expostos

### Após Deploy
- ✅ Verifique logs de erro
- ✅ Teste funcionalidades críticas
- ✅ Monitore performance
- ✅ Mantenha backup acessível por 30 dias

## 🔧 Comandos Úteis

### Usando script auxiliar (RECOMENDADO):

```bash
# Validar apenas (não faz deploy)
./deploy.sh validate

# Deploy completo (interativo)
./deploy.sh deploy

# Listar backups disponíveis
./deploy.sh rollback-list

# Rollback para último backup
./deploy.sh rollback

# Rollback para backup específico
./deploy.sh rollback app_backup_20251228_143025.tar.gz
```

### Usando Python diretamente:

```bash
# Validar sem fazer deploy
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/deploy_dev_to_prod.py --validate-only

# Deploy completo
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/deploy_dev_to_prod.py

# Deploy com VM
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/deploy_dev_to_prod.py --deploy-vm

# Listar backups
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/rollback_deployment.py --list

# Rollback
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/rollback_deployment.py
```

# Deploy apenas backend
python scripts/deploy_dev_to_prod.py --backend-only

# Deploy apenas frontend
python scripts/deploy_dev_to_prod.py --frontend-only

# Deploy completo + VM
python scripts/deploy_dev_to_prod.py --deploy-vm

# Rollback para backup anterior
python scripts/rollback_deployment.py

# Listar backups disponíveis
python scripts/rollback_deployment.py --list

# Restaurar backup específico
python scripts/rollback_deployment.py --restore app_backup_20260102.tar.gz
```

## 🎯 Exemplo de Deploy Completo

```bash
# 1. Validar
$ python scripts/deploy_dev_to_prod.py --validate-only
✅ 25 validações executadas
✅ 0 erros encontrados
⚠️  2 avisos (não críticos)

# 2. Deploy
$ python scripts/deploy_dev_to_prod.py
📋 Executando validações...
✅ Código validado
✅ Segurança verificada
✅ Frontend buildado
✅ Banco de dados consistente

📊 Diferenças encontradas:
  - 5 arquivos modificados
  - 2 arquivos novos
  - 0 arquivos removidos

❓ Deseja prosseguir com o deploy? (sim/não): sim

💾 Criando backup...
✅ Backup criado: backups_local/app_backup_20260102_143022.tar.gz

🚀 Fazendo deploy...
✅ Arquivos copiados
✅ Dependências atualizadas
✅ Serviços reiniciados

✅ Deploy concluído com sucesso!
🌐 Aplicação disponível em: http://localhost:5001
```

## 📞 Suporte

Em caso de problemas:
1. Verifique logs em `logs/deploy.log`
2. Execute rollback se necessário
3. Consulte `TROUBLESHOOTING.md`
