#!/bin/bash

# 🚀 SCRIPT PARA REATIVAR O SISTEMA
# Data: 21/01/2026
# Usar quando retomar o desenvolvimento (após implementar SSL/Firewall)

echo "🚀 REATIVANDO SISTEMA FINUP..."
echo ""

ssh -i ~/.ssh/id_rsa_hostinger root@148.230.78.91 << 'ENDSSH'

echo "▶️  Iniciando Backend (FastAPI)..."
systemctl start finup-backend
sleep 3

echo "▶️  Iniciando Frontend (Next.js)..."
systemctl start finup-frontend
sleep 3

echo "▶️  Iniciando Nginx..."
systemctl start nginx
sleep 2

echo ""
echo "📊 Status dos serviços:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

systemctl is-active finup-backend > /dev/null && echo "✅ Backend: ATIVO" || echo "❌ Backend: FALHOU"
systemctl is-active finup-frontend > /dev/null && echo "✅ Frontend: ATIVO" || echo "❌ Frontend: FALHOU"
systemctl is-active nginx > /dev/null && echo "✅ Nginx: ATIVO" || echo "❌ Nginx: FALHOU"

echo ""
echo "🌐 URLs de acesso:"
echo "   - App: http://148.230.78.91"
echo "   - API: http://148.230.78.91/api/v1"
echo "   - Docs: http://148.230.78.91/docs"
echo ""

ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Sistema FinUp reativado!"
echo ""
echo "⚠️  LEMBRE-SE:"
echo "   - Sistema ainda sem SSL/HTTPS (dados em texto claro)"
echo "   - Firewall ainda desabilitado (todas portas expostas)"
echo "   - IMPLEMENTE SEGURANÇA ANTES DE USO PROLONGADO!"
echo ""
