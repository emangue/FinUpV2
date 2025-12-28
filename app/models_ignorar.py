from sqlalchemy import Column, Integer, String
from app.models import Base, get_db_session

class IgnorarEstabelecimento(Base):
    __tablename__ = 'ignorar_estabelecimentos'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False, unique=True)
    tipo = Column(String, nullable=False, default='ambos')  # 'extrato', 'cartao', 'ambos'

def get_ignorar_estabelecimentos():
    session = get_db_session()
    try:
        return session.query(IgnorarEstabelecimento).all()
    finally:
        session.close()
