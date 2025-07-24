from pydantic import BaseModel
from typing import List, Optional


class CategoryModel(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None  # icon/banner
    parentId: Optional[str] = None
    isParent: Optional[bool] = True
    sizeOptions: Optional[List[str]] = None


class UpdateCategoryModel(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    image: Optional[str] = None
    parentId: Optional[str] = None
    isParent: Optional[bool] = None
    sizeOptions: Optional[List[str]] = None
