#!/bin/bash

# 📁 Script de Reorganização - ProjetoFinancasV5
# Organiza arquivos da raiz em estrutura modular

set -e  # Para em caso de erro

PROJECT_ROOT="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
cd "$PROJECT_ROOT"

echo "🔄 REORGANIZAÇÃO DO PROJETO - ProjetoFinancasV5"
echo "================================================"
echo ""

# 1. CRIAR BACKUP
echo "📦 1/5 - Criando backup..."
BACKUP_DIR="_backup_reorganize_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
ls -A | grep -v "^${BACKUP_DIR}$" | grep -v "^app_dev$" | grep -v "^_arquivos_historicos$" | xargs -I {} cp -r {} "$BACKUP_DIR/" 2>/dev/null || true
echo "   ✅ Backup criado: $BACKUP_DIR"
echo ""

# 2. CRIAR ESTRUTURA DE PASTAS
echo "📁 2/5 - Criando estrutura de pastas..."
mkdir -p docs/{deploy,architecture,features/investimentos,planning/reports}
mkdir -p scripts/{deploy,database,maintenance,testing,migration}
mkdir -p temp/{logs,pids}
echo "   ✅ Estrutura criada"
echo ""

# 3. MOVER DOCUMENTAÇÃO
echo "📚 3/5 - Movendo documentação..."

# Deploy
mv STATUS_DEPLOY.md docs/deploy/ 2>/dev/null || true
mv GUIA_DEPLOY_PRODUCAO.md docs/deploy/ 2>/dev/null || true
mv GUIA_SERVIDORES.md docs/deploy/ 2>/dev/null || true
mv PROXIMOS_PASSOS_DEPLOY.md docs/deploy/ 2>/dev/null || true
mv AUDITORIA_SERVIDOR_VPS.md docs/deploy/ 2>/dev/null || true

# Architecture
mv AUDITORIA_MODULARIDADE.md docs/architecture/ 2>/dev/null || true
mv RELATORIO_MODULARIDADE.md docs/architecture/ 2>/dev/null || true
mv DATABASE_CONFIG.md docs/architecture/ 2>/dev/null || true
mv PERFORMANCE_OPTIMIZATION_SUMMARY.md docs/architecture/ 2>/dev/null || true
mv SISTEMA_DEDUPLICACAO.md docs/architecture/ 2>/dev/null || true

# Features
mv PLANO_AUTENTICACAO.md docs/features/ 2>/dev/null || true
mv RESUMO_AUTENTICACAO.md docs/features/ 2>/dev/null || true
mv VALIDACAO_AUTENTICACAO.md docs/features/ 2>/dev/null || true
mv PROCESSADOR_MERCADOPAGO.md docs/features/ 2>/dev/null || true
mv PROPOSTA_MARCACOES_GENERICAS.md docs/features/ 2>/dev/null || true
mv TIPOS_GASTO_CONFIGURADOS.md docs/features/ 2>/dev/null || true

# Features - Investimentos
mv RELATORIO_INVESTIMENTOS_COMPLETO.md docs/features/investimentos/ 2>/dev/null || true
mv RELATORIO_INVESTIMENTOS_SPRINT1.md docs/features/investimentos/ 2>/dev/null || true
mv TODO_INVESTIMENTOS.md docs/features/investimentos/ 2>/dev/null || true
mv MELHORIAS_SIMULADOR.md docs/features/investimentos/ 2>/dev/null || true

# Planning
mv PROGRESSO_SPRINT3.md docs/planning/ 2>/dev/null || true
mv PLANO_ISOLAMENTO_DADOS.md docs/planning/ 2>/dev/null || true
mv PLANO_LIMPEZA_GITHUB.md docs/planning/ 2>/dev/null || true
mv RELATORIO_FASE1.md docs/planning/reports/ 2>/dev/null || true
mv RELATORIO_FINAL_LIMPEZA.md docs/planning/reports/ 2>/dev/null || true

echo "   ✅ Documentação organizada"
echo ""

# 4. MOVER SCRIPTS
echo "🔧 4/5 - Movendo scripts..."

# Deploy
mv quick_start.sh scripts/deploy/ 2>/dev/null || true
mv quick_stop.sh scripts/deploy/ 2>/dev/null || true
mv backup_daily.sh scripts/deploy/ 2>/dev/null || true
mv pausar_sistema_seguranca.sh scripts/deploy/ 2>/dev/null || true
mv reativar_sistema.sh scripts/deploy/ 2>/dev/null || true
mv audit_server.sh scripts/deploy/ 2>/dev/null || true

# Database
mv adicionar_user_id_investimentos.py scripts/database/ 2>/dev/null || true
mv copiar_dados_usuario.py scripts/database/ 2>/dev/null || true
mv copiar_investimentos_teste.py scripts/database/ 2>/dev/null || true
mv fix_categoria_geral_from_config.py scripts/database/ 2>/dev/null || true
mv fix_mp_dates.py scripts/database/ 2>/dev/null || true
mv limpar_grupos_planning_vazios.py scripts/database/ 2>/dev/null || true
mv popular_base_marcacoes.py scripts/database/ 2>/dev/null || true
mv popular_budget_geral_faltantes.py scripts/database/ 2>/dev/null || true
mv popular_grupos_faltantes_planning.py scripts/database/ 2>/dev/null || true

# Maintenance
mv check_version.py scripts/maintenance/ 2>/dev/null || true
mv fix_version.py scripts/maintenance/ 2>/dev/null || true
mv cleanup_project.sh scripts/maintenance/ 2>/dev/null || true
mv fix_all_fetch.sh scripts/maintenance/ 2>/dev/null || true

# Testing
mv test_hash_mercadopago.py scripts/testing/ 2>/dev/null || true
mv test_hash_standalone.py scripts/testing/ 2>/dev/null || true
mv test_mercadopago_processor.py scripts/testing/ 2>/dev/null || true
mv test_mercadopago_simple.py scripts/testing/ 2>/dev/null || true
mv test_pdf_processors_integration.py scripts/testing/ 2>/dev/null || true
mv test_token_flow.sh scripts/testing/ 2>/dev/null || true

# Migration
mv reimport_mp.py scripts/migration/ 2>/dev/null || true

echo "   ✅ Scripts organizados"
echo ""

# 5. MOVER TEMPORÁRIOS
echo "🗂️  5/5 - Movendo arquivos temporários..."

mv backend.log temp/logs/ 2>/dev/null || true
mv frontend.log temp/logs/ 2>/dev/null || true
mv backend.pid temp/pids/ 2>/dev/null || true
mv "backend 2.pid" temp/pids/ 2>/dev/null || true
mv frontend.pid temp/pids/ 2>/dev/null || true
mv "frontend 2.pid" temp/pids/ 2>/dev/null || true

echo "   ✅ Temporários movidos"
echo ""

# 6. CRIAR .gitignore para temp
echo "⚙️  Atualizando .gitignore..."
cat >> .gitignore << 'EOF'

# Arquivos temporários
temp/logs/*.log
temp/pids/*.pid
EOF
echo "   ✅ .gitignore atualizado"
echo ""

# 7. CRIAR README em docs/
echo "📝 Criando README de documentação..."
cat > docs/README.md << 'EOF'
# 📚 Documentação - FinUp

## Estrutura

### 📦 Deploy (`deploy/`)
Documentação sobre infraestrutura, deploy e servidor VPS.

### 🏗️ Arquitetura (`architecture/`)
Decisões arquiteturais, performance, banco de dados e modularidade.

### ✨ Features (`features/`)
Documentação de funcionalidades específicas (autenticação, investimentos, etc).

### 📋 Planejamento (`planning/`)
Sprints, relatórios de progresso e planejamentos futuros.

---

**Para voltar ao projeto:** [README principal](../README.md)
EOF
echo "   ✅ README de docs criado"
echo ""

# 8. ATUALIZAR README PRINCIPAL
echo "📝 Criando novo README principal..."
cat > README_NEW.md << 'EOF'
# 💰 FinUp - Sistema de Gestão Financeira

Sistema modular de controle financeiro pessoal com frontend Next.js e backend FastAPI.

## 🚀 Quick Start

```bash
# Iniciar sistema
./scripts/deploy/quick_start.sh

# Parar sistema
./scripts/deploy/quick_stop.sh
```

## 📁 Estrutura do Projeto

```
ProjetoFinancasV5/
├── app_dev/              # Aplicação (backend + frontend)
├── docs/                 # Documentação completa
├── scripts/              # Scripts auxiliares
├── temp/                 # Logs e PIDs temporários
└── _arquivos_historicos/ # Código legado
```

## 📚 Documentação

- **[Deploy](docs/deploy/)** - Infraestrutura e deploy
- **[Arquitetura](docs/architecture/)** - Design e decisões técnicas
- **[Features](docs/features/)** - Funcionalidades específicas
- **[Planejamento](docs/planning/)** - Sprints e roadmap

## 🌐 Acesso

- **App:** https://meufinup.com.br
- **API:** https://meufinup.com.br/api/v1
- **Docs:** https://meufinup.com.br/docs

## 👨‍💻 Desenvolvimento

Ver [docs/architecture/](docs/architecture/) para detalhes técnicos.

---

**Versão:** $(cat VERSION.md 2>/dev/null || echo "5.0")
EOF

echo "   ✅ README novo criado (README_NEW.md)"
echo ""

# RESUMO
echo ""
echo "✅ REORGANIZAÇÃO CONCLUÍDA!"
echo "=========================="
echo ""
echo "📊 Resumo:"
echo "  - Backup criado: $BACKUP_DIR"
echo "  - Documentação: docs/"
echo "  - Scripts: scripts/"
echo "  - Temporários: temp/"
echo ""
echo "📋 Próximos passos:"
echo "  1. Revisar estrutura: ls -la"
echo "  2. Testar scripts: ./scripts/deploy/quick_start.sh"
echo "  3. Atualizar README: mv README_NEW.md README.md"
echo "  4. Commit: git add . && git commit -m 'Reorganiza estrutura do projeto'"
echo ""
echo "⚠️  Se algo der errado, restaure: cp -r $BACKUP_DIR/* ."
echo ""
