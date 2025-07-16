from pydantic import BaseModel, Field
from typing import List, Optional

class Specifications(BaseModel):
    material: str = ""
    weight: str = ""
    dimensions: str = ""
    gemstone: str = ""

class ProductImportModel(BaseModel):
    name: str = ""
    slug: Optional[str] = None
    category: str = ""
    description: str = ""
    price: float = 0.0
    images: List[str] = Field(default_factory=list)
    preorderAvailable: bool = False
    inStock: bool = True
    specifications: Specifications = Field(default_factory=Specifications)
    rating: Optional[float] = 0.0
    reviews: Optional[int] = 0
    featured: Optional[bool] = False
    tags: List[str] = Field(default_factory=list)  # bestseller, trending, newIn
    variants: dict = Field(default_factory=dict)  # metal, size, stone


