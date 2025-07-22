from pydantic import BaseModel
from typing import Optional


class AddressModel(BaseModel):
    fullName: str
    mobileNumber: str
    pincode: str
    houseNumber: str
    streetArea: str
    landmark: Optional[str] = ""
    city: str
    state: str
    addressType: str  # 'home' | 'office' | 'other'
    isDefault: bool = False


class PincodeResponse(BaseModel):
    pincode: str
    city: str
    state: str
    district: str
    isValid: bool
