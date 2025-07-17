from pydantic import BaseModel, Field
from typing import Optional, List, Annotated


class ReviewModel(BaseModel):
    userId: str
    rating: Annotated[float, Field(ge=1.0, le=5.0)]
    title: Optional[str] = ""
    comment: str
    images: List[str] = Field(default_factory=list)
    isVerifiedPurchase: Optional[bool] = False
    isApproved: Optional[bool] = None  # for moderation
    helpfulCount: Optional[int] = 0
