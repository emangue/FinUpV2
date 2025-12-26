"""
Upload Blueprint - Processamento temporário de novos arquivos
"""
from flask import Blueprint

upload_bp = Blueprint('upload', __name__, template_folder='templates')

from app.blueprints.upload import routes
