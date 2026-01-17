"""
Screen Visibility Model
Controla quais telas aparecem para diferentes tipos de usuários
Status: P (Production - todos), A (Admin - só admin), D (Development - só admin)
"""
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class ScreenVisibility(Base):
    """Modelo de controle de visibilidade de telas"""
    __tablename__ = "screen_visibility"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    screen_key = Column(String, unique=True, nullable=False, index=True)  # Ex: 'dashboard', 'transactions'
    screen_name = Column(String, nullable=False)  # Nome exibido na sidebar
    status = Column(String, nullable=False, default='P')  # P/A/D
    icon = Column(String, nullable=True)  # Nome do ícone lucide-react
    display_order = Column(Integer, default=0)  # Ordem de exibição
    parent_key = Column(String, nullable=True)  # Chave do pai (para hierarquia)
    url = Column(String, nullable=True)  # URL completa da rota
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('P', 'A', 'D')", name="check_status_values"),
    )

    def __repr__(self):
        return f"<ScreenVisibility(screen_key='{self.screen_key}', screen_name='{self.screen_name}', status='{self.status}')>"
