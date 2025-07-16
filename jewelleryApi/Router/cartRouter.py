# routers/cartWishlistRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from pydantic import BaseModel
from Database.cartWishlistDb import (
    addToCartDb, getCartDb,
    addToWishlistDb, getWishlistDb
)
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiDatetime.yensiDatetime import formatDateTime
from Models.cartWishlistModel import CartItemModel, WishlistItemModel
router = APIRouter(tags=["Cart & Wishlist"])



@router.post("/cart/add")
async def add_to_cart(request: Request, payload: CartItemModel):
    user_id = request.state.userMetadata.get("id")
    try:
        cart_item = {
            "id": str(ObjectId()),
            "userId": user_id,
            "productId": payload.productId,
            "quantity": payload.quantity,
            "createdAt": formatDateTime(),
        }
        addToCartDb(cart_item)
        return returnResponse(2060, result=cart_item)
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return returnResponse(2062)

@router.get("/cart")
async def get_cart(request: Request):
    user_id = request.state.userMetadata.get("id")
    try:
        cart = list(getCartDb(user_id))
        return returnResponse(2061, result=cart)
    except Exception as e:
        logger.error(f"Error fetching cart: {e}")
        return returnResponse(2062)

@router.post("/wishlist/add")
async def add_to_wishlist(request: Request, payload: WishlistItemModel):
    user_id = request.state.userMetadata.get("id")
    try:
        wishlist_item = {
            "id": str(ObjectId()),
            "userId": user_id,
            "productId": payload.productId,
            "createdAt": formatDateTime(),
        }
        addToWishlistDb(wishlist_item)
        return returnResponse(2070, result=wishlist_item)
    except Exception as e:
        logger.error(f"Error adding to wishlist: {e}")
        return returnResponse(2072)

@router.get("/wishlist")
async def get_wishlist(request: Request):
    user_id = request.state.userMetadata.get("id")
    try:
        wishlist = list(getWishlistDb(user_id))
        return returnResponse(2071, result=wishlist)
    except Exception as e:
        logger.error(f"Error fetching wishlist: {e}")
        return returnResponse(2072)