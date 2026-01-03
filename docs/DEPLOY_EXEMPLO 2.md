# 📸 Deploy - Exemplo Visual Completo

## Cenário: Deploy de Nova Funcionalidade

Você desenvolveu uma nova funcionalidade no dashboard e está pronto para fazer deploy.

---

## Etapa 1: Validação

```bash
$ ./deploy.sh validate
```

**Output:**
```
🔍 Executando validações...

🔍 Executando validações...
✅ Estrutura de diretórios
✅ Syntax Python
✅ Imports
✅ Modelos do banco
✅ Rotas
✅ Segurança
✅ Frontend build
✅ Dependências

📊 Resumo das Validações
8/8 validações passaram

Avisos (1):
  ⚠️  DEBUG=True encontrado - certifique-se de desabilitar em produção

✅ Apenas validação solicitada. Deploy não executado.
```

**Análise:**
- ✅ Todas as 8 validações passaram
- ⚠️ 1 aviso sobre DEBUG mode (aceitável em dev)
- ✅ Pronto para deploy

---

## Etapa 2: Deploy Interativo

```bash
$ ./deploy.sh deploy
```

**Output:**
```
🚀 Iniciando deploy...

🔍 Executando validações...
✅ Estrutura de diretórios
✅ Syntax Python
✅ Imports
✅ Modelos do banco
✅ Rotas
✅ Segurança
✅ Frontend build
✅ Dependências

📊 Resumo das Validações
8/8 validações passaram

Avisos (1):
  ⚠️  DEBUG=True encontrado - certifique-se de desabilitar em produção

🔎 Comparando app_dev com app...

Diferenças encontradas:
  📝 156 arquivos existentes
  ✨ 12 arquivos novos
  🗑️  3 arquivos removidos

Novos arquivos (mostrando primeiros 5):
  + backend/api/blueprints/dashboard_dev.py
  + frontend/src/components/app-sidebar.tsx
  + frontend/src/components/section-cards.tsx
  + frontend/src/components/chart-area-interactive.tsx
  + frontend/src/components/data-table.tsx
  ... e mais 7 arquivos

❓ Deseja prosseguir com o deploy? (sim/não):
```

**Você digita:** `sim`

---

## Etapa 3: Backup Automático

**Output continua:**
```
💾 Criando backup de app/ ...
ℹ️  Backup do banco: financas_backup_20251228_143025.db
✅ Backup criado: app_backup_20251228_143025.tar.gz
ℹ️  Backup salvo em: /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/backups_local/app_backup_20251228_143025.tar.gz
```

**O que aconteceu:**
1. Criou arquivo compactado de todo `app/`
2. Backup do banco de dados também
3. Arquivos salvos em `backups_local/`

---

## Etapa 4: Deploy

**Output continua:**
```
🚀 Executando deploy...
ℹ️  app/ removido
✅ Arquivos copiados
✅ Deploy concluído!

✅ Deploy concluído com sucesso!
ℹ️  Aplicação disponível em: http://localhost:5001
```

**O que aconteceu:**
1. `app/` antigo foi removido
2. `app_dev/` foi copiado para `app/`
3. Aplicação pronta para uso

---

## Etapa 5: Verificação

```bash
# Acessar aplicação
$ open http://localhost:5001

# Verificar logs
$ tail -f logs/app.log
```

**✅ Deploy bem-sucedido!**

---

## Cenário Alternativo: Rollback Necessário

Imagine que após o deploy você descobriu um bug crítico.

### Passo 1: Listar Backups

```bash
$ ./deploy.sh rollback-list
```

**Output:**
```
📦 Listando backups...

📦 Backups disponíveis:

🌟 [1] app_backup_20251228_143025.tar.gz
      Data: 28/12/2025 14:30:25 | Tamanho: 45.32 MB
   [2] app_backup_20251228_120000.tar.gz
      Data: 28/12/2025 12:00:00 | Tamanho: 44.87 MB
   [3] app_backup_20251227_180000.tar.gz
      Data: 27/12/2025 18:00:00 | Tamanho: 43.21 MB
```

### Passo 2: Restaurar Backup

```bash
$ ./deploy.sh rollback
```

**Output:**
```
♻️  Restaurando backup mais recente...

♻️  Restaurando backup: app_backup_20251228_143025.tar.gz

⚠️  ATENÇÃO: Esta ação vai substituir o app/ atual!
❓ Deseja continuar? (sim/não):
```

**Você digita:** `sim`

**Output continua:**
```
ℹ️  Criando backup de segurança do estado atual...
✅ Backup de segurança criado: app_before_rollback_20251228_145030.tar.gz
ℹ️  app/ removido
ℹ️  Extraindo backup...
✅ Backup restaurado com sucesso!
ℹ️  Restaurando banco de dados...
ℹ️  Backup de segurança do banco: financas_before_rollback_20251228_145030.db
✅ Banco de dados restaurado!

✅ Rollback concluído!
ℹ️  Aplicação restaurada. Reinicie o servidor se necessário.
```

**O que aconteceu:**
1. Criou backup de segurança do estado atual
2. Restaurou `app/` do backup anterior
3. Também restaurou banco de dados
4. Aplicação voltou ao estado anterior ao deploy

---

## Resumo do Fluxo

```
┌─────────────────────┐
│ 1. ./deploy.sh      │
│    validate         │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Validações   │ ✅ 8/8 passaram
    └──────┬───────┘
           │
           ▼
┌─────────────────────┐
│ 2. ./deploy.sh      │
│    deploy           │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Comparação   │ 📝 12 novos, 3 removidos
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Confirmação  │ ❓ sim/não
    └──────┬───────┘
           │ sim
           ▼
    ┌──────────────┐
    │ Backup       │ 💾 app_backup_*.tar.gz
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Deploy       │ 🚀 app_dev → app
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ ✅ Sucesso   │
    └──────────────┘
```

---

## Dicas Práticas

### ✅ Deploy Seguro
```bash
# Sempre validar primeiro
./deploy.sh validate

# Nunca pule a revisão de mudanças
./deploy.sh deploy
# [revisar diferenças cuidadosamente]
# sim [apenas se tudo OK]
```

### ⚠️ Rollback Rápido
```bash
# Problema detectado? Rollback imediato
./deploy.sh rollback
```

### 📊 Monitoramento
```bash
# Ver logs após deploy
tail -f logs/app.log

# Testar endpoints críticos
curl http://localhost:5001/api/v1/health
```

---

## Arquivos Gerados

Após um deploy completo, você terá:

```
backups_local/
├── app_backup_20251228_143025.tar.gz              # Backup do deploy
├── financas_backup_20251228_143025.db             # Banco correspondente
├── app_before_rollback_20251228_145030.tar.gz     # Backup de segurança (se fez rollback)
└── financas_before_rollback_20251228_145030.db    # Banco de segurança (se fez rollback)
```

**Limpeza recomendada:**
- Manter últimos 5 backups
- Remover backups > 30 dias
- Manter sempre 1 backup de produção estável conhecido
