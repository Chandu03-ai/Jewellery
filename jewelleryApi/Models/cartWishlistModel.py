from pydantic import BaseModel
from typing import List, Optional


class ProductModel(BaseModel):
    name: str
    slug: str
    category: str
    description: Optional[str] = None
    initialPrice: Optional[float] = None
    price: Optional[float] = None
    comparePrice: Optional[float] = None
    images: Optional[List[str]] = []
    stock: Optional[bool] = True
    updatedAt: Optional[str] = None
    id: Optional[str] = None
    createdBy: Optional[str] = None
    createdAt: Optional[str] = None
    isDeleted: Optional[bool] = False


class CartItemModel(BaseModel):
    productId: str
    quantity: int
    product: Optional[ProductModel] = None


class BulkCartRequest(BaseModel):
    items: List[CartItemModel]
