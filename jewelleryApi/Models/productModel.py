from pydantic import BaseModel
from typing import List, Optional



class ProductSpecifications(BaseModel):
    material: str
    weight: str
    dimensions: str
    gemstone: str


class ProductModel(BaseModel):
    name: str
    category: str
    description: Optional[str]
    price: float
    images: List[str] = []
    preorderAvailable: bool
    inStock: bool
    specifications: ProductSpecifications
    rating: Optional[float] = 0
    reviews: Optional[int] = 0
    featured: bool = False

