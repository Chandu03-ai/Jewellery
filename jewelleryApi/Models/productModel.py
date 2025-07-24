from pydantic import BaseModel, Field
from typing import List, Optional


class ProductImportModel(BaseModel):
    name: str
    slug: Optional[str] = None  # SEO-friendly URL
    category: str  # slug or ObjectId reference
    description: Optional[str] = ""
    initialPrice: float  # what admin paid
    price: float  # selling price to customer
    comparePrice: Optional[float] = 0  # optional MRP
    images: List[str] = Field(default_factory=list)
    stock: bool = True
    details: Optional[str] = None
