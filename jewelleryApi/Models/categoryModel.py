from pydantic import BaseModel
from typing import List, Literal, Optional


class CategoryModel(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None  # icon/banner
    sizeOptions: Optional[List[str]] = None
    categoryType: Optional[Literal["handmade", "handloom"]] = None


class UpdateCategoryModel(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    image: Optional[str] = None
    sizeOptions: Optional[List[str]] = None
    categoryType: Optional[Literal["handmade", "handloom"]] = None
