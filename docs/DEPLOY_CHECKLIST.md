# ✅ Checklist de Deploy

Use este checklist para garantir um deploy seguro e sem problemas.

---

## Pré-Deploy

### 1️⃣ Ambiente de Desenvolvimento
- [ ] Todas as mudanças estão em `app_dev/`
- [ ] Código testado localmente
- [ ] Sem erros no console do navegador
- [ ] Sem erros no terminal (backend)
- [ ] Banco de dados local funcionando

### 2️⃣ Validações Técnicas
```bash
./deploy.sh validate
```
- [ ] ✅ Estrutura de diretórios OK
- [ ] ✅ Syntax Python OK
- [ ] ✅ Imports OK
- [ ] ✅ Modelos do banco OK
- [ ] ✅ Rotas OK
- [ ] ✅ Segurança OK
- [ ] ✅ Frontend build OK
- [ ] ✅ Dependências OK

### 3️⃣ Segurança
- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` diferente de dev
- [ ] Sem senhas hardcoded
- [ ] Sem tokens expostos no código
- [ ] `.env` não commitado

### 4️⃣ Documentação
- [ ] Mudanças documentadas em `changes/`
- [ ] Versão atualizada (se aplicável)
- [ ] README atualizado (se necessário)
- [ ] CHANGELOG atualizado (para releases)

---

## Durante Deploy

### 5️⃣ Validação Final
```bash
./deploy.sh deploy
```
- [ ] Revisei todas as mudanças mostradas
- [ ] Número de arquivos modificados está correto
- [ ] Número de arquivos novos está correto
- [ ] Número de arquivos removidos está correto

### 6️⃣ Confirmação
- [ ] Li todas as diferenças cuidadosamente
- [ ] Confirmo que mudanças estão corretas
- [ ] Backup será criado automaticamente
- [ ] Digitei `sim` para confirmar

### 7️⃣ Backup Verificado
- [ ] Backup criado com sucesso
- [ ] Nome do backup anotado para rollback
- [ ] Tamanho do backup parece correto
- [ ] Banco de dados também foi backupado

---

## Pós-Deploy

### 8️⃣ Verificação Imediata
- [ ] Deploy concluiu sem erros
- [ ] Aplicação reiniciou (se aplicável)
- [ ] Porta correta em uso
- [ ] Sem mensagens de erro no terminal

### 9️⃣ Teste Funcional
- [ ] Acesso à aplicação: http://localhost:5001
- [ ] Login funciona
- [ ] Dashboard carrega corretamente
- [ ] Transações aparecem
- [ ] Upload de arquivo funciona
- [ ] Filtros funcionam
- [ ] Modal de edição abre

### 🔟 Verificação de Logs
```bash
tail -f logs/app.log
```
- [ ] Sem erros 500
- [ ] Sem exceções Python
- [ ] Sem warnings críticos
- [ ] Requests sendo processados corretamente

### 1️⃣1️⃣ Teste de Performance
- [ ] Tempo de resposta < 2s
- [ ] Dashboard carrega em < 3s
- [ ] Upload processa em tempo razoável
- [ ] Memória dentro do esperado

---

## Em Caso de Problema

### ⚠️ Deploy Falhou

#### Sintomas:
- Aplicação não inicia
- Erros 500
- Página em branco
- Funcionalidade quebrada

#### Ação Imediata:
```bash
# 1. Ver backups disponíveis
./deploy.sh rollback-list

# 2. Restaurar último backup
./deploy.sh rollback
```

#### Checklist de Rollback:
- [ ] Backup listado corretamente
- [ ] Confirmei rollback
- [ ] Aplicação restaurada
- [ ] Testei funcionalidade básica
- [ ] Aplicação voltou ao normal

---

## Deploy para Produção (VM)

Se você também precisa fazer deploy na VM:

### 1️⃣2️⃣ Pré-Requisitos VM
- [ ] Acesso SSH configurado
- [ ] Chaves SSH funcionando
- [ ] VM respondendo: `ping 148.230.78.91`
- [ ] Espaço em disco suficiente
- [ ] Backup da VM feito

### 1️⃣3️⃣ Deploy na VM
```bash
# Via SCP (recomendado)
scp -r app/ root@148.230.78.91:/opt/financial-app/

# Ou via script de deploy
python deployment_scripts/deploy.py --target production \
  --vm-user root --vm-host 148.230.78.91
```

### 1️⃣4️⃣ Verificação VM
```bash
# Conectar na VM
ssh root@148.230.78.91

# Verificar serviço
systemctl status financial-app

# Ver logs
tail -f /opt/financial-app/logs/app.log

# Reiniciar se necessário
systemctl restart financial-app
```

### 1️⃣5️⃣ Teste em Produção
- [ ] https://finup.emangue.com.br carrega
- [ ] SSL válido (cadeado verde)
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Upload funciona
- [ ] Performance OK

---

## Checklist Final

### ✅ Deploy Bem-Sucedido
- [ ] Deploy local completado
- [ ] Testes locais passaram
- [ ] Deploy VM completado (se aplicável)
- [ ] Testes em produção passaram
- [ ] Backups criados e verificados
- [ ] Documentação atualizada
- [ ] Equipe notificada (se aplicável)

### 📝 Anotações Pós-Deploy
```
Data: ____/____/______
Hora: ____:____
Versão: _______________
Backup: _______________
Mudanças principais:
- _______________________
- _______________________
- _______________________

Problemas encontrados:
- _______________________
- _______________________

Tempo total: _____ minutos
```

---

## Tempo Estimado

| Etapa | Tempo Estimado |
|-------|----------------|
| Pré-Deploy | 10-15 min |
| Validações | 2-3 min |
| Deploy Local | 5-10 min |
| Testes | 5-10 min |
| Deploy VM | 10-15 min |
| **TOTAL** | **30-50 min** |

---

## Frequência Recomendada

- **Deploy Local:** A cada feature completa
- **Deploy Staging:** Diariamente (se disponível)
- **Deploy Produção:** Semanal ou quinzenal
- **Backups:** Automático a cada deploy + diário

---

## Comandos de Emergência

```bash
# Parar aplicação
pkill -f "python.*run.py"

# Rollback rápido
./deploy.sh rollback

# Ver último backup
ls -lht backups_local/ | head -3

# Verificar processos
ps aux | grep python

# Liberar porta (se travada)
lsof -ti:5001 | xargs kill -9
```

---

**Lembre-se:**
- 🚫 NUNCA edite `app/` diretamente
- ✅ SEMPRE desenvolva em `app_dev/`
- ✅ SEMPRE valide antes de deploy
- ✅ SEMPRE revise mudanças antes de confirmar
- ✅ Backups são criados automaticamente
- ⚡ Rollback é rápido se necessário
