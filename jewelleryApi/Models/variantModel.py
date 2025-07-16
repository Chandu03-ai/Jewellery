from pydantic import BaseModel
from typing import Literal

class VariantModel(BaseModel):
    type: Literal["size", "metal", "stone"]
    value: str
