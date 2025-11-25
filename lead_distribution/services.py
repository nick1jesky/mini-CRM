from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import random
from models import Lead, Contact, Operator, OperatorSourceAssignment

class DistributionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def find_or_create_lead(self, external_id: str, email: str = None, phone: str = None) -> Lead:
        result = await self.db.execute(
            select(Lead).where(Lead.external_id == external_id)
        )
        lead = result.scalar_one_or_none()
        
        if not lead:
            lead = Lead(external_id=external_id, email=email, phone=phone)
            self.db.add(lead)
            await self.db.commit()
            await self.db.refresh(lead)
        return lead
    
    async def get_available_operators(self, source_id: int) -> list:
        result = await self.db.execute(
            select(OperatorSourceAssignment)
            .options(selectinload(OperatorSourceAssignment.operator))
            .where(OperatorSourceAssignment.source_id == source_id)
        )
        assignments = result.scalars().all()
        
        available_operators = []
        for assignment in assignments:
            operator = assignment.operator
            if (operator.is_active and 
                operator.current_load < operator.max_load):
                available_operators.append({
                    'operator': operator,
                    'weight': assignment.weight
                })
        
        return available_operators
    
    def select_operator(self, available_operators: list) -> Operator:
        if not available_operators:
            return None
        
        total_weight = sum(op['weight'] for op in available_operators)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for op_data in available_operators:
            current_weight += op_data['weight']
            if random_value <= current_weight:
                return op_data['operator']
        
        return available_operators[0]['operator']
    
    async def create_contact(self, contact_data: dict) -> Contact:
        lead = await self.find_or_create_lead(
            external_id=contact_data['external_id'],
            email=contact_data.get('email'),
            phone=contact_data.get('phone')
        )
        
        available_operators = await self.get_available_operators(contact_data['source_id'])
        operator = self.select_operator(available_operators)
        
        contact = Contact(
            lead_id=lead.id,
            source_id=contact_data['source_id'],
            operator_id=operator.id if operator else None,
            message=contact_data.get('message')
        )
        
        self.db.add(contact)
        
        if operator:
            operator.current_load += 1
        
        await self.db.commit()
        await self.db.refresh(contact)
        return contact