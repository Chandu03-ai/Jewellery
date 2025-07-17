# routers/cartWishlistRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from Database.cartWishlistDb import addToCartDb, getCartDb, addToWishlistDb, getWishlistDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiDatetime.yensiDatetime import formatDateTime
from Models.cartWishlistModel import CartItemModel, WishlistItemModel

router = APIRouter(tags=["Cart & Wishlist"])


@router.post("/cart/add")
async def addToCart(request: Request, payload: CartItemModel):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Adding to cart for user:{userId}")
        cartItem = {
            "id": str(ObjectId()),
            "userId": userId,
            "productId": payload.productId,
            "quantity": payload.quantity,
            "createdAt": formatDateTime(),
        }
        addToCartDb(cartItem)
        logger.info(f"cartItem added sussessfully")
        return returnResponse(2060, result=cartItem)
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return returnResponse(2062)


@router.get("/cart")
async def getCart(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"feetching cart fo use :{userId}")
        cart = list(getCartDb(userId))
        return returnResponse(2061, result=cart)
    except Exception as e:
        logger.error(f"Error fetching cart: {e}")
        return returnResponse(2062)


@router.post("/wishlist/add")
async def addToWishlist(request: Request, payload: WishlistItemModel):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Adding to wishlist for user:{userId}")
        wishlistItem = {
            "id": str(ObjectId()),
            "userId": userId,
            "productId": payload.productId,
            "createdAt": formatDateTime(),
        }
        addToWishlistDb(wishlistItem)
        logger.info(f"wishlistItem added successfully,user:{userId}")
        return returnResponse(2070, result=wishlistItem)
    except Exception as e:
        logger.error(f"Error adding to wishlist: {e}")
        return returnResponse(2072)


@router.get("/wishlist")
async def getWishlist(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"fetching wishlist for user :{userId}")
        wishlist = list(getWishlistDb(userId))
        logger.info(f"wishlist fetched successfully for user:{userId}")
        return returnResponse(2071, result=wishlist)
    except Exception as e:
        logger.error(f"Error fetching wishlist: {e}")
        return returnResponse(2072)
