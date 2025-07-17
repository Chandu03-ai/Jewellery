from pydantic import BaseModel, Field
from typing import Literal, Optional


class VariantModel(BaseModel):
    type: Literal['size', 'metal', 'stone']
    value: str
    isActive: Optional[bool] = True
    sortOrder: Optional[int] = 0


