from pydantic import BaseModel, Field
from typing import Optional

class ShipmentRequestModel(BaseModel):
    orderId: str
    customerName: str
    customerPhone: str
    customerEmail: Optional[str] = ""
    addressLine1: str
    addressLine2: Optional[str] = ""
    city: str
    state: str
    pincode: str
    country: str = "India"
    productName: str
    productQuantity: int = Field(gt=0)
    productWeight: float = Field(gt=0)
    declaredValue: float = Field(gt=0)
    # paymentMode: str = Field(..., regex="^(COD|Prepaid)$")
