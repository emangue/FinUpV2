# 🧹 PLANO DE LIMPEZA - REPOSITÓRIO GITHUB

## Status Atual
- **Repo:** https://github.com/emangue/FinUp
- **Problema:** Tem arquivos antigos e estrutura confusa
- **Meta:** Começar do zero com apenas `app_dev/`

---

## ✅ ESTRUTURA FINAL DESEJADA

```
FinUp/
├── .gitignore                    # Completo
├── README.md                     # Documentação limpa
├── requirements.txt              # Backend dependencies
├── package.json                  # Frontend dependencies (opcional)
├── .env.example                  # Template de variáveis
├── docker-compose.yml            # Deploy via Docker (opcional)
│
└── app_dev/                      # ⭐ ÚNICO DIRETÓRIO NECESSÁRIO
    ├── backend/
    │   ├── app/
    │   │   ├── core/
    │   │   ├── domains/
    │   │   ├── shared/
    │   │   └── main.py
    │   ├── database/
    │   │   └── .gitkeep          # Pasta vazia (banco não vai pro Git)
    │   ├── requirements.txt
    │   ├── run.py
    │   └── .env.example
    │
    └── frontend/
        ├── src/
        ├── public/
        ├── package.json
        ├── tsconfig.json
        ├── next.config.js
        └── .env.example
```

---

## 🗑️ ARQUIVOS PARA REMOVER (RAIZ DO PROJETO)

### Arquivos/Pastas que NÃO devem ir pro deploy:
```
❌ adicionar_user_id_investimentos.py
❌ backup_daily.sh                       # Deploy tem próprio sistema de backup
❌ check_version.py
❌ cleanup_project.sh
❌ copiar_dados_usuario.py
❌ copiar_investimentos_teste.py
❌ fix_all_fetch.sh
❌ fix_categoria_geral_from_config.py
❌ fix_mp_dates.py
❌ fix_version.py
❌ limpar_grupos_planning_vazios.py
❌ popular_*.py                          # Scripts de dev/migração
❌ reimport_mp.py
❌ test_*.py                             # Testes locais
❌ quick_start.sh                        # Script de dev local
❌ quick_stop.sh                         # Script de dev local
❌ *.pid                                 # Process IDs locais
❌ backend.log                           # Logs locais
❌ frontend.log                          # Logs locais
❌ _arquivos_historicos/                 # Histórico de desenvolvimento
❌ scripts/                              # Scripts de migração antigos
```

### Documentos que PODEM ficar (mas limpar):
```
✅ README.md                             # Reescrever do zero
✅ .gitignore                            # Revisar/completar
⚠️ DATABASE_CONFIG.md                    # Mover para docs/ (opcional)
⚠️ GUIA_DEPLOY_PRODUCAO.md               # Mover para docs/ (opcional)
⚠️ PLANO_*.md                            # Mover para docs/ ou remover
```

---

## 📝 .gitignore COMPLETO (CRIAR/ATUALIZAR)

```gitignore
# ========================================
# Python
# ========================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
*.egg-info/
.pytest_cache/
.coverage

# ========================================
# Node.js
# ========================================
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.next/
.turbo/
out/
build/
dist/

# ========================================
# Ambiente e Segredos
# ========================================
.env
.env.*
!.env.example
*.local

# ========================================
# Banco de Dados
# ========================================
*.db
*.sqlite
*.sqlite3
app_dev/backend/database/*.db
app_dev/backend/database/backups_daily/
app_dev/backend/database/backups/

# ========================================
# Logs e PIDs
# ========================================
*.log
*.pid
logs/
backend.log
frontend.log
backend*.pid
frontend*.pid

# ========================================
# IDE e Editores
# ========================================
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# ========================================
# Uploads Temporários
# ========================================
uploads_temp/
temp/
tmp/

# ========================================
# Scripts Locais (Não ir para produção)
# ========================================
quick_start.sh
quick_stop.sh
backup_daily.sh
check_version.py
fix_*.py
test_*.py
*_test.py
adicionar_*.py
copiar_*.py
limpar_*.py
popular_*.py
reimport_*.py

# ========================================
# Histórico de Desenvolvimento
# ========================================
_arquivos_historicos/
backups_antigos/
pids_antigos/
scripts_migracao/

# ========================================
# Certificados SSL (se usar)
# ========================================
*.pem
*.key
*.crt
ssl/
certs/
```

---

## 🚀 COMANDOS PARA LIMPAR O REPOSITÓRIO

### Opção A: Começar do Zero (Recomendado)

```bash
# 1. Criar novo branch limpo
cd /caminho/FinUp
git checkout --orphan clean-main
git rm -rf .

# 2. Copiar apenas app_dev do projeto local
cp -r /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev .

# 3. Criar arquivos essenciais
cat > .gitignore << 'EOF'
# [Colar conteúdo do .gitignore acima]
EOF

cat > README.md << 'EOF'
# FinUp - Sistema de Gestão Financeira

Sistema completo de gestão financeira pessoal com dashboard, categorização automática e planejamento orçamentário.

## Stack
- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** Next.js 16 + React 19
- **Database:** PostgreSQL (produção) / SQLite (dev)

## Deploy
Ver `GUIA_DEPLOY_PRODUCAO.md`

## Desenvolvimento Local
Ver documentação em `app_dev/README_DEV.md`
EOF

cp /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/GUIA_DEPLOY_PRODUCAO.md .

# 4. Criar .env.example
cat > .env.example << 'EOF'
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/financas_db
JWT_SECRET_KEY=change-me-min-64-chars
DEBUG=false
BACKEND_CORS_ORIGINS=https://seu-dominio.com

# Frontend
NEXT_PUBLIC_API_URL=https://seu-dominio.com/api
NODE_ENV=production
EOF

# 5. Commit e forçar push
git add .
git commit -m "🧹 Repositório limpo - apenas app_dev para produção"
git branch -M main
git push -f origin main
```

### Opção B: Limpar Branch Atual

```bash
cd /caminho/FinUp

# 1. Backup local (precaução)
git branch backup-old-structure

# 2. Remover arquivos antigos
git rm -r _arquivos_historicos/ scripts/
git rm *.py *.sh *.pid *.log 2>/dev/null || true
git rm -r --cached node_modules/ venv/ 2>/dev/null || true

# 3. Atualizar .gitignore
# [Criar arquivo .gitignore com conteúdo acima]

# 4. Commit
git add .gitignore
git commit -m "🧹 Remove arquivos de desenvolvimento e histórico"
git push origin main
```

---

## ✅ CHECKLIST PÓS-LIMPEZA

Antes de fazer deploy, validar:

- [ ] ✅ Repositório tem APENAS `app_dev/` + arquivos essenciais
- [ ] ✅ `.gitignore` bloqueia `.env`, `*.db`, `*.log`, `*.pid`
- [ ] ✅ `.env.example` existe e está documentado
- [ ] ✅ README.md está atualizado e claro
- [ ] ✅ Sem scripts de dev (`quick_start.sh`, `test_*.py`, etc)
- [ ] ✅ Sem arquivos históricos (`_arquivos_historicos/`)
- [ ] ✅ Sem logs, PIDs, ou databases commitados
- [ ] ✅ `app_dev/backend/database/` vazio (sem .db)
- [ ] ✅ Tamanho do repo < 50MB (sem node_modules/venv)

---

## 🎯 PRÓXIMO PASSO

Após limpar:
1. Validar repo no GitHub
2. Clonar limpo no servidor
3. Seguir `GUIA_DEPLOY_PRODUCAO.md`
