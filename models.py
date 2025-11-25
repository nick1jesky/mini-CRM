from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DATABASE_DIR, 'leads.db')}"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)
    current_load = Column(Integer, default=0)
    
    assignments = relationship("OperatorSourceAssignment", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contacts = relationship("Contact", back_populates="lead")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    assignments = relationship("OperatorSourceAssignment", back_populates="source")
    contacts = relationship("Contact", back_populates="source")

class OperatorSourceAssignment(Base):
    __tablename__ = "operator_source_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Integer, default=1)
    
    operator = relationship("Operator", back_populates="assignments")
    source = relationship("Source", back_populates="assignments")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    message = Column(String)
    status = Column(String, default="new")  
    created_at = Column(DateTime, default=datetime.now())
    
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")