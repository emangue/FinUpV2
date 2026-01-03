#!/bin/bash

# 🔧 Script de Configuração Git Interativo
# Configura identidade, credential helper e repositório remoto

set -e  # Parar se houver erro

echo "🔧 Configuração Git - ProjetoFinancasV3"
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir status
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "GIT_CONFIG.md" ]; then
    print_error "Execute este script da raiz do projeto!"
    exit 1
fi

echo "1. Verificando configurações atuais..."
echo "----------------------------------------"

# Verificar nome de usuário
CURRENT_USER=$(git config user.name || echo "")
CURRENT_EMAIL=$(git config user.email || echo "")
CURRENT_HELPER=$(git config credential.helper || echo "")
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")

if [ -n "$CURRENT_USER" ]; then
    print_status "Nome configurado: $CURRENT_USER"
else
    print_warning "Nome de usuário NÃO configurado"
fi

if [ -n "$CURRENT_EMAIL" ]; then
    print_status "Email configurado: $CURRENT_EMAIL"
else
    print_warning "Email NÃO configurado"
fi

if [ -n "$CURRENT_HELPER" ]; then
    print_status "Credential helper: $CURRENT_HELPER"
else
    print_warning "Credential helper NÃO configurado"
fi

if [ -n "$CURRENT_REMOTE" ]; then
    print_status "Repositório remoto: $CURRENT_REMOTE"
else
    print_warning "Repositório remoto NÃO configurado"
fi

echo ""
echo "2. Configuração"
echo "----------------------------------------"

# Perguntar se quer configurar nome
if [ -z "$CURRENT_USER" ]; then
    read -p "Digite seu nome completo: " USER_NAME
    if [ -n "$USER_NAME" ]; then
        git config user.name "$USER_NAME"
        print_status "Nome configurado: $USER_NAME"
    fi
else
    read -p "Manter nome atual ($CURRENT_USER)? [S/n]: " KEEP_NAME
    if [[ $KEEP_NAME =~ ^[Nn]$ ]]; then
        read -p "Digite seu nome completo: " USER_NAME
        git config user.name "$USER_NAME"
        print_status "Nome atualizado: $USER_NAME"
    fi
fi

# Perguntar se quer configurar email
if [ -z "$CURRENT_EMAIL" ]; then
    read -p "Digite seu email: " USER_EMAIL
    if [ -n "$USER_EMAIL" ]; then
        git config user.email "$USER_EMAIL"
        print_status "Email configurado: $USER_EMAIL"
    fi
else
    read -p "Manter email atual ($CURRENT_EMAIL)? [S/n]: " KEEP_EMAIL
    if [[ $KEEP_EMAIL =~ ^[Nn]$ ]]; then
        read -p "Digite seu email: " USER_EMAIL
        git config user.email "$USER_EMAIL"
        print_status "Email atualizado: $USER_EMAIL"
    fi
fi

# Configurar credential helper se não existir
if [ -z "$CURRENT_HELPER" ]; then
    echo ""
    print_info "Configurando credential helper..."
    
    # Detectar sistema operacional
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        git config --global credential.helper osxkeychain
        print_status "Credential helper configurado: osxkeychain (macOS Keychain)"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Escolha o credential helper:"
        echo "1. cache (temporário - 15min)"
        echo "2. cache --timeout=3600 (temporário - 1 hora)"
        echo "3. store (permanente - armazena em texto plano)"
        read -p "Opção [1-3]: " HELPER_OPTION
        
        case $HELPER_OPTION in
            1)
                git config --global credential.helper cache
                print_status "Credential helper: cache (15 minutos)"
                ;;
            2)
                git config --global credential.helper 'cache --timeout=3600'
                print_status "Credential helper: cache (1 hora)"
                ;;
            3)
                git config --global credential.helper store
                print_warning "Credential helper: store (⚠️ credenciais em texto plano)"
                ;;
            *)
                git config --global credential.helper cache
                print_status "Credential helper: cache (padrão - 15 minutos)"
                ;;
        esac
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        git config --global credential.helper wincred
        print_status "Credential helper configurado: wincred (Windows Credential Manager)"
    else
        print_warning "Sistema operacional não detectado. Configure manualmente."
    fi
fi

# Configurar repositório remoto
if [ -z "$CURRENT_REMOTE" ]; then
    echo ""
    read -p "Deseja configurar repositório remoto? [S/n]: " CONFIG_REMOTE
    
    if [[ ! $CONFIG_REMOTE =~ ^[Nn]$ ]]; then
        echo "Escolha o tipo de autenticação:"
        echo "1. HTTPS (recomendado - usa token)"
        echo "2. SSH (requer chave SSH configurada)"
        read -p "Opção [1-2]: " AUTH_TYPE
        
        read -p "Digite o usuário/organização do GitHub: " GH_USER
        read -p "Digite o nome do repositório: " GH_REPO
        
        if [ "$AUTH_TYPE" == "2" ]; then
            REMOTE_URL="git@github.com:$GH_USER/$GH_REPO.git"
        else
            REMOTE_URL="https://github.com/$GH_USER/$GH_REPO.git"
        fi
        
        git remote add origin "$REMOTE_URL"
        print_status "Repositório remoto configurado: $REMOTE_URL"
        
        if [ "$AUTH_TYPE" == "1" ]; then
            echo ""
            print_warning "IMPORTANTE: GitHub não aceita senha da conta!"
            print_info "No primeiro push, use TOKEN DE ACESSO PESSOAL como senha"
            print_info "Criar token em: https://github.com/settings/tokens"
        fi
    fi
else
    read -p "Manter remoto atual ($CURRENT_REMOTE)? [S/n]: " KEEP_REMOTE
    if [[ $KEEP_REMOTE =~ ^[Nn]$ ]]; then
        git remote remove origin
        
        echo "Escolha o tipo de autenticação:"
        echo "1. HTTPS (recomendado - usa token)"
        echo "2. SSH (requer chave SSH configurada)"
        read -p "Opção [1-2]: " AUTH_TYPE
        
        read -p "Digite o usuário/organização do GitHub: " GH_USER
        read -p "Digite o nome do repositório: " GH_REPO
        
        if [ "$AUTH_TYPE" == "2" ]; then
            REMOTE_URL="git@github.com:$GH_USER/$GH_REPO.git"
        else
            REMOTE_URL="https://github.com/$GH_USER/$GH_REPO.git"
        fi
        
        git remote add origin "$REMOTE_URL"
        print_status "Repositório remoto atualizado: $REMOTE_URL"
    fi
fi

echo ""
echo "3. Resumo da Configuração"
echo "----------------------------------------"

# Mostrar configurações finais
FINAL_USER=$(git config user.name)
FINAL_EMAIL=$(git config user.email)
FINAL_HELPER=$(git config credential.helper)
FINAL_REMOTE=$(git remote get-url origin 2>/dev/null || echo "Não configurado")

echo "Nome:              $FINAL_USER"
echo "Email:             $FINAL_EMAIL"
echo "Credential Helper: $FINAL_HELPER"
echo "Repositório:       $FINAL_REMOTE"

echo ""
echo "4. Próximos Passos"
echo "----------------------------------------"

if [ "$FINAL_REMOTE" != "Não configurado" ]; then
    print_info "Para fazer o primeiro push:"
    echo "  git push -u origin main"
    echo ""
    
    if [[ $FINAL_REMOTE == https* ]]; then
        print_warning "No primeiro push, digite:"
        echo "  - Username: seu-usuario-github"
        echo "  - Password: seu-token-de-acesso-pessoal"
        echo ""
        print_info "Criar token em: https://github.com/settings/tokens"
        echo "  Marcar: repo (full control of private repositories)"
    fi
    
    echo ""
    print_status "Após o primeiro push, as credenciais serão salvas!"
    print_status "Próximos pushes não pedirão senha 🎉"
else
    print_info "Configure o repositório remoto manualmente:"
    echo "  git remote add origin <URL>"
fi

echo ""
print_status "Configuração concluída!"
echo ""
echo "Para mais detalhes, consulte: GIT_CONFIG.md"
