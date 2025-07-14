from typing import  Optional, Dict
from pydantic import BaseModel, EmailStr

class CustomerRequest(BaseModel):
    name: Optional[str] = None
    contact: Optional[int] = None
    email: Optional[EmailStr] = None
    fail_existing: Optional[bool] = False
    notes: Optional[Dict[str, str]] = None


class OrderRequest(BaseModel):
    amount: int  
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[Dict[str, str]] = {}


class PaymentCaptureRequest(BaseModel):
    amount: int  # amount in paise
    currency: str = "INR"

