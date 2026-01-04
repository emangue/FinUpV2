"""
Routers do backend FastAPI
"""
from . import auth, dashboard, marcacoes, compatibility, cartoes, exclusoes, users, upload, upload_classifier

__all__ = ["auth", "dashboard", "marcacoes", "compatibility", "cartoes", "exclusoes", "users", "upload", "upload_classifier"]
