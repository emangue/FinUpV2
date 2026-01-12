#!/bin/bash

# ==========================================
# DIAGNÓSTICO SSH COMPLETO
# Identifica e corrige problemas de conexão SSH
# ==========================================

echo "🔍 DIAGNÓSTICO SSH COMPLETO"
echo "=================================================="

# Configurações
SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[OK] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

echo ""
echo "1. 🔑 VERIFICANDO CHAVE SSH"
echo "----------------------------------------"

if [ -f "$SSH_KEY" ]; then
    log "Chave encontrada: $SSH_KEY"
    echo "Permissões da chave:"
    ls -la "$SSH_KEY"
    
    # Verificar permissões
    PERM=$(stat -f "%A" "$SSH_KEY" 2>/dev/null || stat -c "%a" "$SSH_KEY" 2>/dev/null)
    if [ "$PERM" = "600" ] || [ "$PERM" = "400" ]; then
        log "Permissões corretas: $PERM"
    else
        warn "Permissões incorretas: $PERM (deve ser 600)"
        echo "Corrigindo permissões..."
        chmod 600 "$SSH_KEY"
        log "Permissões corrigidas para 600"
    fi
else
    error "Chave SSH não encontrada: $SSH_KEY"
    echo ""
    echo "Opções para resolver:"
    echo "a) Criar nova chave: ssh-keygen -t rsa -b 4096 -f $SSH_KEY"
    echo "b) Usar chave existente diferente"
    echo "c) Configurar autenticação por senha"
    echo ""
    
    read -p "Quer que eu crie uma nova chave? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Criando nova chave SSH..."
        ssh-keygen -t rsa -b 4096 -f "$SSH_KEY" -N ""
        chmod 600 "$SSH_KEY"
        log "Nova chave criada: $SSH_KEY"
        
        echo ""
        warn "⚠️  IMPORTANTE: Você precisa adicionar a chave pública ao servidor!"
        echo "Chave pública:"
        echo "----------------------------------------"
        cat "${SSH_KEY}.pub"
        echo "----------------------------------------"
        echo ""
        echo "Execute no servidor:"
        echo "mkdir -p ~/.ssh && echo '$(cat ${SSH_KEY}.pub)' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
        echo ""
        read -p "Pressione ENTER após configurar a chave no servidor..."
    else
        error "Não é possível prosseguir sem chave SSH"
        exit 1
    fi
fi

echo ""
echo "2. 🌐 VERIFICANDO CONECTIVIDADE BÁSICA"
echo "----------------------------------------"

echo "Testando ping..."
if ping -c 3 148.230.78.91 >/dev/null 2>&1; then
    log "Servidor responde ao ping"
else
    error "Servidor não responde ao ping"
    echo "Verifique:"
    echo "- Conexão com internet"
    echo "- IP do servidor: 148.230.78.91"
    echo "- Firewall bloqueando ICMP"
fi

echo ""
echo "3. 🔌 VERIFICANDO PORTA SSH"
echo "----------------------------------------"

echo "Testando porta 22..."
if timeout 10 nc -z 148.230.78.91 22 2>/dev/null; then
    log "Porta 22 (SSH) está aberta"
else
    error "Porta 22 (SSH) não está acessível"
    echo "Possíveis causas:"
    echo "- SSH não está rodando no servidor"
    echo "- Firewall bloqueando porta 22"
    echo "- SSH rodando em porta diferente"
    echo ""
    echo "Testando porta 2222..."
    if timeout 5 nc -z 148.230.78.91 2222 2>/dev/null; then
        warn "SSH pode estar rodando na porta 2222"
    fi
fi

echo ""
echo "4. 🔐 TESTANDO CONEXÃO SSH"
echo "----------------------------------------"

echo "Teste básico SSH (timeout 10s)..."
if timeout 10 ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o BatchMode=yes "$SERVER" "echo 'SSH OK'" 2>/dev/null; then
    log "✅ SSH funcionando perfeitamente!"
    
    echo ""
    echo "5. 🧪 TESTES AVANÇADOS"
    echo "----------------------------------------"
    
    echo "Testando comando simples:"
    ssh -i "$SSH_KEY" "$SERVER" "uptime"
    
    echo ""
    echo "Testando sudo:"
    ssh -i "$SSH_KEY" "$SERVER" "sudo echo 'sudo OK'"
    
    echo ""
    log "🎉 SSH está funcionando corretamente!"
    log "Problema resolvido - scripts de deploy devem funcionar agora"
    
else
    error "❌ SSH não está funcionando"
    echo ""
    echo "Diagnóstico detalhado:"
    echo "----------------------------------------"
    
    echo "Tentativa com debug verbose:"
    timeout 10 ssh -v -i "$SSH_KEY" -o ConnectTimeout=5 "$SERVER" "echo test" 2>&1 | head -20
    
    echo ""
    echo "6. 🔧 OPÇÕES DE SOLUÇÃO"
    echo "----------------------------------------"
    
    echo "OPÇÃO A - Tentar com senha (sem chave):"
    echo "  ssh root@148.230.78.91"
    echo ""
    
    echo "OPÇÃO B - Verificar se chave está no servidor:"
    echo "  ssh root@148.230.78.91 'cat ~/.ssh/authorized_keys'"
    echo ""
    
    echo "OPÇÃO C - Adicionar chave ao servidor:"
    echo "  ssh-copy-id -i $SSH_KEY root@148.230.78.91"
    echo ""
    
    echo "OPÇÃO D - Reconfigurar SSH no servidor:"
    echo "  1. Conectar com senha: ssh root@148.230.78.91"
    echo "  2. Verificar config: cat /etc/ssh/sshd_config"
    echo "  3. Reiniciar SSH: systemctl restart ssh"
    echo ""
    
    read -p "Tentar conectar com senha (sem chave)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Tentando conexão com senha..."
        ssh root@148.230.78.91 "echo 'Conexão com senha funcionou!'"
        
        if [ $? -eq 0 ]; then
            log "✅ Conexão com senha funcionou!"
            echo ""
            echo "Para configurar a chave:"
            echo "ssh-copy-id -i $SSH_KEY root@148.230.78.91"
        fi
    fi
fi

echo ""
echo "7. 📋 RESUMO"
echo "=========================================="

if timeout 5 ssh -i "$SSH_KEY" -o BatchMode=yes "$SERVER" "echo test" >/dev/null 2>&1; then
    log "✅ SSH: Funcionando"
    log "✅ Deploy scripts: Devem funcionar"
else
    warn "❌ SSH: Não funcionando"
    warn "❌ Deploy scripts: Não vão funcionar"
    echo ""
    echo "PRÓXIMOS PASSOS:"
    echo "1. Resolver autenticação SSH"
    echo "2. Testar novamente: ./diagnose_ssh.sh"
    echo "3. Executar deploy: ./deploy_robust.sh"
fi

echo ""