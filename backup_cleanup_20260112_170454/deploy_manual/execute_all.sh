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
