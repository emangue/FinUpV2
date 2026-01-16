import sys
import os

# Adiciona o diretório atual ao path para permitir imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
# Importar todos os modelos para que o SQLAlchemy os reconheça
from app.domains.transactions.models import JournalEntry
from app.domains.users.models import User
from app.domains.budget.models import BudgetPlanning, BudgetGeral, BudgetCategoriaConfig, BudgetGeralHistorico
from app.domains.upload.history_models import UploadHistory
# Adicione outros modelos se necessário

print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")
print(f"Banco de dados: {engine.url}")
