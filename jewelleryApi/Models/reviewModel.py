from pydantic import BaseModel, Field
from typing import Optional, Annotated

class ReviewModel(BaseModel):
    userId: str
    rating: Annotated[float, Field(ge=1.0, le=5.0)]
    comment: Optional[str] = ""
