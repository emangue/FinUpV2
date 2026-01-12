#!/bin/bash

# ==========================================
# CORRETOR AUTOMÁTICO SSH
# Corrige problemas comuns de SSH automaticamente
# ==========================================

echo "🔧 CORRETOR AUTOMÁTICO SSH"
echo "=================================================="

# Configurações
SERVER="root@148.230.78.91"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[FIX] $1${NC}"; }
warn() { echo -e "${YELLOW}[INFO] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

echo ""
warn "Este script vai tentar corrigir problemas comuns de SSH"
echo ""

echo "1. 🔑 CONFIGURANDO CHAVE SSH"
echo "----------------------------------------"

# Criar diretório .ssh se não existir
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# Se chave não existe, criar
if [ ! -f "$SSH_KEY" ]; then
    log "Criando nova chave SSH..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY" -N "" -q
    log "✅ Chave criada: $SSH_KEY"
fi

# Corrigir permissões
chmod 600 "$SSH_KEY" 2>/dev/null
if [ -f "${SSH_KEY}.pub" ]; then
    chmod 644 "${SSH_KEY}.pub"
fi
log "✅ Permissões corrigidas"

echo ""
echo "2. 🌐 TESTANDO CONECTIVIDADE"
echo "----------------------------------------"

# Teste básico de rede
if ! ping -c 1 148.230.78.91 >/dev/null 2>&1; then
    error "❌ Servidor não responde ao ping"
    echo "Verifique sua conexão de internet"
    exit 1
fi
log "✅ Servidor responde ao ping"

# Teste porta SSH
if ! timeout 5 nc -z 148.230.78.91 22 2>/dev/null; then
    error "❌ Porta SSH (22) não acessível"
    echo "SSH pode não estar rodando no servidor"
    exit 1
fi
log "✅ Porta SSH acessível"

echo ""
echo "3. 🔐 CONFIGURANDO AUTENTICAÇÃO"
echo "----------------------------------------"

# Verificar se já funciona com a chave
if timeout 5 ssh -i "$SSH_KEY" -o ConnectTimeout=3 -o BatchMode=yes "$SERVER" "echo test" >/dev/null 2>&1; then
    log "✅ SSH com chave já funciona!"
    
    # Testar deploy script
    echo ""
    log "🧪 Testando deploy script..."
    if timeout 10 ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SERVER" "echo 'Deploy test OK'" >/dev/null 2>&1; then
        log "✅ Deploy scripts devem funcionar!"
        exit 0
    fi
fi

warn "Chave SSH não está configurada no servidor"
echo ""

echo "Opções de configuração:"
echo "A) Tentar ssh-copy-id (automático)"
echo "B) Conectar com senha e configurar manualmente"  
echo "C) Mostrar chave para configuração manual"
echo ""

read -p "Escolha uma opção [A/B/C]: " -n 1 -r opcao
echo
echo ""

case $opcao in
    [Aa])
        log "Tentando ssh-copy-id..."
        if ssh-copy-id -i "$SSH_KEY" "$SERVER" 2>/dev/null; then
            log "✅ Chave copiada com sucesso!"
        else
            warn "ssh-copy-id falhou, tentando método manual..."
            opcao="B"
        fi
        ;;
esac

case $opcao in
    [Bb])
        log "Configuração manual via conexão com senha..."
        echo ""
        warn "Você precisará digitar a senha do servidor"
        echo ""
        
        # Obter chave pública
        PUB_KEY=$(cat "${SSH_KEY}.pub")
        
        echo "Executando comandos no servidor..."
        ssh "$SERVER" "
            mkdir -p ~/.ssh
            chmod 700 ~/.ssh
            echo '$PUB_KEY' >> ~/.ssh/authorized_keys
            chmod 600 ~/.ssh/authorized_keys
            # Remover duplicatas
            sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
            mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys
            echo 'Chave SSH configurada com sucesso!'
        "
        
        if [ $? -eq 0 ]; then
            log "✅ Configuração manual concluída!"
        else
            error "❌ Configuração manual falhou"
            opcao="C"
        fi
        ;;
esac

case $opcao in
    [Cc])
        log "Configuração manual necessária"
        echo ""
        warn "Execute os seguintes comandos NO SERVIDOR:"
        echo "==========================================="
        echo "mkdir -p ~/.ssh"
        echo "chmod 700 ~/.ssh"
        echo "cat >> ~/.ssh/authorized_keys << 'EOF'"
        cat "${SSH_KEY}.pub"
        echo "EOF"
        echo "chmod 600 ~/.ssh/authorized_keys"
        echo "==========================================="
        echo ""
        read -p "Pressione ENTER após executar os comandos no servidor..."
        ;;
esac

echo ""
echo "4. ✅ VERIFICAÇÃO FINAL"
echo "----------------------------------------"

# Teste final
echo "Testando conexão SSH..."
if timeout 10 ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SERVER" "echo 'SSH funcionando perfeitamente!'" 2>/dev/null; then
    log "🎉 SSH CONFIGURADO COM SUCESSO!"
    echo ""
    log "✅ Chave SSH funcionando"
    log "✅ Conexão estabelecida" 
    log "✅ Deploy scripts podem ser executados"
    echo ""
    
    warn "Comandos para testar deploy:"
    echo "  ./deploy_robust.sh"
    echo "  ./deploy_clean_orchestrator.sh"
    echo ""
    
    # Teste rápido de comando
    log "Testando comando sudo no servidor..."
    if ssh -i "$SSH_KEY" "$SERVER" "sudo echo 'sudo OK'" 2>/dev/null; then
        log "✅ Sudo funcionando"
    else
        warn "⚠️  Problema com sudo - pode precisar de senha"
    fi
    
else
    error "❌ SSH ainda não está funcionando"
    echo ""
    echo "Diagnóstico adicional:"
    echo "----------------------"
    
    # Debug detalhado
    echo "Teste com verbose:"
    ssh -v -i "$SSH_KEY" -o ConnectTimeout=3 "$SERVER" "echo test" 2>&1 | grep -E "(debug|ERROR|Failed|Permission)"
    
    echo ""
    warn "Possíveis soluções:"
    echo "1. Verificar se sshd está rodando: sudo systemctl status ssh"
    echo "2. Verificar configuração SSH: sudo nano /etc/ssh/sshd_config"
    echo "3. Reiniciar SSH: sudo systemctl restart ssh"
    echo "4. Verificar logs: sudo tail -f /var/log/auth.log"
    echo ""
    
    error "Resolva os problemas acima e execute novamente"
    exit 1
fi

echo ""
log "🎯 SSH PRONTO PARA DEPLOY!"