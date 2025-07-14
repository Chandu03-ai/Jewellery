from typing import List,  Optional, Dict
from pydantic import BaseModel, EmailStr

class AddonItem(BaseModel):
    name: str
    amount: int
    currency: str = "INR"
    
class Addon(BaseModel):
    item: AddonItem

class NotifyInfo(BaseModel):
    notify_email: Optional[EmailStr] = None
    notify_phone: Optional[int] = None

class SubscriptionRequest(BaseModel):
    plan_id: str 
    subscriptionType:Optional[str] = None
    teamName: Optional[str] = None
    quantity: Optional[int] = 1  # Number of units; defaults to 1
    total_count: Optional[int] = 12  # Number of billing cycles; required if 'expire_by' not set
    customer_notify: bool = True  # Notify customer via email/SMS; default is True
    expire_by: Optional[int] = None  # Unix timestamp after which subscription expires
    addons: Optional[List[Addon]] = []  # Optional list of add-ons to include in the subscription
    notes: Optional[Dict[str, str]] = {}  # Custom notes (metadata) for internal tracking
    notify_info: Optional[NotifyInfo] = None  # Optional contact info overrides
    offer_id: Optional[str] = None  # Optional Razorpay offer ID for discounts


class SubscriptionUpdateRequest(BaseModel):
    subscriptionId: str
    plan_id: Optional[str] = None
    offer_id: Optional[str] = None
    quantity: Optional[int] = None
    remaining_count: Optional[int] = None
    start_at: Optional[int] = None
    schedule_change_at: Optional[str] = None  # "now" or "cycle_end"
    customer_notify: Optional[bool] = True