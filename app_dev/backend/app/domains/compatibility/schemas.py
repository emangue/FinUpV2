from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

StatusType = Literal["OK", "WIP", "TBD"]

class BankCompatibilityBase(BaseModel):
    bank_name: str
    file_format: str
    status: StatusType

class BankCompatibilityCreate(BankCompatibilityBase):
    pass

class BankCompatibilityUpdate(BaseModel):
    bank_name: Optional[str] = None
    file_format: Optional[str] = None
    status: Optional[StatusType] = None

class BankCompatibilityResponse(BankCompatibilityBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BankCompatibilityListResponse(BaseModel):
    banks: list[BankCompatibilityResponse]
    total: int
