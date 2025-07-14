from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class AdjustTokenRequest(BaseModel):
    tokens: int
    type: str  # consume | bonus | refund 
    reason: str
    meta: Optional[dict] = {}

class TopUpRequest(BaseModel):
    tokens: int  # Number of tokens to top up or reset
    reason: Optional[str] = "Top-up via Razorpay"
    meta: Optional[Dict] = {}

    # Optional subscription-related fields
    cycleStart: Optional[str] = None  # Format: YYYYMMDDHHMMSS
    cycleEnd: Optional[str] = None    # Format: YYYYMMDDHHMMSS
    planId: Optional[str] = None
    subscriptionId: Optional[str] = None

class TokenBalance(BaseModel):
    userId: str
    planId: str
    subscriptionId: str
    currentTokens: int
    totalAllocated: int
    cycleStart: datetime
    cycleEnd: datetime
    lastUpdated: datetime

class TokenLog(BaseModel):
    userId: str
    type: str  # consume | topup | bonus | refund | reset
    tokens: int
    reason: str
    meta: Optional[Dict] = Field(default_factory=dict)
    timestamp: datetime