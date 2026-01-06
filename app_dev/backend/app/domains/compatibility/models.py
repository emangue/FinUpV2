from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class BankFormatCompatibility(Base):
    __tablename__ = "bank_format_compatibility"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    status = Column(String, nullable=False)  # OK, WIP, TBD
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
