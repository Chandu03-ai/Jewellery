from pydantic import BaseModel
from typing import Optional


class CategoryModel(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None  # icon/banner


class UpdateCategoryModel(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    image: Optional[str] = None
