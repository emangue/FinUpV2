# 📜 Scripts de Deploy e Versionamento

## 🚀 Deploy Scripts

### `deploy_dev_to_prod.py`
Script principal de deploy de `app_dev/` para `app/` (produção).

**Funcionalidades:**
- ✅ Validações automáticas (syntax, imports, security, frontend)
- ✅ Comparação detalhada dev vs prod
- ✅ Backup automático antes de deploy
- ✅ Confirmação interativa
- ✅ Deploy seguro com rollback

**Uso:**
```bash
# Via script auxiliar (RECOMENDADO)
./deploy.sh validate      # Apenas validações
./deploy.sh deploy        # Deploy completo

# Via Python direto
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/deploy_dev_to_prod.py --validate-only
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/deploy_dev_to_prod.py
```

### `rollback_deployment.py`
Script de rollback para restaurar backups anteriores.

**Funcionalidades:**
- ✅ Lista todos os backups disponíveis
- ✅ Restaura backup específico ou mais recente
- ✅ Backup de segurança antes de restaurar
- ✅ Restaura também banco de dados

**Uso:**
```bash
# Via script auxiliar (RECOMENDADO)
./deploy.sh rollback-list                                # Lista backups
./deploy.sh rollback                                      # Último backup
./deploy.sh rollback app_backup_20251228_143025.tar.gz   # Backup específico

# Via Python direto
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/rollback_deployment.py --list
/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python scripts/rollback_deployment.py
```

## 🔧 Version Manager

### `version_manager.py`
Gerenciador de versionamento para arquivos críticos do projeto.

**Funcionalidades:**
- ✅ Marca arquivos como `-dev` durante desenvolvimento
- ✅ Cria branches git automáticas
- ✅ Gera documentação de mudanças em `changes/`
- ✅ Protege contra commits de versões dev
- ✅ Facilita rollback de mudanças

**Uso:**
```bash
# Iniciar mudança em arquivo crítico
python scripts/version_manager.py start app/models.py

# Finalizar mudança (remove -dev, documenta, commit)
python scripts/version_manager.py finish app/models.py "Descrição da mudança"

# Ver status atual
python scripts/version_manager.py status

# Rollback para versão específica
python scripts/version_manager.py rollback v2.1.0

# Criar release (patch/minor/major)
python scripts/version_manager.py release patch
```

## 📁 Estrutura de Backups

```
backups_local/
├── app_backup_20251228_143025.tar.gz       # Backup de app/
├── financas_backup_20251228_143025.db      # Backup do banco
├── app_before_rollback_20251228_150130.tar.gz  # Backup de segurança
└── ...
```

**Retenção:**
- Backups são mantidos indefinidamente
- Recomenda-se limpar backups > 30 dias manualmente
- Backups de segurança (`before_rollback`) podem ser removidos após confirmar sucesso

## 🔐 Git Hooks

### `pre-commit`
Hook que bloqueia commits inválidos:
- ❌ Versões terminando em `-dev`
- ❌ Versões terminando em `-test`
- ❌ Mudanças em arquivos críticos sem documentação em `changes/`

**Instalação:**
```bash
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 📊 Workflow Completo

### Desenvolvimento Normal
1. Trabalhar em `app_dev/`
2. Testar localmente
3. Validar: `./deploy.sh validate`
4. Deploy: `./deploy.sh deploy`

### Com Versionamento
1. Iniciar mudança: `python scripts/version_manager.py start <arquivo>`
2. Fazer modificações
3. Finalizar: `python scripts/version_manager.py finish <arquivo> "descrição"`
4. Deploy: `./deploy.sh deploy`

### Em Caso de Problemas
1. Listar backups: `./deploy.sh rollback-list`
2. Restaurar: `./deploy.sh rollback`

## 🎯 Arquivos Críticos (requerem versionamento)

- `app/models.py` - Schema do banco
- `app/utils/hasher.py` - Lógica de hash
- `app/utils/processors/*.py` - Processadores
- `app/blueprints/*/routes.py` - Rotas e lógica
- `app/config.py` - Configurações

## 📖 Documentação Adicional

- **Workflow completo**: [`docs/WORKFLOW_DEPLOY.md`](../docs/WORKFLOW_DEPLOY.md)
- **Versionamento**: [`VERSIONAMENTO.md`](../VERSIONAMENTO.md)
- **Contribuição**: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- **Instruções Copilot**: [`.github/copilot-instructions.md`](../.github/copilot-instructions.md)
