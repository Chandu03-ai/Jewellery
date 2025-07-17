from pydantic import BaseModel, Field
from typing import List, Optional

class Dimensions(BaseModel):
    length: Optional[float] = 0
    width: Optional[float] = 0
    height: Optional[float] = 0
    weight: Optional[float] = 0

class Specifications(BaseModel):
    material: Optional[str] = ""
    weight: Optional[str] = ""
    dimensions: Optional[str] = ""
    gemstone: Optional[str] = ""
class ProductImportModel(BaseModel):
    name: str
    slug: Optional[str] = None
    category: str
    description: str = ""
    price: float
    comparePrice: Optional[float] = 0
    images: List[str] = Field(default_factory=list)
    preorderAvailable: bool = False
    inStock: bool = True
    specifications: Specifications = Field(default_factory=Specifications)
    rating: Optional[float] = 0.0
    reviews: Optional[int] = 0
    featured: Optional[bool] = False
    tags: List[str] = Field(default_factory=list)
    noOfProducts: int = 0
    variants: dict = Field(default_factory=dict)  # you can also create a nested model if preferred
    visibility: bool = True
    sortOrder: Optional[int] = 0
    viewCount: Optional[int] = 0
    salesCount: Optional[int] = 0
    stockAlert: Optional[int] = 0
    dimensions: Dimensions = Field(default_factory=Dimensions)
    seoKeywords: List[str] = Field(default_factory=list)
    relatedProducts: List[str] = Field(default_factory=list)
    metaTitle: Optional[str] = ""
    metaDescription: Optional[str] = ""

