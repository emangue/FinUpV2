# 📁 Estrutura Completa do Projeto FinUp

Este documento detalha todas as pastas, arquivos principais e a função de cada componente do sistema.

---

## 🗂️ Estrutura de Pastas (Raiz)

```
ProjetoFinancasV5/
├── CHANGELOG.md                # Histórico de mudanças
├── README.md                   # Introdução rápida
├── VERSION.md                  # Versão atual do sistema
├── docs/                       # Documentação completa
├── scripts/                    # Scripts de deploy, backup, manutenção
├── temp/                       # Arquivos temporários (logs, pids)
├── app_dev/                    # Código da aplicação (backend + frontend)
├── _arquivos_historicos/       # Backups, versões antigas, testes
```

---

## 📚 docs/
- **architecture/**: Diagramas, explicações de arquitetura, DDD, modularização
- **deploy/**: Processos de deploy, SSH, backup, auditoria, paridade dev-prod
- **features/**: Documentação de funcionalidades, autenticação, marcações
- **planning/**: Sprints, TODOs, relatórios de progresso
- **README_PROJETO_COMPLETO.md**: Visão geral do sistema
- **README_ESTRUTURA_COMPLETA.md**: Estrutura detalhada (este arquivo)

---

## 🔧 scripts/
- **database/**: Migrations, fixes, populações de dados
- **deploy/**: quick_start.sh, quick_stop.sh, backup_daily.sh, safe_deploy.sh
- **maintenance/**: Limpeza, reorganização, scripts de pausa
- **migration/**: Migração de dados entre bancos
- **testing/**: Testes standalone, validações de paridade
- **Exemplo:**
  - `backup_daily.sh`: Backup automático do banco
  - `deploy_safe_v2.sh`: Deploy seguro com validações
  - `validate_parity.py`: Validação dev-prod

---

## 🗂️ temp/
- **logs/**: backend.log, frontend.log (logs de execução)
- **pids/**: backend.pid, frontend.pid (controle de processos)
- **Ignorado no git**: Protege dados sensíveis e arquivos temporários

---

## 📱 app_dev/
- **backend/**: Backend FastAPI
- **frontend/**: Frontend Next.js
- **monitoring/**: Scripts e configs de monitoramento
- **uploads_temp/**: Arquivos de upload temporários
- **venv/**: Ambiente virtual Python (usado pelo backend)
- **init_db.py**: Inicialização do banco local
- **migrate_all_user_data.py**: Migração de dados entre usuários
- **README_DEV.md**: Documentação de desenvolvimento

### Estrutura do Backend (app_dev/backend/)
```
backend/
├── app/
│   ├── core/              # Configurações globais (config.py, database.py)
│   ├── domains/           # Domínios isolados (transactions, users, upload, investments)
│   │   ├── transactions/  # Lançamentos financeiros
│   │   ├── users/         # Usuários e autenticação
│   │   ├── upload/        # Upload e processamento de arquivos
│   │   ├── investments/   # Investimentos e portfólio
│   ├── shared/            # Dependências e utilitários compartilhados
│   └── main.py            # Inicialização FastAPI, registro de rotas
├── database/
│   ├── financas_dev.db    # Banco de dados SQLite (dev)
│   ├── backups_daily/     # Backups automáticos
│   └── migrations/        # Migrations Alembic
├── .env                   # Variáveis de ambiente (NUNCA commitado)
```

#### Função de cada pasta:
- **core/**: Configuração global, path do banco, setup do SQLAlchemy
- **domains/**: Cada domínio é autocontido (models, schemas, repository, service, router)
- **shared/**: Funções utilitárias e dependências comuns
- **database/**: Banco SQLite, backups, migrations

### Estrutura do Frontend (app_dev/frontend/)
```
frontend/
├── src/
│   ├── core/
│   │   └── config/            # Configuração de APIs, paths, endpoints
│   ├── features/
│   │   ├── dashboard/         # Dashboard financeiro (desktop/mobile)
│   │   ├── investimentos/     # Dashboard de investimentos
│   │   ├── transactions/      # Listagem e edição de transações
│   │   ├── upload/            # Upload de arquivos
│   │   └── settings/          # Configurações do usuário/admin
│   ├── components/
│   │   ├── app-sidebar.tsx    # Sidebar global
│   │   ├── dashboard-layout.tsx # Layout principal
│   │   └── ui/                # Componentes UI compartilhados
│   └── types/                 # Tipos compartilhados
├── public/                    # Assets estáticos (imagens, ícones)
├── .next/                     # Build do Next.js
├── package.json               # Dependências do frontend
```

#### Função de cada pasta:
- **core/config/**: Centraliza URLs de API, paths, endpoints
- **features/**: Cada feature é isolada (dashboard, investimentos, upload, etc)
- **components/**: Componentes compartilhados entre features
- **ui/**: Botões, cards, inputs reutilizáveis
- **types/**: Tipos TypeScript globais
- **public/**: Imagens, ícones, favicons

---

## 🗄️ _arquivos_historicos/
- **backups_antigos/**: Backups manuais e automáticos
- **docs_antigas/**: Documentação de versões anteriores
- **scripts_migracao/**: Scripts de migração antigos
- **testes/**: Testes de integração e validação
- **pids_antigos/**: Controle de processos antigos
- **codigos_apoio/**: Códigos auxiliares e experimentais

---

## 📝 Arquivos Principais
- **CHANGELOG.md**: Histórico de todas as mudanças relevantes
- **VERSION.md**: Versão atual do sistema
- **README.md**: Introdução rápida ao projeto
- **README_PROJETO_COMPLETO.md**: Visão geral funcional
- **README_ESTRUTURA_COMPLETA.md**: Estrutura detalhada (este)

---

## 🏗️ Fluxo de Deploy e Backup
- **Deploy:**
  - Scripts em `scripts/deploy/` automatizam todo o processo
  - Validação local, backup, git pull, build, migrations, restart
- **Backup:**
  - Backup diário automático em `app_dev/backend/database/backups_daily/`
  - Backup manual via script

---

## 🔒 Segurança
- **.env**: Variáveis sensíveis (NUNCA commitado)
- **.gitignore**: Protege arquivos sensíveis e temporários
- **Rate limiting, CORS, autenticação JWT**
- **Auditoria de acessos e modificações**

---

## 📚 Referências
- Para detalhes de cada domínio, veja `docs/architecture/`
- Para processos de deploy, veja `docs/deploy/`
- Para scripts, veja `scripts/`
- Para histórico, veja `CHANGELOG.md`

---

**Esta estrutura garante modularidade, segurança e rastreabilidade total do sistema.**
