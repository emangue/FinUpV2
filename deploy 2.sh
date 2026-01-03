#!/bin/bash
# Script auxiliar para deploy com Python do venv

VENV_PYTHON="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python"
SCRIPT_DIR="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/scripts"

# Validar apenas
if [ "$1" = "validate" ]; then
    echo "🔍 Executando validações..."
    $VENV_PYTHON $SCRIPT_DIR/deploy_dev_to_prod.py --validate-only
    exit $?
fi

# Verificar separação
if [ "$1" = "verify" ]; then
    echo "🔍 Verificando separação dev vs prod..."
    $VENV_PYTHON $SCRIPT_DIR/verify_separation.py
    exit $?
fi

# Deploy completo
if [ "$1" = "deploy" ]; then
    echo "🚀 Iniciando deploy..."
    $VENV_PYTHON $SCRIPT_DIR/deploy_dev_to_prod.py
    exit $?
fi

# Rollback - listar
if [ "$1" = "rollback-list" ]; then
    echo "📦 Listando backups..."
    $VENV_PYTHON $SCRIPT_DIR/rollback_deployment.py --list
    exit $?
fi

# Rollback - restaurar
if [ "$1" = "rollback" ]; then
    if [ -z "$2" ]; then
        echo "♻️  Restaurando backup mais recente..."
        $VENV_PYTHON $SCRIPT_DIR/rollback_deployment.py
    else
        echo "♻️  Restaurando backup: $2"
        $VENV_PYTHON $SCRIPT_DIR/rollback_deployment.py --restore "$2"
    fi
    exit $?
fi

# Help
echo "📖 Uso do script de deploy:"
echo ""
echo "  ./deploy.sh validate         # Apenas validações"
echo "  ./deploy.sh verify           # Verificar separação dev vs prod"
echo "  ./deploy.sh deploy           # Deploy completo (interativo)"
echo "  ./deploy.sh rollback-list    # Lista backups disponíveis"
echo "  ./deploy.sh rollback         # Rollback para último backup"
echo "  ./deploy.sh rollback <file>  # Rollback para backup específico"
echo ""
echo "Exemplos:"
echo "  ./deploy.sh validate"
echo "  ./deploy.sh verify"
echo "  ./deploy.sh deploy"
echo "  ./deploy.sh rollback-list"
echo "  ./deploy.sh rollback app_backup_20251228_143025.tar.gz"
