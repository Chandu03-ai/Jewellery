from pydantic import BaseModel, Field

class ShipmentModel(BaseModel):
    trackingNumber: str = Field(..., description="Tracking ID from courier partner")
    orderId: str = Field(..., description="Internal order ID")
