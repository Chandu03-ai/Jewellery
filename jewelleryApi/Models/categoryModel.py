from pydantic import BaseModel, Field
from typing import Optional


class CategoryModel(BaseModel):
    name: str
    description: Optional[str] = ""
    slug: Optional[str] = None
    image: Optional[str] = ""  # URL or path
    parentCategory: Optional[str] = None  # ObjectId as string
    sortOrder: Optional[int] = 0
    isActive: Optional[bool] = True
    metaTitle: Optional[str] = ""
    metaDescription: Optional[str] = ""
    productCount: Optional[int] = 0
