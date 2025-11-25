from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, AsyncGenerator
from contextlib import asynccontextmanager

from models import Base, engine, AsyncSessionLocal
from schemas import *
from services import DistributionService

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating database tables...")
    await create_tables()
    yield
    print("Shutting down...")
    await engine.dispose()

app = FastAPI(
    title="Lead Distribution CRM",
    lifespan=lifespan
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.post("/operators/", response_model=Operator)
async def create_operator(operator: OperatorCreate, db: AsyncSession = Depends(get_db)):
    from models import Operator
    db_operator = Operator(**operator.model_dump())
    db.add(db_operator)
    await db.commit()
    await db.refresh(db_operator)
    return db_operator

@app.get("/operators/", response_model=List[Operator])
async def read_operators(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models import Operator
    result = await db.execute(select(Operator).offset(skip).limit(limit))
    operators = result.scalars().all()
    return operators

@app.patch("/operators/{operator_id}", response_model=Operator)
async def update_operator(operator_id: int, operator_update: OperatorCreate, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models import Operator
    result = await db.execute(select(Operator).where(Operator.id == operator_id))
    operator = result.scalar_one_or_none()
    
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    update_data = operator_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operator, field, value)
    
    await db.commit()
    await db.refresh(operator)
    return operator

@app.post("/sources/", response_model=Source)
async def create_source(source: SourceCreate, db: AsyncSession = Depends(get_db)):
    from models import Source
    db_source = Source(**source.model_dump())
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    return db_source

@app.get("/sources/", response_model=List[Source])
async def read_sources(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models import Source
    result = await db.execute(select(Source).offset(skip).limit(limit))
    sources = result.scalars().all()
    return sources

@app.post("/assignments/", response_model=Assignment)
async def create_assignment(assignment: AssignmentCreate, db: AsyncSession = Depends(get_db)):
    from models import OperatorSourceAssignment
    db_assignment = OperatorSourceAssignment(**assignment.model_dump())
    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)
    return db_assignment

@app.post("/contacts/", response_model=Contact)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    distribution_service = DistributionService(db)
    contact_data = contact.model_dump()
    return await distribution_service.create_contact(contact_data)

@app.get("/contacts/", response_model=List[Contact])
async def read_contacts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models import Contact
    result = await db.execute(select(Contact).offset(skip).limit(limit))
    contacts = result.scalars().all()
    return contacts

@app.get("/leads/", response_model=List[Lead])
async def read_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models import Lead
    result = await db.execute(select(Lead).offset(skip).limit(limit))
    leads = result.scalars().all()
    return leads