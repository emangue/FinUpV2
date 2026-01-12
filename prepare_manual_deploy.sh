#!/bin/bash

# ==========================================
# PREPARADOR DE DEPLOY MANUAL
# Prepara scripts para execução manual no servidor
# ==========================================

echo "📋 PREPARADOR DE DEPLOY MANUAL"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}$1${NC}"; }
warn() { echo -e "${YELLOW}$1${NC}"; }
info() { echo -e "${BLUE}$1${NC}"; }

log "Preparando scripts para execução manual..."

# Criar pasta de deploy
mkdir -p deploy_manual
cd deploy_manual

log "1. Copiando scripts..."
cp ../audit_server.sh .
cp ../clean_server.sh .
cp ../fresh_deploy.sh .

log "2. Criando script de execução sequencial..."

cat > execute_all.sh << 'EOF'
#!/bin/bash

# ==========================================
# EXECUTAR NO SERVIDOR
# Execute este script DIRETAMENTE no servidor VPS
# ==========================================

echo "🎯 DEPLOY LIMPO - EXECUÇÃO NO SERVIDOR"
echo "=================================================="
echo "IMPORTANTE: Execute este script como root no servidor!"
echo ""

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

echo "📋 Plano de execução:"
echo "  1. 🔍 Auditoria do estado atual"
echo "  2. 🧹 Limpeza completa"  
echo "  3. 🚀 Deploy fresco"
echo ""

read -p "Continuar? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operação cancelada"
    exit 0
fi

echo ""
echo "=== ETAPA 1: AUDITORIA ==="
if [ -f "audit_server.sh" ]; then
    chmod +x audit_server.sh
    ./audit_server.sh > audit_report.txt 2>&1
    echo "📄 Relatório salvo em audit_report.txt"
    echo ""
    echo "Ver relatório? [y/N]"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat audit_report.txt
    fi
else
    echo "❌ audit_server.sh não encontrado"
    exit 1
fi

echo ""
echo "=== ETAPA 2: LIMPEZA ==="
echo "⚠️  ATENÇÃO: Isso vai remover TUDO relacionado ao sistema de finanças"
echo "Digite 'CONFIRMO' para prosseguir:"
read confirmacao
if [ "$confirmacao" != "CONFIRMO" ]; then
    echo "Limpeza cancelada"
    exit 0
fi

if [ -f "clean_server.sh" ]; then
    chmod +x clean_server.sh
    ./clean_server.sh
else
    echo "❌ clean_server.sh não encontrado"
    exit 1
fi

echo ""
echo "=== ETAPA 3: DEPLOY FRESCO ==="
if [ -f "fresh_deploy.sh" ]; then
    chmod +x fresh_deploy.sh
    ./fresh_deploy.sh
else
    echo "❌ fresh_deploy.sh não encontrado"
    exit 1
fi

echo ""
echo "🎉 PROCESSO CONCLUÍDO!"
echo "Ver status: financas-status"
echo "Logs: tail -f /var/log/financas/backend.log"
EOF

chmod +x execute_all.sh

log "3. Criando instruções detalhadas..."

cat > INSTRUCOES.md << 'EOF'
# 🎯 INSTRUÇÕES PARA DEPLOY LIMPO

## 📋 Situação Atual
- Servidor com múltiplos deploys parciais
- Processos conflitantes rodando  
- Estrutura de pastas inconsistente
- Necessário começar do zero

## 🚀 Solução: Deploy Limpo Completo

### Passo 1: Copiar arquivos para o servidor

```bash
# No seu computador, copie a pasta deploy_manual para o servidor
scp -r deploy_manual root@148.230.78.91:/tmp/
```

### Passo 2: Executar no servidor

```bash
# Conectar no servidor
ssh root@148.230.78.91

# Ir para a pasta
cd /tmp/deploy_manual

# Executar script principal
sudo ./execute_all.sh
```

### Passo 3: Acompanhar execução

O script vai:
1. **Auditoria**: Mapear tudo que está no servidor
2. **Limpeza**: Remover TUDO relacionado ao sistema 
3. **Deploy**: Criar aplicação limpa do zero

### 📊 Resultado Esperado

- ✅ Backend FastAPI funcionando na porta 8000
- ✅ Aplicação web acessível externamente
- ✅ Logs organizados em /var/log/financas/
- ✅ Comando `financas-status` para monitoramento
- ✅ Arquitetura modular pronta para expansão

### 🌐 URLs após deploy

- **Sistema**: http://148.230.78.91:8000
- **API Docs**: http://148.230.78.91:8000/api/docs
- **Health Check**: http://148.230.78.91:8000/api/health

### 🔧 Comandos úteis no servidor

```bash
# Status completo
financas-status

# Ver logs
tail -f /var/log/financas/backend.log

# Restart se necessário
pkill uvicorn
cd /var/www/financas/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > /var/log/financas/backend.log 2>&1 &
```

## 🎯 Próximos Passos (após deploy limpo)

1. ✅ **Sistema base funcionando** (este deploy)
2. 🔐 Implementar autenticação JWT
3. 🗄️ Configurar banco SQLite
4. 📁 Sistema de upload de arquivos
5. ⚛️ Frontend Next.js
6. 📊 Dashboard e relatórios

## ⚠️ Importante

- Execute como **root** no servidor
- O script vai **deletar tudo** relacionado ao sistema
- Faça backup se tiver dados importantes
- Processo demora ~5-10 minutos

EOF

cat > RESUMO.txt << 'EOF'
=====================================
RESUMO DO DEPLOY LIMPO
=====================================

PROBLEMA:
- Servidor "poluído" com múltiplos deploys
- Processos conflitantes
- Estrutura inconsistente

SOLUÇÃO:
- Auditoria completa
- Limpeza total
- Deploy fresco e organizado

ARQUIVOS CRIADOS:
- audit_server.sh      (mapear estado atual)
- clean_server.sh      (limpeza completa)
- fresh_deploy.sh      (deploy organizado)
- execute_all.sh       (orquestrador)
- INSTRUCOES.md        (guia completo)

EXECUÇÃO:
1. scp -r deploy_manual root@148.230.78.91:/tmp/
2. ssh root@148.230.78.91
3. cd /tmp/deploy_manual && sudo ./execute_all.sh

RESULTADO:
- Sistema limpo e funcionando
- Backend FastAPI na porta 8000
- Pronto para desenvolvimento incremental

PRÓXIMO: Implementar funcionalidades uma por vez
=====================================
EOF

cd ..

log "4. Criando arquivo .tar.gz para facilitar transferência..."
tar -czf deploy_manual.tar.gz deploy_manual/

echo ""
log "============================================"
log "🎉 PREPARAÇÃO CONCLUÍDA!"
log "============================================"
echo ""

info "📁 Arquivos criados:"
echo "  deploy_manual/          - Pasta com todos os scripts"
echo "  deploy_manual.tar.gz    - Arquivo compactado"
echo ""

info "📋 Para executar o deploy limpo:"
echo ""
echo "OPÇÃO A - Pasta completa:"
echo "  scp -r deploy_manual root@148.230.78.91:/tmp/"
echo "  ssh root@148.230.78.91 'cd /tmp/deploy_manual && sudo ./execute_all.sh'"
echo ""

echo "OPÇÃO B - Arquivo compactado:"
echo "  scp deploy_manual.tar.gz root@148.230.78.91:/tmp/"
echo "  ssh root@148.230.78.91 'cd /tmp && tar -xzf deploy_manual.tar.gz && cd deploy_manual && sudo ./execute_all.sh'"
echo ""

warn "⚠️  IMPORTANTE:"
echo "  - Execute como root no servidor"
echo "  - Processo vai deletar TUDO do sistema atual"
echo "  - Resultado: sistema limpo e funcionando"
echo ""

info "📄 Leia INSTRUCOES.md para detalhes completos"

echo ""
log "🚀 Tudo pronto para deploy limpo!"