"""
Configuração do banco de dados SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

# Cria engine - usa DATABASE_URL (suporta SQLite e PostgreSQL)
# SQLite: sqlite:///path/to/database.db
# PostgreSQL: postgresql://user:pass@host:port/dbname
connect_args = {}
if not settings.is_postgres:
    # SQLite precisa do check_same_thread=False
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency para injetar sessão do banco nas rotas
    
    Usage:
        @router.get("/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
