# 🎯 INSTRUÇÕES PARA DEPLOY LIMPO

## 📋 Situação Atual
- Servidor com múltiplos deploys parciais
- Processos conflitantes rodando  
- Estrutura de pastas inconsistente
- Necessário começar do zero

## 🚀 Solução: Deploy Limpo Completo

### Passo 1: Copiar arquivos para o servidor

```bash
# No seu computador, copie a pasta deploy_manual para o servidor
scp -r deploy_manual root@148.230.78.91:/tmp/
```

### Passo 2: Executar no servidor

```bash
# Conectar no servidor
ssh root@148.230.78.91

# Ir para a pasta
cd /tmp/deploy_manual

# Executar script principal
sudo ./execute_all.sh
```

### Passo 3: Acompanhar execução

O script vai:
1. **Auditoria**: Mapear tudo que está no servidor
2. **Limpeza**: Remover TUDO relacionado ao sistema 
3. **Deploy**: Criar aplicação limpa do zero

### 📊 Resultado Esperado

- ✅ Backend FastAPI funcionando na porta 8000
- ✅ Aplicação web acessível externamente
- ✅ Logs organizados em /var/log/financas/
- ✅ Comando `financas-status` para monitoramento
- ✅ Arquitetura modular pronta para expansão

### 🌐 URLs após deploy

- **Sistema**: http://148.230.78.91:8000
- **API Docs**: http://148.230.78.91:8000/api/docs
- **Health Check**: http://148.230.78.91:8000/api/health

### 🔧 Comandos úteis no servidor

```bash
# Status completo
financas-status

# Ver logs
tail -f /var/log/financas/backend.log

# Restart se necessário
pkill uvicorn
cd /var/www/financas/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > /var/log/financas/backend.log 2>&1 &
```

## 🎯 Próximos Passos (após deploy limpo)

1. ✅ **Sistema base funcionando** (este deploy)
2. 🔐 Implementar autenticação JWT
3. 🗄️ Configurar banco SQLite
4. 📁 Sistema de upload de arquivos
5. ⚛️ Frontend Next.js
6. 📊 Dashboard e relatórios

## ⚠️ Importante

- Execute como **root** no servidor
- O script vai **deletar tudo** relacionado ao sistema
- Faça backup se tiver dados importantes
- Processo demora ~5-10 minutos

