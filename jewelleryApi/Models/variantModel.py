from pydantic import BaseModel
from typing import List, Literal, Optional

class Variants(BaseModel):
    colors: List[str] = []
    sizes: List[str] = []
    materials: List[str] = []
    size: Optional[str] = ""
    metal: Optional[str] = ""
    stone: Optional[str] = ""
