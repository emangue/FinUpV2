"""
Models do domínio Auth.
Não cria novos models, apenas reusa User do domínio users.
"""
from app.domains.users.models import User

__all__ = ["User"]
