from pydantic import BaseModel


class CartItemModel(BaseModel):
    productId: str
    quantity: int

class WishlistItemModel(BaseModel):
    productId: str