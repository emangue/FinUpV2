# 🏦 FinUp - Sistema Modular de Finanças

## 📖 História do Projeto

O FinUp nasceu da necessidade de organizar, analisar e automatizar a gestão financeira pessoal e familiar, integrando múltiplas fontes de dados (bancos, cartões, investimentos) em um único ambiente. O projeto evoluiu de um sistema monolítico para uma arquitetura modular, escalável e segura, com deploy automatizado e integração contínua.

Principais marcos:
- Início como app Flask monolítico (2023)
- Migração para FastAPI + Next.js (2024)
- Modularização por domínios (transactions, users, upload, investments)
- Implementação de upload inteligente e deduplicação
- Deploy seguro v2 com validações, backup e health check
- Paridade dev-prod com PostgreSQL
- Dashboards mobile e desktop

---

# 📁 Estrutura Completa do Projeto

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

## 📚 docs/
- **architecture/**: Diagramas, explicações de arquitetura, DDD, modularização
- **deploy/**: Processos de deploy, SSH, backup, auditoria, paridade dev-prod
- **features/**: Documentação de funcionalidades, autenticação, marcações
- **planning/**: Sprints, TODOs, relatórios de progresso
- **README_PROJETO_COMPLETO.md**: Visão geral e estrutura do sistema (este arquivo)

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

## 🗂️ temp/
- **logs/**: backend.log, frontend.log (logs de execução)
- **pids/**: backend.pid, frontend.pid (controle de processos)
- **Ignorado no git**: Protege dados sensíveis e arquivos temporários

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

## 🗄️ _arquivos_historicos/
- **backups_antigos/**: Backups manuais e automáticos
- **docs_antigas/**: Documentação de versões anteriores
- **scripts_migracao/**: Scripts de migração antigos
- **testes/**: Testes de integração e validação
- **pids_antigos/**: Controle de processos antigos
- **codigos_apoio/**: Códigos auxiliares e experimentais

## 📝 Arquivos Principais
- **CHANGELOG.md**: Histórico de todas as mudanças relevantes
- **VERSION.md**: Versão atual do sistema
- **README.md**: Introdução rápida ao projeto
- **README_PROJETO_COMPLETO.md**: Visão geral funcional e estrutura (este)

---

## 🖥️ Telas e Funcionalidades

### 1. Dashboard Financeiro
- **Desktop:** Visão geral de receitas, despesas, saldo, gráficos de evolução, filtros por período e categoria.
- **Mobile:** Layout vertical, navegação por BottomNav, filtros simplificados, gráficos adaptados.
- **Componentes:**
  - Cards de resumo
  - Gráficos de pizza e linha
  - Filtros de data, categoria, grupo

### 2. Dashboard de Investimentos
- **Desktop:** Resumo de portfólio, evolução temporal, distribuição por tipo, visão por corretora.
- **Mobile:** Adaptação vertical, navegação mobile, cards empilhados, filtros rápidos.
- **Componentes:**
  - PortfolioOverview
  - DistribuicaoChart
  - VisaoPorCorretora
  - TimelineIndicators

### 3. Transações
- Listagem completa de lançamentos
- Filtros avançados (data, grupo, categoria, tipo)
- Edição inline, exclusão, agrupamento
- Modal de edição e criação

### 4. Upload de Arquivos
- **Processo:**
  - Upload de extratos bancários, faturas de cartão, comprovantes
  - Processamento automático: parser, validação, deduplicação
  - Detecção de tipo de documento (extrato/fatura)
  - Geração de IdTransacao único (hash condicional)
  - Marcação automática e manual
  - Confirmação e integração ao banco
- **Componentes:**
  - UploadDialog
  - ConfirmarUpload
  - EmptyStates para feedback

### 5. Hierarquia de Marcações
- **BaseMarcacoes:** Grupos e subgrupos configuráveis
- **Marcacoes:** Marcações aplicadas a transações
- **Processo:**
  - Marcação automática por regras
  - Marcação manual via UI
  - Hierarquia: Grupo Geral > Subgrupo > Categoria
  - Permite múltiplas marcações por transação

### 6. Configurações
- Gestão de usuários, permissões, grupos, categorias
- Configuração de metas, orçamentos, limites
- Admin: visibilidade de telas, backup, auditoria

---

## 🔄 Processo de Upload e Deduplicação

1. **Upload do arquivo** (extrato/fatura)
2. **Detecção do tipo de documento**
   - Extrato: hash preserva nome completo do lançamento
   - Fatura: hash normaliza parcela/estabelecimento
3. **Parser e validação**
   - Extração de campos: data, valor, nome, categoria
   - Validação de formato e integridade
4. **Deduplicação**
   - Geração de IdTransacao único
   - Verificação de duplicidade no banco
5. **Marcação automática**
   - Aplicação de regras de marcação
   - Sugestão de grupos/categorias
6. **Confirmação manual**
   - Usuário revisa e ajusta marcações
7. **Integração ao banco**
   - Transações salvas, marcações aplicadas

---

## 🏷️ Hierarquia de Marcações

- **BaseMarcacoes:**
  - Grupos principais (Despesa, Receita, Investimento)
  - Subgrupos (ex: Alimentação, Transporte, Renda Fixa)
  - Categorias específicas
- **Processo de Marcação:**
  - Automática: regras por nome, valor, data
  - Manual: UI permite ajuste fino
  - Permite múltiplas marcações por transação
  - Marcações influenciam dashboards e relatórios

---

## 🚀 Deploy Seguro v2

- **Script:** `./scripts/deploy/deploy_safe_v2.sh --with-migrations`
- **Etapas:**
  1. Validação local (git, sintaxe, migrations)
  2. Backup automático do banco
  3. Deploy no servidor (git pull, build, migrations)
  4. Restart dos serviços (backend, frontend)
  5. Health check e validação de endpoints
- **Benefícios:**
  - Previne deploy quebrado
  - Garante backup antes de alterações
  - Sincroniza ambientes dev/prod
  - Valida paridade de schema

---

## 🛡️ Segurança e Auditoria

- **Autenticação JWT, rate limiting, CORS restrito**
- **Proteção de dados sensíveis (.env, .db, .log)**
- **Auditoria de acessos e modificações**
- **Backup diário automático**
- **Validação de paridade dev-prod**

---

## 📊 Relatórios e Dashboards

- Dashboards dinâmicos por período, categoria, grupo
- Relatórios mensais, anuais, por categoria
- Exportação de dados
- Visualização mobile e desktop

---

## 🏗️ Arquitetura Modular

- **Backend:** FastAPI, domínios isolados (transactions, users, upload, investments)
- **Frontend:** Next.js, features isoladas, componentes compartilhados
- **Banco:** SQLite (dev), PostgreSQL (prod)
- **Deploy:** Scripts automatizados, versionamento semântico

---

## 📚 Referências e Documentação

- Documentação completa: `docs/`
- Scripts de deploy, backup, auditoria: `scripts/`
- Histórico de mudanças: `CHANGELOG.md`
- Auditoria de segurança: `docs/deploy/`
- Estrutura de dados: `docs/architecture/`

---

## 💡 Observações Finais

O FinUp é um sistema em constante evolução, focado em modularidade, segurança e automação financeira. Cada tela e processo foi desenhado para máxima flexibilidade e rastreabilidade, permitindo fácil expansão e adaptação a novos cenários financeiros.

Para dúvidas, sugestões ou contribuições, consulte a documentação ou entre em contato com o time de desenvolvimento.
