from pydantic import BaseModel, Field
from typing import Optional


class TagModel(BaseModel):
    name: str
    slug: Optional[str] = None
    color: Optional[str] = "#000000"  # default black
    isActive: Optional[bool] = True
    sortOrder: Optional[int] = 0
    productCount: Optional[int] = 0


class TagUpdateModel(BaseModel):
    tags: list[str]


