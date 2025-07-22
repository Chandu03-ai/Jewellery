from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr


class CustomerRequest(BaseModel):
    name: Optional[str] = None
    contact: Optional[int] = None
    email: Optional[EmailStr] = None
    fail_existing: Optional[bool] = False
    notes: Optional[Dict[str, str]] = None


class PaymentCaptureRequest(BaseModel):
    amount: int  # amount in paise
    currency: str = "INR"


class Item(BaseModel):
    productId: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[int] = None
    name: Optional[str] = None
    image: Optional[str] = None


class ShippingAddress(BaseModel):
    fullName: Optional[str] = None
    mobileNumber: Optional[str] = None
    pincode: Optional[str] = None
    houseNumber: Optional[str] = None
    streetArea: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    addressType: Optional[str] = None
    isDefault: Optional[bool] = None
    id: Optional[str] = None
    userId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    isDeleted: Optional[bool] = None


class OrderRequest(BaseModel):
    amount: Optional[int]
    currency: Optional[str] = "INR"
    receipt: Optional[str]
    notes: Optional[Dict[str, str]]
    items: Optional[List[Item]]
    shippingAddress: Optional[ShippingAddress]
