# 📁 Estrutura do Projeto - Financial Management System v3.0.1

**Data:** 02/01/2026  
**Status:** Organizado e em produção

---

## 🗂️ Estrutura de Diretórios

```
ProjetoFinancasV3/
│
├── 📂 app/                          # Código principal da aplicação Flask
│   ├── __init__.py                  # Inicialização Flask + blueprints
│   ├── config.py                    # Configurações (dev/prod)
│   ├── extensions.py                # Extensões Flask (db, login_manager)
│   ├── filters.py                   # Filtros Jinja2 customizados
│   ├── models.py                    # Modelos SQLAlchemy (User, JournalEntry, etc)
│   │
│   ├── 📂 blueprints/               # Módulos da aplicação
│   │   ├── 📂 admin/                # Painel administrativo
│   │   │   ├── routes.py            # Rotas de admin (grupos, marcações, etc)
│   │   │   └── templates/           # Templates específicos do admin
│   │   │
│   │   ├── 📂 auth/                 # Autenticação e usuários
│   │   │   ├── routes.py            # Login, logout, registro, perfil
│   │   │   └── templates/           # Templates de autenticação
│   │   │
│   │   ├── 📂 dashboard/            # Dashboard principal
│   │   │   ├── routes.py            # Visualização de transações
│   │   │   └── templates/           # Templates do dashboard
│   │   │
│   │   └── 📂 upload/               # Upload e processamento de arquivos
│   │       ├── routes.py            # Upload, validação, confirmação
│   │       ├── 📂 classifiers/      # Classificação automática
│   │       ├── 📂 processors/       # Processadores de extratos
│   │       └── templates/           # Templates de upload
│   │
│   └── 📂 utils/                    # Utilitários compartilhados
│       ├── hasher.py                # Geração de IDs (FNV-1a)
│       ├── normalizer.py            # Normalização de textos
│       ├── deduplicator.py          # Detecção de duplicatas
│       └── 📂 processors/
│           └── 📂 preprocessadors/  # Preprocessadores de bancos (BB, Itaú, XP, etc)
│
├── 📂 templates/                    # Templates Jinja2 compartilhados
│   ├── base.html                    # Layout base
│   ├── transacoes.html              # Lista de transações (compartilhada)
│   ├── confirmar_upload.html        # Confirmação de upload
│   ├── 📂 _macros/                  # Componentes reutilizáveis
│   │   ├── transacao_filters.html   # Filtros de pesquisa
│   │   └── transacao_modal_edit.html # Modal de edição
│   └── 📂 _partials/                # Seções compartilhadas
│
├── 📂 static/                       # Arquivos estáticos
│   ├── 📂 css/                      # Estilos CSS
│   │   └── style.css
│   ├── 📂 js/                       # JavaScript
│   │   └── main.js
│   └── 📂 logos/                    # Logos de estabelecimentos (PNG, SVG, WEBP)
│
├── 📂 scripts/                      # Scripts utilitários
│   ├── backup_database.py           # Sistema de backup automático
│   ├── database_health_check.py     # Verificação de saúde do BD
│   ├── deployment_diff.py           # Detecção de mudanças para deploy
│   ├── version_manager.py           # Gerenciamento de versões
│   ├── pre-commit                   # Hook Git para versionamento
│   ├── install_hooks.sh             # Instalador de hooks Git
│   │
│   ├── 📂 Migração (HISTÓRICO):
│   │   ├── migrate_to_multiuser.py
│   │   ├── migrate_add_user_relationships.py
│   │   ├── populate_id_parcela.py
│   │   └── ... (outros scripts de migração)
│   │
│   └── 📂 Análise:
│       ├── analisar_transacoes.py
│       ├── buscar_similares.py
│       └── check_groups.py
│
├── 📂 deployment_scripts/           # 🆕 Scripts de deployment
│   ├── deploy_hostinger.sh          # Deploy completo para Hostinger
│   ├── deploy.py                    # Orquestrador de deployment
│   └── deployment_diff.py           # (pode mover de scripts/)
│
├── 📂 tests/                        # Testes automatizados
│   └── deployment_health_check.py   # 12 testes de capabilities
│
├── 📂 docs/                         # 🆕 Documentação
│   ├── SECURITY_AND_DEPLOYMENT.md   # 🆕 Segurança completa (este arquivo)
│   ├── ARQUITETURA_COMPONENTES.md   # Arquitetura de componentes
│   ├── BUGS.md                      # Histórico de bugs
│   ├── CHANGELOG.md                 # Histórico de versões
│   ├── CONTRIBUTING.md              # Guia de contribuição
│   ├── DEPLOYMENT.md                # Guia de deployment
│   ├── DEPLOYMENT_QUICK_START.md    # Quick start de deployment
│   ├── DEPLOYMENT_SUMMARY.md        # Resumo de deployment
│   ├── ESTRUTURA_PROJETO.md         # Estrutura do projeto
│   ├── IMPLEMENTACAO_VERSIONAMENTO.md # Sistema de versionamento
│   ├── MODULARIZACAO.md             # Histórico de modularização
│   ├── PROTECAO_BASES.md            # Proteção de dados
│   ├── README.md                    # README principal
│   ├── RESPOSTA_COMPLETA.md         # FAQ deployment
│   ├── STATUSPROJETO.md             # Status atual do projeto
│   ├── TODO_MULTIUSUARIO.md         # Roadmap multi-usuário
│   ├── VERSION.md                   # Versão atual (3.0.1)
│   ├── VERSIONAMENTO.md             # Sistema de versionamento
│   └── VM_INFO_CHECKLIST.md         # Checklist de informações da VM
│
├── 📂 data_samples/                 # 🆕 Arquivos de dados de exemplo
│   ├── extrato_ana_beatriz_BB.csv
│   ├── fatura_202601.csv
│   ├── fatura_azul_202501.csv
│   ├── account_statement-*.xlsx
│   ├── extrato_btg.xls
│   ├── extrato_itau.xls
│   ├── mp_agosto.xlsx
│   ├── mp_dez_parcial.xlsx
│   └── OUROCARD_VISA_GOLD-Jan_25.ofx
│
├── 📂 backups_local/                # 🆕 Backups locais do banco
│   └── financas.db.backup_*
│
├── 📂 changes/                      # Logs de mudanças (versionamento)
│   └── 2025-12-*.md
│
├── 📂 _csvs_historico/              # CSVs históricos (arquivados)
├── 📂 _temp_scripts/                # Scripts temporários (debug)
│
├── 📂 backups/                      # Backups criados por deploy.py
├── 📂 flask_session/                # Sessões Flask (server-side)
├── 📂 uploads_temp/                 # Uploads temporários (limpar periodicamente)
│
├── 📂 venv/                         # Ambiente virtual Python (não commitar)
│
├── 📄 run.py                        # Entry point da aplicação
├── 📄 requirements.txt              # Dependências Python
├── 📄 .gitignore                    # Arquivos ignorados pelo Git
├── 📄 .env                          # Variáveis de ambiente (local)
├── 📄 .env.production.template      # Template para produção
├── 📄 financas.db                   # Banco de dados SQLite (local)
├── 📄 import_base_inicial.py        # Script de importação inicial
├── 📄 import_marcacoes_seguro.py    # Importação de marcações
├── 📄 local_manifest.json           # Manifest de deployment
├── 📄 database_health_report_*.txt  # Relatórios de saúde do BD
└── 📄 deployment_diff_*.md          # Relatórios de diff de deployment

```

---

## 📊 Estatísticas do Projeto

### Código Fonte
- **Linhas de código Python:** ~8,500 linhas
- **Templates Jinja2:** ~3,200 linhas
- **JavaScript:** ~400 linhas
- **CSS:** ~150 linhas

### Banco de Dados
- **Tabelas:** 12
- **Transações:** 4,153
- **Usuários:** 2
- **Padrões de classificação:** 373
- **Grupos configurados:** 20

### Documentação
- **Arquivos Markdown:** 17
- **Páginas de documentação:** ~3,500 linhas

---

## 🔍 Descrição dos Principais Diretórios

### `/app/` - Aplicação Principal
Contém todo o código Flask organizado em blueprints modulares. Cada blueprint é responsável por uma funcionalidade específica (auth, admin, dashboard, upload).

### `/docs/` - Documentação 🆕
Centralizamos TODA a documentação aqui. Antes os arquivos .md ficavam espalhados na raiz, agora estão organizados.

### `/deployment_scripts/` - Scripts de Deploy 🆕
Scripts responsáveis pelo deployment automatizado na VM Hostinger. Separados dos scripts utilitários.

### `/data_samples/` - Dados de Exemplo 🆕
Arquivos CSV, XLSX, XLS, OFX de exemplo para testar processadores. NUNCA commitar dados reais aqui (dados sensíveis).

### `/backups_local/` - Backups Locais 🆕
Backups do banco de dados local. Mantidos por 30 dias. NÃO commitar no Git (já está no .gitignore).

### `/scripts/` - Scripts Utilitários
Scripts de manutenção, análise, migração e versionamento. Subdivididos por categoria.

### `/templates/` - Templates Compartilhados
Templates Jinja2 usados por múltiplos blueprints. Templates específicos de um blueprint ficam em `app/blueprints/<nome>/templates/`.

### `/static/` - Arquivos Estáticos
CSS, JavaScript e logos servidos diretamente pelo Nginx em produção (cache de 30 dias).

### `/changes/` - Versionamento
Logs de mudanças criados pelo `version_manager.py`. Agregados no CHANGELOG.md a cada release.

### `/tests/` - Testes Automatizados
Testes de capabilities e integração. Executados antes de cada deployment.

---

## 🚫 O que NÃO commitar no Git

```
# Já configurado no .gitignore:
venv/                    # Ambiente virtual (cada dev tem o seu)
__pycache__/             # Cache Python
*.pyc                    # Bytecode compilado
*.db                     # Banco de dados local
*.db-*                   # Arquivos temporários do SQLite
financas.db.backup_*     # Backups locais
flask_session/           # Sessões Flask
.env                     # Variáveis de ambiente (senhas)
.DS_Store                # Arquivos do macOS
uploads_temp/            # Uploads temporários
backups_local/           # Backups locais (novo)
data_samples/*.csv       # Dados sensíveis (opcional - ver abaixo)
```

### ⚠️ ATENÇÃO: Dados Sensíveis

Se os arquivos em `data_samples/` contêm dados REAIS (CPF, valores, estabelecimentos reais), adicione ao `.gitignore`:

```bash
# Adicionar ao .gitignore:
data_samples/
```

Se são apenas exemplos/mockups (sem dados sensíveis), pode commitar.

---

## 🔄 Fluxo de Trabalho Recomendado

### 1. Desenvolvimento Local
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação em modo desenvolvimento
python run.py
# Acessa: http://localhost:5000
```

### 2. Versionamento
```bash
# Antes de modificar arquivo crítico:
python scripts/version_manager.py start app/models.py

# Fazer modificações...

# Após testar:
python scripts/version_manager.py finish app/models.py "Descrição da mudança"
```

### 3. Testes Pré-Deployment
```bash
# Rodar health check:
python scripts/database_health_check.py

# Rodar testes de capabilities:
python tests/deployment_health_check.py

# Verificar mudanças:
python deployment_scripts/deploy.py --check-only
```

### 4. Deployment para Produção
```bash
# Deploy completo (recomendado):
./deployment_scripts/deploy_hostinger.sh

# Ou deployment incremental:
python deployment_scripts/deploy.py --target production --vm-user root --vm-host 148.230.78.91
```

### 5. Backup Manual
```bash
# Criar backup local:
python scripts/backup_database.py --output backups_local/manual_$(date +%Y%m%d).db.backup.gz

# Restaurar backup:
python scripts/backup_database.py restore backups_local/manual_20260102.db.backup.gz
```

---

## 📦 Dependências Principais

### Python (requirements.txt)
```
Flask==3.0.0              # Framework web
Flask-Login==0.6.3        # Autenticação
Flask-Session==0.5.0      # Sessões server-side
SQLAlchemy==2.0.23        # ORM banco de dados
pandas==2.1.4             # Processamento de dados
openpyxl==3.1.2          # Leitura de XLSX
xlrd==2.0.1              # Leitura de XLS (antigo)
bcrypt==5.0.0            # Hash de senhas
python-dateutil==2.8.2   # Manipulação de datas
```

### Sistema (Produção - VM)
```
Python 3.12.3            # Interpretador
Nginx 1.24.0             # Servidor web
Gunicorn 23.0.0          # WSGI server
SQLite 3.45.1            # Banco de dados
Certbot 2.9.0            # SSL/Let's Encrypt
Fail2ban 1.0.2           # Proteção brute force
UFW                      # Firewall
```

---

## 🎯 Próximos Passos (Roadmap)

### Curto Prazo (1-2 semanas)
- [ ] Limpar pasta `_temp_scripts/` (mover scripts úteis para `scripts/`)
- [ ] Adicionar `data_samples/` ao `.gitignore` se contém dados sensíveis
- [ ] Remover porta 8080 do firewall (não é mais necessária)
- [ ] Criar arquivo `README.md` principal (overview do projeto)

### Médio Prazo (1-2 meses)
- [ ] Configurar rate limiting (Flask-Limiter)
- [ ] Adicionar monitoramento de uptime (UptimeRobot)
- [ ] Implementar backup remoto (rsync ou cloud criptografado)
- [ ] Criar testes unitários (pytest)

### Longo Prazo (3-6 meses)
- [ ] Migrar para PostgreSQL (se precisar de mais de 5-10 usuários)
- [ ] Adicionar API REST (para app mobile futuro)
- [ ] Implementar 2FA para admin
- [ ] Dashboard com gráficos (Chart.js ou Plotly)

---

## 📞 Contatos e Recursos

- **Produção:** https://finup.emangue.com.br
- **VM:** srv1045889.hstgr.cloud (148.230.78.91)
- **Documentação:** `/docs/` (este diretório)
- **Issues/Bugs:** `docs/BUGS.md`
- **Changelog:** `docs/CHANGELOG.md`

---

**Última atualização:** 02/01/2026  
**Versão do projeto:** 3.0.1  
**Status:** ✅ Em produção
