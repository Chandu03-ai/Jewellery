from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class OfferApplyRequest(BaseModel):
    code: str
    plan_id: Optional[str] = None

class OfferCreateRequest(BaseModel):
    code: str                        # Unique promo/offer code, e.g., "WELCOME10"
    offer_type: Literal["discount", "cashback"] = "discount"
    amount: Optional[int] = None     # Fixed discount in paise (if applicable)
    percent: Optional[float] = None # Discount percent (e.g., 10.0 for 10%)
    max_discount: Optional[int] = None  # Cap for percentage discounts
    min_subscription_amount: Optional[int] = None  # Minimum subscription amount in paise
    plan_ids: Optional[List[str]] = []  # Limit to specific plan(s)
    usage_limit: Optional[int] = 1   # Number of times this code can be used
    per_user_limit: Optional[int] = 1 # How many times a user can use this code
    start_time: Optional[int] = None # Unix timestamp (optional start time)
    end_time: Optional[int] = None   # Unix timestamp (when the offer expires)
    is_active: bool = True           # Offer is active or not
    created_by: Optional[str] = None  # Optional: Admin or system user who created this
    notes: Optional[Dict[str, str]] = {}  # Any additional data


class OfferDeactivateRequest(BaseModel):
    code: str
