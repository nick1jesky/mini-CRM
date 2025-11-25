from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10

class OperatorCreate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int
    current_load: int
    
    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    external_id: str
    email: Optional[str] = None
    phone: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    name: str

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    
    class Config:
        from_attributes = True

class AssignmentBase(BaseModel):
    operator_id: int
    source_id: int
    weight: int = 1

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int
    
    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    message: Optional[str] = None
    status: str = "new"

class ContactCreate(BaseModel):
    external_id: str
    source_id: int
    message: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class Contact(ContactBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True