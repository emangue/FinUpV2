# 📝 Changelog - Sistema FinUp

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

## [v2.0.0] - 2026-02-13 - 🎯 Consolidação Budget Tables (Breaking Changes)

### 🎯 Marcos Principais
- **ARQUITETURA SIMPLIFICADA** - 4 tabelas budget → 1 tabela (75% redução)
- **BREAKING CHANGES** - API endpoints e campos renomeados
- **MIGRATION COMPLETA** - 361 registros migrados sem perda de dados

### ⚡ Redução de Complexidade
- **Tabelas:** 4 → 1 (budget_planning apenas)
- **Modelos:** 4 → 1 (75% redução)
- **Repositories:** 3 → 1 (67% redução)
- **Endpoints:** ~25 → ~12 (52% redução)
- **Schemas:** 13 → 7 (46% redução)

### 🔄 Database Migration
- feat(migration): Migration 635e060a2434 - Consolidação completa
  - Migra 361 records: budget_geral → budget_planning
  - DROP tables: budget_geral, budget_categoria_config, budget_geral_historico
  - Resultado: 1206 total records em budget_planning
  - Backup automático: financas_dev.db.backup_pre_consolidation_*
- feat(migration): Campo valor_medio_3_meses calculado automaticamente
- feat(migration): Suporte a ativo/inativo sem perder valor_planejado

### 🚨 Breaking Changes - Backend
- **REMOVIDOS** endpoints obsoletos (retornam HTTP 410 Gone):
  - ❌ POST /api/v1/budget/geral/bulk-upsert → ✅ /api/v1/budget/planning/bulk-upsert
  - ❌ GET /api/v1/budget/geral → ✅ /api/v1/budget/planning
  - ❌ GET /api/v1/budget/geral/grupos-disponiveis → ✅ /api/v1/budget/planning/grupos-disponiveis
  - ❌ POST /api/v1/budget/categorias-config/* (removidos permanentemente)
  - ❌ POST /api/v1/budget/geral/copy-to-year (removido temporariamente)
- **CAMPO RENOMEADO:** categoria_geral → grupo
- **CAMPO REMOVIDO:** total_mensal (calculado via transações agora)
- **CAMPO NOVO:** valor_medio_3_meses (média automática)

### 🗂️ Backend - Arquivos Removidos
- delete: app/domains/budget/repository_geral.py
- delete: app/domains/budget/repository_categoria_config.py
- delete: schemas BudgetGeral*, BudgetCategoriaConfig*
- delete: models BudgetGeral, BudgetCategoriaConfig, BudgetGeralHistorico

### ⚛️ Frontend - Mudanças Massivas
- refactor(frontend): 20+ arquivos TypeScript atualizados
- refactor(goals): Interfaces Goal usando grupo em vez de categoria_geral
- refactor(goals): calculateGoalProgress() recebe valorRealizado como parâmetro
- refactor(mobile/budget): 4 páginas atualizadas (page, new, [goalId], manage)
- refactor(desktop/budget): 3 páginas atualizadas (page, page 2, simples)
- refactor(components): EditGoalModal sem referências a total_mensal
- refactor(components): ManageGoalsListItem usa valor_medio_3_meses

### 📚 Documentação
- docs(plano): PLANO_IMPLEMENTACAO.md - 4 sprints detalhados
- docs(sprint): Sprint 1 completo (2.5 horas, 153 arquivos)
- docs(breaking): Breaking changes documentados em migration

### ✅ Validações
- ✅ Migration executada sem erros
- ✅ Backend inicia corretamente
- ✅ Frontend compila sem erros TypeScript
- ✅ Endpoints antigos retornam HTTP 410
- ✅ 153 arquivos commitados

### 🔜 Próximo Release
- Sprint 2: Auto-criação de grupos/subgrupos via API
- Sprint 3: UI para criar grupos no upload
- Sprint 4: Validação E2E completa

---

## [v1.1.0] - 2026-01-22 - 🚀 Deploy Produção & Migração Completa

### 🎯 Marcos Principais
- **DEPLOY PRODUÇÃO COMPLETO** - Sistema 100% operacional em meufinup.com.br
- **MIGRAÇÃO DATABASE** - SQLite → PostgreSQL (11.521 registros migrados)
- **7.738 TRANSAÇÕES** migrando com sucesso para produção

### ✨ Deploy e Infraestrutura
- feat(deploy): Deploy completo em produção com HTTPS (meufinup.com.br)
- feat(deploy): Configuração systemd para backend (finup-backend) e frontend (finup-frontend)
- feat(deploy): Scripts quick_start.sh e quick_stop.sh para gerenciamento rápido
- feat(deploy): Backup diário automático em backups_daily/ (mantém 7 dias)
- feat(deploy): Auditoria de segurança e otimizações de permissões

### 🔄 Migração SQLite → PostgreSQL
- feat(migration): Script completo migrate_sqlite_to_postgres.py (26 tabelas, 290 linhas)
- feat(migration): Script fix_migration_v2.py com correções de schema (349 linhas)
- feat(migration): Suporte a schemas case-sensitive PostgreSQL (colunas com aspas duplas)
- feat(migration): Conversão automática integer→boolean para campos ativo/flags
- feat(migration): PRAGMA table_info para descoberta dinâmica de colunas
- feat(migration): Commit individual por linha (evita transaction aborted)
- feat(migration): Migração bem-sucedida de:
  - ✅ journal_entries: 7.738 transações
  - ✅ base_marcacoes: 405 grupos
  - ✅ generic_classification_rules: 55 regras
  - ✅ investimentos_portfolio: 626 ativos
  - ✅ investimentos_historico: 626 registros mensais
  - ✅ investimentos_cenarios: 6 cenários
  - ✅ investimentos_aportes_extraordinarios: 12 aportes
  - ✅ 16 outras tabelas de configuração: 2.654 registros

### 🐛 Correções de Schema PostgreSQL
- fix(migration): Mapeamento correto de colunas case-sensitive (Data, GRUPO, SUBGRUPO)
- fix(migration): generic_classification_rules usa nome_regra (não pattern)
- fix(migration): investimentos_portfolio usa nome_produto, balance_id, corretora
- fix(migration): investimentos_cenarios usa nome_cenario, patrimonio_inicial, rendimento_mensal_pct
- fix(migration): investimentos_historico usa ano, mes, anomes, data_referencia
- fix(migration): investimentos_aportes_extraordinarios usa mes_referencia (não data_prevista)
- fix(backend): Conexão PostgreSQL com psycopg2 configurada
- fix(backend): DATABASE_URL em .env para produção

### 🔧 Frontend - Correções de API
- fix(frontend): Todas as rotas usam /api/v1/ prefix correto
- fix(frontend): fetchWithAuth() implementado em todas as páginas
- fix(frontend): Tokens JWT funcionando (localStorage + headers Authorization)
- fix(frontend): Proxy genérico [...proxy] substituindo rotas individuais
- fix(frontend): URLs centralizadas em API_CONFIG.BACKEND_URL
- fix(frontend): Dashboard, transações, settings funcionando 100%

### 🏗️ Arquitetura e Organização
- refactor: Reorganização de pastas - docs/, scripts/, temp/
- refactor: Scripts de database em scripts/database/
- refactor: Scripts de deploy em scripts/deploy/
- refactor: Scripts de migração em scripts/migration/
- refactor: Logs e PIDs em temp/ (ignorados no git)
- cleanup: Remove script obsoleto fix_migration_issues.py

### 📚 Documentação
- docs: INSTRUCOES_MIGRACAO_FINAL.md com processo completo
- docs: Copilot instructions atualizadas com regras de organização
- docs: Mapeamento de estrutura de pastas obrigatória
- docs: Guias de troubleshooting e rollback

### ✅ Validações e Testes
- test: Backend rodando em porta 8000 (2 workers Uvicorn)
- test: Frontend rodando em porta 3000 (Next.js 16.1.1)
- test: PostgreSQL aceitando conexões localhost:5432
- test: Dashboard mostrando 7.738 transações corretamente
- test: Admin pages mostrando dados (bancos, screens, categorias)
- test: Upload, classificações, exclusões funcionando

---

## [v1.0.0] - 2026-01-22

### ✨ Novas Funcionalidades
- feat(simulador): Adiciona evolução de aportes extraordinários e marcadores anuais no gráfico (8db3bf76)
- feat: Implementar campos completos preview/journal e corrigir upload (f3f0e69f)
- feat: Adiciona módulo de Gestão de Grupos e correções visuais e de lógica no Dashboard (4110f831)
- feat: corrige filtros e cálculos do dashboard + adiciona mês fatura (4baf1cbf)
- feat: Dashboard improvements and automatic transaction classification system (b85806f7)
- feat: implementar geração automática de CategoriaGeral e MesFatura (d908f226)
- feat: Sistema de hash v4.2.1 com normalizacao condicional (a16c6180)
- feat(budget): Script para recalcular médias com MesFatura + IgnorarDashboard - 369 registros atualizados (a419beb8)
- feat(budget): Drill-down de média com detalhamento (f20b67cf)
- feat(budget): Adiciona coluna valor_medio_3_meses e popula histórico (6f7b9f46)
- feat(budget): Adiciona botões de aplicar média e corrige cálculo (435c3f72)
- feat(budget): Remove Pagamento Fatura e adiciona botões de aplicar média (eab3662f)
- feat(budget): Adiciona Meta Simples por Tipo de Gasto com médias dos últimos 3 meses (e3c7b78d)
- feat(frontend): Refatora Meta Detalhada com categorias dinâmicas e drag & drop (4b205cd7)
- feat(budget): Adiciona endpoints REST para configuração de categorias (47ed31be)
- feat(budget): Backend para sistema hierárquico de orçamento (3ad58b48)
- feat(budget): Implementa sistema completo de orçamento em dois níveis (2dc75d05)
- feat: Sistema de orçamento - backend e componente dashboard funcionais (3bb65aeb)
- feat: Novo processador BTG completo e documentado (bff3771b)
- feat: Implementa hash recursivo v4.1.0 para duplicados (78db3577)
- feat: Sistema completo de deduplicação e melhorias no preview de upload (3c34bbd9)
- feat(upload): adiciona validação de saldo para extratos bancários (3ae85719)
- feat: adicionar validacao de saldo para extratos bancarios (77e24490)
- feat(frontend): Implementa visualização matricial de compatibilidade de bancos (4b7b2598)
- feat(compatibility): Reestrutura banco para formato matricial + validação no upload (80a3c13f)
- feat(upload): Adiciona filtros Base Parcelas e Journal Entries com ordem do processo cascata (56e67d92)
- feat: Adiciona abas de filtro na pré-visualização de upload (c9b1d995)
- feat: Implementa classificador de regras genéricas e edição manual na pré-visualização (932efdf1)
- feat: Sistema de exclusões e fixes no upload (d90c5d1b)

### 🐛 Correções
- feat: corrige filtros e cálculos do dashboard + adiciona mês fatura (4baf1cbf)
- fix(budget): Usa MesFatura para cálculo de média e detalhamento (não Data da compra) (eadb35dc)
- fix(budget): Exclui transações com IgnorarDashboard=1 do cálculo de média e detalhamento (8c9d6857)
- fix(budget): Aplica filtros imediatamente ao navegar do drill-down para transações (17855d10)
- fix(budget): Corrige filtro de mês no drill-down - converte YYYY-MM para year/month e exibe filtros visualmente (9156493d)
- fix(budget): Adiciona funções aplicarMedia e aplicarTodasMedias faltantes (30434e39)
- feat(budget): Adiciona botões de aplicar média e corrige cálculo (435c3f72)
- fix(budget): Corrige cálculo de média dos últimos 3 meses (650a05dc)
- fix: Adiciona componente Progress faltante e instala dependência @radix-ui/react-progress (3e990986)
- fix: Corrige mapeamento SQLAlchemy e filtros do dashboard (96561cd0)
- fix: Corrige estrutura RawTransaction no processador BTG (9cc651d8)
- fix: Corrige processador BTG para filtrar Saldo Diário e manter todas transações (62b53eb6)
- fix: Corrige envio de nome do banco no upload (41d02d42)
- fix: Implementa lógica condicional correta para extrato vs fatura (dac26a58)
- fix: remover lançamentos futuros do extrato Itaú (3308278e)
- fix: corrigir processamento de extrato Itaú XLS (072dd52e)
- fix: corrigir case-sensitivity dos formatos de arquivo no upload (6dba5b01)
- fix(frontend): Remove dependência de useToast não existente (a7b1918c)
- fix(upload): Corrige ordem dos filtros para seguir processo cascata correto (f8bef9f9)
- fix: Remove colunas inexistentes do modelo JournalEntry (d3b872c3)
- fix: Corrige nome de coluna Estabelecimento em JournalEntry model (f733ed73)
- fix: Corrige inversão de sinal em fatura Itaú (2272c52c)
- fix: Restaura multiplicação por -1 nos valores de fatura Itaú (1058d384)
- fix: Simplifica lógica de exclusão - remove filtros de banco/tipo (68e6779c)
- fix: Correção de sintaxe no service.py - fechamento de métodos (edeb0556)
- feat: Sistema de exclusões e fixes no upload (d90c5d1b)
- fix: Corrigir imports antigos em hasher.py + extrair_parcela_do_estabelecimento (79fdab03)
- fix: Corrigir marker.py - adaptar para detectar_parcela do normalizer (51e672c8)
- fix: Corrigir processamento Itaú CSV - normalização e detecção cabeçalho (e42a7806)
- fix: Corrigir dataclass MarkedTransaction - ordem de campos com defaults (a0a8597f)

### 🔧 Melhorias e Refatoração
- Nenhuma

### 📚 Documentação
- docs: Atualiza instruções para SEMPRE usar scripts quick (577c04ad)
- docs: Adiciona roadmap de próximos passos do sistema de budget hierárquico (2a4e725f)
- feat: Novo processador BTG completo e documentado (bff3771b)

### 🔄 Outras Mudanças
- chore: Limpeza de arquivos desnecessarios na raiz (c9ee4e40)
- revert(budget): Remove botões de aplicar média do frontend (30a6bbf0)
- chore(frontend): Instala dependências para drag & drop e color picker (f38bc1f0)
- chore(frontend): remove componente não utilizado BankFormModal (2b655174)
- chore: Remove tabela legacy upload_preview do banco (427b70a9)

---
