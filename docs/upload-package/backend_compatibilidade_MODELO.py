from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class BankFormatCompatibility(Base):
    """  
    Modelo de Compatibilidade de Formatos por Banco
    
    Estrutura Matricial: 1 linha = 1 banco com colunas para cada formato
    - csv_status: Status do formato CSV
    - excel_status: Status do formato Excel
    - pdf_status: Status do formato PDF
    - ofx_status: Status do formato OFX
    
    Status possíveis: OK, WIP, TBD
    """
    __tablename__ = "bank_format_compatibility"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, nullable=False, unique=True)
    csv_status = Column(String, nullable=False, default='TBD')  # OK, WIP, TBD
    excel_status = Column(String, nullable=False, default='TBD')
    pdf_status = Column(String, nullable=False, default='TBD')
    ofx_status = Column(String, nullable=False, default='TBD')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
