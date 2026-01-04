"""
Inicializa o banco de dados DEV
"""
import sys
from pathlib import Path

# Adiciona o diretório app_dev ao path
sys.path.insert(0, str(Path(__file__).parent))

from backend import create_app_dev, db

app = create_app_dev()

with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")
    print(f"📁 Local: {app.config['SQLALCHEMY_DATABASE_URI']}")
