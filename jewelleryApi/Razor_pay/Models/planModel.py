from typing import Literal
from pydantic import BaseModel


class PlanItem(BaseModel):
    name: str
    amount: int  # in paise
    currency: str = "INR"
    description: str


class Notes(BaseModel):
    type: Literal["Solo", "Team", "Enterprise"]
    tokens: int  # or str if you prefer
    model_config = {
        "extra": "allow"  
    }


class PlanRequest(BaseModel):
    period: Literal["weekly","monthly", "yearly"]
    interval: int
    item: PlanItem
    notes: Notes