#!/bin/bash

# ==========================================
# DETECTOR E CORRETOR DE PORTA SSH
# Encontra a porta SSH correta e ajusta configurações
# ==========================================

echo "🔍 DETECTOR DE PORTA SSH"
echo "=================================================="

# Configurações
SERVER_IP="148.230.78.91"
SERVER="root@$SERVER_IP"
SSH_KEY="$HOME/.ssh/financas_deploy"

# Portas comuns de SSH para testar
PORTAS=(22 2222 2022 22222 8022 1022 10022)

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[OK] $1${NC}"; }
warn() { echo -e "${YELLOW}[INFO] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }

echo ""
echo "1. 🔌 TESTANDO PORTAS SSH COMUNS"
echo "----------------------------------------"

PORTA_SSH=""

for porta in "${PORTAS[@]}"; do
    echo -n "Testando porta $porta... "
    
    # Testar se a porta está aberta (usando nc se disponível, ou telnet, ou python)
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w 3 "$SERVER_IP" "$porta" 2>/dev/null; then
            echo -e "${GREEN}ABERTA${NC}"
            
            # Testar se é realmente SSH
            echo -n "  Verificando se é SSH... "
            if echo "" | nc -w 3 "$SERVER_IP" "$porta" 2>/dev/null | grep -q "SSH"; then
                echo -e "${GREEN}✅ SSH ENCONTRADO!${NC}"
                PORTA_SSH="$porta"
                break
            else
                echo -e "${YELLOW}não é SSH${NC}"
            fi
        else
            echo -e "${RED}fechada${NC}"
        fi
    else
        # Fallback usando timeout e /dev/tcp se nc não estiver disponível
        if exec 3<>"/dev/tcp/$SERVER_IP/$porta" 2>/dev/null; then
            echo -e "${GREEN}ABERTA${NC}"
            exec 3>&-
            
            # Assumir que é SSH se a porta estiver aberta
            PORTA_SSH="$porta"
            warn "SSH assumido na porta $porta (nc não disponível para verificação)"
            break
        else
            echo -e "${RED}fechada${NC}"
        fi
    fi
done

if [ -z "$PORTA_SSH" ]; then
    error "❌ Nenhuma porta SSH encontrada"
    echo ""
    echo "Possíveis soluções:"
    echo "1. SSH pode estar em porta customizada"
    echo "2. Firewall bloqueando conexões"
    echo "3. Servidor SSH não está rodando"
    echo ""
    
    read -p "Quer testar uma porta específica? Digite a porta (ou ENTER para pular): " porta_custom
    if [ ! -z "$porta_custom" ]; then
        PORTA_SSH="$porta_custom"
        warn "Usando porta customizada: $porta_custom"
    else
        error "Não é possível continuar sem porta SSH"
        exit 1
    fi
fi

log "✅ Porta SSH encontrada: $PORTA_SSH"

echo ""
echo "2. 🔐 TESTANDO AUTENTICAÇÃO SSH"
echo "----------------------------------------"

# Função para testar SSH em uma porta específica
test_ssh() {
    local porta="$1"
    local method="$2"
    
    case "$method" in
        "key")
            if [ -f "$SSH_KEY" ]; then
                ssh -i "$SSH_KEY" -p "$porta" -o ConnectTimeout=5 -o BatchMode=yes "$SERVER" "echo 'SSH OK'" 2>/dev/null
            else
                return 1
            fi
            ;;
        "password")
            ssh -p "$porta" -o ConnectTimeout=5 -o PasswordAuthentication=yes -o PubkeyAuthentication=no "$SERVER" "echo 'SSH OK'" 2>/dev/null
            ;;
        "agent")
            ssh -p "$porta" -o ConnectTimeout=5 "$SERVER" "echo 'SSH OK'" 2>/dev/null
            ;;
    esac
}

# Testar métodos de autenticação
METODO_SSH=""

echo "Testando autenticação por chave..."
if test_ssh "$PORTA_SSH" "key"; then
    log "✅ Autenticação por chave funcionando!"
    METODO_SSH="key"
else
    warn "❌ Chave SSH não funciona"
    
    echo ""
    echo "Testando autenticação por senha..."
    echo "Será solicitada a senha do servidor..."
    
    if test_ssh "$PORTA_SSH" "password"; then
        log "✅ Autenticação por senha funcionando!"
        METODO_SSH="password"
        
        echo ""
        warn "⚠️  Configurando chave SSH automaticamente..."
        
        # Configurar chave SSH
        if [ -f "$SSH_KEY" ]; then
            echo "Copiando chave SSH para o servidor..."
            if ssh-copy-id -i "$SSH_KEY" -p "$PORTA_SSH" "$SERVER" 2>/dev/null; then
                log "✅ Chave SSH configurada!"
                METODO_SSH="key"
            else
                warn "Configuração manual da chave necessária"
            fi
        fi
    else
        error "❌ Nenhum método de autenticação funciona"
        exit 1
    fi
fi

echo ""
echo "3. 🔧 AJUSTANDO SCRIPTS DE DEPLOY"
echo "----------------------------------------"

if [ "$PORTA_SSH" != "22" ]; then
    warn "Porta SSH não é padrão ($PORTA_SSH). Ajustando scripts..."
    
    # Ajustar scripts de deploy para usar a porta correta
    SCRIPTS_PARA_AJUSTAR=(
        "deploy_robust.sh"
        "deploy_final.sh"
        "deploy_simple.sh"
        "deploy_via_scp.sh"
        "deploy_clean_orchestrator.sh"
    )
    
    for script in "${SCRIPTS_PARA_AJUSTAR[@]}"; do
        if [ -f "$script" ]; then
            echo "Ajustando $script..."
            
            # Backup
            cp "$script" "${script}.backup"
            
            # Substituir comandos SSH para incluir porta
            sed -i.bak "s/ssh -i \"\$SSH_KEY\"/ssh -i \"\$SSH_KEY\" -p $PORTA_SSH/g" "$script" 2>/dev/null || \
            sed -i "s/ssh -i \"\$SSH_KEY\"/ssh -i \"\$SSH_KEY\" -p $PORTA_SSH/g" "$script" 2>/dev/null
            
            sed -i.bak "s/scp -i \"\$SSH_KEY\"/scp -i \"\$SSH_KEY\" -P $PORTA_SSH/g" "$script" 2>/dev/null || \
            sed -i "s/scp -i \"\$SSH_KEY\"/scp -i \"\$SSH_KEY\" -P $PORTA_SSH/g" "$script" 2>/dev/null
            
            log "✅ $script ajustado para porta $PORTA_SSH"
        fi
    done
fi

echo ""
echo "4. ✅ TESTANDO CONFIGURAÇÃO FINAL"
echo "----------------------------------------"

# Teste final completo
echo "Testando comando simples..."
if ssh -i "$SSH_KEY" -p "$PORTA_SSH" -o ConnectTimeout=5 "$SERVER" "echo 'Teste simples OK'"; then
    log "✅ Comando simples funcionando"
else
    error "❌ Comando simples falhando"
    exit 1
fi

echo ""
echo "Testando comando com sudo..."
if ssh -i "$SSH_KEY" -p "$PORTA_SSH" "$SERVER" "sudo echo 'Sudo OK'"; then
    log "✅ Sudo funcionando"
else
    warn "⚠️  Sudo pode precisar de senha"
fi

echo ""
echo "5. 📋 CRIANDO CONFIGURAÇÃO SSH"
echo "----------------------------------------"

# Criar ou atualizar ~/.ssh/config
SSH_CONFIG="$HOME/.ssh/config"

if grep -q "Host.*148.230.78.91\|Host.*financas-server" "$SSH_CONFIG" 2>/dev/null; then
    warn "Configuração SSH já existe, atualizando..."
else
    warn "Criando nova configuração SSH..."
fi

# Adicionar/atualizar configuração
cat >> "$SSH_CONFIG" << EOF

# Sistema de Finanças V4 - Server
Host financas-server
    HostName 148.230.78.91
    Port $PORTA_SSH
    User root
    IdentityFile $SSH_KEY
    IdentitiesOnly yes
    ConnectTimeout 10
    ServerAliveInterval 30
    ServerAliveCountMax 3
EOF

chmod 600 "$SSH_CONFIG"
log "✅ Configuração SSH criada/atualizada"

echo ""
echo "============================================"
echo "🎉 CONFIGURAÇÃO SSH CONCLUÍDA!"
echo "============================================"
echo ""

log "📊 Resumo da configuração:"
echo "  Servidor: $SERVER_IP"
echo "  Porta SSH: $PORTA_SSH"
echo "  Autenticação: $METODO_SSH"
echo "  Chave: $SSH_KEY"
echo ""

log "🔧 Comandos para usar:"
echo "  Conexão direta: ssh financas-server"
echo "  Ou: ssh -i $SSH_KEY -p $PORTA_SSH $SERVER"
echo ""

log "🚀 Scripts de deploy ajustados:"
echo "  ./deploy_robust.sh"
echo "  ./deploy_clean_orchestrator.sh"
echo ""

# Teste final de deploy
warn "🧪 Testando script de deploy..."
if timeout 10 ssh -i "$SSH_KEY" -p "$PORTA_SSH" "$SERVER" "echo 'Deploy test OK'" >/dev/null 2>&1; then
    log "✅ Scripts de deploy devem funcionar!"
    echo ""
    warn "Pronto para executar:"
    echo "  ./deploy_clean_orchestrator.sh"
else
    error "❌ Ainda há problemas com deploy"
fi

echo ""