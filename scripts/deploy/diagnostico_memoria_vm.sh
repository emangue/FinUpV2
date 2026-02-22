#!/bin/bash

# Diagnóstico de memória na VM - identificar processos que mais consomem RAM
# Uso: ./scripts/deploy/diagnostico_memoria_vm.sh
# Ou na VM: bash -s < scripts/deploy/diagnostico_memoria_vm.sh (rodar localmente via SSH)

VM_HOST="${1:-minha-vps-hostinger}"

echo "🔍 DIAGNÓSTICO DE MEMÓRIA - $VM_HOST"
echo "========================================"

ssh -o ConnectTimeout=10 "$VM_HOST" '
echo "📊 Memória total:"
free -h
echo ""

echo "📋 Top 15 processos por uso de RAM (RSS):"
ps aux --sort=-rss 2>/dev/null | head -16
echo ""

echo "📋 Processos do projeto FinUp:"
ps aux | grep -E "finup|node|python|uvicorn|next" | grep -v grep
echo ""

echo "📋 PostgreSQL (se existir):"
ps aux | grep -E "postgres|postgresql" | grep -v grep
echo ""

echo "📋 Config PostgreSQL shared_buffers (se aplicável):"
grep -E "shared_buffers|work_mem" /etc/postgresql/*/main/postgresql.conf 2>/dev/null || \
  grep -rE "shared_buffers|work_mem" /var/lib/postgresql/*/main/*.conf 2>/dev/null || echo "   (não encontrado)"
echo ""

echo "📋 Serviços systemd ativos (finup, nginx, postgres):"
systemctl list-units --type=service --state=running 2>/dev/null | grep -E "finup|nginx|postgres" || true
'

echo ""
echo "💡 Se PostgreSQL shared_buffers estiver alto (ex: 2GB+), considere reduzir."
echo "💡 Múltiplos workers/instâncias do mesmo app duplicam uso de RAM."
