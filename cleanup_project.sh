#!/bin/bash

# 🧹 Script de Limpeza Automática - ProjetoFinancasV5
# Data: 16/01/2026
# Objetivo: Remover arquivos duplicados e organizar arquivos históricos

set -e

echo "🧹 Iniciando limpeza do projeto..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretório base
BASE_DIR="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5"
cd "$BASE_DIR"

# 1. REMOVER PIDS DUPLICADOS
echo -e "${YELLOW}📋 Etapa 1: Removendo PIDs duplicados${NC}"
if [ -f "backend 2.pid" ]; then
    rm "backend 2.pid"
    echo -e "${GREEN}✅ Removido: backend 2.pid${NC}"
fi

if [ -f "frontend 2.pid" ]; then
    rm "frontend 2.pid"
    echo -e "${GREEN}✅ Removido: frontend 2.pid${NC}"
fi

echo ""

# 2. CRIAR ESTRUTURA DE ARQUIVOS HISTÓRICOS
echo -e "${YELLOW}📁 Etapa 2: Criando estrutura de arquivos históricos${NC}"
mkdir -p _arquivos_historicos/scripts_migracao
mkdir -p _arquivos_historicos/docs_planejamento
mkdir -p _arquivos_historicos/testes
echo -e "${GREEN}✅ Estrutura criada${NC}"
echo ""

# 3. MOVER SCRIPTS DE MIGRAÇÃO
echo -e "${YELLOW}🔧 Etapa 3: Movendo scripts de migração${NC}"
scripts=(
    "add_categoria_geral_to_base_padroes.py"
    "apply_new_patterns.py"
    "migrate_fase6a_base_parcelas.py"
    "regenerate_patterns_preview.py"
    "regenerate_sql.py"
    "test_pattern_generator.py"
    "validate_final.py"
    "validate_patterns.py"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" _arquivos_historicos/scripts_migracao/
        echo -e "${GREEN}✅ Movido: $script${NC}"
    fi
done
echo ""

# 4. MOVER DOCUMENTAÇÕES DE PLANEJAMENTO
echo -e "${YELLOW}📄 Etapa 4: Movendo documentações de planejamento${NC}"
docs=(
    "ANALISE_IMPACTO_COMPLETA.md"
    "IMPLEMENTACAO_CAMPOS_COMPLETA.md"
    "INTEGRACAO_UPLOAD_COMPLETA.md"
    "MAPEAMENTO_UPLOAD_JOURNAL.md"
    "PLANO_ADICIONAR_CAMPOS_PREVIEW.md"
    "PLANO_INCREMENTAL_REFATORACAO.md"
    "PLANO_REFATORACAO_CATEGORIAS.md"
    "PROXIMOS_PASSOS_BUDGET.md"
    "RELATORIO_BASE_PADROES.md"
    "STATUS_ATUAL.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        mv "$doc" _arquivos_historicos/docs_planejamento/
        echo -e "${GREEN}✅ Movido: $doc${NC}"
    fi
done
echo ""

# 5. MOVER ARQUIVOS DE TESTE
echo -e "${YELLOW}🧪 Etapa 5: Movendo arquivos de teste${NC}"
if [ -f "arquivo_teste_n8n.json" ]; then
    mv "arquivo_teste_n8n.json" _arquivos_historicos/testes/
    echo -e "${GREEN}✅ Movido: arquivo_teste_n8n.json${NC}"
fi
echo ""

# 6. LIMPAR BUILD FRONTEND (OPCIONAL)
echo -e "${YELLOW}🗑️  Etapa 6: Limpar build do frontend? (y/n)${NC}"
read -p "Remover app_dev/frontend/.next (725 MB)? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "app_dev/frontend/.next" ]; then
        rm -rf app_dev/frontend/.next
        echo -e "${GREEN}✅ Removido: .next/ (build do frontend)${NC}"
    fi
else
    echo -e "${YELLOW}⏭️  Pulado: .next/ mantido${NC}"
fi
echo ""

# 7. RELATÓRIO FINAL
echo -e "${GREEN}🎉 Limpeza concluída!${NC}"
echo ""
echo "📊 Resumo:"
echo "  - PIDs duplicados removidos"
echo "  - Scripts movidos para _arquivos_historicos/scripts_migracao/"
echo "  - Docs movidos para _arquivos_historicos/docs_planejamento/"
echo "  - Testes movidos para _arquivos_historicos/testes/"
echo ""
echo "📁 Estrutura mantida:"
echo "  ✅ quick_start.sh, quick_stop.sh, backup_daily.sh"
echo "  ✅ check_version.py, fix_version.py"
echo "  ✅ README.md, VERSION.md, DATABASE_CONFIG.md"
echo "  ✅ .gitignore, .copilot-rules.md"
echo ""
echo -e "${GREEN}✨ Projeto limpo e organizado!${NC}"
