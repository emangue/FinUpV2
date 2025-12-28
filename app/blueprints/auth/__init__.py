"""
Blueprint de Autenticação

Versão: 2.1.0-dev
Data: 28/12/2025

Gerencia autenticação de usuários (login/logout/register)
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

from . import routes
