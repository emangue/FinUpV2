# 🗂️ App Dev - Estrutura Limpa e Banco de Dados

**Data:** 04 de Janeiro de 2026 às 19:55

---

## ✅ ESTRUTURA LIMPA DO APP_DEV

```
app_dev/
├── .github/                    # Workflows GitHub
├── backend/                    # 🔥 Backend FastAPI
│   ├── app/                    # Código da aplicação
│   ├── database/               # Banco + backups
│   │   └── financas_dev.db.backup_20260104_152749 (3.8MB)
│   ├── requirements.txt
│   ├── run.py
│   └── start_server.sh
├── frontend/                   # 🌐 Frontend Next.js
│   ├── src/
│   ├── node_modules/
│   ├── package.json
│   └── ...
├── venv/                       # Ambiente Python 3.9
├── financas_dev.db            # 🎯 BANCO PRINCIPAL (3.8MB)
├── init_db.py
├── run_dev_api.py
├── run.py
├── start_all_servers.sh
└── stop_all_servers.sh
```

---

## 🎯 BANCO DE DADOS SENDO USADO

### ⚠️ CONFLITO DETECTADO

**Existem DOIS bancos de dados:**

1. **`app_dev/financas_dev.db`** (raiz) - 3.8MB ✅ **CONTÉM DADOS**
2. **`app_dev/backend/database/financas_dev.db.backup`** (pasta database) - 3.8MB (backup)

### 📍 Configuração Atual do Backend

**Arquivo:** `app_dev/backend/app/config.py`

```python
DATABASE_URL: str = "sqlite:///./database/financas_dev.db"
DATABASE_PATH: Path = Path(__file__).parent.parent / "database" / "financas_dev.db"
```

**Caminho apontado:** `app_dev/backend/database/financas_dev.db`

### ⚠️ PROBLEMA

O backend está configurado para usar **`backend/database/financas_dev.db`**, mas esse arquivo **NÃO EXISTE** (só tem o backup).

O banco com dados está em **`app_dev/financas_dev.db`** (raiz).

---

## 🔧 SOLUÇÃO NECESSÁRIA

### Opção 1: Mover o banco para onde o backend espera (Recomendado)

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev
cp financas_dev.db backend/database/financas_dev.db
```

### Opção 2: Mudar config do backend para apontar para a raiz

Editar `app_dev/backend/app/config.py`:

```python
# ANTES:
DATABASE_URL: str = "sqlite:///./database/financas_dev.db"

# DEPOIS:
DATABASE_URL: str = "sqlite:///../financas_dev.db"
```

---

## 📊 CONTEÚDO DO BANCO

**Tabelas no banco `financas_dev.db`:**

1. `journal_entries` - Transações financeiras principais
2. `users` - Usuários do sistema
3. `base_marcacoes` - Categorias/marcações
4. `base_padroes` - Padrões de classificação automática
5. `base_parcelas` - Controle de parcelas
6. `cartoes` - Cartões cadastrados
7. `categories` - Categorias
8. `estabelecimento_logo` - Logos de estabelecimentos
9. `grupo_config` - Configurações de grupos
10. `ignorar_estabelecimentos` - Estabelecimentos ignorados
11. `bank_format_compatibility` - Compatibilidade de formatos
12. `transacoes_exclusao` - Transações excluídas
13. `user_relationships` - Relacionamentos entre usuários
14. `duplicados_temp` - Tabela temporária de duplicados
15. `audit_log` - Log de auditoria

**Status:** Banco **possui estrutura completa e dados**.

---

## 🧹 ARQUIVOS REMOVIDOS

### Documentação antiga/desnecessária:
- ❌ Todos os `*.txt` (relatórios antigos)
- ❌ Todos os `*.md` duplicados
- ❌ `changes/` (histórico de mudanças)
- ❌ `docs/` (documentação antiga)
- ❌ `backups/` (backups antigos)
- ❌ `scripts/` (scripts do sistema antigo)
- ❌ `tests/` (testes antigos)

### Pastas duplicadas:
- ❌ `app/` (sistema Flask antigo dentro do app_dev)
- ❌ `codigos_apoio/`
- ❌ `deployment_scripts/`

### Arquivos Next.js na raiz (duplicados):
- ❌ `node_modules/` (correto está em frontend/)
- ❌ `public/` (correto está em frontend/)
- ❌ `src/` (correto está em frontend/)
- ❌ `package.json` e `package-lock.json` (corretos estão em frontend/)
- ❌ Configs do Next.js na raiz

### Arquivos temporários:
- ❌ `backend/backend.pid`
- ❌ `*.log` (logs antigos)
- ❌ Arquivos de teste

---

## 🚀 PRÓXIMO PASSO: CORRIGIR BANCO

**Escolha uma das opções acima e execute antes de iniciar o backend.**

### Depois de corrigir:

```bash
# Backend (porta 8000)
cd app_dev/backend
source ../venv/bin/activate
python run.py

# Frontend (porta 3000) - em outro terminal
cd app_dev/frontend
npm run dev
```

---

## 📝 RESUMO

✅ **Estrutura limpa:** 13 itens no app_dev (antes: 71)  
✅ **Banco identificado:** `financas_dev.db` com 15 tabelas e dados  
⚠️ **Correção necessária:** Mover banco para `backend/database/` ou ajustar config  
🎯 **Pronto para rodar:** Após correção do caminho do banco

