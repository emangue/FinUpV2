#!/bin/bash

# 🛑 SCRIPT PARA PAUSAR O SISTEMA POR SEGURANÇA
# Data: 21/01/2026
# Motivo: Evitar exposição de dados sem SSL/Firewall

echo "🛑 PAUSANDO SISTEMA FINUP POR SEGURANÇA..."
echo ""

ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 << 'ENDSSH'

echo "⏸️  Parando Frontend (Next.js)..."
systemctl stop finup-frontend
sleep 1

echo "⏸️  Parando Backend (FastAPI)..."
systemctl stop finup-backend
sleep 1

echo "⏸️  Parando Nginx..."
systemctl stop nginx
sleep 1

echo ""
echo "📊 Status dos serviços:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

systemctl is-active finup-frontend > /dev/null && echo "❌ Frontend: AINDA ATIVO" || echo "✅ Frontend: PARADO"
systemctl is-active finup-backend > /dev/null && echo "❌ Backend: AINDA ATIVO" || echo "✅ Backend: PARADO"
systemctl is-active nginx > /dev/null && echo "❌ Nginx: AINDA ATIVO" || echo "✅ Nginx: PARADO"

echo ""
echo "🔒 PostgreSQL continua rodando (apenas localhost)"
systemctl is-active postgresql > /dev/null && echo "✅ PostgreSQL: RODANDO (seguro)" || echo "⚠️  PostgreSQL: PARADO"

echo ""
echo "✅ SISTEMA PAUSADO COM SUCESSO!"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Dados estão seguros no PostgreSQL (localhost)"
echo "   - Servidor não está mais acessível publicamente"
echo "   - Para retomar: ./reativar_sistema.sh"

ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 Sistema FinUp pausado com sucesso!"
echo "📍 IP 148.230.78.91 não está mais respondendo"
echo ""
